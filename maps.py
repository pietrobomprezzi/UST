# Import packages and setup
import geopandas as gpd
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Polygon

from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.colors import Normalize
import geopandas as gpd

pd.options.mode.chained_assignment = None
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Crimea shapefile prep --if it aint broke dont fix it (or touch it)
shapefile_crimea = 'Shapefile/ne_50m_admin_0_breakaway_disputed_areas/ne_50m_admin_0_breakaway_disputed_areas.shp'

gdf_crimea = gpd.read_file(shapefile_crimea)[['ADMIN', 'ADM0_A3', 'geometry']]
print(gdf_crimea)
print("Shape:", gdf_crimea.shape)
# Rename columns
gdf_crimea.columns = ['country', 'iso', 'geometry']

# Keep crimea
gdf_crimea = gdf_crimea.drop(index=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,24,25,26])

gdf_crimea.country[gdf_crimea.country == 'Russia'] = 'Crimea'
gdf_crimea.iso[gdf_crimea.country == 'Crimea'] = 'UKR'

print("Shape:", gdf_crimea.shape)
gdf_crimea

# Prepare all other shapefiles
shapefile = 'Shapefile/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'

gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]

# Rename ISO codes
gdf['ADM0_A3'].replace({'KOS': 'XKX', 'PSX': 'PSE', 'SDS': 'SSD'}, inplace=True)

# Rename columns
gdf.columns = ['country', 'iso', 'geometry']

# Drop Algeria, Greenland, Iceland, Iraq, Iran, Morocco, Northern Cyprus, Russia, Syria, Tunesia, Kazakhstan, Libanon
gdf = gdf[gdf.iso != 'DZA']
gdf = gdf[gdf.iso != 'GRL']
gdf = gdf[gdf.iso != 'IRN']
gdf = gdf[gdf.iso != 'IRQ']
gdf = gdf[gdf.iso != 'MAR']
gdf = gdf[gdf.iso != 'CYN']
gdf = gdf[gdf.iso != 'CNM']
gdf = gdf[gdf.iso != 'RUS']
gdf = gdf[gdf.iso != 'SYR']
gdf = gdf[gdf.iso != 'TUN']
gdf = gdf[gdf.iso != 'KAZ']
gdf = gdf[gdf.iso != 'LBN']

# Append crimea
gdf = pd.concat([gdf, gdf_crimea])

#final world  gdf
print("Shape:", gdf.shape)
gdf.plot()

#data is raw UNCHR data
df_refugee = pd.read_excel('Refugee data.xlsx', '311023 UNCHR data')
pop = pd.read_excel('Refugee data.xlsx', 'country sample and pop')

def get_last_value(series):
    return series.iloc[-1]

# Create a new column 'Last_Value' with the last value of each group
df_refugee['Number'] = df_refugee.groupby('iso3')['individuals'].transform(get_last_value)
#cutoff of PREVIOUS RELEASE - CHANGE ACCORDINGLY
# Specify the year, month, and day
year = 2023
month = 7
day = 31
cutoff = datetime(year, month, day)

def find_closest_date_before_cutoff(series, cutoff_date):
    # Ensure that the series is in datetime format
    series = pd.to_datetime(series)
    
    # Filter the series for dates before the cutoff
    filtered_series = series[series < cutoff_date]
    
    # Find the closest date before the cutoff
    closest_date = filtered_series.max()
    
    return closest_date

df_refugee['Closest_Date_Before_Cutoff'] = df_refugee.groupby('iso3')['correct date'].transform(
    lambda group_series: find_closest_date_before_cutoff(group_series, cutoff)
)

# value at last cutoff date
df_refugee['Temp_Column'] = df_refugee.apply(lambda row: row['individuals'] if row['correct date'] == row['Closest_Date_Before_Cutoff'] else None, axis=1)

df_refugee['last_number'] = df_refugee.groupby('iso3')['Temp_Column'].transform('max')
# Drop the temporary column
df_refugee = df_refugee.drop(columns=['Temp_Column'])

#basic calculations
#variation since last release -many negatives
df_refugee['variation'] = (df_refugee['Number'] - df_refugee['last_number'])/df_refugee['last_number']


