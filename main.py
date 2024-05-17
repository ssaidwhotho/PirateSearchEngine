from invertedIndex import InvertedIndex


def main() -> None:
    #     inverted_index = InvertedIndex()
    #     inverted_index.create_inverted_index()
    #     inverted_index.create_report()
    #     print("Finished creating the inverted index.")
    index = InvertedIndex()
    index.create_inverted_index()

    print("Finished creating the inverted index.")
    return


if __name__ == "__main__":
    main()
