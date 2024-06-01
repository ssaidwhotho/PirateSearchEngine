import query
import numpy
import time

function_inputs = [0.1, 0.3, 1, 0.3, 1, 0.3, 1, 0.3, 1]
desired_output = 3.4


def find_best_weights():
    """This function will find the best weights for the search engine."""
    best_weights = [0, 0, 0, 0, 0]
    range_list = [0, 0.01, 0.1,
                  0.2, 0.4, 0.6, 0.8, 1,
                  1.5,
                  2, 5]
    best_score = 100000
    search = query.SearchEngine()
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
    top_weights.sort(key=lambda a: a[1], reverse=False)
    with open("best_weights.txt", "w") as f:
        for weights, score in top_weights:
            f.write(f"{weights}: {score}\n")


def fitness_func(ga_instance, solution, solution_idx):
    """This function will take in the solution and return the fitness value."""
    search = query.SearchEngine()
    with open("inverted_index.txt", "r") as f:
        attempt = []
        for i in range(len(function_inputs)):
            attempt.append(solution[i] * function_inputs[i])
        attempt = [round(i, 5) for i in attempt]
        p, ml, l, mt, t, mh, h, mb, b = attempt
        search.pagerank_weight = p
        search.m_linked_weight = ml
        search.linked_weight = l
        search.m_title_weight = mt
        search.title_weight = t
        search.m_header_weight = mh
        search.header_weight = h
        search.m_bold_weight = mb
        search.bold_weight = b
        score = 0

        result, test_res = search.run_query(f, "cristina lopes")
        result = result[:20]
        if "21462" not in result or "37119" not in result or "13255" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("21462") + result.index("37119") + (result.index("13255") / 2)

        result, test_res = search.run_query(f, "research areas in cs")
        result = result[:20]
        if "9664" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("9664")

        result, test_res = search.run_query(f, "ics")
        result = result[:20]
        if "15684" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("15684")

        result, test_res = search.run_query(f, "klefstad")
        result = result[:20]
        if "17824" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("17824")

        result, test_res = search.run_query(f, "professor klefstad")
        result = result[:20]
        if "17824" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("17824")

        result, test_res = search.run_query(f, "ai club")
        result = result[:20]
        if "0" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("0") * 2

        result, test_res = search.run_query(f, "masters of software engineering")
        result = result[:20]
        if "37203" not in result or "36741" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("37203") + result.index("36741")

        result, test_res = search.run_query(f, "statistics")
        result = result[:20]
        if "37443" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("37443")

        result, test_res = search.run_query(f, "shu kong")
        result = result[:20]
        if "23372" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("23372")

        result, test_res = search.run_query(f, "computer science")
        result = result[:20]
        if "9747" not in result or "15684" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("9747") + result.index("15684")

        result, test_res = search.run_query(f, "ramesh jain")
        result = result[:20]
        if "6523" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("6523")

        result, test_res = search.run_query(f, "bs game design")
        result = result[:20]
        if "36715" not in result:
            score = 200
            fitness = 1.0 / numpy.abs(score - desired_output)
            return fitness
        score += result.index("36715")

        fitness = 1.0 / numpy.abs(score - desired_output)

        #print("Solution: ", solution)
        #print("Attempt: ", attempt)
        #print(f"Score: {score}, Fitness: {fitness:.4f}")
        return fitness


def run_pygad(init_population: list, mtype: str, mprob: list) -> (list[list[float]], float):
    import pygad

    fitness_function = fitness_func

    num_generations = 50
    num_parents_mating = 5

    initial_population = init_population

    sol_per_pop = 10
    num_genes = len(function_inputs)
    gene_type = [float, 5]  # limits the gene to 5 decimal places

    init_range_low = 0
    init_range_high = 10

    parent_selection_type = "sss"
    keep_parents = 1

    crossover_type = "single_point"

    mutation_type = mtype
    mutation_probability = mprob

    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           fitness_func=fitness_function,
                           sol_per_pop=sol_per_pop,
                           num_genes=num_genes,
                           initial_population=initial_population,
                           gene_type=gene_type,
                           init_range_low=init_range_low,
                           init_range_high=init_range_high,
                           parent_selection_type=parent_selection_type,
                           keep_parents=keep_parents,
                           crossover_type=crossover_type,
                           mutation_type=mutation_type,
                           mutation_probability=mutation_probability,
                           parallel_processing=["process", 8])

    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness=solution_fitness))

    list_population = []
    for i in range(len(ga_instance.population)):
        list_population.append(list(ga_instance.population[i]))
    print(f"Last generation's population:\n{list_population}\n")
    solution_times_inputs = [solution[i] * function_inputs[i] for i in range(len(function_inputs))]
    print(f"Usable values of the best solution = {solution_times_inputs}")

    return list_population, solution_fitness


