
#----------ecdf with seaborn
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
#df = px.data.tips()
#fig = px.ecdf(df, x="total_bill", y="tip", color="sex", ecdfnorm=None)
#fig.show()


df = pd.read_excel('weapons.xlsx')
#By weapon type

# making ECDF plot 
sns.ecdfplot(data=df,x='months', hue = 'Weapon type')
plt.show()

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



