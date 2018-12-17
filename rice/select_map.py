# import copy
# import geopandas
import json
# import matplotlib.pyplot as plt
# import random
# from osgeo import ogr
import sys 
import base64
import os
# from matplotlib.colors import ListedColormap
# import seaborn


# Dictionary storing, for each supported state, its FIPS code and a label indicating the district assignment being used
# by the initial map for that state ("CD113" for the 113th Congress, and "CD" for the assignment preceding the 2010
# redistricting).
state_info = {
    "NH": {"code": "33", "cd": "CD113", "districts": 2},
    "TX": {"code": "48", "cd": "CD", "districts": 32}
}

# Map from 1-character abbreviations to district numbers, allowing for the district assignments of a map to be decoded
# from a string, if the VTD order is standardized
district_abbreviations_reversed = {
    "0": "01",
    "1": "02",
    "2": "03",
    "3": "04",
    "4": "05",
    "5": "06",
    "6": "07",
    "7": "08",
    "8": "09",
    "9": "10",
    "a": "11",
    "b": "12",
    "c": "13",
    "d": "14",
    "e": "15",
    "f": "16",
    "g": "17",
    "h": "18",
    "i": "19",
    "j": "20",
    "k": "21",
    "l": "22",
    "m": "23",
    "n": "24",
    "o": "25",
    "p": "26",
    "q": "27",
    "r": "28",
    "s": "29",
    "t": "30",
    "u": "31",
    "v": "32"
}


# # Gets the initial map for the given state (which is represented by its standard two-letter abbreviation).
# # The map is saved as initial_map.png in this directory.
# # Returns a dictionary with keys "f", "c1", "c2", "fp", "c1p", "c2p", "d", "r", and "e", which respectively map to
# # the fairness score, competitiveness score, compactness score, fairness percentile, competitiveness percentile,
# # compactness percentile, Democratic election results (in the form of a dictionary where the keys are the district
# # labels and the values are the number of Democratic votes in that district race), Republican election results (in the
# # same form as the Democratic ones), and efficiency gap of that district map.
# def initial_map(state):
#     # Open the file containing the precomputed maps
#     with open("./" + state + "/maps.json") as f:
#         data = json.load(f)
#     # The initial map
#     selected_map = data["maps"][0]
#     shapefile_name = ("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/" + state_info[state]["code"] +
#                       "/initial/tl_2012_" + state_info[state]["code"] + "_vtd10.shp")
#
#     # Set the district assignments in the shapefile
#     driver = ogr.GetDriverByName('ESRI Shapefile')
#     data_source = driver.Open(shapefile_name, 1)
#     layer = data_source.GetLayer()
#     index = 0
#     for feat in layer:
#         feat.SetField(state_info[state]["cd"], selected_map["a"][index])
#         layer.SetFeature(feat)
#         index += 1
#     data_source = None
#
#     # Returning the district assignments is unnecessary
#     selected_map.pop("a")
#
#     # Save the map
#     df = geopandas.read_file(shapefile_name)
#     df.plot(column=state_info[state]["cd"], legend=True)
#     plt.axis("off")
#     plt.savefig("./initial_map.png", bbox_inches="tight")
#     # matplotlib.pyplot.show()
#
#     # Returning the constraint indices is unnecessary
#     selected_map.pop("fi")
#     selected_map.pop("c1i")
#     selected_map.pop("c2i")
#
#     # Return the map stats
#     return selected_map


# # Use fast_select() instead, after calling pre_filter().
# def select(state, fairness, competitiveness, compactness):
#     with open("./" + state + "/maps.json") as f:
#         data = json.load(f)
#     maps = data["maps"]
#     min_acceptable_fairness = int(0.2 * (fairness - 1) * data["num_unique_fairness_scores"])
#     max_acceptable_fairness = int(0.2 * fairness * data["num_unique_fairness_scores"])
#     min_acceptable_competitiveness = int(0.2 * (competitiveness - 1) * data["num_unique_competitiveness_scores"])
#     max_acceptable_competitiveness = int(0.2 * competitiveness * data["num_unique_competitiveness_scores"])
#     min_acceptable_compactness = int(0.2 * (compactness - 1) * data["num_unique_compactness_scores"])
#     max_acceptable_compactness = int(0.2 * compactness * data["num_unique_compactness_scores"])
#     map_pool = []
#     for cur_map in maps:
#         if (min_acceptable_fairness <= cur_map["fi"] <= max_acceptable_fairness
#                 and min_acceptable_competitiveness <= cur_map["c1i"] <= max_acceptable_competitiveness
#                 and min_acceptable_compactness <= cur_map["c2i"] <= max_acceptable_compactness):
#             map_pool.append(cur_map)
#     if not map_pool:
#         return {"num_maps": 0, "map": None}
#     selected_map = random.choice(map_pool)
#     shapefile_name = ("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/" + state_info[state]["code"] +
#                       "/shapefile/tl_2012_" + state_info[state]["code"] + "_vtd10.shp")
#     driver = ogr.GetDriverByName('ESRI Shapefile')
#     data_source = driver.Open(shapefile_name, 1)
#     layer = data_source.GetLayer()
#     index = 0
#     for feat in layer:
#         feat.SetField(state_info[state]["cd"], selected_map["a"][index])
#         layer.SetFeature(feat)
#         index += 1
#     data_source = None
#     selected_map.pop("a")
#     df = geopandas.read_file(shapefile_name)
#     df.plot(column=state_info[state]["cd"], legend=True)
#     plt.axis("off")
#     plt.savefig("./new_map.png", bbox_inches="tight")
#     # matplotlib.pyplot.show()
#     return {"num_maps": len(map_pool), "map": selected_map}


