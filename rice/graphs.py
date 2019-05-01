from matplotlib.lines import Line2D

import json
import matplotlib.pyplot as plt
import numpy
import pandas
import seaborn

with open("TX_final/maps.json", "r") as f:
    maps = json.load(f)
for cmap in maps:
    lst = []
    for key in cmap["d"].keys():
        lst.append(cmap["d"][key] / (cmap["d"][key] + cmap["r"][key]))
    cmap["percents"] = tuple(lst)
data = pandas.DataFrame(sorted(cmap["percents"]) for cmap in maps)
with open("TX_final/stats.json", "r") as f:
    stats = json.load(f)
for i in range(16):
    for j in range(6):
        for k in range(6):
            name = str(i) + str(j) + str(k)
            assignment = stats[name]["a"]
            idx = 0
            for cmap in maps:
                if cmap["a"] == assignment:
                    break
                idx += 1
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axhline(0.5, color="#cccccc")
            data.boxplot(ax=ax, positions=range(len(data.columns)))
            data.iloc[idx].plot(style="ro", ax=ax)
            ax.set_ylabel("Democratic vote share")
            ax.set_xlabel("Sorted districts")
            ax.set_ylim(0, 1)
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
            plt.savefig("TX_final/" + name + "graph1.png", bbox_inches="tight")
            plt.close()
            print("done with " + name)


f_scores = []
c1_scores = []
c2_scores = []
for cmap in maps:
    f_scores.append(cmap["f"])
    c1_scores.append(cmap["c1"])
    c2_scores.append(cmap["c2"])
for i in range(16):
    for j in range(6):
        for k in range(6):
            name = str(i) + str(j) + str(k)
            smap = stats[name]
            fig, ax = plt.subplots(figsize=(8, 6))
            seaborn.set_style("whitegrid")
            red = "#FF0000"
            green = "#008000"
            blue = "#0000FF"
            seaborn.kdeplot(numpy.array(f_scores), color=green)
            seaborn.kdeplot(numpy.array(c1_scores), color=blue)
            seaborn.kdeplot(numpy.array(c2_scores), color=red)
            ax.axvline(smap["f"], color=green, linestyle="--")
            ax.axvline(smap["c1"], color=blue, linestyle="--")
            ax.axvline(smap["c2"], color=red, linestyle="--")
            lines = [Line2D([0], [0], color=green),
                     Line2D([0], [0], color=green, linestyle="dashed"),
                     Line2D([0], [0], color=blue),
                     Line2D([0], [0], color=blue, linestyle="dashed"),
                     Line2D([0], [0], color=red),
                     Line2D([0], [0], color=red, linestyle="dashed")]
            ax.set_xlabel("Score")
            ax.set_ylabel("Density")
            ax.legend(lines, ["Fairness density", "Current fairness",
                              "Competitiveness density", "Current competitiveness",
                              "Compactness density", "Current compactness"])
            plt.savefig("TX_final/" + name + "graph2.png", bbox_inches="tight")
            plt.close()
            print("done with " + name)
