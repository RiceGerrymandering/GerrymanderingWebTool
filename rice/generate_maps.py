from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain import MarkovChain
from gerrychain.constraints import Validator, single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import metropolis_hastings_constrained
from gerrychain.updaters import Election, Tally
from gerrychain.updaters.election import fairness_score, competitiveness_score, ideal_population, population_score
from gerrychain.updaters.election import efficiency_gap
import json
from osgeo import ogr


# Map from district numbers to 1-character abbreviations, allowing for the district assignments of a map to be stored
# as a string, if the VTD order is standardized
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
    "32": "v"
}


# Returns a function that weighs a map's population score according to the input weight.
def score_function(population_weight):
    def fn(partition):
        return population_weight * partition["population_score"]
    return fn


# Runs a Markov chain on Texas, with pop_weight as the population score weight, until num_accepted maps are accepted
# (including the initial map). Only maps where each district is under percent_pop_parity are considered for statistics.
def tune_pop_weight(pop_weight, num_accepted, percent_pop_parity):
    # Read in the adjacency graph from file
    graph = Graph.from_json("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010final.json")
    # Store the standardized VTD order
    vtds = []
    driver = ogr.GetDriverByName('ESRI Shapefile')
    data_source = driver.Open("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/shapefile/tl_2012_48_vtd10.shp", 1)
    layer = data_source.GetLayer()
    for feat in layer:
        vtds.append(feat.GetField("GEOID10"))
    data_source = None
    # Set up the election updater, initial partition, and Markov chain
    election = Election(
        "Election",
        {"Democratic": "D_VOTES", "Republican": "R_VOTES"},
        alias="Election"
    )
    initial_partition = GeographicPartition(graph, assignment="CD",
                                            updaters={"Election": election,
                                                      "fairness_score": fairness_score,
                                                      "competitiveness_score": competitiveness_score,
                                                      "population": Tally("POP10", alias="population"),
                                                      "ideal_population": ideal_population,
                                                      "population_score": population_score,
                                                      "efficiency_gap": efficiency_gap})
    chain = MarkovChain(
        proposal=propose_random_flip,
        is_valid=Validator([single_flip_contiguous]),
        accept=metropolis_hastings_constrained(1, score_function(pop_weight)),
        initial_state=initial_partition,
        total_steps=num_accepted
    )
    # Baselines for min/max statistics
    min_fairness = 1000
    max_fairness = -1000
    min_competitiveness = 1000
    max_competitiveness = -1000
    min_compactness = 1000
    max_compactness = -1000
    min_efficiency_gap = 1000
    max_efficiency_gap = -1000
    # Number of maps meeting the population parity constraint
    num_good = 0
    # Store district assignments for each map to remove duplicates
    assignments = []
    for partition in chain:
        # Determine if the current map meets the population parity constraint
        good = True
        for pop in partition["population"].values():
            if (abs(pop - partition["ideal_population"]) / float(partition["ideal_population"]) >
                    percent_pop_parity / 100.0):
                good = False
                break
        if good:
            num_good += 1
            # Store the current map's district assignments as a string
            assignment = ""
            for vtd in vtds:
                assignment += district_abbreviations[partition.assignment[vtd]]
            if assignment not in assignments:
                assignments.append(assignment)
                # Update min/max statistics
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
                if partition["efficiency_gap"] < min_efficiency_gap:
                    min_efficiency_gap = partition["efficiency_gap"]
                if partition["efficiency_gap"] > max_efficiency_gap:
                    max_efficiency_gap = partition["efficiency_gap"]
    # Print diagnostic information
    print("Number of steps in chain: " + str(chain.num_valid))
    print("Number of accepted maps (including initial): " + str(num_accepted))
    print("Percent of valid maps rejected: " + str((chain.num_valid - num_accepted) / chain.num_valid * 100))
    print("Number of maps under " + str(percent_pop_parity) + "% population parity: " + str(num_good))
    print("Number of unique maps under " + str(percent_pop_parity) + "% population parity: " + str(len(assignments)))
    print()
    print("Statistics on maps under " + str(percent_pop_parity) + "% population parity:")
    print("Fairness scores: minimum " + str(min_fairness) + ", maximum " + str(max_fairness))
    print("Competitiveness scores: minimum " + str(min_competitiveness) + ", maximum " + str(max_competitiveness))
    print("Compactness scores: minimum " + str(min_compactness) + ", maximum " + str(max_compactness))
    print("Efficiency gap: minimum " + str(min_efficiency_gap) + ", maximum " + str(max_efficiency_gap))


