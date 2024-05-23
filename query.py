import tokenizer
from pathlib import Path


def start_search_engine():
    """Main function to run the search engine"""
    print("Search Engine Started")

    if not check_files_exist():
        print("Search engine closing, Goodbye!")
        exit(1)

    token_list, pos_list = load_bookkeeping_lists()

    while True:
        result = get_query()
        if result.lower() == "exit":
            break
        if result.lower().startswith("error: "):
            print(result)
            continue

        print("(TESTING) Query: ", result)
        result = run_query(result, token_list, pos_list)
        print_results(result)

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
            token, pos = line.split(":")
            token_list.append(token)
            pos_list.append(pos)
    return token_list, pos_list


def print_results(result: list) -> None:
    """This function will print the results of the search query."""
    if len(result) == 0:
        print("No results found.")
        return
    if len(result) == 1 and result[0].lower().startswith("error: "):
        print(result[0])
        return
    print("Results: ")
    for i in range(10):
        print(f"{i + 1}. {result[i]}")


def get_query() -> str: #TODO: Replace with the GUI
    """This function will get the query from the user and return it as a string."""
    query = input("Enter a query or type 'exit' to quit: ")
    if query.lower() == "exit":
        return query
    if len(query) == 0:
        return "Error: Query cannot be empty."
    if not query.isalnum():
        return "Error: Query must contain only alphanumeric characters."
    return query


def run_query(query: str, token_list: list, pos_list: list) -> list:
    """This function will run the query and return the results."""
    # Start timer here

    # Step 1: Get the inverted index (maybe pass it in)
    # Step 2: Parse the query
    tokenizer.tokenize(query)
    # Step 3: Get the postings list for each term in the query
    # Step 4: Rank the documents based on the query

    # End timer here

    # Step 5: Return the top documents in order
    return []
