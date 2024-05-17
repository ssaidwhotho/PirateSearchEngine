import math


class Posting:
    def __init__(self, doc_id, word_count=0, tfidf=0, positions=None):

        if positions is None:
            positions = []

        self.doc_id = doc_id
        self.word_count = word_count
        self.tfidf = tfidf
        self.positions = positions

    def increment(self):
        self.word_count += 1

    def get_doc_id(self):
        return self.doc_id

    def calculate_tfidf(self, doc_len, total_docs, doc_freq):
        tf = self.word_count / doc_len
        idf = 1 + math.log(total_docs / doc_freq)
        self.tfidf = tf * idf

    def add_position(self, position):
        self.positions.append(position)