if __name__ == "__main__":
    first = [[8.25364, 2.74457, 5.86986, 3.43919, 7.43271, -1.58637, 2.78897, 4.86555, 0.23013],
             [8.25364, 2.74457, 5.55908, 3.31577, 7.94837, -1.58637, 2.78353, 4.19092, -0.69804],
             [6.80756, 2.74457, 5.55908, 3.80757, 7.94837, -1.58637, 1.91136, 4.4848, -1.11299],
             [7.50533, 2.74457, 5.86986, 3.43919, 7.43271, -1.58637, 2.78897, 4.86555, -1.95341],
             [7.50533, 2.74457, 5.86986, 3.43919, 7.43271, -1.46569, 2.78897, 4.86555, -0.68536],
             [8.25364, 2.74457, 5.86986, 3.43919, 6.74691, -1.58637, 2.78897, 4.86555, 0.23013],
             [7.79638, 2.74457, 5.55908, 3.31577, 7.94837, -1.58637, 2.78897, 4.19092, -0.69804],
             [6.80756, 2.74457, 6.44891, 3.31577, 7.94837, -1.58637, 2.78897, 4.19092, -1.11299],
             [7.71777, 2.74457, 5.61658, 3.43919, 7.43271, -1.58637, 2.78897, 4.86555, -0.7122],
             [7.28102, 2.74457, 5.55908, 3.31577, 7.43271, -1.58637, 2.78897, 3.56411, -0.68536]]
    second = [[3.21429, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.21429, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.27162, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.23238, -0.53662],
              [3.28053, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.28053, 2.67908, 2.06533, 3.98087, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.21429, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.21429, 2.67908, 2.06533, 3.61781, 2.02183, 0.39379, 9.39931, 6.25393, -0.53662],
              [3.27162, 2.67908, 1.78809, 3.61781, 2.02183, 0.29257, 8.81621, 5.23238, -0.53662],
              [3.28053, 2.67908, 2.77434, 2.80197, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662],
              [3.28053, 2.67908, 2.06533, 3.61781, 2.02183, 0.29257, 8.81621, 5.29695, -0.53662]]
    third = [[7.16477, 2.65631, 2.96847, 3.45988, 1.57478, 0.2245, 6.83978, 0.75421, 6.63524],
             [7.16477, 2.65631, 2.96847, 3.45988, 2.77948, 0.87584, 6.83978, 0.75421, 8.19611],
             [7.16477, 2.65631, 2.12273, 2.88248, 1.38262, 0.72435, 7.07649, 0.64169, 6.63524],
             [6.67074, 2.65631, 2.96847, 3.15631, 1.38262, 0.87584, 6.28331, 0.64169, 6.63524],
             [7.16477, 2.65631, 2.96847, 3.45988, 1.57478, 0.87584, 6.83978, 0.75421, 8.19611],
             [7.16477, 2.65631, 2.96847, 3.47638, 1.57478, 0.2245, 6.83978, 0.75421, 6.63524],
             [7.16477, 2.84181, 2.96847, 3.45988, 2.20118, 1.78405, 6.83978, 0.75421, 7.3798],
             [7.16477, 2.65631, 2.96847, 4.1802, 1.38262, 1.10292, 7.07649, 0.7588, 6.63524],
             [6.7921, 2.65631, 2.96847, 3.15631, 1.57478, 0.87584, 6.28331, 0.64169, 6.63524],
             [7.16477, 2.65631, 2.96847, 3.15631, 1.57478, 0.87584, 6.83978, 0.75421, 8.19611]]

    t1 = time.time()
    l1, l2, l3, l4, l5, l6 = run_pygad(None, "adaptive", [0.25, 0.1]), run_pygad(None, "adaptive",
                                                                                 [0.25, 0.1]), run_pygad(None,
                                                                                                         "adaptive",
                                                                                                         [0.5,
                                                                                                          0.05]), run_pygad(
        None, "random", None), run_pygad(None, "random", None), run_pygad(None, "random", None)
    fit = [l[1] for l in [l1, l2, l3, l4, l5, l6]]
    fit.sort(reverse=True)
    t2 = time.time()
    print("Took", t2 - t1, "seconds to run.")

    while True:
        print(f"Best fitnesses: {fit}")
        top_three = []
        for t in fit[:3]:
            for l in [l1, l2, l3, l4, l5, l6]:
                if l[1] == t:
                    top_three.append(l[0])
                    break
            if len(top_three) == 3:
                break
        t1 = time.time()
        print(f"Top three:\n1st:{top_three[0]}\n2nd:{top_three[1]}\n3rd:{top_three[2]}\n")
        l1, l2, l3, l4, l5, l6 = run_pygad(top_three[0], "adaptive", [0.25, 0.1]), run_pygad(top_three[0], "random",
                                                                                             None), run_pygad(
            top_three[1], "adaptive", [0.25, 0.1]), run_pygad(top_three[1], "random", None), run_pygad(top_three[2],
                                                                                                       "adaptive",
                                                                                                       [0.25,
                                                                                                        0.1]), run_pygad(
            top_three[2], "random", None)
        new_fit = [l[1] for l in [l1, l2, l3, l4, l5, l6]]
        new_fit.sort(reverse=True)
        t2 = time.time()
        print("Took", t2 - t1, "seconds to run.")
        if new_fit[0] <= fit[0]:
            break
        fit = new_fit
    print("Best fitnesses: ", new_fit)
    top_three = []
    for t in new_fit[:3]:
        for l in [l1, l2, l3, l4, l5, l6]:
            if l[1] == t:
                top_three.append(l[0])
                break
        if len(top_three) == 3:
            break
    print(f"Top three:\n1st:{top_three[0]}\n2nd:{top_three[1]}\n3rd:{top_three[2]}\n")
