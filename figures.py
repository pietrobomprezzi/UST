

#sankey chart

from floweaver import *
import pandas as pd 
import numpy as np
import matplotlib
weapons = pd.read_csv('weapons.csv')

#--------------mid point macroregions

#two separate charts
#generate grouped data (stats)
flows = (
    weapons.groupby(['source',"weapons"])
    .agg({"comm": "first"})
    .reset_index().rename(columns={'weapons':'target','comm':'value'})
    )

nodes = {
    "embark_port": ProcessGroup(flows["source"].unique().tolist()),
    "disembark_port": ProcessGroup(flows["target"].unique().tolist()),
}

ordering = [["embark_port"], ["disembark_port"]]

bundles = [Bundle("embark_port", "disembark_port")]

sdd = SankeyDefinition(nodes, bundles, ordering)
weave(sdd, flows).to_widget()

#---------------do all the graph setup
embark_port = Partition.Simple("process", flows["source"].unique().tolist())
disembark_port = Partition.Simple("process", flows["target"].unique().tolist())

nodes["embark_port"].partition = embark_port
nodes["disembark_port"].partition = disembark_port

weave(sdd, flows, link_color=QuantitativeScale('value',palette='Blues_9')).to_widget()

#---deliveries


#two separate charts
#generate grouped data (stats)
flows = (
    weapons.groupby(['weapons',"target"])
    .agg({"del": "first"})
    .reset_index().rename(columns={'weapons':'source','del':'value'})
    )

nodes = {
    "embark_port": ProcessGroup(flows["source"].unique().tolist()),
    "disembark_port": ProcessGroup(flows["target"].unique().tolist()),
}

ordering = [["embark_port"], ["disembark_port"]]

bundles = [Bundle("embark_port", "disembark_port")]

sdd = SankeyDefinition(nodes, bundles, ordering)
weave(sdd, flows).to_widget()

#---------------do all the graph setup
embark_port = Partition.Simple("process", flows["source"].unique().tolist())
disembark_port = Partition.Simple("process", flows["target"].unique().tolist())

nodes["embark_port"].partition = embark_port
nodes["disembark_port"].partition = disembark_port

weave(sdd, flows, link_color=QuantitativeScale('value',palette='Blues_5')).to_widget()