# refugee data with shapefile
me_refugee = gdf.merge(df_refugee[['iso3','Number','last_number','variation']], left_on='iso', right_on='iso3', how='left', suffixes=('_shape', ''))

# Create a custom polygon
polygon = Polygon([(-25,35.225), (50.5,35.225), (50.5,72.5),(-25,75)])

poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=me_refugee.crs)
# Clip polygon from the map of Europe
europe = gpd.clip(me_refugee, polygon)


#collapse to the iso3 level otherwise double info
europe = europe.groupby('country').first().reset_index()
#add percent population
europe = europe.merge(pop, left_on='country', right_on='Country', how='left',validate = '1:1')

# MAP 1 absolute values

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

europe.plot(column='Number', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f", 'pad': 0.1})

cb_ax = fig.axes[1]
cb_ax.tick_params(labelsize=9)

plt.show()

#% of population
europe['percent'] = europe['Number']/europe['Population2020']

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

europe.plot(column='percent', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0), 'pad': 0.1})

cb_ax = fig.axes[1]
cb_ax.tick_params(labelsize=9)

plt.show()


#-------------NEW MAPS WORK IN PROGRESS

#% of population
pop = pd.read_excel('Refugee data.xlsx', 'population 2020')

europe2 = europe.merge(pop, left_on='country', right_on='Country', how='left',validate = '1:1')

europe2['percent'] = europe2['Number']/europe2['Population in 2020']

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

europe2[europe2.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

europe2.plot(column='percent', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0), 'pad': 0.1})

cb_ax = fig.axes[1]
cb_ax.tick_params(labelsize=9)

plt.show()


# MAP 2 absolute values with arrows
#map with total values, arrows with variation

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

# Get centroid
europe["centroid"] = europe["geometry"].centroid

# Plot the countries
ukraine_centroid = europe[europe['country'] == 'Ukraine']['centroid'].iloc[0]

# Plot the underlying map
ax = europe.plot(column='Number', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f"})

# Plot Ukraine
europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=1)

# Normalize the 'Number' column for line thickness
norm = Normalize(vmin=europe['Number'].min(), vmax=europe['Number'].max())

# Function to create a curved path between two points
def concave_curved_line(p1, p2, curvature=0.2, lw=1):
    x1, y1 = p1
    x2, y2 = p2
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2 - curvature * (x2 - x1)
    return Path([p1, (cx, cy), p2], [Path.MOVETO, Path.CURVE3, Path.CURVE3]), lw

# Plot curved lines from Ukraine's centroid to other countries' centroids if Number is not NaN
for i, row in europe[europe['Number'].notna()].iterrows():
    if row['country'] != 'Ukraine':
        line_path, line_width = concave_curved_line((ukraine_centroid.x, ukraine_centroid.y), (row['centroid'].x, row['centroid'].y), lw=norm(row['Number']) * 5)
        patch = PathPatch(line_path, facecolor='none', lw=line_width, edgecolor='lightcoral')
        ax.add_patch(patch)

plt.legend()
plt.show()


#test - basically same as test2 but im playing with the parameter 2 vs *5
fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

# Get centroid
europe["centroid"] = europe["geometry"].centroid

# Plot the underlying map
ax = europe.plot(column='Number', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f"})

# Plot Ukraine
ukraine_centroid = europe[europe.iso == 'UKR']['centroid'].iloc[0]
europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=1)

# Normalize the 'variation' column for line thickness
norm = Normalize(vmin=europe['variation'].min(), vmax=europe['variation'].max())

# Function to create a curved path between two points
def concave_curved_line(p1, p2, curvature=0.2, lw=1):
    x1, y1 = p1
    x2, y2 = p2
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2 - curvature * (x2 - x1)
    return Path([p1, (cx, cy), p2], [Path.MOVETO, Path.CURVE3, Path.CURVE3]), lw

# Plot curved lines from Ukraine's centroid to other countries' centroids if Number is not NaN
for i, row in europe[europe['variation'].notna()].iterrows():
    if row['country'] != 'Ukraine':
        line_path, line_width = concave_curved_line((ukraine_centroid.x, ukraine_centroid.y), (row['centroid'].x, row['centroid'].y), lw=norm(row['variation']) * 2)
        patch = PathPatch(line_path, facecolor='none', lw=line_width, edgecolor='lightblue' if row['variation'] >= 0 else 'lightcoral')
        ax.add_patch(patch)

