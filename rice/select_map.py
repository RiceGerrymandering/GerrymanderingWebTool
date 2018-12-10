from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain.updaters import Election, Tally
from gerrychain.updaters.election import fairness_score, competitiveness_score, ideal_population, population_score
from gerrychain.updaters.election import efficiency_gap
import json
import geopandas
import matplotlib.pyplot
import random
from osgeo import ogr
import sys


def initial_map(state):
    with open("./nhmaps.json") as f:
        data = json.load(f)
        # assignment = data["maps"][0]["a"]
        # driver = ogr.GetDriverByName('ESRI Shapefile')
        # data_source = driver.Open(
        #     "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/initial/tl_2012_33_vtd10.shp", 1)
        # layer = data_source.GetLayer()
        # index = 0
        # for feat in layer:
        #     feat.SetField("CD113", assignment[index])
        #     layer.SetFeature(feat)
        #     index += 1
        # data_source = None
        df = geopandas.read_file("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/initial/tl_2012_33_vtd10.shp")
        df.plot(column="CD113", legend=True)
        matplotlib.pyplot.axis("off")
        matplotlib.pyplot.savefig("./initial_map.png", bbox_inches="tight")
        matplotlib.pyplot.show()
        return data["maps"][0]


def select(state, fairness, competitiveness, compactness):
    with open("./nhmaps.json") as f:
        data = json.load(f)
        min_acceptable_fairness = int(0.2 * (fairness - 1) * data["num_unique_fairness_scores"])
        max_acceptable_fairness = int(0.2 * fairness * data["num_unique_fairness_scores"])
        min_acceptable_competitiveness = int(0.2 * (competitiveness - 1) * data["num_unique_competitiveness_scores"])
        max_acceptable_competitiveness = int(0.2 * competitiveness * data["num_unique_competitiveness_scores"])
        min_acceptable_compactness = int(0.2 * (compactness - 1) * data["num_unique_compactness_scores"])
        max_acceptable_compactness = int(0.2 * compactness * data["num_unique_compactness_scores"])
        map_pool = []
        for i in range(len(data["maps"])):
            if (min_acceptable_fairness <= data["maps"][i]["fi"] <= max_acceptable_fairness
                    and min_acceptable_competitiveness <= data["maps"][i]["c1i"] <= max_acceptable_competitiveness
                    and min_acceptable_compactness <= data["maps"][i]["c2i"] <= max_acceptable_compactness):
                map_pool.append(i)
        if not map_pool:
            return {"num_maps": 0, "map": None}
        selected_map = data["maps"][random.choice(map_pool)]
        driver = ogr.GetDriverByName('ESRI Shapefile')
        data_source = driver.Open(
            "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp", 1)
        layer = data_source.GetLayer()
        index = 0
        for feat in layer:
            feat.SetField("CD113", selected_map["a"][index])
            layer.SetFeature(feat)
            index += 1
        data_source = None
        df = geopandas.read_file("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp")
        df.plot(column="CD113", legend=True)
        matplotlib.pyplot.savefig("./new_map.png", bbox_inches="tight")
        matplotlib.pyplot.show()

        return {"num_maps": len(map_pool), "map": selected_map}


print(select("", 3, 5, 3))
