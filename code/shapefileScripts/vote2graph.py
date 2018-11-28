import json
import geopandas


# Load adjacency graph
json_string = open('txqueen.json')
graph = json.load(json_string)

# Load shapefile dataframe
df = geopandas.read_file('Texas_Shapefile/Texas_VTD.shp')

# Store VTD vote information in dictionary
vtd2votes = {}
for entry in df.iterrows():
    entry = entry[1]
    entry['VTD'] = entry['VTD'].lstrip('0')  # Strip leading zeroes
    vtd2votes[entry['VTD']] = {'D_VOTES': entry['NV_D'], 'R_VOTES': entry['NV_R']}

unlistedVTDs = []

# Iterate over graph nodes to add vote info
for node in graph['nodes']:
    vtd = node['NAME10'].lstrip('0')  # Strip leading zeroes
    # Add vote info if keys match up
    if vtd in vtd2votes.keys():
        dvotes = vtd2votes[vtd]['D_VOTES']
        rvotes = vtd2votes[vtd]['R_VOTES']
    # Otherwise add 1 vote per side (to avoid division by zero)
    else:
        unlistedVTDs.append(vtd)
        dvotes = 1
        rvotes = 1
    node['D_VOTES'] = dvotes
    node['R_VOTES'] = rvotes

unlistedVTDs.sort()
print('VTDs not in shapefile: ' + str(unlistedVTDs))

with open('graph.json', 'w') as outfile:
    json.dump(graph, outfile)