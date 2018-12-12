import json
import geopandas
import pandas as pd
import re


# Load adjacency graph
json_string = open('txrook.json')
graph = json.load(json_string)

# Load shapefile dataframe
# df = geopandas.read_file('Texas_Shapefile/Texas_VTD.shp')
df = pd.read_csv('TX_2010.txt', sep='\t', header = 0)


# Store VTD vote information in dictionary
vtd2votes = {}
for idx, row in df.iterrows():
    # print (row)
    # entry = entry[]
    # print(row)
    # print(getattr(row, 'year'))
    # row['VTD'] = getattr(row, 'VTD').lstrip('0')  # Strip leading zeroes
    # df.loc[idx, 'VTD'] = df.loc[idx, 'vtd'].upper().replace("'", "").replace('*', "")  # Set to
    # df.loc[idx, 'CNTYVTD'] = df.loc[idx, 'CNTYVTD']
    # vtd2votes[entry['CNTYVTD']] = {'D_VOTES': entry['NV_D'], 'R_VOTES': entry['NV_R']}
    vtd2votes[df.loc[idx, 'cntyvtd']] = {'D_VOTES': getattr(row, 'g2010_USH_dv'), 'R_VOTES': getattr(row, 'g2010_USH_rv')}

unlistedVTDs = []

# Iterate over graph nodes to add vote info
for node in graph['nodes']:
    # vtd = node['NAME10'].lstrip('0')  # Strip leading zeroes
    # print(node['NAME10'])
    # vtd = node['NAME10'].replace('TOWN OF ', '')
    # vtd = vtd.replace('TOWNSHIP OF ', '')
    # vtd = node['NAME10'].lstrip('0')
    # vtd = node['id'].replace()
    vtd = re.sub('^48', '', node['id'], count=1).lstrip('0')
    # print(vtd)
    # print('')
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
print(len(unlistedVTDs))

with open('graph.json', 'w') as outfile:
    json.dump(graph, outfile)