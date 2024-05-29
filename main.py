from invertedIndex import InvertedIndex
import query


def main() -> None:
    #     inverted_index = InvertedIndex()
    #     inverted_index.create_inverted_index()
    #     inverted_index.create_report()
    #     print("Finished creating the inverted index.")
    #index = InvertedIndex()
    #index.create_inverted_index()
    #print("Finished creating the inverted index.")
    query.start_search_engine()
    #find_most_common_words()
    #find_highest_tfidf()
    return


def find_highest_tfidf():
    with open("inverted_index.txt", "r") as f:
        highest_tfidf = []
        for line in f:
            if line[0] == ":" or line == "\n":
                continue
            lines = line.split(' ')
            token = lines[0]
            print(token)
            postings = query.decode_postings(lines[1:])
            highest_tfidf.append((token, max(postings, key = lambda a: a[2])[2]))

        highest_tfidf.sort(key = lambda a: a[1], reverse = True)
        with open("highest_tfidf.txt", "w") as f:
            for token, tfidf in highest_tfidf:
                f.write(f"{token}: {tfidf}\n")



def find_most_common_words():

    most_common = []

    token_list = []
    pos_list = []
    with open("token_positions_list.txt", "r") as f:
        for line in f:
            if line[0] == ":" or line == "\n": #Shouldn't be necessary, but an easy precaution
                continue
            token, pos = line.split(":")
            token_list.append(token)
            pos_list.append(pos)

    with open("inverted_index.txt", "r") as f:
        for i, token in enumerate(token_list):
            f.seek(int(pos_list[i]))

            ### FOR TESTING - NEED TO FIX INVERTED INDEX ###
            testing_line = f.readline()
            while True:
                line = f.readline()
                if not line or line == "\n" or line[0] != ' ' or line[1] == ":":
                    break
                testing_line += line
            line = testing_line
            ### FOR TESTING - NEED TO FIX INVERTED INDEX ###

            # line = f.readline() #TODO: Get rid of above testing code, uncomment this line
            lines = line.split(' ')
            if lines[0] != token:
                print(f"Error: Expected token '{token}' but got '{lines[0]}'")
                continue
            postings = query.decode_postings(lines[1:])

            total_count = 0
            for post in postings:
                doc_id, word_count, tfidf, positions = post
                total_count += word_count

            most_common.append((token, total_count))

    print('Sorting the list of most common words...')
    most_common.sort(key = lambda a: a[1], reverse = True)
    with open("top_words.txt", "w") as f:
        for token, count in most_common:
            f.write(f"{token}: {count}\n")


if __name__ == "__main__":
    main()