#test
data = {
    'nodes': [
        {'name': 'Czech Republic'},
        {'name': 'Denmark'},
        {'name': 'France'},
        {'name': 'Germany'},
        {'name': 'Italy'},
        {'name': 'Netherlands'},
        {'name': 'Norway'},
        {'name': 'Poland'},
        {'name': 'Slovenia'},
        {'name': 'United Kingdom'},
        {'name': 'United States'},
        {'name': 'Howitzers (Committed)'},
        {'name': 'Howitzers (Delivered)'},
        {'name': 'MLRS (Committed)'},
        {'name': 'MLRS (Delivered)'},
        {'name': 'Tanks (Committed)'},
        {'name': 'Tanks (Delivered)'},
        {'name': 'Anti-Aircraft (Committed)'},
        {'name': 'Anti-Aircraft (Delivered)'},
        {'name': 'IFV (Committed)'},
        {'name': 'IFV (Delivered)'},
        {'name': 'Ukraine'}
    ],
    'links': [
        {'source': 0, 'target': 10, 'value': 38},    # Czech Republic to Howitzers (Committed)
        {'source': 0, 'target': 11, 'value': 38},    # Czech Republic to Howitzers (Delivered)
        {'source': 2, 'target': 12, 'value': 2},     # France to Howitzers (Committed)
        {'source': 2, 'target': 13, 'value': 2},     # France to Howitzers (Delivered)
        {'source': 3, 'target': 14, 'value': 33},    # Germany to MLRS (Committed)
        {'source': 3, 'target': 15, 'value': 33},    # Germany to MLRS (Delivered)
        {'source': 4, 'target': 16, 'value': 2},     # Italy to Tanks (Committed)
        {'source': 4, 'target': 17, 'value': 0},     # Italy to Tanks (Delivered)
        {'source': 5, 'target': 18, 'value': 0},     # Netherlands to Anti-Aircraft (Committed)
        {'source': 5, 'target': 19, 'value': 0},     # Netherlands to Anti-Aircraft (Delivered)
        {'source': 6, 'target': 20, 'value': 201},   # Norway to IFV (Committed)
        {'source': 6, 'target': 21, 'value': 201},   # Norway to IFV (Delivered)
        {'source': 7, 'target': 10, 'value': 54},    # Poland to Howitzers (Committed)
        {'source': 7, 'target': 11, 'value': 54},    # Poland to Howitzers (Delivered)
        {'source': 8, 'target': 22, 'value': 35},    # Slovenia to Ukraine (IFV Delivered)
        {'source': 9, 'target': 23, 'value': 0},     # United Kingdom to Ukraine (Howitzers Delivered)
        {'source': 9, 'target': 24, 'value': 0},     # United Kingdom to Ukraine (MLRS Delivered)
        {'source': 9, 'target': 25, 'value': 0},     # United Kingdom to Ukraine (Tanks Delivered)
        {'source': 9, 'target': 26, 'value': 0},     # United Kingdom to Ukraine (Anti-Aircraft Delivered)
        {'source': 9, 'target': 27, 'value': 0},     # United Kingdom to Ukraine (IFV Delivered)
        {'source': 10, 'target': 22, 'value': 0},    # United States to Ukraine (Howitzers Delivered)
        {'source': 10, 'target': 23, 'value': 38},   # United States to Howitzers (Committed)
        {'source': 10, 'target': 24, 'value': 32},   # United States to MLRS (Committed)
        {'source': 10, 'target': 25, 'value': 0},    # United States to Ukraine (Tanks Delivered)
        {'source': 10, 'target': 26, 'value': 18.5}, # United States to Anti-Aircraft (Committed)
        {'source': 10, 'target': 27, 'value': 8},    # United States to IFV (Committed)
    ]
}


import plotly.graph_objects as go


# Define nodes and links for the Sankey diagram
nodes = [dict(label=node['name']) for node in data['nodes']]
links = [
    dict(
        source=link['source'],
        target=link['target'],
        value=link['value']
    ) for link in data['links']
]

# Add a midway point for each equipment type
for idx, equipment in enumerate(['Howitzers', 'MLRS', 'Tanks', 'Anti-Aircraft', 'IFV']):
    nodes.append(dict(label=equipment))

    # Links from donor countries to equipment types
    for donor_idx in range(10):
        links.append(dict(source=donor_idx, target=len(nodes) - 1, value=data['links'][donor_idx * 2]['value']))

    # Links from equipment types to Ukraine
    links.append(dict(source=len(nodes) - 1, target=11, value=0))  # Delivered value set to 0 initially

fig = go.Figure(data=[go.Sankey(
    node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=nodes),
    link=dict(source=[link['source'] for link in links], target=[link['target'] for link in links],
              value=[link['value'] for link in links]))
])

fig.update_layout(title_text="Military Equipment Flow",
                  font=dict(size=10, color="RebeccaPurple"),
                  width=1000, height=600)

fig.show()



#FROM COUNTRY TO WEAPON
#-----------testing - need to sort it so the colors make more sense. us first for example
import pandas as pd
import plotly.graph_objects as go

