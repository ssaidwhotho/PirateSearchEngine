# Path: invertedIndex.py
import re
import json
import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer



class InvertedIndex:
    def __init__(self):
        self.hash_table = {}
        self.url_dict = {}
        self.save_files = []

    @staticmethod
    def read_json(file_path) -> dict:
        # read json file directly and return the dictionary
        with open(file_path, 'r') as file:
            return json.load(file)

    def get_tokens(self, document) -> list:
        current_doc = document['content']  # Copy current document to use regex
        clean_text = re.sub('<[^>]*>', '', current_doc)
        tokens = word_tokenize(clean_text)
        tokens = [token.lower() for token in tokens if
                  token.isalnum() or (token.replace(".", "").isalnum() and len(token) > 1)]
        return tokens

    def build_index(self, documents) -> None:
        n = -1  # So it starts with 0
        # documents are json files
        for document in documents:
            n += 1

            curr_url = document['url']  # This url needs to be saved to a json where key = n, value = url
            self.url_dict[n] = curr_url
            tokens = self.get_tokens(document)
            p_stemmer = PorterStemmer()
            tokens = [p_stemmer.stem(word) for word in tokens]  # Stem using PorterStemmer
            # tokens = list(set(tokens))  # Part of the Sudo-Code, but doesn't make any sense...

            doc_len = len(tokens)
            fields = None  #TODO: Make a list of bolded & header (important) words

            for token in tokens:
                if token not in self.hash_table:
                    self.hash_table[token] = {n: Posting(n, doc_len, fields)}

                elif n not in self.hash_table[token]:
                    self.hash_table[token][n] = Posting(n, doc_len, fields)

                self.hash_table[token][n].increment(n)

            if n % 10 == 0:
                print(f"Processed {n} documents, saving to json file...")
                self.save_to_json(n)

        print("Finished processing all documents, saving final hash_table to json.")
        if self.hash_table != {}:
            self.save_to_json((n + 9) // 10 * 10) # Round up to nearest 10 for the file_name

    def save_doc_id_json(self, n) -> None:
        # Save to json file
        with open('url_ids.json', 'w') as new_save_file:
            json.dump(self.url_dict, new_save_file)

    def save_to_json(self, n) -> None:
        # Save to json file
        new_file_name = f'inverted_index{n / 10}.json'
        with open(new_file_name, 'w') as new_save_file:
            json.dump(self.convert_inner_dict_to_list(), new_save_file)
            self.hash_table = {}
            self.save_files.append(new_file_name)

    def convert_inner_dict_to_list(self) -> dict:
        new_hash_table = dict()
        for key in self.hash_table.keys():
            new_hash_table[key] = [self.hash_table[key][i] for i in range(len(self.hash_table[key].keys()))]
        return new_hash_table


class Posting:
    def __init__(self, doc_id, doc_len, fields):
        self.doc_id = doc_id
        self.word_count = 0
        self.doc_len = doc_len
        self.tfidf = self.word_count / self.doc_len  # Frequency works for now, updates every word_count increment
        self.fields = fields

    def increment(self):
        self.word_count += 1
        self.tfidf = self.word_count / self.doc_len # Update for new frequency

    def get_doc_id(self):
        return self.doc_id


if __name__ == "__main__":
    # need to recursively read all files in the directory
    # directory = 'DEV'
    # documents = []

    # read documents and make the InvertedIndex
    # json.dumps() every page in Dev :) use os most likely
    # inverted_index = InvertedIndex()
    # inverted_index.build_index(documents)
    directory = 'DEV'
    documents = []
    inverted_index = InvertedIndex()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                documents.append(inverted_index.read_json(os.path.join(root, file)))
                print(documents)

    exit()
