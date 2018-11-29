from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain import MarkovChain
from gerrychain.constraints import Validator, single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import metropolis_hastings_constrained
from gerrychain.updaters import Election, Tally
from gerrychain.updaters.election import fairness_score, competitiveness_score, ideal_population, population_score
from gerrychain.updaters.election import efficiency_gap
import math, json, geopandas, matplotlib
from osgeo import ogr

graph = Graph.from_json("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/queen.json")
election = Election(
    "2014 House",
    {"Democratic": "DVOTES", "Republican": "RVOTES"},
    alias="2014_House"
)
initial_partition = GeographicPartition(graph, assignment="CD113",
                                        updaters={"2014_House": election,
                                                  "fairness_score": fairness_score,
                                                  "competitiveness_score": competitiveness_score,
                                                  "population": Tally("POP10", alias="population"),
                                                  "ideal_population": ideal_population,
                                                  "population_score": population_score,
                                                  "efficiency_gap": efficiency_gap})
steps = 5000


# def score_function(fairness_weight, competitiveness_weight, compactness_weight):
#     def fn(partition):
#         return fairness_weight * partition["fairness_score"] +\
#                competitiveness_weight * partition["competitiveness_score"] +\
#                compactness_weight * partition["compactness_score"]
#     return fn
def score_function(population_weight):
    def fn(partition):
        return population_weight * partition["population_score"]
    return fn


population_weight = 100
chain = MarkovChain(
    proposal=propose_random_flip,
    is_valid=Validator([single_flip_contiguous]),
    accept=metropolis_hastings_constrained(1, score_function(population_weight)),
    initial_state=initial_partition,
    total_steps=steps
)

data = dict()
data["maps"] = []
sum_fairness = 0
sum_efficiency = 0
num = 0
min_fairness = 1000
max_fairness = 0
min_competitiveness = 1000
max_competitiveness = 0
min_compactness = 1000
max_compactness = 0
for partition in chain:
    good = True
    for pop in partition["population"].values():
        if abs(pop - partition["ideal_population"]) / partition["ideal_population"] > 0.01:
            good = False
            break
    if good:
        map_data = dict()
        map_data["assignment"] = partition.assignment
        map_data["fairness_score"] = partition["fairness_score"]
        map_data["competitiveness_score"] = partition["competitiveness_score"]
        map_data["compactness_score"] = partition["compactness_score"]
        map_data["democratic"] = partition["2014_House"].counts("Democratic")
        map_data["republican"] = partition["2014_House"].counts("Republican")
        map_data["efficiency_gap"] = partition["efficiency_gap"]
        data["maps"].append(map_data)

        num += 1
        sum_fairness += partition["fairness_score"]
        sum_efficiency += partition["efficiency_gap"]
        if partition["fairness_score"] < min_fairness:
            min_fairness = partition["fairness_score"]
        if partition["fairness_score"] > max_fairness:
            max_fairness = partition["fairness_score"]
        if partition["competitiveness_score"] < min_competitiveness:
            min_competitiveness = partition["competitiveness_score"]
        if partition["competitiveness_score"] > max_competitiveness:
            max_competitiveness = partition["competitiveness_score"]
        if partition["compactness_score"] < min_compactness:
            min_compactness = partition["compactness_score"]
        if partition["compactness_score"] > max_compactness:
            max_compactness = partition["compactness_score"]
with open("data2.json", "w") as f:
    json.dump(data, f, indent=4)
print("avg fairness: " + str(sum_fairness / num))
print("fairness: " + str(min_fairness) + ", " + str(max_fairness))
print("competitiveness: " + str(min_competitiveness) + ", " + str(max_competitiveness))
print("compactness: " + str(min_compactness) + ", " + str(max_compactness))
print("num maps: " + str(num))
print("avg efficiency gap: " + str(sum_efficiency / num))


