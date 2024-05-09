# Path: invertedIndex.py
import re
import json
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


SAVE_FREQ = 100



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
        p_stemmer = PorterStemmer()
        tokens = [p_stemmer.stem(word) for word in tokens]  # Stem using PorterStemmer
        return tokens

    def build_index(self, documents) -> None:
        n = -1
        # documents are json files
        for document in documents:
            n += 1

            curr_url = document['url']  # This url needs to be saved to a json where key = n, value = url
            tokens = self.get_tokens(document)
            # tokens = list(set(tokens))  # Part of the Sudo-Code, but doesn't make any sense...

            doc_len = len(tokens)
            self.url_dict[n] = (curr_url, doc_len)
            fields = None  #TODO: Make a list of bolded & header (important) words

            for token in tokens:
                if token not in self.hash_table:
                    self.hash_table[token] = {n: Posting(n, doc_len, fields)}

                elif n not in self.hash_table[token]:
                    self.hash_table[token][n] = Posting(n, doc_len, fields)

                self.hash_table[token][n].increment()

            if n % SAVE_FREQ == 0 and n != 0:
                print(f"Processed {n} documents, saving to json file...")
                self.save_to_json(n)

        print(f"Finished processing all {n} documents, saving final hash_table to json.")
        if self.hash_table != {}:
            self.save_to_json((n + (SAVE_FREQ-1)) // SAVE_FREQ * SAVE_FREQ) # Round up to nearest SAVE_FREQ for the file_name

    def save_doc_id_json(self) -> None:
        # Save to json file
        with open('url_ids.json', 'w') as new_save_file:
            json.dump(self.url_dict, new_save_file)

    def save_to_json(self, n) -> None:
        # Save Urls to matching doc_ids
        self.save_doc_id_json()

        # Save to json file
        new_file_name = f'inverted_index{n / SAVE_FREQ}.json'
        with open(new_file_name, 'w') as new_save_file:
            json.dump(
            self.convert_inner_dict_to_list(), new_save_file)
            self.hash_table = dict()
            self.save_files.append(new_file_name)

    def convert_inner_dict_to_list(self) -> dict:
        new_hash_table = dict()
        for key in self.hash_table.keys():
            new_hash_table[key] = []
            for i in self.hash_table[key].keys():
                new_hash_table[key].append(self.hash_table[key][i].toJSON())
        return new_hash_table

    def merge_files(self) -> None:
        # Merge all the files into one
        if len(self.save_files) == 0:
            print("No files to merge.")
            return

        for letter in "abcdefghijklmnopqrstuvwxyz":  # Loop through all the letters
            letter_dict = dict()
            for next_file in self.save_files: # Loop through all the files
                next_hast_table = dict()  #TODO: Is this needed to save data outside of the with statement?

                with open(next_file, 'r') as f:  # Get tokens from the file that start with the letter
                    next_hast_table = json.load(f)
                    for key in next_hast_table.keys():
                        if key[0] == letter:
                            if key not in letter_dict:
                                letter_dict[key] = next_hast_table[key]
                            else:
                                letter_dict[key] += next_hast_table[key]
                            next_hast_table.pop(key)

                with open(next_file, 'w') as f:  # Save the new hash_table without the letter tokens
                    json.dump(next_hast_table, f)

            with open(f'inverted_index_{letter}.json', 'w') as letter_file:  # Save the letter tokens to a new file
                json.dump(letter_dict, letter_file)

        other_char_dict = dict()
        # Do this same thing one more time to check for tokens starting with non-letters
        for next_file in self.save_files:
            next_hast_table = dict()  # TODO: Is this needed to save data outside of the with statement?

            with open(next_file, 'r') as f:  # Get the rest of the tokens from each file
                next_hast_table = json.load(f)
                for key in next_hast_table.keys():
                        if key not in other_char_dict:
                            other_char_dict[key] = next_hast_table[key]
                        else:
                            other_char_dict[key] += next_hast_table[key]
                        next_hast_table.pop(key)

            print(f"Finished merging {next_file}. Size should be 0: Size={len(next_hast_table)}")

        with open('inverted_index_OTHERCHAR.json','w') as other_char_file:  # Save the rest of the tokens to a new file
            json.dump(other_char_dict, other_char_file)

        print("Finished merging all files into one per letter plus an OTHERCHAR.")


class Posting:
    def __init__(self, doc_id, doc_len, fields):

        self.doc_id = doc_id
        self.word_count = 0
        #self.doc_len = doc_len
        #self.tfidf = self.word_count / self.doc_len  # Frequency works for now, updates every word_count increment
        #self.fields = fields

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    def increment(self):
        self.word_count += 1
        #self.tfidf = self.word_count / self.doc_len # Update for new frequency

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
    LLLL = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                LLLL += 1
                documents.append(inverted_index.read_json(os.path.join(root, file)))
                if LLLL % 5000 == 0:
                    print(f'Now appended {LLLL} documents')

    print(f'Total documents to search: {LLLL}')
    inverted_index.build_index(documents)

    exit()