# Runs a Markov chain on the state whose adjacency graph is at graph_file_loc and whose corresponding shapefile is at
# shapefile_loc, with pop_weight as the population score weight, until num_accepted maps are accepted (including the
# initial map). The attribute storing district assignments is represented by cd_label. Only maps where each district is
# under percent_pop_parity are stored and consider for statistics. Data for the chain is written at out_file_loc.
def generate(graph_file_loc, shapefile_loc, out_file_loc, cd_label, pop_weight, percent_pop_parity, num_accepted):
    # Read in the adjacency graph from file
    graph = Graph.from_json(graph_file_loc)
    # Set up the election updater and initial partition
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
    # Store the standardized VTD order
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
    # Set up the Markov chain
    chain = MarkovChain(
        proposal=propose_random_flip,
        is_valid=Validator([single_flip_contiguous]),
        accept=metropolis_hastings_constrained(1, score_function(pop_weight)),
        initial_state=initial_partition,
        total_steps=num_accepted
    )
    # Data to be written to file
    data = {}
    maps = []
    # Store district assignments for each map to remove duplicates
    assignments = []
    # Store constraint scores for all usable maps in chain
    fairness_scores = []
    competitiveness_scores = []
    compactness_scores = []
    # Store constraint scores for all unique usable maps in chain
    unique_fairness_scores = []
    unique_competitiveness_scores = []
    unique_compactness_scores = []
    # Store unique constraint scores for all unique usable maps in chain
    unique_fairness_scores_filtered = []
    unique_competitiveness_scores_filtered = []
    unique_compactness_scores_filtered = []
    # Baselines for min/max statistics
    min_fairness = 1000
    max_fairness = -1000
    min_competitiveness = 1000
    max_competitiveness = -1000
    min_compactness = 1000
    max_compactness = -1000
    min_efficiency_gap = 1000
    max_efficiency_gap = -1000
    # The current step in the chain
    idx = 0
    for partition in chain:
        print(idx)
        idx += 1
        # Determine if the current map meets the population parity constraint
        good = True
        for pop in partition["population"].values():
            if (abs(pop - partition["ideal_population"]) / float(partition["ideal_population"]) >
                    percent_pop_parity / 100.0):
                good = False
                break
        if good:
            fairness_scores.append(partition["fairness_score"])
            competitiveness_scores.append(partition["competitiveness_score"])
            compactness_scores.append(partition["compactness_score"])
            # Store the current map's district assignments as a string
            assignment = ""
            for vtd in vtds:
                assignment += district_abbreviations[partition.assignment[vtd]]
            if assignment not in assignments:
                assignments.append(assignment)
                unique_fairness_scores.append(partition["fairness_score"])
                unique_competitiveness_scores.append(partition["competitiveness_score"])
                unique_compactness_scores.append(partition["compactness_score"])
                map_data = {"a": assignment, "f": partition["fairness_score"], "c1": partition["competitiveness_score"],
                            "c2": partition["compactness_score"],
                            "d": partition["Election"].counts_labeled("Democratic"),
                            "r": partition["Election"].counts_labeled("Republican"),
                            "e": round(partition["efficiency_gap"], 4)}
                maps.append(map_data)
                # Update min/max statistics
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
                if partition["efficiency_gap"] < min_efficiency_gap:
                    min_efficiency_gap = partition["efficiency_gap"]
                if partition["efficiency_gap"] > max_efficiency_gap:
                    max_efficiency_gap = partition["efficiency_gap"]
    # Sort and remove duplicates from the constraint scores for all unique usable maps
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
    # Store the number of unique constraint scores for all unique usable maps in chain, for later filtering
    data["num_unique_fairness_scores"] = len(unique_fairness_scores_filtered)
    data["num_unique_competitiveness_scores"] = len(unique_competitiveness_scores_filtered)
    data["num_unique_compactness_scores"] = len(unique_compactness_scores_filtered)
    for cur_map in maps:
        # Store the index of the current map's constraint score in the sorted list
        cur_map["fi"] = unique_fairness_scores_filtered.index(cur_map["f"])
        cur_map["c1i"] = unique_competitiveness_scores_filtered.index(cur_map["c1"])
        cur_map["c2i"] = unique_compactness_scores_filtered.index(cur_map["c2"])
        # Calculate percentiles for each constraint
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
        # Round constraint scores to save space on file
        cur_map["f"] = round(cur_map["f"], 4)
        cur_map["c1"] = round(cur_map["c1"], 4)
        cur_map["c2"] = round(cur_map["c2"], 4)
    # Write data to file
    data["maps"] = maps
    open(out_file_loc, "w").close()
    with open(out_file_loc, "w") as f:
        json.dump(data, f)
    # Print diagnostic information
    print("Number of steps in chain: " + str(chain.num_valid))
    print("Number of accepted maps (including initial): " + str(num_accepted))
    print("Percent of valid maps rejected: " + str((chain.num_valid - num_accepted) / chain.num_valid * 100))
    print("Number of maps under " + str(percent_pop_parity) + "% population parity: " + str(len(fairness_scores)))
    print("Number of unique maps under " + str(percent_pop_parity) + "% population parity: " + str(len(assignments)))
    print()
    print("Statistics on maps under " + str(percent_pop_parity) + "% population parity:")
    print("Fairness scores: minimum " + str(min_fairness) + ", maximum " + str(max_fairness))
    print("Competitiveness scores: minimum " + str(min_competitiveness) + ", maximum " + str(max_competitiveness))
    print("Compactness scores: minimum " + str(min_compactness) + ", maximum " + str(max_compactness))
    print("Efficiency gap: minimum " + str(min_efficiency_gap) + ", maximum " + str(max_efficiency_gap))


# generate("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/nhrookfinal.json",
#          "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp",
#          "./NH/maps.json", "CD113", 100, 25000)
# tune_pop_weight(10000, 5000, 5)
# generate("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010final.json",
#          "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/shapefile/tl_2012_48_vtd10.shp",
#          "./TX/maps.json", "CD", 10000, 5, 16000)
