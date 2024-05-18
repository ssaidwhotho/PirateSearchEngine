# Path: invertedIndex.py
import json
import os
import sys
import psutil

from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from posting import Posting
from bs4 import BeautifulSoup
from hashing import sim_hash, Simhash

SAVE_FREQ = 10000


def get_tokens(document) -> list:
    try:
        current_doc = document['content']  # Copy current document
        soup = BeautifulSoup(current_doc, 'xml')  # Parse the document with BeautifulSoup
        for script in soup(["script", "style"]):
            script.extract()
        clean_text = soup.get_text()  # Get the text from the document
        tokens = word_tokenize(clean_text)
        tokens = [token.lower() for token in tokens if
                  token.isalnum() or (token.replace(".", "").isalnum() and len(token) > 1)]
        p_stemmer = PorterStemmer()
        tokens = [p_stemmer.stem(word) for word in tokens]  # Stem using PorterStemmer
        return tokens
    except Exception as e:
        print(document['content'])
        print(f"Error: {e}")
        return []


def get_memory_usage():
    # Get the current memory usage of the program by percentage of total memory
    process = psutil.Process(os.getpid())
    return process.memory_percent()


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
        # firstly we need to read all the documents
        for root, dirs, files in os.walk('DEV'):
            for file in files:
                if file.endswith('.json'):
                    documents.append(self.read_json(os.path.join(root, file)))  # read the json file

        print(f"Total documents to search: {len(documents)}")

        self.build_index(documents)  # build the inverted index

    def compare_hash(self, obj: Simhash, url: str) -> bool:
        # compare the hash with the existing hashes
        # if the result is greater than 0.9 then the hashes are similar
        if len(self.bits) == 0:
            self.bits.append((obj, url))
            return False
        for other_hash in self.bits:
            if obj.similarity(other_hash[0]) >= 0.9:
                # print(f"Document {url} is a duplicate of {other_hash[1]}. Skipping.")
                return True
        self.bits.append((obj, url))
        return False

    def build_index(self, documents: list) -> None:
        print(f"Starting to create the inverted index.")

        while len(documents) > 0:
            batch = documents[:SAVE_FREQ]  # Get the first 1000 documents
            documents = documents[SAVE_FREQ:]  # Remove the first 1000 documents
            for document in batch:
                tokens = get_tokens(document)
                # hash the tokens and create the inverted index
                if self.compare_hash(sim_hash(tokens), document['url']):  # Check if the document is a duplicate
                    continue
                self.id += 1
                doc_len = len(tokens)
                self.url_dict[self.id] = (document['url'], doc_len)  # save the url and the length of the document
                # we save the length though tbh
                fields = None  # TODO: get the fields from the document (bold, italic, headers, title, etc.)

                for i in range(len(tokens)):  # Loop through all the tokens
                    if tokens[i] not in self.hash_table:
                        self.hash_table[tokens[i]] = {self.id: Posting(self.id)}
                    elif self.id not in self.hash_table[tokens[i]]:
                        self.hash_table[tokens[i]][self.id] = Posting(self.id)

                    self.hash_table[tokens[i]][self.id].increment()  # increment the word count
                    self.hash_table[tokens[i]][self.id].add_position(i)  # add the position of the token

            # memory = get_memory_usage()
            # print(f"Memory usage is {memory}%")
            # if get_memory_usage() > 10:

            self.sort_and_save_batch()  # generate partial files
            print(f"Finished creating inverted index for batch {self.id + 1}")
            self.hash_table = dict()  # clear the hash table

        if len(self.hash_table) > 0:
            self.sort_and_save_batch()
            self.hash_table = dict()

        print("Finished creating the inverted index now merging files.")
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
                        f"p{self.hash_table[key][doc_id].positions}")  # positions [list]
                new_save_file.write("\n")
            self.save_files.append(f'inverted_index_{self.name}.txt')

        self.id += 1
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
        term_dict = dict()
        lines = []
        for i in range(len(file_handles)):
            line = file_handles[i].readline()
            if line == '':
                continue
            lines.append(line)
            term = line.split(' ')[0]
            if term not in term_dict:
                term_dict[term] = []
            term_dict[term].append(i)

        # merge the files
        with open('inverted_index.txt', 'w') as f:
            while len(lines) > 0:
                min_term = min([line.split(' ')[0] for line in lines])  # get the minimum term (alphabetically)
                min_lines = [line for line in lines if line.split(' ')[0] == min_term]  # get all the lines with the term
                # merge the lines
                merged_line = min_term[0]
                for line in min_lines:
                    merged_line += line.split(' ')[1:]  # add the rest of the line besides the term
                f.write(merged_line)
                # read the next line
                for fd in term_dict[min_term]:  # get the file descriptor
                    line = file_handles[fd].readline() # get the next line in the files that were read
                    if line == '':
                        lines.remove(lines[fd])
                    else:
                        lines[fd] = line
                        term = line.split(' ')[0]
                        if term not in term_dict:
                            term_dict[term] = []
                        term_dict[term].append(fd)
                    # remove entry from term_dict list
                    term_dict[min_term].remove(fd)
                    if len(term_dict[min_term]) == 0:
                        del term_dict[min_term]

        # close all the files
        for file in file_handles:
            file.close()
            # os.remove(file.name)

        # TODO: Make bookkeeping for indexing the inverted_index.txt file
        # TODO: Get td-idf for each term :( so sad idk where to put that though
        print("Saving the url dictionary.")
        with open('url_dict.txt', 'w') as url_file:
            for key in self.url_dict.keys():
                url_file.write(f"{key} {self.url_dict[key][0]} {self.url_dict[key][1]}\n")
                # format = key url length
                # can maybe make this a json for faster lookup tbh
        print("Finished merging all files.")


if __name__ == "__main__":
    inverted_index = InvertedIndex()
    inverted_index.create_inverted_index()
    exit(0)