# Updated data - needs to follow the same ordering
data = {
    'country': ['Czech Republic', 'Germany', 'Netherlands', 'Poland', 'United Kingdom', 'United States'],
    'howitzers_committed': [38, 37.333, 8, 54, 58, 198],
    'mlrs_committed': [33, 5, 0, 0, 6, 38],
    'tanks_committed': [90, 80, 88.667, 324, 14, 76],
    'aa_committed': [16, 23, 2, 0, 0, 15],
    'ifv_committed': [201, 100, 196, 42, 0, 190]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Extract weapon types from column names
weapon_types = [col.split('_')[0] for col in df.columns[1:]]

# Define colors for each source country
source_colors = {'Czech Republic': 'red', 'Germany': 'green', 'Netherlands': 'blue', 'Poland': 'orange', 'United Kingdom': 'purple', 'United States': 'pink'}

# Initialize nodes and links lists for Sankey diagram
nodes = []
links = []

# Add source nodes
for country in df['country']:
    nodes.append(country)

# Add target nodes and links
for idx, weapon_type in enumerate(weapon_types):
    nodes.append(weapon_type)
    for i, country in enumerate(df['country']):
        links.append({
            'source': i,  # index of the country in nodes list
            'target': len(df) + idx,  # index of the weapon type in nodes list
            'value': df[f'{weapon_type}_committed'][i],  # committed value
            'color': source_colors[country]  # color based on the source country
        })

# Create Sankey diagram with colored links
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes,
    ),
    link=dict(
        source=[link['source'] for link in links],
        target=[link['target'] for link in links],
        value=[link['value'] for link in links],
        color=[link['color'] for link in links]  # color based on the source country
    )
)])

# Update layout
fig.update_layout(title_text="Weapons Committed by Countries",
                  font=dict(size=10, color="white"),
                  plot_bgcolor="black", paper_bgcolor="black")

# Show plot
fig.show()



#-----------SECOND PART -- working a bit
import pandas as pd
import plotly.graph_objects as go

# Updated data
data = {
    'weapon_type': ['howitzers', 'mlrs', 'tanks', 'aa', 'ifv'],
    'delivered': [33, 33, 90, 16, 201]  # Assuming these are the delivered amounts for each weapon type
}

# Create a DataFrame
df = pd.DataFrame(data)

# Define colors for each weapon type
weapon_colors = {'howitzers': 'red', 'mlrs': 'green', 'tanks': 'blue', 'aa': 'orange', 'ifv': 'purple'}

# Initialize nodes and links lists for Sankey diagram
nodes = []
links = []

# Add source nodes (weapon types)
for weapon_type in df['weapon_type']:
    nodes.append(weapon_type)

# Add target node (Ukraine)
target_node = 'Ukraine'
nodes.append(target_node)

# Add links (delivered amounts) from weapon types to Ukraine
for i, weapon_type in enumerate(df['weapon_type']):
    links.append({
        'source': i,  # index of the weapon type in nodes list
        'target': len(df),  # index of the target node (Ukraine) in nodes list
        'value': df['delivered'][i],  # delivered amount for the weapon type
        'color': weapon_colors[weapon_type]  # color based on the weapon type
    })

# Create Sankey diagram with colored links
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes,
    ),
    link=dict(
        source=[link['source'] for link in links],
        target=[link['target'] for link in links],
        value=[link['value'] for link in links],
        color=[link['color'] for link in links]  # color based on the weapon type
    )
)])

# Update layout
fig.update_layout(title_text="Weapons Delivered to Ukraine",
                  font=dict(size=10, color="white"),
                  plot_bgcolor="black", paper_bgcolor="black")

# Show plot
fig.show()


-------GETTTING THERE

import pandas as pd
import plotly.graph_objects as go

