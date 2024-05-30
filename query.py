import tokenizer
from pathlib import Path
import time
import os
import math

PAGERANK_WEIGHT = 0/20  # 0-1, 0 = only tfidf, 1 = only pagerank
PROXIMITY_WEIGHT = 0.5  # 0.5 = 50% of the weight is given to the first word, 25% to the second, 12.5% to the third, etc.
LINKED_WEIGHT = 2/20
TITLE_WEIGHT = 4/20
HEADER_WEIGHT = 8/20
BOLD_WEIGHT = 6/20

def find_best_weights():
    """This function will find the best weights for the search engine."""
    best_weights = [0, 0, 0, 0, 0]
    range_list = [0, 0.0001, 0.001, 0.01, 0.05, 0.1, 0.15,
                  0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1,
                  1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
                  2, 2.25, 2.5, 2.75, 3, 4, 5, 7.5, 10]
    best_time = 1000000
    highest_ranked = 10000
    search = search_engine()
    with open("inverted_index.txt", "r") as f:
        for i in range_list:
            for l in range_list:
                for m in range_list:
                    for n in range_list:
                        for o in range_list:
                            start_time = time.time()
                            search.pagerank_weight = i
                            search.linked_weight = l
                            search.title_weight = m
                            search.header_weight = n
                            search.bold_weight = o
                            result, test_res = search.run_query(f, "cristina lopes")
                            end_time = time.time()
                            if result[0].lower().startswith("error: "):
                                print(result[0])
                            elif len(result) > 2 and int(result[0]) in [21462,37119] and int(result[1]) in [21462,37119]:
                                if result.index('13255') < highest_ranked:
                                    highest_ranked = result.index('13255')
                                    print("new best weights =", [i, l, m, n, o])
                                    best_weights = [i, l, m, n, o]
                                    best_time = end_time - start_time

    print(f"Best weights: {best_weights} with time: {best_time}")





