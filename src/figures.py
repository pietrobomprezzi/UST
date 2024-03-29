



# delivered vs committed - not the appropriate graph
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
        label=['Germany', 'Greece: Marder-1A3 for BMP-1', 'Czechia: Leopard-2A4 for T-72', 'Slovakia: Leopard-2A4 for BMP-1', 'Lithuania', 'Latvia', 'Ukraine'],
        color=['#C2D4FF','#a6cee3', '#fdbf6f', '#b2df8a', '#ff9896', '#f0e442',  '#FFFFB2']
    ),
    link=dict(
        source=[0, 0, 0, 0, 0, 1, 2, 3, 4, 5],  # Sources for committed flows
        target=[1, 2, 3, 4, 5, 6, 6, 6, 6, 6],  # Targets for committed flows
        value=[40, 16, 15, 8, 5, 40, 20, 30, 2, 3],  # Total committed amount
        color=['#C2D4FF', '#C2D4FF', '#C2D4FF', '#C2D4FF', '#C2D4FF', '#FFFFB2', '#FFFFB2', '#FFFFB2', '#FFFFB2', '#FFFFB2']  # Link colors
    )
)])

# Update layout
fig.update_layout(title_text="German Circular exchanges",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()

---------------------WEAPONS TRANSFERS

import pandas as pd
import plotly.graph_objects as go

#notes for me: this is the dutch dk leopards https://www.rheinmetall.com/en/media/news-watch/news/2023/june/2023-06-27-rheinmetall-supplies-ukraine-with-leopard-2a4
#23.5 (leopard 1 with denmark)
#denamrk to german industry: t-72 tanks (70) + leopard 1 (23.5)

# Create Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=['United States','Netherlands','UK','Germany','Denmark','Czech industry','Private','German industry', 'Domestic stocks', 'Tanks', 'Howitzers 155mm'],
        color=['#C2D4FF', '#BC8F8F', '#CD853F', '#DAA520', '#556B2F', '#8B4513', '#FF4500', '#B8860B', '#006400', '#8FBC8F', '#2E8B57']

    ),
    link=dict(
        source=[0,1,1,2,3,3,4,         5,6,7,8],  # Sources for committed flows
        target=[5,5,7,6,7,8,7,          9,10,9,9],  # Targets for committed flows
        value=[45,45,70,48.5,23.5,180,93.5,   90,48.5,175,180],  # Total committed amount
        color=['#C2D4FF', '#BC8F8F', '#CD853F', '#DAA520', '#556B2F', '#8B4513', '#FF4500', '#B8860B', '#006400', '#8FBC8F', '#2E8B57']
  # Link colors
    )
)])

# Update layout
fig.update_layout(title_text="Main European weapon exchange schemes (value estimates, millions of USD)",
                  font=dict(size=10, color="black"),
                  plot_bgcolor="white", paper_bgcolor="white")

# Show plot
fig.show()

#-----------------------------step plot for weapons


#test code
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
#df = px.data.tips()
#fig = px.ecdf(df, x="total_bill", y="tip", color="sex", ecdfnorm=None)
#fig.show()


df = pd.read_excel('weapons.xlsx')
#By weapon type

fig = px.ecdf(df, x="months", y="Total commitments", color="Weapon type", ecdfnorm=None)

fig.update_xaxes(
    title_text='Months since start of war',  # Set custom x-axis title
    tickvals=df.months.values,           # Set custom tick values
    ticktext=df.Month.values,  # Set custom tick labels
    tickangle=45,                      # Rotate tick labels for better visibility
    showline=False,                     # Show x-axis line
    linewidth=2,                       # Set x-axis line width
    linecolor='black'                  # Set x-axis line color
)

fig.update_yaxes(
    title_text='Weapon commitments (number of)',  # Set custom y-axis title
    showline=False,                     # Show y-axis line
    linewidth=2,                       # Set y-axis line width
    linecolor='black'                  # Set y-axis line color
)

