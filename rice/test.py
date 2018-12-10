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

graph = Graph.from_json("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/nhrookfinal.json")
election = Election(
    "2014 House",
    {"Democratic": "D_VOTES", "Republican": "R_VOTES"},
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
steps = 20000


def score_function(population_weight):
    def fn(partition):
        return population_weight * partition["population_score"]
    return fn


vtds = []
# fldDef = ogr.FieldDefn('CD113', ogr.OFTString)
# fldDef.SetWidth(16)
driver = ogr.GetDriverByName('ESRI Shapefile')
data_source = driver.Open(
    "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp", 1)
layer = data_source.GetLayer()
# layer.CreateField(fldDef)
for feat in layer:
    # feat.SetField("CD113", initial_partition.assignment[feat.GetField("GEOID10")])
    # layer.SetFeature(feat)
    vtds.append(feat.GetField("GEOID10"))
data_source = None

population_weight = 100
chain = MarkovChain(
    proposal=propose_random_flip,
    is_valid=Validator([single_flip_contiguous]),
    accept=metropolis_hastings_constrained(1, score_function(population_weight)),
    initial_state=initial_partition,
    total_steps=steps
)

data = dict()
maps = []
assignments = []
fairness_scores = []
competitiveness_scores = []
compactness_scores = []
unique_fairness_scores = []
unique_competitiveness_scores = []
unique_compactness_scores = []
unique_fairness_scores_filtered = []
unique_competitiveness_scores_filtered = []
unique_compactness_scores_filtered = []
min_fairness = 1000
max_fairness = -1000
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
        fairness_scores.append(partition["fairness_score"])
        competitiveness_scores.append(partition["competitiveness_score"])
        compactness_scores.append(partition["compactness_score"])
        if partition.assignment not in assignments:
            assignments.append(partition.assignment)
            unique_fairness_scores.append(partition["fairness_score"])
            unique_competitiveness_scores.append(partition["competitiveness_score"])
            unique_compactness_scores.append(partition["compactness_score"])
            map_data = dict()
            map_assignments = []
            for vtd in vtds:
                map_assignments.append(partition.assignment[vtd])
            map_data["a"] = map_assignments
            map_data["f"] = partition["fairness_score"]
            map_data["c1"] = partition["competitiveness_score"]
            map_data["c2"] = partition["compactness_score"]
            map_data["d"] = partition["2014_House"].counts("Democratic")
            map_data["r"] = partition["2014_House"].counts("Republican")
            map_data["e"] = partition["efficiency_gap"]
            maps.append(map_data)
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


unique_fairness_scores.sort()
unique_competitiveness_scores.sort()
unique_compactness_scores.sort()
for i in range(len(unique_fairness_scores)):
    if i == 0 or unique_fairness_scores[i] != unique_fairness_scores[i - 1]:
        unique_fairness_scores_filtered.append(unique_fairness_scores[i])
    if i == 0 or unique_competitiveness_scores[i] != unique_competitiveness_scores[i - 1]:
        unique_competitiveness_scores_filtered.append(unique_competitiveness_scores[i])
    if i == 0 or unique_compactness_scores[i] != unique_compactness_scores[i - 1]:
        unique_compactness_scores_filtered.append(unique_compactness_scores[i])
data["num_unique_fairness_scores"] = len(unique_fairness_scores_filtered)
data["num_unique_competitiveness_scores"] = len(unique_competitiveness_scores_filtered)
data["num_unique_compactness_scores"] = len(unique_compactness_scores_filtered)
for i in range(len(maps)):
    maps[i]["fi"] = unique_fairness_scores_filtered.index(maps[i]["f"])
    maps[i]["c1i"] = unique_competitiveness_scores_filtered.index(maps[i]["c1"])
    maps[i]["c2i"] = unique_compactness_scores_filtered.index(maps[i]["c2"])
    # for j in range(len(maps)):
    #     if unique_fairness_scores[j][0] == i:
    #         maps[i]["fi"] = j
    #         break
    # for j in range(len(maps)):
    #     if unique_competitiveness_scores[j][0] == i:
    #         maps[i]["c1i"] = j
    #         break
    # for j in range(len(maps)):
    #     if unique_compactness_scores[j][0] == i:
    #         maps[i]["c2i"] = j
    #         break
    num_lower = 0
    for j in range(len(fairness_scores)):
        if fairness_scores[j] < maps[i]["f"]:
            num_lower += 1
    maps[i]["fp"] = int(num_lower / len(fairness_scores) * 100)
    num_lower = 0
    for j in range(len(competitiveness_scores)):
        if competitiveness_scores[j] < maps[i]["c1"]:
            num_lower += 1
    maps[i]["c1p"] = int(num_lower / len(competitiveness_scores) * 100)
    num_lower = 0
    for j in range(len(compactness_scores)):
        if compactness_scores[j] < maps[i]["c2"]:
            num_lower += 1
    maps[i]["c2p"] = int(num_lower / len(compactness_scores) * 100)
data["maps"] = maps
with open("nhmaps.json", "w") as f:
    json.dump(data, f)
print("num maps in chain: " + str(chain.num_valid))
print("num accepted maps: " + str(steps))
print("num usable maps: " + str(len(fairness_scores)))
print("num unique usable maps: " + str(len(assignments)))
print("fairness: " + str(min_fairness) + ", " + str(max_fairness))
print("competitiveness: " + str(min_competitiveness) + ", " + str(max_competitiveness))
print("compactness: " + str(min_compactness) + ", " + str(max_compactness))
