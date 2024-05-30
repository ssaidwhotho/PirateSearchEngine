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
    #find_most_common_words()
    #find_total_and_highest_tfidf()
    #find_highest_pagerank()
    the_search_engine = query.search_engine()
    the_search_engine.start_search_engine()
    return


def find_total_and_highest_tfidf():
    print('Finding the total and highest tfidf...')
    total_tfidf = 0
    with open("inverted_index.txt", "r") as f:
        highest_tfidf = []
        for line in f:
            if line[0] == ":" or line == "\n":
                continue
            lines = line.split(' ')
            token = lines[0]
            postings = query.decode_postings(lines[1:])
            max_tfidf = 0
            for post in postings:
                doc_id, word_count, tfidf, positions = post
                total_tfidf += tfidf
                if tfidf > max_tfidf:
                    max_tfidf = tfidf
            highest_tfidf.append((token, max_tfidf))

        print('Sorting the list of highest tfidf...')
        highest_tfidf.sort(key = lambda a: a[1], reverse = True)
        with open("highest_tfidf.txt", "w") as f:
            for token, tfidf in highest_tfidf:
                f.write(f"{token}: {tfidf}\n")

        with open("total_tfidf.txt", "w") as f:
            f.write(f"{total_tfidf}")
    print('Finished finding the total and highest tfidf.')


def find_highest_pagerank():
    print('Finding the highest pagerank...')
    with open("page_rank.txt", "r") as f:
        highest_pg = []
        for line in f:
            if line[0] == ":" or line == "\n":
                continue
            lines = line.split(' ')
            token = lines[0]
            pg = float(lines[1])
            highest_pg.append((token, pg))

        print('Sorting the list of highest pagerank...')
        highest_pg.sort(key = lambda a: a[1], reverse = True)
        with open("highest_pagerank.txt", "w") as f:
            for token, tfidf in highest_pg:
                f.write(f"{token}: {tfidf}\n")
    print('Finished finding the highest pagerank.')



def find_most_common_words():

    print('Finding the most common words...')
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

            line = f.readline() #TODO: Get rid of above testing code, uncomment this line
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
    print('Finished finding the most common words.')



if __name__ == "__main__":
    main()