# for weight in range(100, 110, 10):
#     num_trials = 3
#     sum_percentages = 0
#     sum_min_fairness = 0
#     sum_avg_fairness = 0
#     sum_max_fairness = 0
#     sum_min_competitiveness = 0
#     sum_avg_competitiveness = 0
#     sum_max_competitiveness = 0
#     sum_min_compactness = 0
#     sum_avg_compactness = 0
#     sum_max_compactness = 0
#     for trial in range(num_trials):
#         chain = MarkovChain(
#             proposal=propose_random_flip,
#             is_valid=Validator([single_flip_contiguous]),
#             accept=metropolis_hastings_constrained(1, score_function(weight)),
#             initial_state=initial_partition,
#             total_steps=steps
#         )
#
#         # fairness_sum = 0
#         # competitiveness_sum = 0
#         # compactness_sum = 0
#         # first = 1
#         # for partition in chain:
#         #     if first:
#         #         print(partition["fairness_score"])
#         #         print(partition["competitiveness_score"])
#         #         print(partition["compactness_score"])
#         #         first = 0
#         #     fairness_sum += partition["fairness_score"]
#         #     competitiveness_sum += partition["competitiveness_score"]
#         #     compactness_sum += partition["compactness_score"]
#         # print()
#         # print(fairness_sum / steps)
#         # print(competitiveness_sum / steps)
#         # print(compactness_sum / steps)
#         # df = geopandas.read_file("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/NH_Shapefile/nh_final.shp")
#         # df.plot()
#         # matplotlib.pyplot.show()
#         # print(chain.num_accepted)
#
#         num_good = 0
#         min_fairness = 1000
#         min_competitiveness = 1
#         min_compactness = 1
#         max_fairness = 0
#         max_competitiveness = 0
#         max_compactness = 0
#         sum_fairness = 0
#         sum_competitiveness = 0
#         sum_compactness = 0
#         for partition in chain:
#             good = True
#             for pop in partition["population"].values():
#                 if abs(pop - partition["ideal_population"]) / partition["ideal_population"] > 0.01:
#                     good = False
#                     break
#             if good:
#                 num_good += 1
#                 sum_fairness += partition["fairness_score"]
#                 sum_competitiveness += partition["competitiveness_score"]
#                 sum_compactness += partition["compactness_score"]
#                 if partition["fairness_score"] < min_fairness:
#                     min_fairness = partition["fairness_score"]
#                 if partition["competitiveness_score"] < min_competitiveness:
#                     min_competitiveness = partition["competitiveness_score"]
#                 if partition["compactness_score"] < min_compactness:
#                     min_compactness = partition["compactness_score"]
#                 if partition["fairness_score"] > max_fairness:
#                     max_fairness = partition["fairness_score"]
#                 if partition["competitiveness_score"] > max_competitiveness:
#                     max_competitiveness = partition["competitiveness_score"]
#                 if partition["compactness_score"] > max_compactness:
#                     max_compactness = partition["compactness_score"]
#         sum_percentages += num_good / steps
#         sum_min_fairness += min_fairness
#         sum_avg_fairness += sum_fairness / num_good
#         sum_max_fairness += max_fairness
#         print(max_fairness)
#         sum_min_competitiveness += min_competitiveness
#         sum_avg_competitiveness += sum_competitiveness / num_good
#         sum_max_competitiveness += max_competitiveness
#         sum_min_compactness += min_compactness
#         sum_avg_compactness += sum_compactness / num_good
#         sum_max_compactness += max_compactness
#     print("weight " + str(weight) + ":")
#     print("percent usable: " + str(sum_percentages / num_trials))
#     print("fairness: " + str(sum_min_fairness / num_trials) + ", " + str(sum_avg_fairness / num_trials) +
#           ", " + str(sum_max_fairness / num_trials))
#     print("competitiveness: " + str(sum_min_competitiveness / num_trials) +
#           ", " + str(sum_avg_competitiveness / num_trials) + ", " + str(sum_max_competitiveness / num_trials))
#     print("compactness: " + str(sum_min_compactness / num_trials) + ", " + str(sum_avg_compactness / num_trials) +
#           ", " + str(sum_max_compactness / num_trials))
