from functools import partial
from gerrychain import GeographicPartition, Graph, MarkovChain
from gerrychain.accept import always_accept
from gerrychain.constraints import contiguous, within_percent_of_ideal_population
from gerrychain.updaters import Election, Tally
from gerrychain.proposals import recom
from osgeo import ogr
from gerrychain.scores import efficiency_gap
import math
import json


# Computes the fairness score of the input map.
def fairness_score(partition):
    return 1 - abs(1.0 * partition["Election"].seats("Democratic") / len(partition) -
                   partition["Election"].percent("Democratic"))


# Computes the unfairness score of the input map (in favor of Democrats).
def unfairness_score(partition):
    return (1.0 * partition["Election"].seats("Democratic") / len(partition) -
            partition["Election"].percent("Democratic") + 1) / 2


# Compute the competitiveness score of the input map.
def competitiveness_score(partition):
    return 1 - math.sqrt(sum((partition["Election"].percent("Democratic", race) - 0.5) ** 2
                             for race in partition["Election"].races)) * 2 / math.sqrt(len(partition))


# Compute the efficiency gap of the input map (in favor of Democrats).
def efficiency_gap_updater(partition):
    return efficiency_gap(partition["Election"])


def compactness_score(partition):
    return sum(partition["polsby_popper"].values()) / len(partition)


district_abbreviations = {
    "01": "0",
    "02": "1",
    "03": "2",
    "04": "3",
    "05": "4",
    "06": "5",
    "07": "6",
    "08": "7",
    "09": "8",
    "10": "9",
    "11": "a",
    "12": "b",
    "13": "c",
    "14": "d",
    "15": "e",
    "16": "f",
    "17": "g",
    "18": "h",
    "19": "i",
    "20": "j",
    "21": "k",
    "22": "l",
    "23": "m",
    "24": "n",
    "25": "o",
    "26": "p",
    "27": "q",
    "28": "r",
    "29": "s",
    "30": "t",
    "31": "u",
    "32": "v",
    "33": "w",
    "34": "x",
    "35": "y",
    "36": "z"
}

vtds = []
driver = ogr.GetDriverByName('ESRI Shapefile')
data_source = driver.Open("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/shapefile/tl_2012_48_vtd10.shp", 1)
layer = data_source.GetLayer()
for feat in layer:
    vtds.append(feat.GetField("GEOID10"))
data_source = None

graph = Graph.from_json("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010finalnew.json")
election = Election("Election",
                    {"Democratic": "D_VOTES", "Republican": "R_VOTES"},
                    alias="Election")
initial_partition = GeographicPartition(graph,
                                        assignment="CD113NEW",
                                        updaters={"Election": election,
                                                  "population": Tally("POP10", alias="population"),
                                                  "fairness_score": fairness_score,
                                                  "unfairness_score": unfairness_score,
                                                  "competitiveness_score": competitiveness_score,
                                                  "efficiency_gap": efficiency_gap_updater,
                                                  "compactness_score": compactness_score})
ideal_population = 1.0 * sum(initial_partition["population"].values()) / len(initial_partition)
proposal = partial(recom, pop_col="POP10", pop_target=ideal_population, epsilon=0.01, node_repeats=10)
pop_constraint = within_percent_of_ideal_population(initial_partition, percent=0.09)
chain = MarkovChain(proposal=proposal,
                    constraints=[contiguous, pop_constraint],
                    accept=always_accept,
                    initial_state=initial_partition,
                    total_steps=2000)

index = 0
maps = []
try:
    for partition in chain:
        if index % 10 == 0:
            print(index)
        index += 1

        assignment = ""
        for vtd in vtds:
            assignment += district_abbreviations[partition.assignment[vtd]]
        map_data = {"a": assignment,
                    "f": partition["fairness_score"],
                    "u": partition["unfairness_score"],
                    "c1": partition["competitiveness_score"],
                    "c2": partition["compactness_score"],
                    "d": partition["Election"].counts_labeled("Democratic"),
                    "r": partition["Election"].counts_labeled("Republican"),
                    "e": partition["efficiency_gap"]}
        maps.append(map_data)
except:
    pass
open("TX_final/maps.json", "w").close()
with open("TX_final/maps.json", "w") as f:
    json.dump(maps, f)
