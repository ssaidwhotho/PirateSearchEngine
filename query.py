import tokenizer
from pathlib import Path
import time
import os

PAGERANK_WEIGHT = 0.3  #0-1, 0 = only tfidf, 1 = only pagerank


class search_engine:
    """This class will run the search engine."""
    def __init__(self):
        print("Search Engine Started")

        if not check_files_exist():
            print("Search engine closing, Goodbye!")
            exit(1)

        self.pagerank_weight = PAGERANK_WEIGHT
        self.tfidf_weight = 1 - PAGERANK_WEIGHT

        self.token_list = []
        self.pos_list = []
        self.url_dict = {}
        self.page_rank = {}
        self.load_bookkeeping_lists()
        self.min_pg, self.max_pg = get_min_max("highest_pagerank.txt")
        self.min_tf, self.max_tf = get_min_max("highest_tfidf.txt")


    def start_search_engine(self):
        """Main function to run the search engine"""
        with open("inverted_index.txt", "r") as f:
            while True:
                result = get_query()
                if result.lower() == "exit":
                    break
                if result.lower().startswith("error: "):
                    print(result)
                    continue

                print("(TESTING) Query: ", result)
                result = self.run_query(f, result)
                self.print_results(result)

        print("Search engine closing, Goodbye!")


    def load_bookkeeping_lists(self) -> None:
        """This function will load the bookkeeping lists into memory."""
        token_list = []
        pos_list = []
        with open("token_positions_list.txt", "r") as f:
            for line in f:
                if line[0] == ":" or line == "\n": #Shouldn't be necessary, but an easy precaution
                    continue
                token, pos = line.split(":")
                token_list.append(token)
                pos_list.append(pos)

        url_dict = {}
        with open("url_dict.txt", "r") as f:
            for line in f:
                doc_id, url, doc_size = line.split(" ")
                url_dict[doc_id] = url

        page_rank = {}
        with open("page_rank.txt", "r") as f:
            for line in f:
                doc_id, rank = line.split(" ")
                page_rank[doc_id] = float(rank)

        self.token_list = token_list
        self.pos_list = pos_list
        self.url_dict = url_dict
        self.page_rank = page_rank


    def print_results(self, result: list) -> None:
        """This function will print the results of the search query."""
        if len(result) == 0:
            print("No results found.")
            return
        if len(result) == 1 and result[0].lower().startswith("error: "):
            print(result[0])
            return
        print("Results: ")
        for i in range(min(10, len(result))):
            print(f"{i + 1}. doc_id={result[i]}, url={self.url_dict[result[i]]}")

    def run_query(self, f, query: str) -> list:
        """This function will run the query and return the results."""
        # Start timer here
        start_time = time.time()

        # Step 1: Get the inverted index (maybe pass it in)
        # Step 2: Parse the query
        q_tokens = tokenizer.tokenize(query)

        # Step 3: Get the postings list for each term in the query
        q_pos = []
        q_tokens_copy = q_tokens.copy()
        for token in q_tokens_copy:
            # Get the index of the token in the token list
            #index = -1
            #for num in "0123456789":
            #    if num in token:
            #        index = token_list.index(token)
            #if index == -1:
            index = binary_search(self.token_list, token)
            if index == -1:
                print(f"(TESTING) Token '{token}' not found in the index.")
                q_tokens.remove(token)
                continue
            q_pos.append(self.pos_list[index])


        # Step 4: Rank the documents based on the query
        doc_rankings = {}
        sorted_rankings = []
        for i, pos in enumerate(q_pos):
            f.seek(int(pos))

            line = f.readline()
            lines = line.split(' ')
            if lines[0] != q_tokens[i]:
                print(f"Error: Expected token '{q_tokens[i]}' but got '{lines[0]}'")
                continue
            postings = decode_postings(lines[1:])

            for post in postings:
                doc_id, word_count, tfidf, positions = post
                tfidf = (float(tfidf) - self.min_tf) / (self.max_tf - self.min_tf) # Normalize the tfidf
                if doc_id in doc_rankings:
                    doc_rankings[doc_id] += tfidf
                else:
                    doc_rankings[doc_id] = tfidf

        for doc_id in doc_rankings:
            doc_rankings[doc_id] = self.combine_tf_pg(doc_id, doc_rankings[doc_id])

        for key in sorted(doc_rankings, key = doc_rankings.get, reverse = True):
            sorted_rankings.append(key)

        # End timer here
        end_time = time.time()
        print(f"{len(sorted_rankings)} results found in {end_time - start_time:.10f} seconds. Less than 300ms = {end_time - start_time < 0.3}")

        # Step 5: Return the top documents in order
        return sorted_rankings

    def combine_tf_pg(self, doc_id: str, tfidf: float) -> float:
        """This function will combine the tfidf and pagerank values."""
        pg = self.min_pg
        if doc_id in self.page_rank:
            pg = self.page_rank[doc_id]
        pg = (pg - self.min_pg) / (self.max_pg - self.min_pg)
        return self.tfidf_weight * tfidf + self.pagerank_weight * pg


def binary_search(arr: list, target: str) -> int:
    """This function will perform a binary search on the list and return the index of the target."""
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
        elif arr[mid] > target:
            right = mid - 1
        else:
            return mid
    return -1


def decode_postings(postings: list) -> list:
    """This function will decode the postings list and return it as a list of tuples."""
    decoded = []
    for post in postings:
        doc_id, other = post.split("w")
        doc_id = doc_id[1:]
        word_count, other = other.split("t")
        word_count = int(word_count)
        tfidf, positions = other.split("p")
        tfidf = float(tfidf)
        positions = positions[1:-1].split(",")
        decoded.append((doc_id, word_count, tfidf, positions))
    return decoded


def get_min_max(file_name: str) -> (float, float):
    min_val = 0
    max_val = 0

    with open(file_name, "r") as f:
        top_line = f.readline()
        line = top_line.split(": ")
        max_val =  float(line[1])

    with open(file_name, "rb") as f:
        try:
            f.seek(-2, os.SEEK_END)  # Code from https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
        line = last_line.split(": ")
        min_val = float(line[1])

    return min_val, max_val

def check_files_exist() -> bool:
    """This function will check if the necessary files exist."""
    ii = Path("inverted_index.txt")
    tpl = Path("token_positions_list.txt")
    ud = Path("url_dict.txt")

    if not ii.is_file():
        print("Error: Inverted index file not found.")
        return False
    if not tpl.is_file():
        print("Error: Token positions list file not found.")
        return False
    if not ud.is_file():
        print("Error: URL dictionary file not found.")
        return False
    return True


def get_query() -> str: #TODO: Replace with the GUI
    """This function will get the query from the user and return it as a string."""
    query = input("\nEnter a query or type 'exit' to quit: ")
    if query.lower() == "exit":
        return query
    if len(query) == 0:
        return "ERROR: Query cannot be empty."
    return query