# Updated dataset
data = {
    'weapon_status': ['howitzers_committed', 'howitzers_delivered', 'mlrs_committed', 'mlrs_delivered', 'tanks_committed', 'tanks_delivered', 'aa_committed', 'aa_delivered', 'ifv_committed', 'ifv_delivered'],
    'USA_amount': [198, 198, 38, 32, 76, 18, 15, 8, 190, 0]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Define colors for committed and delivered categories
colors = {
    'committed': 'rgba(31, 119, 180, 0.8)',
    'delivered': 'rgba(255, 127, 14, 0.8)'
}

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=['Howitzers Committed', 'Howitzers Delivered', 'MLRS Committed', 'MLRS Delivered', 'Tanks Committed', 'Tanks Delivered', 'AA Committed', 'AA Delivered', 'IFV Committed', 'IFV Delivered', 'Committed', 'UKR_How','UKR_IFV','UKR_Tanks','UKR_MLRS','UKR_AA'],
        color=['rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(31, 119, 180, 0.8)',
               'rgba(255, 127, 14, 0.8)', 'rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)',
               'rgba(31, 119, 180, 0.8)', 'rgba(255, 127, 14, 0.8)', 'rgba(31, 119, 180, 0.8)',
               'rgba(255, 127, 14, 0.8)', 'rgba(166, 206, 227, 0.8)', 'rgba(255, 255, 0, 0.8)']
    ),
    link=dict(
        source=[0, 2, 4, 6, 8,        10, 10, 10, 10, 10, 10,10,10,10,10],  # Sources for committed flows
        target=[10, 10, 10, 10, 10,    11,11, 12,12, 13,13, 14,14, 15,15],  # targets for committed flows
        value=[198, 38, 76, 15, 190,    198,0, 32,6,  18,58, 8,7,  0,190],  # Total committed amount
        color=['blue','blue','blue','blue','blue',  'blue','red','blue','red','blue','red','blue','red','blue','red',]
    )
)])

# Update layout
fig.update_layout(title_text="Weapons Flow to Ukraine",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()




import pandas as pd
import plotly.graph_objects as go

# Updated dataset
data = {
    'weapon_status': ['howitzers_committed', 'howitzers_delivered', 'mlrs_committed', 'mlrs_delivered', 'tanks_committed', 'tanks_delivered', 'aa_committed', 'aa_delivered', 'ifv_committed', 'ifv_delivered'],
    'USA_amount': [198, 198, 38, 32, 76, 18, 15, 8, 190, 0]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=['Howitzers Committed', 'MLRS Committed','Tanks Committed', 'AA Committed', 'IFV Committed', 'Committed', 'UKR_How','UKR_MLRS','UKR_Tanks','UKR_AA','UKR_IFV'],
        color=[]
    ),
    link=dict(
        source=[ 0, 1, 2, 3, 4,  5, 5, 5, 5, 5, 5,5,5,5,5],  # Sources for committed flows
        target=[5, 5, 5, 5, 5,    6,6, 7,7, 8,8, 9,9, 10,10],  # targets for committed flows
        value=[198, 38, 76, 15, 190,    198,0, 32,6,  18,58, 8,7,  0,190],  # Total committed amount
        color=['blue','blue','blue','blue','blue',  'blue','red','blue','red','blue','red','blue','red','blue','red',]
    )
)])

# Update layout
fig.update_layout(title_text="Weapons Flow to Ukraine",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()

----------------------------Circular exchanges

import pandas as pd
import plotly.graph_objects as go


# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=['Germany', 'Greece','Czechia','Slovakia','Lithuania','Latvia', 'Ukraine'],
        color=[]
    ),
    link=dict(
        source=[ 0,0,0,0,0  ,1,2,3,4,5   ],  # Sources for committed flows
        target=[1,2,3,4,5,   6,6,6,6,6],  # targets for committed flows
        value=[40, 20, 30, 8, 5,     40, 16, 15, 2,3   ],  # Total committed amount
        color=[]
    )
)])

# Update layout
fig.update_layout(title_text="German Circular exchanges",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()



import pandas as pd
import plotly.graph_objects as go

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=['Germany', 'Greece', 'Czechia', 'Slovakia', 'Lithuania', 'Latvia', 'Ukraine'],
        color=[]
    ),
    link=dict(
        source=[0, 0, 0, 0, 0, 1, 2, 3, 4, 5],  # Sources for committed flows
        target=[1, 2, 3, 4, 5, 6, 6, 6, 6, 6],  # Targets for committed flows
        value=[40, 20, 30, 8, 5, 40, 16, 15, 2, 3],  # Total committed amount
        color=['#C2D4FF', '#C2D4FF', '#C2D4FF', '#C2D4FF', '#C2D4FF', '#FFFFB2', '#FFFFB2', '#FFFFB2', '#FFFFB2', '#FFFFB2']  # Link colors
    )
)])

# Update layout
fig.update_layout(title_text="German Circular exchanges",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()