plt.legend()
plt.show()

#test2 --works ok can play with transparency?
fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)

fig.set_size_inches(16, 10)

mpl.rc('hatch', color='black', linewidth=0.20)

# Get centroid
europe["centroid"] = europe["geometry"].centroid

# Plot the underlying map
ax = europe.plot(column='Number', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f"})

# Plot Ukraine
ukraine_centroid = europe[europe.iso == 'UKR']['centroid']
europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=1)

# Normalize the 'variation' column for line thickness
norm_thickness = Normalize(vmin=europe['variation'].min(), vmax=europe['variation'].max())

# Function to create a curved path between two points
def concave_curved_line(p1, p2, curvature=0.2):
    x1, y1 = p1
    x2, y2 = p2
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2 - curvature * (x2 - x1)
    return Path([p1, (cx, cy), p2], [Path.MOVETO, Path.CURVE3, Path.CURVE3])

# Plot curved lines from Ukraine's centroid to other countries' centroids if Number is not NaN
for i, row in europe[europe['variation'].notna()].iterrows():
    if row['country'] != 'Ukraine':
        line_path = concave_curved_line((ukraine_centroid.x.values[0], ukraine_centroid.y.values[0]), (row['centroid'].x, row['centroid'].y))
        line_width = abs(norm_thickness(row['variation'])) * 5
        patch = PathPatch(line_path, facecolor='none', lw=line_width, edgecolor='lightblue' if row['variation'] >= 0 else 'lightcoral')
        ax.add_patch(patch)

plt.legend()
plt.show()

# MAP 3 - (% population)

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)


fig.set_size_inches(16, 10)


mpl.rc('hatch', color='black', linewidth=0.20)


europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

europe.plot(column='PopulationShare', ax=ax, legend=True, cmap='Blues', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.200, 'format':'%.0f%%', 'orientation': 'horizontal', 'anchor':(0.5, 2.0)})

cb_ax = fig.axes[1]
cb_ax.tick_params(labelsize=9)

#plt.title('Incoming Ukrainian refugees until May 6 (% of population)')

plt.savefig('Refugees_May31_PercentPop.png', dpi=800, bbox_inches='tight')

#MAPS ON HEAVY WEAPON DELIVERIES

# Import weapon data

df_weapon = pd.read_excel('Heavy weapons _ June 7.xlsx', 'Release 4 _ 0706')

print('Shape:', df_weapon.shape)
# df_weapon

# Merge shapefile

me_weapon = gdf.merge(df_weapon, left_on='iso', right_on='CountryISO', how='left', suffixes=('_shape', ''))

me_weapon['MapColor'] = me_weapon['MapColor'].fillna('lightgray')

print('Shape:', me_weapon.shape)
# me_weapon

# Create a custom polygon

polygon = Polygon([(-25,35.225), (45.5,35.225), (45.5,72.5),(-25,75)])

poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=me_weapon.crs)


# Clip polygon from the map of Europe
europe = gpd.clip(me_weapon, polygon)

#europe.plot()

# -- Generate plot

fig, ax = plt.subplots(1, 1)

ax.axis('off')
ax.margins(x=0.0)


fig.set_size_inches(16, 10)


mpl.rc('hatch', color='black', linewidth=0.20)


europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

europe.plot(color=europe['MapColor'], ax=ax, edgecolor='dimgray', linewidth=0.15, legend=True)


patch_deliver = mpatches.Patch(color='firebrick', label='Delivered')
patch_commit = mpatches.Patch(color='lightcoral', label='Commitment without delivery')
# patch_none = mpatches.Patch(color='lightgrey', label='No data or commitment')

plt.legend(handles=[patch_deliver, patch_commit], loc='upper left', facecolor='white', framealpha=1, edgecolor='white', bbox_to_anchor=(0.025,0.975))


plt.suptitle("         Heavy weapons to Ukraine: commitments vs. deliveries\n", fontsize=12, y=0.925)

plt.title('between January 24, 2022 and May 31, 2023', fontsize=10, style='italic')

plt.savefig('HeavyWeapons_May31.png', dpi=800, bbox_inches='tight')