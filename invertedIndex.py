# Path: invertedIndex.py
import json
import math
import os
import sys
import time
from urllib.parse import urldefrag
import tokenizer

import psutil

from posting import Posting
from hashing import sim_hash, Simhash

SAVE_FREQ = 10000


class InvertedIndex:
    def __init__(self):
        self.id = -1
        self.hash_table = {}
        self.url_dict = {}
        self.save_files = []
        self.bits = []

        self.name = 0  # name of file

    @staticmethod
    def read_json(file_path) -> dict:
        # read json file directly and return the dictionary
        with open(file_path, 'r') as j_file:
            return json.load(j_file)

    def create_inverted_index(self) -> None:
        """
        This function is the starting function for creating the inverted index.
        :return:
        """
        documents = []
        print(f"Starting to create the inverted index.")
        skipped_documents = 0
        sim_hashes_so_far = []
        # firstly we need to read all the documents
        for root, dirs, files in os.walk('DEV'):
            for file in files:
                if file.endswith('.json'):
                    document = self.read_json(os.path.join(root, file))
                    if len(document['content']) < 30:
                        skipped_documents += 1
                        continue
                    sim_hashes_so_far.append((sim_hash(tokenizer.tokenize(document['content'])), document))
                    if len(sim_hashes_so_far) % 1000 == 0:
                        print(f"Read {len(sim_hashes_so_far)} documents.")

        # now compare and populate document list
        # O(n^2) but it's fine i hope
        for i in range(len(sim_hashes_so_far)):
            for j in range(i + 1, len(sim_hashes_so_far)):
                if self.compare_hash(sim_hashes_so_far[i][0], sim_hashes_so_far[j][1]['url']):
                    skipped_documents += 1
                    break
            if i % 1000 == 0:
                print(f"Compared {i} documents.")
            documents.append(sim_hashes_so_far[i][1])

        print(f"Finished reading all documents.")
        print(f"Total documents to search: {len(documents)}")
        with open("save_for_later.txt", 'w') as save_file:
            for doc in documents:
                save_file.write(f"{doc['url']}\n")
        self.build_index(documents)  # build the inverted index

    def compare_hash(self, obj: Simhash, url: str) -> bool:
        # compare the hash with the existing hashes
        # if the result is greater than 0.9 then the hashes are similar
        if len(self.bits) == 0:
            self.bits.append((obj, url))
            return False
        for other_hash in self.bits:
            if obj.similarity(other_hash[0]) >= 0.9:
                return True
        self.bits.append((obj, url))
        return False

    def build_index(self, documents: list) -> None:
        print(f"Starting to create the inverted index.")
        skipped_documents = 0
        n = 0
        for doc in documents:
            self.url_dict[n] = (doc['url'], 0)
            n += 1
        while len(documents) > 0:
            batch = documents[:SAVE_FREQ]  # Get the first 10000 documents
            documents = documents[SAVE_FREQ:]  # Remove the first 10000 documents
            for document in batch:
                tokens, links = tokenizer.get_tokens(document)
                # hash the tokens and create the inverted index
                self.id += 1
                self.url_dict[self.id] = (document['url'], len(tokens))
                for token in tokens.keys():
                    if token not in self.hash_table:
                        self.hash_table[token] = {self.id: Posting(self.id)}
                    elif self.id not in self.hash_table[token]:
                        self.hash_table[token][self.id] = Posting(self.id)

                    self.hash_table[token][self.id].word_count = tokens[token][0]
                    self.hash_table[token][self.id].positions = tokens[token][3]
                    if tokens[token][1]:
                        self.hash_table[token][self.id].tfidf += 2
                    if tokens[token][2]:
                        self.hash_table[token][self.id].tfidf += 1

                for hyper_links in links:
                    if hyper_links[0] in self.url_dict.values():
                        # tokenize the text
                        tokens = tokenizer.tokenize(hyper_links[1])
                        for token in tokens:
                            if token not in self.hash_table:
                                self.hash_table[token] = {self.id: Posting(self.id)}
                            elif self.id not in self.hash_table[token]:
                                self.hash_table[token][self.id] = Posting(self.id)

                            self.hash_table[token][self.id].tfidf += 3

            # save the batch to a file
            self.sort_and_save_batch()  # generate partial files
            print(f"Finished creating inverted index for batch {self.id + 1}")
            self.hash_table = dict()  # clear the hash table

        if len(self.hash_table) > 0:
            self.sort_and_save_batch()
            self.hash_table = dict()

        print("Finished creating the inverted index now merging files.")
        print(f"Skipped {skipped_documents} documents.")
        self.merge_files()

    def sort_and_save_batch(self) -> None:
        # sort the hash table and save to custom txt file for seeking
        # sort the dictionary by the keys alphabetically with numbers last
        self.hash_table = dict(sorted(self.hash_table.items(), key=lambda x: (not x[0].isnumeric(), x[0])))
        # every new line is a token, and it's posting is to the right of the line
        # create a new file for the batch
        with open(f'inverted_index_{self.name}.txt', 'w') as new_save_file:
            for key in self.hash_table.keys():
                new_save_file.write(key)
                for doc_id in self.hash_table[key].keys():
                    new_save_file.write(
                        f" d{doc_id}"  # document id
                        f"w{self.hash_table[key][doc_id].word_count}"  # word count
                        f"t{self.hash_table[key][doc_id].tfidf}"  # tf-idf
                        f"p{self.hash_table[key][doc_id].get_positions_str()}")  # positions [list]
                new_save_file.write("\n")
            self.save_files.append(f'inverted_index_{self.name}.txt')

        self.name += 1

    def merge_files(self) -> None:
        # Merge all the files into one
        if len(self.save_files) == 0:
            print("No files to merge.")
            return

        print("Starting to merge all files into one.")
        # open all the files!
        # attempting multi-file merge
        file_handles = []
        for file in self.save_files:
            file_handles.append(open(file, 'r'))

        # read a line for every file and then populate a term dictionary
        term_dict = {}
        lines = {i: file_handles[i].readline() for i in range(len(file_handles))}
        for i in range(len(file_handles)):
            line = lines[i]
            if line == '':
                lines.pop(i)
            else:
                term = line.split(' ')[0]
                if term not in term_dict:
                    term_dict[term] = []
                term_dict[term].append(i)

        # merge the files
        with open('inverted_index.txt', 'w') as f:
            while len(lines) > 0:
                min_term = min(term_dict.keys())
                min_lines = [lines[i] for i in term_dict[min_term]]
                # merge the lines
                merged_line = [min_term]
                postings = []
                for line in min_lines:
                    # create postings to get tf-idf
                    postings.extend(line.split(' ')[1:])
                    merged_line.extend(line.split(' ')[1:])

                # calculate tf-idf
                doc_freq = len(postings)
                total_docs = len(self.url_dict)
                for posting in postings:
                    # format = d{doc_id}w{word_count}t{tfidf}p{positions:list}
                    doc_id = int(posting[1:posting.index('w')])
                    word_count = int(posting[posting.index('w') + 1:posting.index('t')])
                    doc_len = self.url_dict[int(doc_id)][1]
                    tf = word_count / doc_len
                    idf = 1 + math.log(total_docs / doc_freq)
                    tfidf = tf * idf
                    # find the t index
                    t_index = merged_line.index(posting)
                    # get the tfidf value saved in the posting
                    old_tfidf = float(posting[posting.index('t') + 1:posting.index('p')])
                    new_posting = (posting[:posting.index('t')] +
                                   f"t{tfidf + old_tfidf:.4f}{''.join(posting[posting.index('t') + 2:])}")
                    merged_line[t_index] = new_posting
                merged_line = ' '.join(merged_line)
                # take out all the new lines
                merged_line = merged_line.replace('\n', '')
                f.write(merged_line + '\n')
                # read the next line
                for i in term_dict[min_term]:
                    lines[i] = file_handles[i].readline()
                    if lines[i] == '':
                        lines.pop(i)
                    else:
                        term = lines[i].split(' ')[0]
                        if term not in term_dict:
                            term_dict[term] = []
                        term_dict[term].append(i)
                term_dict.pop(min_term)

        # close all the files
        for file in file_handles:
            file.close()
            os.remove(file.name)

        print("Creating the bookkeeping file.")
        with open('inverted_index.txt', 'r') as f:
            # get the positions of each token
            token_list = []
            token_pos_list = []
            while True:
                pos = f.tell()  # get the position of the file for seek
                line = f.readline()  # read the line
                if not line:
                    break
                if line[0] == " ":  #TODO: Fix the inverted index then remove this
                    continue
                word = line.split(' ')[0]
                token_list.append(word)
                token_pos_list.append(pos)
            # save the positions
            with open('token_positions_list.txt', 'w') as pos_file:
                for i in range(len(token_list)):
                    pos_file.write(f"{token_list[i]}:{token_pos_list[i]}\n")

        print("Saving the url dictionary.")
        with open('url_dict.txt', 'w') as url_file:
            for key in self.url_dict.keys():
                url_file.write(f"{key} {self.url_dict[key][0]} {self.url_dict[key][1]}\n")
                # format = key url length
                # can maybe make this a json for faster lookup tbh
        print("Finished merging all files.")


if __name__ == "__main__":
    inverted_index = InvertedIndex()
    # inverted_index.create_inverted_index()
    # TODO: Uncomment the above line for full run and uncomment the below lines to run the inverted index creation with Adam's info
    # documents = []
    # documents_read = 0
    # with open("url_dict.txt", 'r') as f:
    #     # find the document[url] that matches with the url and populate a list of docs
    #     document_dict = {}
    #     for root, dirs, files in os.walk('DEV'):
    #         for file in files:
    #             if file.endswith('.json'):
    #                 document = inverted_index.read_json(os.path.join(root, file))
    #                 document_dict[document['url']] = document
    #     print("reading the url_dict.txt file.")
    #     for line in f:
    #         doc_id, url, doc_len = line.split(' ')
    #         # now look through dev folder to find the document
    #         if url in document_dict:
    #             documents.append(document_dict[url])
    #             documents_read += 1
    #         if documents_read % 2500 == 0:
    #             print(f"Read {documents_read} documents.")
    #     document_dict = {}
    #
    # print("read all the documents.")
    # inverted_index.build_index(documents)
    exit(0)
