
def start_search_engine():
    """Main function to run the search engine"""
    print("Search Engine Started")

    # TODO: Check that there is an inverted index to use (and the other files)
    # Maybe we need to pass it in?

    while True:
        result = get_query()
        if result.lower() == "exit":
            break
        if result.lower().startswith("error: "):
            print(result)
            continue

        print("(TESTING) Query: ", result)
        result = run_query(result)
        print_results(result)

    print("Search engine finished, Goodbye!")


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


def run_query(query: str) -> list:
    """This function will run the query and return the results."""
    # Start timer here

    # Step 1: Get the inverted index (maybe pass it in)
    # Step 2: Parse the query
    # Step 3: Get the postings list for each term in the query
    # Step 4: Rank the documents based on the query

    # End timer here

    # Step 5: Return the top documents in order
    pass