# # For the given state (which is represented by its standard two-letter abbreviation), gets a map satisfying the
# # given constraints (on 1-5 scales). This is the fast version, where the filtering is done beforehand to create files
# # of the form mapsXYZ.json in the folder for that state in this directory.
# # The map is saved as new_map.png in this directory.
# # Returns a dictionary with key "num_maps" mapping to the number of maps meeting the constraints and key "map" mapping
# # to a dictionary with keys "f", "c1", "c2", "fp", "c1p", "c2p", "d", "r", and "e", which respectively map to
# # the fairness score, competitiveness score, compactness score, fairness percentile, competitiveness percentile,
# # compactness percentile, Democratic election results (in the form of a dictionary where the keys are the district
# # labels and the values are the number of Democratic votes in that district race), Republican election results (in the
# # same form as the Democratic ones), and efficiency gap of that district map.
# # WARNING: This requires pre_filter() to have been called already.
# def fast_select(state, fairness, competitiveness, compactness):
#     # Open the file containing the maps meeting those constraints for that state
#     with open("./" + state + "/maps" + str(fairness) + str(competitiveness) + str(compactness) + ".json") as f:
#         #print(f)
#         map_pool = json.load(f)
#         #print(map_pool)
#     # If no maps meet the constraints:
#     if not map_pool:
#         return {"num_maps": 0, "map": None}
#     # Randomly choose a map to show
#     selected_map = random.choice(map_pool)
#     shapefile_name = ("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/" + state_info[state]["code"] +
#                       "/shapefile/tl_2012_" + state_info[state]["code"] + "_vtd10.shp")
#     # Apply the district assignments in the map to the shapefile for the state
#     driver = ogr.GetDriverByName('ESRI Shapefile')
#     data_source = driver.Open(shapefile_name, 1)
#     layer = data_source.GetLayer()
#     index = 0
#     for feat in layer:
#         feat.SetField(state_info[state]["cd"], selected_map["a"][index])
#         layer.SetFeature(feat)
#         index += 1
#     data_source = None
#     # Returning the district assignments is unnecessary
#     selected_map.pop("a")
#     # Save the map as a .png file
#     df = geopandas.read_file(shapefile_name)
#     df.plot(column=state_info[state]["cd"], legend=True)
#     plt.axis("off")
#     # matplotlib.pyplot.savefig("./new_map.png", bbox_inches="tight")
#     plt.savefig("./" + state + "/map" + str(fairness) + str(competitiveness) + str(compactness) + ".png",
#                               bbox_inches="tight")
#     plt.close()
#     print("saved " + str(state) + " " + str(fairness) + str(competitiveness) + str(compactness))
#     # matplotlib.pyplot.show()
#     return {"num_maps": len(map_pool), "map": selected_map}


