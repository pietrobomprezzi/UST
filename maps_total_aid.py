#EUROPE MAPS - AID % GDP
#total and military

# Import packages and setup
import geopandas as gpd
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Polygon
import countrynames
from collections import Counter
import math 
import matplotlib.font_manager as fm
from matplotlib.patheffects import withStroke
import geopandas as gpd


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

#IMPORT % GDP DATA

#REMEMBER TO UPDATE THE DATA SHEET IN THIS FOLDER WITH LATEST UST DATA
data_UST = pd.read_excel('latest UST data.xlsx')
#add iso codes
#countryname - iso packages
def country_iso(name):
    code = countrynames.to_code(name,fuzzy=True)
    return code

iso3 = [countrynames.to_code_3(r,fuzzy=True) for r in data_UST['Country']]
Counter(iso3)
data_UST['iso3'] = iso3 
checker=data_UST.loc[data_UST.iso3.isna(), 'Country']
Counter(checker)
#commission and council, none iso, ok

# data with shapefile
data_UST = gdf.merge(data_UST, left_on='iso', right_on='iso3', how='left', suffixes=('_shape', ''),indicator=True)
#check
data_UST._merge.value_counts()
#both==41, ok as it should be


# Create a custom polygon
polygon = Polygon([(-25,35.225), (50.5,35.225), (50.5,72.5),(-25,75)])

poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=data_UST.crs)
# Clip polygon from the map of Europe
europe = gpd.clip(data_UST, polygon)


# MAP 1 % gdp all commitments

fig, ax = plt.subplots(1, 1)
ax.axis('off')
ax.margins(x=0.0)
fig.set_size_inches(16, 10)
mpl.rc('hatch', color='black', linewidth=0.20)

europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

#no legend 
europe.plot(column='Total bilateral commitments % 2021 GDP', ax=ax, legend=False, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'})

#with legend
#europe.plot(column='Total bilateral commitments % 2021 GDP', ax=ax, legend=True, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f"})

# Add values on top of the map, excluding "nan"
for idx, row in europe.iterrows():
    x, y = row.geometry.centroid.x, row.geometry.centroid.y
    value = row['Total bilateral commitments % 2021 GDP']
    if not math.isnan(value):
        text = ax.annotate(f'{value:.2f}', xy=(x, y), xytext=(-15, 0), textcoords="offset points", fontsize=10, color='black',weight='bold')
        text.set_path_effects([withStroke(linewidth=2, foreground='white')])

#for legend put this back
#cb_ax = fig.axes[1]
#cb_ax.tick_params(labelsize=9)

title_font = fm.FontProperties(family='Copperplate Gothic Bold', style='normal', size=16)
ax.set_title("Bilateral Commitments, % 2021 GDP", fontproperties=title_font,loc='left')

# Add a subtitle
subtitle_font = fm.FontProperties(family='Copperplate Gothic Light', style='italic', size=9)
ax.text(0.5, 0.95, "Total bilateral commitments as of January 15th, 2024", ha='right', va='center', fontproperties=subtitle_font, transform=ax.transAxes)

# Add a footnote
footnote_font = fm.FontProperties(family='Calibri', style='normal', size=8)
ax.text(0.5, 0.02, "Note: Short and multi-year. Does not include EU aid.", ha='right', va='center', fontproperties=footnote_font, transform=ax.transAxes)

plt.show()

# MAP 2 % gdp military commitments
#produce military commitments as share of GDP
milgdp = [(a/b)*100 for (a,b) in zip(europe['Military commitments € billion'],europe['GDP (2021) € billion'])]

europe['total military comm perc. GDP'] = milgdp 

fig, ax = plt.subplots(1, 1)
ax.axis('off')
ax.margins(x=0.0)
fig.set_size_inches(16, 10)
mpl.rc('hatch', color='black', linewidth=0.20)

europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

#europe.plot(column='total military comm perc. GDP', ax=ax, legend=True, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, legend_kwds={'shrink': 0.250, 'orientation':'horizontal','anchor': (0.5, 2.0),'format':"%.0f"})

#no legend 
europe.plot(column='total military comm perc. GDP', ax=ax, legend=False, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'})

# Add values on top of the map, excluding "nan"
for idx, row in europe.iterrows():
    x, y = row.geometry.centroid.x, row.geometry.centroid.y
    value = row['total military comm perc. GDP']
    if not math.isnan(value):
        text = ax.annotate(f'{value:.2f}', xy=(x, y), xytext=(-15, 0), textcoords="offset points", fontsize=10, color='black',weight='bold')
        text.set_path_effects([withStroke(linewidth=2, foreground='white')])

#if legend put these two back
#cb_ax = fig.axes[1]
#cb_ax.tick_params(labelsize=9)
# Add a title to the map
title_font = fm.FontProperties(family='Copperplate Gothic Bold', style='normal', size=16)
ax.set_title("Bilaterla military Commitments, % 2021 GDP", fontproperties=title_font,loc='left')

# Add a subtitle
subtitle_font = fm.FontProperties(family='Copperplate Gothic Light', style='italic', size=9)
ax.text(0.5, 0.95, "Total bilateral military commitments as of January 15th, 2024", ha='right', va='center', fontproperties=subtitle_font, transform=ax.transAxes)

# Add a footnote
footnote_font = fm.FontProperties(family='Calibri', style='normal', size=8)
ax.text(0.5, 0.02, "Note: Short and multi-year. Does not include EU aid.", ha='right', va='center', fontproperties=footnote_font, transform=ax.transAxes)


plt.show()
