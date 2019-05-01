from gerrychain import GeographicPartition, Graph
from gerrychain.tree import recursive_tree_part
from gerrychain.updaters import Tally

import json


graph = Graph.from_json("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010finalnew.json")
initial_partition = GeographicPartition(graph,
                                        assignment="CD113NEW",
                                        updaters={"population": Tally("POP10", alias="population")})
ideal_population = 1.0 * sum(initial_partition["population"].values()) / len(initial_partition)
print("ideal " + str(ideal_population))
print(str(initial_partition["population"]))
# assignment = recursive_tree_part(initial_partition.graph,
#                                  list(initial_partition.parts.keys()),
#                                  ideal_population,
#                                  "POP10",
#                                  0.01,
#                                  node_repeats=10)
# with open("seed.json", "w") as f:
#     json.dump(assignment, f)

# with open("seed.json", "r") as f:
#     assignment = json.load(f)
# with open("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010final.json", "r") as f:
#     graph_data = json.load(f)
# for i in range(len(graph_data["nodes"])):
#     graph_data["nodes"][i]["CD113NEW"] = assignment[graph_data["nodes"][i]["id"]]
# with open("vtd-adjacency-graphs-master/vtd-adjacency-graphs/48/txrook2010finalnew.json", "w") as f:
#     json.dump(graph_data, f)
