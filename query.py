from utils import tokenizer
from pathlib import Path
import time
import os

PROXIMITY_WEIGHT = 0.5   # 0.5 = 50% of the weight is given to the first word, 25% to the second, 12.5% to the third, etc.
BEST_WEIGHTS = [0.82536, 0.82337, 5.86986, 1.03176, 7.43271, -0.47591, 2.78897, 1.45966, 0.23013]


class SearchEngine:
    """This class will run the search engine."""

    def __init__(self):
        print("Search Engine Started")

        if not check_files_exist():
            print("Search engine closing, Goodbye!")
            exit(1)

        self.pagerank_weight = BEST_WEIGHTS[0]
        self.tfidf_weight = 1 - self.pagerank_weight
        self.proximity_weight = PROXIMITY_WEIGHT
        self.linked_weight = BEST_WEIGHTS[2]
        self.title_weight = BEST_WEIGHTS[4]
        self.header_weight = BEST_WEIGHTS[6]

        self.bold_weight = BEST_WEIGHTS[8]
        self.m_linked_weight = BEST_WEIGHTS[1]
        self.m_title_weight = BEST_WEIGHTS[3]
        self.m_header_weight = BEST_WEIGHTS[5]
        self.m_bold_weight = BEST_WEIGHTS[7]


        self.token_list = []
        self.pos_list = []
        self.url_dict = {}
        self.page_rank = {}
        self.load_bookkeeping_lists()
        self.min_pg, self.max_pg = get_min_max("highest_pagerank.txt")
        self.min_tf, self.max_tf = get_min_max("highest_tfidf.txt")
        self.stop_words = get_stop_words()
        self.top_words = get_top_words("top_words.txt")

        self.total_tfidf = get_total_tfidf()
        self.min_tf = self.min_tf / self.total_tfidf  # Normalize the min and max tfidf values
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
                result = self.run_query(f, result)
                self.print_results(result)

        print("Search engine closing, Goodbye!")

    def load_bookkeeping_lists(self) -> None:
        """This function will load the bookkeeping lists into memory."""
        token_list = []
        pos_list = []
        with open("token_positions_list.txt", "r") as f:
            for line in f:
                if line[0] == ":" or line == "\n":  #Shouldn't be necessary, but an easy precaution
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
            print(f"{i + 1}. doc_id={result[i]}, tf url={self.url_dict[result[i]]}")

    def run_query(self, f, query: str) -> list:
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

        # Step 2.75: Check for stop words and top words
        slow_words = 1
        sw_count = 0
        for i in range(len(q_tokens)):
            if q_tokens[i] in self.stop_words:
                slow_words *= 2
                sw_count += 1
            elif q_tokens[i] in self.top_words:
                slow_words *= 2

        if sw_count / len(q_tokens) < 0.35:
            qt_copy = q_tokens.copy()
            for i in range(len(q_tokens)):
                if q_tokens[i] in self.stop_words:
                    qt_copy.remove(q_tokens[i])
            q_tokens = qt_copy

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

        # Step 3.5: Assign search ranges to limit search time for stop words
        search_ranges = []
        for i in range(len(q_tokens)):
            search_ranges.append(-1)
            if q_tokens[i] in self.stop_words:
                search_ranges[i] = 1000 // slow_words
            if q_tokens[i] in self.top_words:
                search_ranges[i] = 2000 // slow_words

        # Step 4: Rank the documents based on the query
        doc_rankings = {}
        sorted_rankings = []
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
            postings = self.decode_postings(search_ranges[i], lines[1:])

            for post in postings:
                doc_id, word_count, tfidf, fields, positions = post
                tfidf = float(tfidf) / self.total_tfidf  # Normalize the tfidf

                proximity_multiplier = 1
                last_change = 1
                for j in range(multiplier - 1):
                    for n in range(check_distance(positions, duplicate_tokens[token][j])):
                        last_change = last_change * self.proximity_weight
                        proximity_multiplier += last_change

                for field in fields:
                    if field == "l":  # linked on another page
                        tfidf += self.linked_weight
                        tfidf = float(f"{tfidf:.7f}")
                        tfidf *= float(f"{self.m_linked_weight:.7f}")
                    elif field == "t":  # title
                        tfidf += self.title_weight
                        tfidf = float(f"{tfidf:.7f}")
                        tfidf *= float(f"{self.m_title_weight:.7f}")
                    elif field == "x":  # header
                        tfidf += self.header_weight
                        tfidf = float(f"{tfidf:.7f}")
                        tfidf *= float(f"{self.m_header_weight:.7f}")
                    elif field == "b":  # bold
                        tfidf += self.bold_weight
                        tfidf = float(f"{tfidf:.7f}")
                        tfidf *= float(f"{self.m_bold_weight:.7f}")

                if doc_id in doc_rankings:
                    doc_rankings[doc_id] += tfidf * multiplier * proximity_multiplier
                else:
                    doc_rankings[doc_id] = tfidf * multiplier * proximity_multiplier

        for doc_id in doc_rankings:
            doc_rankings[doc_id] = self.combine_tf_pg(doc_id, doc_rankings[doc_id])

        # Step 4.5: Sort the documents by their rankings
        for key in sorted(doc_rankings, key=doc_rankings.get, reverse=True):
            sorted_rankings.append(key)

        # End timer here
        end_time = time.time()
        print(
            f"{len(sorted_rankings)} results found in {end_time - start_time:.10f} seconds. Less than 300ms = {end_time - start_time < 0.3}")

        # Step 5: Return the top documents in order
        return sorted_rankings

    def combine_tf_pg(self, doc_id: str, tfidf: float) -> float:
        """This function will combine the tfidf and pagerank values."""
        pg = self.min_pg
        if doc_id in self.page_rank:
            pg = self.page_rank[doc_id]
        #pg = (pg - self.min_pg) / (self.max_pg - self.min_pg)
        #pg = math.log(pg+1,1000000000000)
        return self.tfidf_weight * tfidf + self.pagerank_weight * pg

    def decode_postings(self, search_range: int, postings: list) -> list:
        """This function will decode the postings list and return it as a list of tuples."""
        if search_range == 0.0:
            return []
        decoded = []
        top_tfidf = []
        if search_range != -1:
            top_tfidf = [0.0 for i in range(int(search_range))]

        for post in postings:
            doc_id, other = post.split("w")
            doc_id = doc_id[1:]
            first_t = other.index("t")
            word_count = other[0:first_t]
            other = other[first_t + 1:]
            word_count = int(word_count)
            tfidf, fields = other.split("f")
            tfidf = float(tfidf)
            if search_range != -1 and len(top_tfidf) > 0:
                if tfidf > top_tfidf[0]:
                    ind = binary_search_index(top_tfidf, tfidf)
                    top_tfidf.insert(ind, tfidf)
                    top_tfidf.pop(0)
                else:
                    continue
            fields, positions = other.split("p")
            if len(positions) > 0 and positions[
                0] == "[":  # Check to make sure positions isn't empty
                positions = positions[1:-1].split(",")
                if positions[-1][-1] == ']':
                    positions[-1] = positions[-1][:-1]
                positions = [int(pos) for pos in positions]
            else:
                positions = []
            decoded.append((doc_id, word_count, tfidf, fields, positions))
        return decoded


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


