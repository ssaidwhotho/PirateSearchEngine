import json
import os
from collections import Counter, defaultdict
from functools import reduce
from operator import and_

class SearchEngine:
    def __init__(self, index_dir, url_file):
        self.index_dir = index_dir
        self.url_file = url_file
        self.inverted_index = defaultdict(list)
        self.url_dict = self.load_url_dict()
        self.load_index()

    def load_url_dict(self):
        with open(self.url_file, 'r') as f:
            return json.load(f)

    def load_index(self):
        for filename in os.listdir(self.index_dir):
            if filename.startswith('inverted_index_'):
                with open(os.path.join(self.index_dir, filename), 'r') as f:
                    index_part = json.load(f)
                    for token, postings in index_part.items():
                        self.inverted_index[token].extend([json.loads(p) for p in postings])

    def search(self, query):
        query_tokens = set(query.split())

        # Find the intersection of postings lists for all query tokens
        posting_sets = [set([d['doc_id'] for d in self.inverted_index[token]]) for token in query_tokens if
                        token in self.inverted_index]
        if posting_sets:
            relevant_docs = set.intersection(*posting_sets)
        else:
            relevant_docs = set()

        # Calculate scores for relevant documents
        scores = Counter()
        for doc_id in relevant_docs:
            for token in query_tokens:
                scores[doc_id] += sum([d['word_count'] for d in self.inverted_index[token] if d['doc_id'] == doc_id])

        # Get the top 10 results
        top_results = scores.most_common(10)

        # Create a list of (url, score) tuples for the top 10 results
        results = []
        for doc_id, score in top_results:
            url = self.url_dict.get(str(doc_id), None)  # Convert doc_id to string before looking it up in url_dict
            if url is None:
                print(f"Error: Document ID {doc_id} not found in URL dictionary")
            else:
                results.append((url[0], score))

        return results


if __name__ == "__main__":
    search_engine = SearchEngine(
        '/Users/samuelmallari/Documents/UCI_Spring_2024/compsci121/assignment3-stuff/inverted_index',
        '/Users/samuelmallari/Documents/UCI_Spring_2024/compsci121/assignment3-stuff/url_ids.json')

    while True:
        query = input("Enter a search query (or 'quit' to exit): ").lower()

        if query == 'quit_search':
            break

        results = search_engine.search(query)

        print(f"Search results for '{query}':")
        for i, (url, score) in enumerate(results[:5], start=1):
            print(f"{i}. URL: {url}, Score: {score}")
