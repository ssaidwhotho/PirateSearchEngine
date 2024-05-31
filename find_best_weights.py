import query

def find_best_weights():
    """This function will find the best weights for the search engine."""
    best_weights = [0, 0, 0, 0, 0]
    range_list = [0, 0.01, 0.1,
                  0.2, 0.4, 0.6, 0.8, 1,
                  1.5,
                  2, 5]
    best_score = 100000
    search = query.search_engine()
    top_weights = []
    with open("inverted_index.txt", "r") as f:
        for i in [0, 0.01, 0.1,
                  0.2, 0.4, 0.6, 0.8]:
            print(f"\n\t\tfirst outside loop: {i}")
            for l in range_list:
                print(f"\t2nd-to outside loop: {l}")
                for m in range_list:
                    print(f"3rd-to outside loop: {m}")
                    for n in range_list:
                        for o in range_list:
                            search.pagerank_weight = i
                            search.linked_weight = l
                            search.title_weight = m
                            search.header_weight = n
                            search.bold_weight = o
                            score = 0

                            result, test_res = search.run_query(f, "cristina lopes")
                            result = result[:20]
                            if "21462" not in result or "37119" not in result or "13255" not in result:
                                continue
                            score += result.index("21462") + result.index("37119") + (result.index("13255") / 2)
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "research at uci")
                            result = result[:20]
                            if "9664" not in result:
                                continue
                            score += result.index("9664")
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "ics")
                            result = result[:20]
                            if "15684" not in result:
                                continue
                            score += result.index("15684")
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "klefstad")
                            result = result[:20]
                            if "17824" not in result:
                                continue
                            score += result.index("17824")
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "masters of software engineering")
                            result = result[:20]
                            if "37203" not in result or "36741" not in result:
                                continue
                            score += result.index("37203") + result.index("36741")
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "statistics")
                            result = result[:20]
                            if "37443" not in result:
                                continue
                            score += result.index("37443")
                            if score >= best_score:
                                continue

                            result, test_res = search.run_query(f, "computer science")
                            result = result[:20]
                            if "9747" not in result:
                                continue
                            score += result.index("9747")

                            result, test_res = search.run_query(f, "ramesh jain")
                            result = result[:20]
                            if "6523" not in result:
                                continue
                            score += result.index("6523")

                            if score < best_score:
                                best_weights = [i, l, m, n, o]
                                best_score = score
                                print(f"New best weights: {best_weights} at score {best_score}")
                            top_weights.append(([i, l, m, n, o], score))

    print(f"Best weights: {best_weights} at score {best_score}")
    top_weights.sort(key = lambda a: a[1], reverse = False)
    with open("best_weights.txt", "w") as f:
        for weights, score in top_weights:
            f.write(f"{weights}: {score}\n")