# # For the input state, save a PNG containing a map for each combination of the three constraints, plus statistics.
# # Requires, e.g., pre_filter() to have been called already to obtain the maps meeting the constraints.
# def save_map_images(state):
#     # Location of the corresponding shapefile
#     shapefile_name = ("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/" + state_info[state]["code"] +
#                       "/shapefile/tl_2012_" + state_info[state]["code"] + "_vtd10.shp")
#     stats = {}
#     # Iterate over all combinations of the constraints
#     for fairness in range(1, 6):
#         for competitiveness in range(1, 6):
#             for compactness in range(1, 6):
#                 # Open the file containing data for the maps meeting the current combination of constraints
#                 with open(state + "/maps" + str(fairness) + str(competitiveness) + str(compactness) + ".json") as f:
#                     map_pool = json.load(f)
#                 # Store the number of maps in the pool
#                 stats_dict = {"num_maps": len(map_pool), "map": {}}
#                 if map_pool:
#                     # Randomly choose a map meeting the constraints
#                     selected_map = random.choice(map_pool)
#                     # Update the district assignments in the shapefile
#                     driver = ogr.GetDriverByName('ESRI Shapefile')
#                     data_source = driver.Open(shapefile_name, 1)
#                     layer = data_source.GetLayer()
#                     index = 0
#                     for feat in layer:
#                         feat.SetField(state_info[state]["cd"], selected_map["a"][index])
#                         layer.SetFeature(feat)
#                         index += 1
#                     data_source = None
#                     # It is unnecessary to store the assignments in the statistics
#                     selected_map.pop("a")
#                     # Plot and save the map
#                     df = geopandas.read_file(shapefile_name)
#                     df.plot(column=state_info[state]["cd"],
#                             cmap=ListedColormap(seaborn.color_palette("hls", state_info[state]["districts"])),
#                             legend=True)
#                     plt.axis("off")
#                     plt.savefig(state + "/map" + str(fairness) + str(competitiveness) + str(compactness) + ".png",
#                                 bbox_inches="tight")
#                     plt.close()
#                     stats_dict["map"] = selected_map
#                 stats[str(fairness) + str(competitiveness) + str(compactness)] = stats_dict
#                 print("Done with " + str(state) + " " + str(fairness) + str(competitiveness) + str(compactness))
#     # Save the statistics to file
#     stats_path = state + "/stats.json"
#     open(stats_path, "w").close()
#     with open(stats_path, "w") as f:
#         json.dump(stats, f)


# # Saves to file the maps that meet each combination of the three constraints.
# def pre_filter(state):
#     # Open the file containing the precomputed maps
#     with open(state + "/maps.json") as f:
#         data = json.load(f)
#     maps = data["maps"]
#     # Iterate over all combinations of the three constraints
#     for fairness in range(1, 6):
#         for competitiveness in range(1, 6):
#             for compactness in range(1, 6):
#                 # The acceptable range of indices in the sorted lists of fairness, competitiveness, compactness scores
#                 min_acceptable_fairness = int(0.2 * (fairness - 1) * data["num_unique_fairness_scores"])
#                 max_acceptable_fairness = int(0.2 * fairness * data["num_unique_fairness_scores"])
#                 min_acceptable_competitiveness = int(
#                     0.2 * (competitiveness - 1) * data["num_unique_competitiveness_scores"])
#                 max_acceptable_competitiveness = int(0.2 * competitiveness * data["num_unique_competitiveness_scores"])
#                 min_acceptable_compactness = int(0.2 * (compactness - 1) * data["num_unique_compactness_scores"])
#                 max_acceptable_compactness = int(0.2 * compactness * data["num_unique_compactness_scores"])
#                 # Collect all maps meeting this combination of constraints
#                 map_pool = []
#                 for cur_map in maps:
#                     if (min_acceptable_fairness <= cur_map["fi"] <= max_acceptable_fairness
#                             and min_acceptable_competitiveness <= cur_map["c1i"] <= max_acceptable_competitiveness
#                             and min_acceptable_compactness <= cur_map["c2i"] <= max_acceptable_compactness):
#                         # Deep copy to prevent messing with future iterations
#                         copied_map = copy.deepcopy(cur_map)
#                         # Storing the constraint indices is unnecessary after filtering
#                         copied_map.pop("fi")
#                         copied_map.pop("c1i")
#                         copied_map.pop("c2i")
#                         map_pool.append(copied_map)
#                 # Save the filtered maps to file
#                 file_name = state + "/maps" + str(fairness) + str(competitiveness) + str(compactness) + ".json"
#                 open(file_name, "w").close()
#                 with open(file_name, "w") as f:
#                     json.dump(map_pool, f)
#                 print("done with constraints " + str(fairness) + str(competitiveness) + str(compactness) +
#                       ", num maps: " + str(len(map_pool)))


os.chdir("rice")
path = sys.argv[1] + "/" + "map" + sys.argv[2] + sys.argv[3] + sys.argv[4] + ".png"
statsPath = sys.argv[1] + "/stats.json"

statFile = open(statsPath, 'rb')
stats = json.loads(statFile.read())

# open binary file in read mode and encode
try:
    image = open(path, 'rb')
    image_read = image.read()
    image_64_encode = base64.b64encode(image_read)
    string = "data:image/png;base64," + image_64_encode.decode("utf-8")

    data = {
        "stats" : stats,
        "img" : string
    }

    # #Write base64 encoding
    f = open("out.txt", "w")
    f.write(json.dumps(data))
    print(sys.argv)
except IOError:
    f = open("out.txt", "w")
    f.write("No Map!")
    print("Error!")