fig.update_layout(
    plot_bgcolor='lightgray',  # Set the background color of the plot
    legend=dict(
        title='Weapon Type',  # Set custom legend title
        orientation='h',       # Set legend orientation to horizontal ('h') or vertical ('v')
        yanchor='bottom',      # Set legend anchor point along the y-axis
        y=1.02,                # Set legend position relative to the chart
        xanchor='right',       # Set legend anchor point along the x-axis
        x=1                    # Set legend position relative to the chart
    )
)

# Show the modified figure
fig.show()

#POLISHED A BIT
#By country - tanks
df2 = df.loc[df['Weapon type']=='Tanks']
fig = px.ecdf(df2, x="months", y=['EU','non-EU NATO','US'], ecdfnorm=None)

fig.update_xaxes(
    title_text='Months of war',  # Set custom x-axis title
    tickvals=df2.months.values,           # Set custom tick values
    ticktext=df2.Month.values,  # Set custom tick labels
    tickangle=45,                      # Rotate tick labels for better visibility
    showline=False,                     # Show x-axis line
    linewidth=2,                       # Set x-axis line width
    linecolor='black'                  # Set x-axis line color
)

fig.update_yaxes(
    title_text='Tank commitments (number of)',  # Set custom y-axis title
    showline=False,                     # Show y-axis line
    linewidth=2,                       # Set y-axis line width
    linecolor='black',                  # Set y-axis line color
    showgrid=False
    #dont show gridlines
)

fig.update_layout(
    plot_bgcolor='linen',  # Set the background color of the plot
    legend=dict(
        title='Donor group',  # Set custom legend title
        orientation='h',       # Set legend orientation to horizontal ('h') or vertical ('v')
        yanchor='bottom',      # Set legend anchor point along the y-axis
        y=1.02,                # Set legend position relative to the chart
        xanchor='right',       # Set legend anchor point along the x-axis
        x=1                    # Set legend position relative to the chart
    ),
    height=500,  # Set the height of the plot
    width=800    # Set the width of the plot
)

# Show the modified figure
fig.show()

#By country - howitzers
df2 = df.loc[df['Weapon type']=='Howitzers']
fig = px.ecdf(df2, x="months", y=['EU','non-EU NATO','US'], ecdfnorm=None)

fig.update_xaxes(
    title_text='Months since start of war',  # Set custom x-axis title
    tickvals=df2.months.values,           # Set custom tick values
    ticktext=df2.Month.values,  # Set custom tick labels
    tickangle=45,                      # Rotate tick labels for better visibility
    showline=False,                     # Show x-axis line
    linewidth=2,                       # Set x-axis line width
    linecolor='black'                  # Set x-axis line color
)

fig.update_yaxes(
    title_text='Howitzers commitments (number of)',  # Set custom y-axis title
    showline=False,                     # Show y-axis line
    linewidth=2,                       # Set y-axis line width
    linecolor='black'                  # Set y-axis line color
)

fig.update_layout(
    plot_bgcolor='lightgray',  # Set the background color of the plot
    legend=dict(
        title='Donor group',  # Set custom legend title
        orientation='h',       # Set legend orientation to horizontal ('h') or vertical ('v')
        yanchor='bottom',      # Set legend anchor point along the y-axis
        y=1.02,                # Set legend position relative to the chart
        xanchor='right',       # Set legend anchor point along the x-axis
        x=1                    # Set legend position relative to the chart
    )
)

# Show the modified figure
fig.show()

#By country - MLRS
df2 = df.loc[df['Weapon type']=='MLRS']
fig = px.ecdf(df2, x="months", y=['EU','non-EU NATO','US'], ecdfnorm=None)

fig.update_xaxes(
    title_text='Months since start of war',  # Set custom x-axis title
    tickvals=df2.months.values,           # Set custom tick values
    ticktext=df2.Month.values,  # Set custom tick labels
    tickangle=45,                      # Rotate tick labels for better visibility
    showline=False,                     # Show x-axis line
    linewidth=2,                       # Set x-axis line width
    linecolor='black'                  # Set x-axis line color
)

fig.update_yaxes(
    title_text='MLRS commitments (number of)',  # Set custom y-axis title
    showline=False,                     # Show y-axis line
    linewidth=2,                       # Set y-axis line width
    linecolor='black'                  # Set y-axis line color
)

