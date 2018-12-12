# import copy
# import geopandas
# import json
# import matplotlib.pyplot
# import random
# from osgeo import ogr
import sys 
import base64
import os


# # Dictionary storing, for each supported state, its FIPS code and a label indicating the district assignment being used
# # by the initial map for that state ("CD113" for the 113th Congress, and "CD" for the assignment preceding the 2010
# # redistricting).
# state_info = {
#     "NH": {"code": "33", "cd": "CD113"},
#     "TX": {"code": "48", "cd": "CD"}
# }


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

#     # Returning the district assignments is unnecessary
#     selected_map.pop("a")

#     # Save the map
#     df = geopandas.read_file(shapefile_name)
#     df.plot(column=state_info[state]["cd"], legend=True)
#     matplotlib.pyplot.axis("off")
#     matplotlib.pyplot.savefig("./initial_map.png", bbox_inches="tight")
#     # matplotlib.pyplot.show()

#     # Returning the constraint indices is unnecessary
#     selected_map.pop("fi")
#     selected_map.pop("c1i")
#     selected_map.pop("c2i")

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
#     matplotlib.pyplot.axis("off")
#     matplotlib.pyplot.savefig("./new_map.png", bbox_inches="tight")
#     # matplotlib.pyplot.show()
#     return {"num_maps": len(map_pool), "map": selected_map}


# # For the given state (which is represented by its standard two-letter abbreviation), gets a map satisfying the
# # given constraints (on 1-5 scales). This is the fast version, where the filtering is done beforehand to create files
# # of the form mapsXYZ.json in the folder for that state in this directory.
# # The map is saved as new_map.png in this directory.
# # Returns a dictionary with key "num_maps" mapping to the number of maps meeting the constraints, and key "map" mapping
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
#     matplotlib.pyplot.axis("off")
#     matplotlib.pyplot.savefig("./new_map.png", bbox_inches="tight")
#     # matplotlib.pyplot.show()
#     return {"num_maps": len(map_pool), "map": selected_map}


# # Saves to file the maps that meet each combination of the three constraints.
# def pre_filter(state):
#     # Open the file containing the precomputed maps
#     with open("./" + state + "/maps.json") as f:
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
#                 file_name = "./" + state + "/maps" + str(fairness) + str(competitiveness) + str(compactness) + ".json"
#                 open(file_name, "w").close()
#                 with open(file_name, "w") as f:
#                     json.dump(map_pool, f)
#                 print("done with constraints " + str(fairness) + str(competitiveness) + str(compactness) +
#                       ", num maps: " + str(len(map_pool)))



os.chdir("rice")

path = sys.argv[1] + "/" + "map" + sys.argv[2] + sys.argv[3] + sys.argv[4] + ".png"

#print(path)
#pre_filter(sys.argv[1])

#print(fast_select(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))

#open binary file in read mode and encode
try:
    image = open(path, 'rb') 
    image_read = image.read() 
    image_64_encode = base64.b64encode(image_read)
    string = "data:image/png;base64," + image_64_encode.decode("utf-8") 

    # #Write base64 encoding
    f = open("out.txt", "w")
    f.write(string)
    print(sys.argv)
except IOError:
    f = open("out.txt", "w")
    f.write("No Map!")
    print("Error!")
