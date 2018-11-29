from gerrychain import Graph
from gerrychain import GeographicPartition
from gerrychain.updaters import Election, Tally
from gerrychain.updaters.election import fairness_score, competitiveness_score, ideal_population, population_score
import json
import geopandas
import matplotlib.pyplot
import random
from osgeo import ogr


def initialize():
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
                                                      "population_score": population_score})
    map_data = dict()
    map_data["assignment"] = initial_partition.assignment
    map_data["fairness_score"] = initial_partition["fairness_score"]
    map_data["competitiveness_score"] = initial_partition["competitiveness_score"]
    map_data["compactness_score"] = initial_partition["compactness_score"]
    map_data["democratic"] = initial_partition["2014_House"].percents("Democratic")
    map_data["republican"] = initial_partition["2014_House"].percents("Republican")
    df = geopandas.read_file("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/initial/tl_2012_33_vtd10.shp")
    df.plot(column="CD113")
    matplotlib.pyplot.savefig("./initial_map.png")
    return map_data


def select(fairness, competitiveness, compactness):
    fairness = 6 - fairness
    with open("./data2.json") as f:
        data = json.load(f)
        map_pool = []
        map_pool2 = []
        map_pool3 = []
        fairness_scores = []
        competitiveness_scores = []
        compactness_scores = []
        for partition in data["maps"]:
            compactness_scores.append(partition["compactness_score"])
        compactness_scores.sort()
        min_acceptable_compactness = compactness_scores[int(0.2 * (compactness - 1) * (len(compactness_scores) - 1))]
        max_acceptable_compactness = compactness_scores[int(0.2 * compactness * (len(compactness_scores) - 1))]
        for partition in data["maps"]:
            if min_acceptable_compactness <= partition["compactness_score"] <= max_acceptable_compactness:
                map_pool.append(partition)
                fairness_scores.append(partition["fairness_score"])
        fairness_scores.sort()
        min_acceptable_fairness = fairness_scores[int(0.2 * (fairness - 1) * (len(fairness_scores) - 1))]
        max_acceptable_fairness = fairness_scores[int(0.2 * fairness * (len(fairness_scores) - 1))]
        for partition in map_pool:
            if min_acceptable_fairness <= partition["fairness_score"] <= max_acceptable_fairness:
                map_pool2.append(partition)
                competitiveness_scores.append(partition["competitiveness_score"])
        competitiveness_scores.sort()
        min_acceptable_competitiveness = competitiveness_scores[
            int(0.2 * (competitiveness - 1) * (len(competitiveness_scores) - 1))]
        max_acceptable_competitiveness = competitiveness_scores[
            int(0.2 * competitiveness * (len(competitiveness_scores) - 1))]
        for partition in map_pool2:
            if min_acceptable_competitiveness <= partition["competitiveness_score"] <= max_acceptable_competitiveness:
                map_pool3.append(partition)
        partition = map_pool3[0]

        driver = ogr.GetDriverByName('ESRI Shapefile')
        data_source = driver.Open(
            "./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp", 1)
        layer = data_source.GetLayer()
        for feat in layer:
            feat.SetField("CD113", partition["assignment"][feat.GetField("GEOID10")])
            layer.SetFeature(feat)
        data_source = None

        df = geopandas.read_file("./vtd-adjacency-graphs-master/vtd-adjacency-graphs/33/shapefile/tl_2012_33_vtd10.shp")
        df.plot(column="CD113")
        matplotlib.pyplot.savefig("./new_map.png")
        matplotlib.pyplot.show()

        return partition