fig.update_layout(
    plot_bgcolor='lightgray',  # Set the background color of the plot
    legend=dict(
        title='Donor group',  # Set custom legend title
        orientation='h',       # Set legend orientation to horizontal ('h') or vertical ('v')
        yanchor='bottom',      # Set legend anchor point along the y-axis
        y=1.02,                # Set legend position relative to the chart
        xanchor='right',       # Set legend anchor point along the x-axis
        x=1                    # Set legend position relative to the chart
    )
)

# Show the modified figure
fig.show()


#-------------------------------CIRCLE PACKING FOR INTERNATIONAL INITIATIVES

import plotly.express as px
import pandas as pd
import circlify
import matplotlib.pyplot as plt

df = pd.read_excel('international procurement.xlsx')

#collapse to donor initiative level

df = df.groupby(['international initiative','donor'], dropna=False).sum().reset_index()

df['euro'] = df['euro'].astype(int)

# Create a dictionary to store the hierarchy
data_dict = {'id': 'World', 'datum': df['euro'].sum(), 'children': []}

# Group by 'international initiative' and 'donor' and calculate the sum of 'euro'
grouped_df = df.groupby(['international initiative', 'donor'], as_index=False)['euro'].sum()

# Iterate over each international initiative
for initiative, group in grouped_df.groupby('international initiative'):
    initiative_data = {
        'id': initiative,
        'datum': group['euro'].sum(),
        'children': []
    }
    
    # Iterate over each donor in the international initiative
    for index, row in group.iterrows():
        donor_data = {'id': row['donor'], 'datum': row['euro']}
        initiative_data['children'].append(donor_data)
    
    data_dict['children'].append(initiative_data)

# Print the resulting data structure
print([data_dict])
data = [data_dict]

# Compute circle positions thanks to the circlify() function
circles = circlify.circlify(
    data, 
    show_enclosure=False, 
    target_enclosure=circlify.Circle(x=0, y=0, r=1)
)


# Create just a figure and only one subplot
fig, ax = plt.subplots(figsize=(14,14))

# Title
ax.set_title('International military coordination')

# Remove axes
ax.axis('off')

# Find axis boundaries
lim = max(
    max(
        abs(circle.x) + circle.r,
        abs(circle.y) + circle.r,
    )
    for circle in circles
)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

# Print circle the highest level (continents):
for circle in circles:
    if circle.level != 2:
      continue
    x, y, r = circle
    ax.add_patch( plt.Circle((x, y), r, alpha=0.5, linewidth=2, color="lightblue"))

# Print circle and labels for the highest level:
for circle in circles:
    if circle.level != 3:
      continue
    x, y, r = circle
    label = circle.ex["id"]
    ax.add_patch( plt.Circle((x, y), r, alpha=0.5, linewidth=2, color="#69b3a2"))
    plt.annotate(label, (x,y ), ha='center', color="white")

# Print labels for the continents
for circle in circles:
    if circle.level != 2:
      continue
    x, y, r = circle
    label = circle.ex["id"]
    #new y coordinate for the label (bottom)
    new_y = y - r
    plt.annotate(label, (x,new_y) ,va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5))


#ADDITIONAL LAYER
# Add an overarching circle around all existing circles
total_circle = circlify.Circle(x=-1, y=0, r=lim, level=1)
ax.add_patch(plt.Circle((total_circle.x, total_circle.y), total_circle.r, alpha=0.2, linewidth=2, color="red"))

# Annotate the overarching circle
#total_label = "Total Amount"
#plt.annotate(total_label, (total_circle.x, total_circle.y), va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5))



#-NOT LOOKING NICE

import plotly.express as px
import pandas as pd
import circlify
import matplotlib.pyplot as plt

df = pd.read_excel('international procurement.xlsx')

#collapse to donor initiative level

df = df.groupby(['international initiative','donor'], dropna=False).sum().reset_index()

df['euro'] = df['euro'].astype(int)

# Create a dictionary to store the hierarchy
data_dict = {'id': 'World', 'datum': df['euro'].sum(), 'children': []}