def binary_search_index(arr: list, target: float) -> int:
    """This function will perform a binary search on the list and return the index of the target."""
    left = 0
    right = len(arr) - 1
    mid = (left + right) // 2
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] < target:
            left = mid + 1
            mid += 1
        elif arr[mid] > target:
            right = mid - 1
        else:
            return mid
    return mid


def get_min_max(file_name: str) -> (float, float):
    min_val = 0
    max_val = 0

    with open(file_name, "r") as f:
        top_line = f.readline()
        line = top_line.split(": ")
        max_val = float(line[1])

    with open(file_name, "rb") as f:
        try:
            f.seek(-2,
                   os.SEEK_END)  # Code from https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
        line = last_line.split(": ")
        min_val = float(line[1])

    return min_val, max_val


def get_stop_words() -> list:
    stop_words = [
        'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and',
        'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before',
        'being', 'below', 'between', 'both', 'but', 'by', "can't", 'cannot',
        'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing',
        "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had',
        "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd",
        "he'll", "he's", 'her', 'here', "here's", 'hers', 'herself', 'him',
        'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if',
        'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me',
        'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off',
        'on', 'once', 'only', 'or', 'other', "ought", 'our', 'ours', 'ourselves',
        'out', 'over', 'own', 'same', "shan't", 'she', "she'd", "she'll", "she's",
        'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the',
        'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these',
        'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through',
        'to', 'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd",
        "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when',
        "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why',
        "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", "you'll",
        "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']
    return stop_words


def get_top_words(file_name: str) -> list:
    top_words = []
    with open(file_name, "r") as f:
        for i in range(50):
            line = f.readline()
            word = line.split(": ")
            top_words.append(word[0])
    return top_words


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
    tw = Path("top_words.txt")

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
    if not tw.is_file():
        print("Error: Top words file not found.")
        return False
    return True


def get_query() -> str:  #Replaced with the GUI
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
    search = SearchEngine()
    search.start_search_engine()
