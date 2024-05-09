# Path: invertedIndex.py
import re
import json
import os
from nltk.tokenize import word_tokenize



class InvertedIndex:
    def __init__(self):
        self.hash_table = {}

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
        n = 0
        # documents are json files
        for document in documents:
            n += 1

            curr_url = document['url']  # This url needs to be saved to a json where key = n, value = url
            tokens = self.get_tokens(document)
            # tokens = list(set(tokens))  # Part of the Sudo-Code, but doesn't make any sense...

            doc_len = len(tokens)
            fields = None  #TODO: Figure out what this is

            for token in tokens:
                if token not in self.hash_table:
                    self.hash_table[token] = {n: Posting(n, doc_len, fields)}

                elif n not in self.hash_table[token]:
                    self.hash_table[token][n] = Posting(n, doc_len, fields)

                self.hash_table[token][n].increment(n)
        # TODO: Save the url to a json file

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