# Group by 'international initiative' and 'donor' and calculate the sum of 'euro'
grouped_df = df.groupby(['international initiative', 'donor'], as_index=False)['euro'].sum()

# Iterate over each international initiative
for initiative, group in grouped_df.groupby('international initiative'):
    initiative_data = {
        'id': initiative,
        'datum': group['euro'].sum(),
        'children': []
    }
    
    # Iterate over each donor in the international initiative
    for index, row in group.iterrows():
        donor_data = {'id': row['donor'], 'datum': row['euro']}
        initiative_data['children'].append(donor_data)
    
    data_dict['children'].append(initiative_data)

# Print the resulting data structure
print([data_dict])
data = [data_dict]

# Compute circle positions thanks to the circlify() function
circles = circlify.circlify(
    data, 
    show_enclosure=False, 
    target_enclosure=circlify.Circle(x=0, y=0, r=1)
)

# Increase figure size
fig, ax = plt.subplots(figsize=(20, 14))

# Title
ax.set_title('International military coordination')

# Remove axes
ax.axis('off')

# Find axis boundaries
lim = max(
    max(
        abs(circle.x) + circle.r,
        abs(circle.y) + circle.r,
    )
    for circle in circles
)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

# Print circle the highest level (continents):
for circle in circles:
    if circle.level != 2:
        continue
    x, y, r = circle
    ax.add_patch(plt.Circle((x, y), r, alpha=0.5, linewidth=2, color="lightblue"))

# Print circle and labels for the highest level:
for circle in circles:
    if circle.level != 3:
        continue
    x, y, r = circle
    label = circle.ex["id"]
    ax.add_patch(plt.Circle((x, y), r, alpha=0.5, linewidth=2, color="#69b3a2"))
    plt.annotate(label, (x, y), ha='center', color="white")

# Print labels for the continents
for circle in circles:
    if circle.level != 2:
        continue
    x, y, r = circle
    label = circle.ex["id"]
    # New y coordinate for the label (bottom)
    new_y = y - r
    plt.annotate(label, (x, new_y), va='center', ha='center', bbox=dict(facecolor='white', edgecolor='black', boxstyle='round', pad=.5))

# Add an overarching circle around all existing circles
total_circle = circlify.Circle(x=lim/2, y=0, r=lim, level=1)
ax.add_patch(plt.Circle((total_circle.x, total_circle.y), total_circle.r, alpha=0.2, linewidth=2, color="red"))

plt.show()


#STACKED PERCENTAGE PLOTS
import pandas as pd
import matplotlib.pyplot as plt

# Read the Excel file
UST_full = pd.read_excel("Ukraine_Support_Tracker_Release_14_YD.xlsx",
                        sheet_name="Commitments per Month",
                        header=10,  # Skip the first 10 rows
                        usecols="B:AA")

# Cleaning, getting rid of the empty row on top
UST_full = UST_full.iloc[1:]

# Pivot the dataframe
pivoted = UST_full.melt(id_vars=["Country"], value_vars=UST_full.columns[2:],
                       var_name="month", value_name="contribution")

# Apply the 'highlight' condition
highlight_countries = ['United States', 'France', 'Germany', 'EU (Commission and Council)']
pivoted["highlight"] = pivoted["Country"].apply(lambda x: x if x in highlight_countries else "Other")

# Format columns correctly
pivoted["month"] = pd.to_numeric(pivoted["month"], errors="coerce")
pivoted["highlight"] = pd.Categorical(pivoted["highlight"])

#collapse dataset to month-group ("highlight") level taking the sum of all contributions. will need this later for computing percentage of
pivoted = pivoted.groupby(["month", "highlight"], as_index=False)["contribution"].sum()

# Pivot the DataFrame for better handling
df_pivot = pivoted.pivot(index='month', columns='highlight', values='contribution').fillna(0)

#put in terms of percentages of whole
data_perc = df_pivot.divide(df_pivot.sum(axis=1), axis=0)

plt.stackplot(data_perc.index, data_perc.values.T, labels=data_perc.columns)
plt.legend(loc='upper left')
plt.margins(0,0)
plt.title('100 % stacked area chart')
plt.show()
