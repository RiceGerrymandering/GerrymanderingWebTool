from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain import MarkovChain
from gerrychain.constraints import Validator, single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import metropolis_hastings_constrained, always_accept
from gerrychain.updaters import Election, Tally
from gerrychain.updaters.election import fairness_score, competitiveness_score, ideal_population, population_score
from gerrychain.updaters.election import efficiency_gap
import math, json, geopandas, matplotlib
from osgeo import ogr


def generate(graph_file_loc, shapefile_loc, out_file_loc, cd_label, pop_weight, num_accepted):
    graph = Graph.from_json(graph_file_loc)
    election = Election(
        "Election",
        {"Democratic": "D_VOTES", "Republican": "R_VOTES"},
        alias="Election"
    )
    initial_partition = GeographicPartition(graph, assignment=cd_label,
                                            updaters={"Election": election,
                                                      "fairness_score": fairness_score,
                                                      "competitiveness_score": competitiveness_score,
                                                      "population": Tally("POP10", alias="population"),
                                                      "ideal_population": ideal_population,
                                                      "population_score": population_score,
                                                      "efficiency_gap": efficiency_gap})
    vtds = []
    # fldDef = ogr.FieldDefn('CD113', ogr.OFTString)
    # fldDef.SetWidth(16)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_source = driver.Open(shapefile_loc, 1)
    layer = data_source.GetLayer()
    # layer.CreateField(fldDef)
    for feat in layer:
        # feat.SetField("CD113", initial_partition.assignment[feat.GetField("GEOID10")])
        # layer.SetFeature(feat)
        vtds.append(feat.GetField("GEOID10"))
    data_source = None

    def score_function(population_weight):
        def fn(partition):
            return population_weight * partition["population_score"]
        return fn

    chain = MarkovChain(
        proposal=propose_random_flip,
        is_valid=Validator([single_flip_contiguous]),
        accept=metropolis_hastings_constrained(1, score_function(pop_weight)),
        initial_state=initial_partition,
        total_steps=num_accepted
    )

    data = {}
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
                map_data = {}
                map_assignments = []
                for vtd in vtds:
                    map_assignments.append(partition.assignment[vtd])
                map_data["a"] = map_assignments
                map_data["f"] = partition["fairness_score"]
                map_data["c1"] = partition["competitiveness_score"]
                map_data["c2"] = partition["compactness_score"]
                map_data["d"] = partition["Election"].counts_labeled("Democratic")
                map_data["r"] = partition["Election"].counts_labeled("Republican")
                map_data["e"] = round(partition["efficiency_gap"], 4)
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
    for cur_map in maps:
        cur_map["fi"] = unique_fairness_scores_filtered.index(cur_map["f"])
        cur_map["c1i"] = unique_competitiveness_scores_filtered.index(cur_map["c1"])
        cur_map["c2i"] = unique_compactness_scores_filtered.index(cur_map["c2"])
        num_lower = 0
        for j in range(len(fairness_scores)):
            if fairness_scores[j] < cur_map["f"]:
                num_lower += 1
        cur_map["fp"] = int(num_lower / len(fairness_scores) * 100)
        num_lower = 0
        for j in range(len(competitiveness_scores)):
            if competitiveness_scores[j] < cur_map["c1"]:
                num_lower += 1
        cur_map["c1p"] = int(num_lower / len(competitiveness_scores) * 100)
        num_lower = 0
        for j in range(len(compactness_scores)):
            if compactness_scores[j] < cur_map["c2"]:
                num_lower += 1
        cur_map["c2p"] = int(num_lower / len(compactness_scores) * 100)
        cur_map["f"] = round(cur_map["f"], 4)
        cur_map["c1"] = round(cur_map["c1"], 4)
        cur_map["c2"] = round(cur_map["c2"], 4)
    data["maps"] = maps
    open(out_file_loc, "w").close()
    with open(out_file_loc, "w") as f:
        json.dump(data, f)
    print("num maps in chain: " + str(chain.num_valid))
    print("num accepted maps: " + str(num_accepted))
    print("num usable maps: " + str(len(fairness_scores)))
    print("num unique usable maps: " + str(len(assignments)))
    print("fairness: min " + str(min_fairness) + ", max " + str(max_fairness))
    print("competitiveness: min " + str(min_competitiveness) + ", max " + str(max_competitiveness))
    print("compactness: min " + str(min_compactness) + ", max " + str(max_compactness))


generate("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/nhrookfinal.json",
         "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp",
         "./NH/maps.json", "CD113", 100, 25000)
