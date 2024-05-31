import query
import numpy
import time

function_inputs = [0.1, 0.3, 1, 0.3, 1, 0.3, 1, 0.3, 1]
desired_output = 3.5

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


def fitness_func(ga_instance, solution, solution_idx):
    """This function will take in the solution and return the fitness value."""
    search = query.search_engine()
    with open("inverted_index.txt", "r") as f:
        attempt = []
        for i in range(len(function_inputs)):
            attempt.append(solution[i]*function_inputs[i])
        attempt = [round(i, 5) for i in attempt]
        p, ml, l, mt, t, mh, h, mb, b = attempt
        search.pagerank_weight = p
        search.m_linked_weight = ml
        #search.linked_weight = 0
        search.linked_weight = l
        search.m_title_weight = mt
        #search.title_weight = 0
        search.title_weight = t
        search.m_header_weight = mh
        #search.header_weight = 0
        search.header_weight = h
        search.m_bold_weight = mb
        #search.bold_weight = 0
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


def run_pygad(init_population:list) -> (list[list[float]], float):
    import pygad

    fitness_function = fitness_func

    num_generations = 25
    num_parents_mating = 4

    initial_population = init_population
    #initial_population = [[0.46028, 3.06893, 5.3574, 2.39935, 12.42027, 2.83083, 8.08629, 1.67915, 10.20018], [0.0878, 3.06893, 5.3574, 2.39935, 11.8275, 2.83083, 8.08629, 1.67915, 10.34844], [0.0878, 3.06893, 5.3574, 2.39935, 11.81057, 2.83083, 8.41381, 1.67915, 10.34844], [-0.00251, 3.06893, 5.37782, 2.39935, 11.81057, 2.83083, 8.41381, 1.67915, 10.34844], [0.0878, 3.06893, 5.3574, 2.39935, 11.81057, 2.83083, 8.08629, 1.67915, 10.34844], [0.46028, 3.06893, 5.3574, 2.39935, 12.42027, 2.83083, 8.08629, 2.37488, 10.20018], [0.46028, 3.06893, 5.3574, 2.39935, 12.42027, 2.83083, 8.08629, 1.67915, 10.34844], [0.0878, 3.06893, 5.37782, 2.39935, 11.81057, 2.83083, 8.41381, 1.67915, 10.34844], [0.46028, 3.01343, 5.99374, 2.39935, 11.81057, 2.83083, 8.08629, 1.67915, 10.34844], [0.0878, 3.06893, 5.3574, 2.39935, 11.81057, 2.83083, 8.08629, 1.67915, 10.34844]]
    #initial_population = [[0.58736, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.42731, 1.67915, 10.34844], [0.58736, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.12308, 1.67915, 10.34844], [-0.20517, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.42731, 1.67915, 9.89155], [0.58736, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.42731, 1.97829, 10.97991], [0.58736, 3.06893, 4.49027, 2.39935, 12.78193, 2.5289, 8.42731, 1.67915, 10.34844], [0.58736, 3.10027, 5.37782, 2.80006, 12.78193, 2.5289, 8.42731, 1.67915, 10.34844], [1.26522, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.12308, 1.67915, 10.34844], [0.31548, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.12308, 1.67915, 10.34844], [0.58736, 3.06893, 5.37782, 2.39935, 12.78193, 2.5289, 8.42731, 1.97829, 10.97991], [0.58736, 2.78531, 5.37782, 2.39935, 12.78193, 1.91485, 8.42731, 1.67915, 10.34844]]

    sol_per_pop = 10
    num_genes = len(function_inputs)
    gene_type = [float, 5] # limits the gene to 5 decimal places

    init_range_low = 0
    init_range_high = 8

    parent_selection_type = "sss"
    keep_parents = 1

    crossover_type = "single_point"

    mutation_type = "adaptive"
    mutation_probability = [0.25, 0.1]

    ga_instance = pygad.GA(num_generations = num_generations,
                           num_parents_mating = num_parents_mating,
                           fitness_func = fitness_function,
                           sol_per_pop = sol_per_pop,
                           num_genes = num_genes,
                           initial_population = initial_population,
                           gene_type = gene_type,
                           init_range_low = init_range_low,
                           init_range_high = init_range_high,
                           parent_selection_type = parent_selection_type,
                           keep_parents = keep_parents,
                           crossover_type = crossover_type,
                           mutation_type = mutation_type,
                           mutation_probability = mutation_probability,
                           parallel_processing = ["process", 8])

    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution = solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness = solution_fitness))

    list_population = []
    for i in range(len(ga_instance.population)):
        list_population.append(list(ga_instance.population[i]))
    #print(f"Last generation's population:\n{list_population}\n")
    solution_times_inputs = [solution[i]*function_inputs[i] for i in range(len(function_inputs))]
    #print(f"Usable values of the best solution = {solution_times_inputs}")

    return list_population, solution_fitness


if __name__ == "__main__":
    t1 = time.time()
    l1, l2, l3, l4, l5, l6 = run_pygad(None), run_pygad(None), run_pygad(None), run_pygad(None), run_pygad(None), run_pygad(None)
    fit = [l[1] for l in [l1, l2, l3, l4, l5, l6]]
    fit.sort(reverse = True)
    t2 = time.time()
    print("Took", t2-t1, "seconds to run.")

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
        l1, l2, l3, l4, l5, l6 = run_pygad(top_three[0]), run_pygad(top_three[0]), run_pygad(top_three[1]), run_pygad(top_three[1]), run_pygad(top_three[2]), run_pygad(top_three[2])
        new_fit = [l[1] for l in [l1, l2, l3, l4, l5, l6]]
        new_fit.sort(reverse = True)
        t2 = time.time()
        print("Took", t2-t1, "seconds to run.")
        if new_fit[0] <= fit[0]:
            break
    print("Best fitnesses: ", new_fit)
    # 15.5 = [0.87924, 0.87265, 7.48876, 0.64362, 4.13349, 1.05115, 4.78048, 0.14238, 9.20507]
    # 13.5 = [0.09157100000000001, 0.9206789999999999, 5.98522, 0.6483599999999999, 11.80086, 0.695586, 0.54435, 0.429099, 3.88233]