class search_engine:
    """This class will run the search engine."""
    def __init__(self):
        print("Search Engine Started")

        if not check_files_exist():
            print("Search engine closing, Goodbye!")
            exit(1)

        self.pagerank_weight = PAGERANK_WEIGHT
        self.tfidf_weight = 1 - PAGERANK_WEIGHT
        self.proximity_weight = PROXIMITY_WEIGHT
        self.linked_weight = LINKED_WEIGHT
        self.title_weight = TITLE_WEIGHT
        self.header_weight = HEADER_WEIGHT
        self.bold_weight = BOLD_WEIGHT


        self.token_list = []
        self.pos_list = []
        self.url_dict = {}
        self.page_rank = {}
        self.load_bookkeeping_lists()
        self.min_pg, self.max_pg = get_min_max("highest_pagerank.txt")
        self.min_tf, self.max_tf = get_min_max("highest_tfidf.txt")

        self.total_tfidf = get_total_tfidf()
        self.min_tf = self.min_tf / self.total_tfidf # Normalize the min and max tfidf values
        self.max_tf = self.max_tf / self.total_tfidf


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
                result, test_res = self.run_query(f, result)
                self.print_results(result, test_res)

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


    def print_results(self, result: list, test_res:list) -> None:
        """This function will print the results of the search query."""
        if len(result) == 0:
            print("No results found.")
            return
        if len(result) == 1 and result[0].lower().startswith("error: "):
            print(result[0])
            return
        print("Results: ")
        for i in range(min(10, len(result))):
            total_tfidf = []
            total_mult = []
            total_proximity = []
            pg = 0
            for t in test_res[i][:-1]:
                total_tfidf.append(t[0])
                total_mult.append(t[1])
                total_proximity.append(t[2])
            pg = test_res[i][-1]
            print(f"{i + 1}. doc_id={result[i]}, tf url={self.url_dict[result[i]]}")
            print(f"(TESTING) tfidf={total_tfidf}, mult={total_mult}, proximity={total_proximity}, pagerank={pg}")

    def run_query(self, f, query: str) -> (list, list):
        """This function will run the query and return the results."""
        # Start timer here
        start_time = time.time()

        # Step 1: Get the inverted index (maybe pass it in)
        # Step 2: Parse the query
        q_tokens = tokenizer.tokenize(query)

        # Step 2.5: Remove any duplicate tokens, save positions
        duplicate_tokens = {}
        i = 0
        while i < len(q_tokens):
            if q_tokens[i] in q_tokens[:i]:
                distance = i - q_tokens[:i].index(q_tokens[i])
                if q_tokens[i] in duplicate_tokens:
                    duplicate_tokens[q_tokens[i]].append(distance)
                else:
                    duplicate_tokens[q_tokens[i]] = [distance]
                q_tokens.pop(i)
                i -= 1
            i += 1

        # Step 3: Get the postings list for each term in the query
        q_pos = []
        q_tokens_copy = q_tokens.copy()
        for token in q_tokens_copy:
            # Get the index of the token in the token list
            index = binary_search(self.token_list, token)
            if index == -1:
                print(f"(TESTING) Token '{token}' not found in the index.")
                q_tokens.remove(token)
                continue
            q_pos.append(self.pos_list[index])

        # Step 4: Rank the documents based on the query
        doc_rankings = {}
        test_rankings = {}
        sorted_rankings = []
        test_sorted = []
        for i, pos in enumerate(q_pos):
            f.seek(int(pos))

            line = f.readline()
            lines = line.split(' ')
            token = lines[0]
            if lines[0] != q_tokens[i]:
                print(f"Error: Expected token '{q_tokens[i]}' but got '{lines[0]}'")
                continue
            multiplier = 1
            if token in duplicate_tokens:
                multiplier += len(duplicate_tokens[token])
            postings = decode_postings(lines[1:])

            for post in postings:
                doc_id, word_count, tfidf, fields, positions = post
                tfidf = float(tfidf) / self.total_tfidf # Normalize the tfidf
                #tfidf = (float(tfidf) - self.min_tf) / (self.max_tf - self.min_tf) # Normalize the tfidf between 0-1

                proximity_multiplier = 1
                last_change = 1
                for j in range(multiplier-1):
                    for n in range(check_distance(positions, duplicate_tokens[token][j])):
                        last_change = last_change * self.proximity_weight
                        proximity_multiplier += last_change

                for field in fields:
                    if field == "l": #linked on another page
                        tfidf += self.linked_weight
                    elif field == "t": #title
                        tfidf += self.title_weight
                    elif field == "h": #header
                        tfidf += self.header_weight
                    elif field == "b": #bold
                        tfidf += self.bold_weight


                if doc_id in doc_rankings:
                    doc_rankings[doc_id] += tfidf * multiplier * proximity_multiplier
                    test_rankings[doc_id].append([tfidf, multiplier, proximity_multiplier])
                else:
                    doc_rankings[doc_id] = tfidf * multiplier * proximity_multiplier
                    test_rankings[doc_id] = [[tfidf, multiplier, proximity_multiplier]]

        for doc_id in doc_rankings:
            doc_rankings[doc_id] = self.combine_tf_pg(doc_id, doc_rankings[doc_id])
            test_rankings[doc_id].append(self.test_return_pg(doc_id))

        for key in sorted(doc_rankings, key = doc_rankings.get, reverse = True):
            sorted_rankings.append(key)
            test_sorted.append(test_rankings[key])

        # End timer here
        end_time = time.time()
        #TODO: Uncomment: print(f"{len(sorted_rankings)} results found in {end_time - start_time:.10f} seconds. Less than 300ms = {end_time - start_time < 0.3}")

        # Step 5: Return the top documents in order
        return sorted_rankings, test_sorted

    def combine_tf_pg(self, doc_id: str, tfidf: float) -> float:
        """This function will combine the tfidf and pagerank values."""
        pg = self.min_pg
        if doc_id in self.page_rank:
            pg = self.page_rank[doc_id]
        #pg = (pg - self.min_pg) / (self.max_pg - self.min_pg)
        #pg = math.log(pg+1,1000000000000)
        return self.tfidf_weight * tfidf + self.pagerank_weight * pg

    def test_return_pg(self, doc_id: str) -> float:
        """This function will combine the tfidf and pagerank values."""
        pg = self.min_pg
        if doc_id in self.page_rank:
            pg = self.page_rank[doc_id]
        #pg = (pg - self.min_pg) / (self.max_pg - self.min_pg)
        #pg = math.log(pg+1,1000000000000)
        return pg


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
        first_t = other.index("t")
        word_count = other[0:first_t]
        other = other[first_t+1:]
        word_count = int(word_count)
        tfidf, fields = other.split("f")
        tfidf = float(tfidf)
        fields, positions = other.split("p")
        if len(positions) > 0 and positions[0] == "[": # Check to make sure positions isn't empty
            positions = positions[1:-1].split(",")
            if positions[-1][-1] == ']':
                positions[-1] = positions[-1][:-1]
            positions = [int(pos) for pos in positions]
        else:
            positions = []
        decoded.append((doc_id, word_count, tfidf, fields, positions))
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


def get_total_tfidf() -> float:
    with open("total_tfidf.txt", "r") as f:
        total_tfidf = float(f.readline())
    return total_tfidf


def check_files_exist() -> bool:
    """This function will check if the necessary files exist."""
    ii = Path("inverted_index.txt")
    tpl = Path("token_positions_list.txt")
    ud = Path("url_dict.txt")
    hpg = Path("highest_pagerank.txt")
    htf = Path("highest_tfidf.txt")
    ttf = Path("total_tfidf.txt")

    if not ii.is_file():
        print("Error: Inverted index file not found.")
        return False
    if not tpl.is_file():
        print("Error: Token positions list file not found.")
        return False
    if not ud.is_file():
        print("Error: URL dictionary file not found.")
        return False
    if not hpg.is_file():
        print("Error: Highest pagerank file not found.")
        return False
    if not htf.is_file():
        print("Error: Highest tfidf file not found.")
        return False
    if not ttf.is_file():
        print("Error: Total tfidf file not found.")
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


def check_distance(word_positions: list, distance: int) -> int:
    word_positions.sort()
    count = 0

    # Iterate through the list, checking the distance between each pair of words
    for i in range(len(word_positions)):
        j = i + 1
        while j < len(word_positions) and word_positions[j] - word_positions[i] <= distance:
            if word_positions[j] - word_positions[i] == distance:
                count += 1
            j += 1

    return count


if __name__ == "__main__":
    find_best_weights()
    #search = search_engine()
    #search.start_search_engine()

