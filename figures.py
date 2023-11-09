



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
df = px.data.tips()
fig = px.ecdf(df, x="total_bill", y="tip", color="sex", ecdfnorm=None)
fig.show()


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

#By country - tanks
df2 = df.loc[df['Weapon type']=='Tanks']
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
    title_text='Tank commitments (number of)',  # Set custom y-axis title
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
    title_text='Tank commitments (number of)',  # Set custom y-axis title
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
    title_text='Tank commitments (number of)',  # Set custom y-axis title
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