import json

# state = "NH"
state = "TX"

with open(state + "_final/stats.json", "r") as f:
    stats = json.load(f)

for comb in stats:
    tdv = 0
    trv = 0
    tds = 0
    trs = 0
    for dist in stats[comb]["d"]:
        tdv += stats[comb]["d"][dist]
        if stats[comb]["d"][dist] >= stats[comb]["r"][dist]:
            tds += 1
        else:
            trs += 1
    for dist in stats[comb]["r"]:
        trv += stats[comb]["r"][dist]
    stats[comb]["tdv"] = tdv
    stats[comb]["trv"] = trv
    stats[comb]["tds"] = tds
    stats[comb]["trs"] = trs

with open(state + "_final/stats_new.json", "w") as f:
    json.dump(stats, f)
