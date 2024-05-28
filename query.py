import tokenizer
from pathlib import Path
import time


def start_search_engine():
    """Main function to run the search engine"""
    print("Search Engine Started")

    if not check_files_exist():
        print("Search engine closing, Goodbye!")
        exit(1)

    token_list, pos_list, url_dict = load_bookkeeping_lists()

    with open("inverted_index.txt", "r") as f:
        while True:
            result = get_query()
            if result.lower() == "exit":
                break
            if result.lower().startswith("error: "):
                print(result)
                continue

            print("(TESTING) Query: ", result)
            result = run_query(f, result, token_list, pos_list)
            print_results(result, url_dict)

    print("Search engine closing, Goodbye!")


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


def load_bookkeeping_lists() -> tuple:
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
    return token_list, pos_list, url_dict, page_rank


def print_results(result: list, url_dict: dict) -> None:
    """This function will print the results of the search query."""
    if len(result) == 0:
        print("No results found.")
        return
    if len(result) == 1 and result[0].lower().startswith("error: "):
        print(result[0])
        return
    print("Results: ")
    for i in range(min(10, len(result))):
        print(f"{i + 1}. doc_id={result[i]}, url={url_dict[result[i]]}")


def get_query() -> str: #TODO: Replace with the GUI
    """This function will get the query from the user and return it as a string."""
    query = input("\nEnter a query or type 'exit' to quit: ")
    if query.lower() == "exit":
        return query
    if len(query) == 0:
        return "ERROR: Query cannot be empty."
    return query


def run_query(f, query: str, token_list: list, pos_list: list) -> list:
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
        index = binary_search(token_list, token)
        if index == -1:
            print(f"(TESTING) Token '{token}' not found in the index.")
            q_tokens.remove(token)
            continue
        q_pos.append(pos_list[index])


    # Step 4: Rank the documents based on the query
    doc_rankings = {}
    sorted_rankings = []
    for i, pos in enumerate(q_pos):
        f.seek(int(pos))

        # ### FOR TESTING - NEED TO FIX INVERTED INDEX ###
        # testing_line = f.readline()
        # while True:
        #     line = f.readline()
        #     if line[0] != ' ' or line[1] == ":":
        #         break
        #     print('(TESTING) adding another line')
        #     testing_line += line
        # line = testing_line
        # ### FOR TESTING - NEED TO FIX INVERTED INDEX ###

        line = f.readline() #TODO: Get rid of above testing code, uncomment this line
        lines = line.split(' ')
        if lines[0] != q_tokens[i]:
            print(f"Error: Expected token '{q_tokens[i]}' but got '{lines[0]}'")
            continue
        postings = decode_postings(lines[1:])

        for post in postings:
            doc_id, word_count, tfidf, positions = post
            if doc_id in doc_rankings:
                doc_rankings[doc_id] += float(tfidf)
            else:
                doc_rankings[doc_id] = float(tfidf)

        for key in sorted(doc_rankings, key = doc_rankings.get, reverse = True):
            sorted_rankings.append(key)


    # End timer here
    end_time = time.time()
    print(f"{len(sorted_rankings)} results found in {end_time - start_time:.10f} seconds. Less than 300ms = {end_time - start_time < 0.3}")

    # Step 5: Return the top documents in order
    return sorted_rankings


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
