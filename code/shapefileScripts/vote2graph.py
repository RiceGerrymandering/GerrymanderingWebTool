import json
import geopandas
import pandas as pd


# Load adjacency graph
json_string = open('nhrook.json')
graph = json.load(json_string)

# Load shapefile dataframe
# df = geopandas.read_file('Texas_Shapefile/Texas_VTD.shp')
df = pd.read_csv('NH_2012.txt', sep='\t', header = 0)


# Store VTD vote information in dictionary
vtd2votes = {}
for idx, row in df.iterrows():
    # entry = entry[]
    # print(row)
    # print(getattr(row, 'year'))
    # row['VTD'] = getattr(row, 'VTD').lstrip('0')  # Strip leading zeroes
    df.loc[idx, 'precinct'] = df.loc[idx, 'precinct'].upper().replace("'", "").replace('*', "")  # Set to
    # vtd2votes[entry['VTD']] = {'D_VOTES': entry['NV_D'], 'R_VOTES': entry['NV_R']}
    vtd2votes[df.loc[idx, 'precinct']] = {'D_VOTES': getattr(row, 'g2012_USP_dv'), 'R_VOTES': getattr(row, 'g2012_USP_rv')}

unlistedVTDs = []

# Iterate over graph nodes to add vote info
for node in graph['nodes']:
    # vtd = node['NAME10'].lstrip('0')  # Strip leading zeroes
    print(node['NAME10'])
    vtd = node['NAME10'].replace('TOWN OF ', '')
    vtd = vtd.replace('TOWNSHIP OF ', '')
    print(vtd)
    print('')
    # Add vote info if keys match up
    if vtd in vtd2votes.keys():
        dvotes = vtd2votes[vtd]['D_VOTES']
        rvotes = vtd2votes[vtd]['R_VOTES']
    # Otherwise add 0 votes per side
    else:
        unlistedVTDs.append(vtd)
        dvotes = 0
        rvotes = 0
    node['D_VOTES'] = dvotes
    node['R_VOTES'] = rvotes

unlistedVTDs.sort()
print('VTDs not in shapefile: ' + str(unlistedVTDs))

with open('graph.json', 'w') as outfile:
    json.dump(graph, outfile)