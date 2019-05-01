from copy import deepcopy
from matplotlib.colors import ListedColormap
from osgeo import ogr
import geopandas
import json
import matplotlib.pyplot as plt
import seaborn

# district_abbreviations = {"01": "0", "02": "1"}
# with open("NH/maps.json", "r") as f:
#     data = json.load(f)
# for i in range(len(data["maps"])):
#     a = ''
#     for j in range(len(data["maps"][i]["a"])):
#         a += district_abbreviations[data["maps"][i]["a"][j]]
#     data["maps"][i]["a"] = a
#     data["maps"][i]["f"] = 1 - abs(data["maps"][i]["f"])
#     data["maps"][i]["c2"] = data["maps"][i]["c2"] / 2.0
# open("NH/new/maps.json", "w").close()
# with open("NH/new/maps.json", "w") as f:
#     json.dump(data, f)
#
#
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
    "v": "32",
    "w": "33",
    "x": "34",
    "y": "35",
    "z": "36"
}
# state = "NH"
state = "TX"
with open("TX_final/maps.json", "r") as f:
    maps = json.load(f)
min_f = 1000
max_f = -1000
min_c1 = 1000
max_c1 = -1000
min_c2 = 1000
max_c2 = -1000
min_u = 1000
max_u = -1000
for cmap in maps:
    f = cmap["f"]
    c1 = cmap["c1"]
    c2 = cmap["c2"]
    u = cmap["u"]
    if f < min_f:
        min_f = f
    if f > max_f:
        max_f = f
    if c1 < min_c1:
        min_c1 = c1
    if c1 > max_c1:
        max_c1 = c1
    if c2 < min_c2:
        min_c2 = c2
    if c2 > max_c2:
        max_c2 = c2
    if u < min_u:
        min_u = u
    if u > max_u:
        max_u = u
dif_f = max_f - min_f
dif_c1 = max_c1 - min_c1
dif_c2 = max_c2 - min_c2
dif_u = max_u - min_u
for cmap in maps:
    cmap["f!"] = (cmap["f"] - min_f) / dif_f
    cmap["c1!"] = (cmap["c1"] - min_c1) / dif_c1
    cmap["c2!"] = (cmap["c2"] - min_c2) / dif_c2
    cmap["u!"] = (cmap["u"] - min_u) / dif_u
stats = {}
if state == "NH":
    shapefile = "vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp"
    cd = "CD113"
    districts = 2
else:
    shapefile = "vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/shapefile/tl_2012_48_vtd10.shp"
    cd = "CD113"
    districts = 36
for i in range(16):
    for j in range(6):
        c1 = j
        for k in range(6):
            c2 = k
            for cmap in maps:
                cmap["score"] = c1 * cmap["c1!"] + c2 * cmap["c2!"]
                if i < 6:
                    cmap["score"] += i * cmap["f!"]
                elif i < 11:
                    cmap["score"] += (i % 6 + 1) * cmap["u!"]
                else:
                    cmap["score"] += (i % 6 + 1) * (1 - cmap["u!"])
            maps.sort(key=lambda d: d["score"], reverse=True)
            smap = deepcopy(maps[0])
            smap.pop("score")
            smap.pop("f!")
            smap.pop("c1!")
            smap.pop("c2!")
            smap.pop("u!")
            # driver = ogr.GetDriverByName('ESRI Shapefile')
            # data_source = driver.Open(shapefile, 1)
            # layer = data_source.GetLayer()
            # idx = 0
            # for feat in layer:
            #     feat.SetField(cd, district_abbreviations_reversed[smap["a"][idx]])
            #     layer.SetFeature(feat)
            #     idx += 1
            # data_source = None

            # df = geopandas.read_file(shapefile)
            # df.plot(column=cd,
            #         cmap=ListedColormap(seaborn.color_palette("hls", districts)),
            #         legend=True)
            # plt.axis("off")
            name = str(i) + str(c1) + str(c2)
            stats[name] = smap
            # plt.savefig(state + "/new2/map" + name + ".png",
            #             bbox_inches="tight")
            # plt.close()
            print("done with " + name)
stats_path = "TX_final/stats.json"
open(stats_path, "w").close()
with open(stats_path, "w") as f:
    json.dump(stats, f)
