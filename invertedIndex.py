# Path: invertedIndex.py
import re
from nltk.tokenize import word_tokenize


class InvertedIndex:
    def __init__(self):
        self.hash_table = {}

    def build_index(self, documents) -> None:
        n = 0
        # documents are json files
        for document in documents:
            n += 1
            # parsing means to make them into tokens
            # nltk tokenizer and stemmer!
            curr_url = document['url']  # This url needs to be saved to a json where key = n, value = url
            current_doc = document['content']  # Copy current document to use regex
            clean_text = re.sub('<[^>]*>', '', current_doc)
            tokens = word_tokenize(clean_text)
            tokens = [token.lower() for token in tokens if
                               token.isalnum() or (token.replace(".", "").isalnum() and len(token) > 1)]
            # json.loads()
            # tokens = list(set(tokens))  # Considering that parse doesn't already give unique results
            
            token_len = len(tokens)
            fields = None
            
            for token in tokens:
                if token not in self.hash_table:
                    # need to make sure we create a new posting for each document
                    # list of posting for each document_id, Every document id is represented by
                    # the variable n
                    self.hash_table[token] = Posting(n, len(tokens), fields)
                self.hash_table[token].append(n)


class Posting:
    def __init__(self, doc_id, doc_len, fields):
        self.doc_id = doc_id
        self.word_count = 0
        self.doc_len = doc_len
        self.tfidf = self.word_count / self.doc_len # frequency counts for now
        self.fields = fields

    def append(self, doc_id):
        pass

    def get_doc_id(self):
        return self.doc_id


if __name__ == "__main__":
    # read documents and make the InvertedIndex
    # json.dumps() every page in Dev :) use os most likely
    # inverted_index = InvertedIndex()
    # inverted_index.build_index(documents)
    #
    pass
