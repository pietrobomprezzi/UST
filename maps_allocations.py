#EUROPE MAPS - AID % GDP OVER TIME

# Import packages and setup
import geopandas as gpd
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Polygon
import countrynames
from collections import Counter
import math 
import matplotlib.font_manager as fm
from matplotlib.patheffects import withStroke
import os 

import geopandas as gpd
import datetime

#for gifs
import imageio

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
#gdf.plot()

#REMEMBER TO UPDATE THE DATA SHEET IN THIS FOLDER WITH LATEST UST DATA
gdpdata = pd.read_excel('latest UST data.xlsx','country summary (euro)')
#add iso codes
#countryname - iso packages
def country_iso(name):
    code = countrynames.to_code(name,fuzzy=True)
    return code

iso3 = [countrynames.to_code_3(r,fuzzy=True) for r in gdpdata['Country']]
Counter(iso3)
gdpdata['iso3'] = iso3 
checker=gdpdata.loc[gdpdata.iso3.isna(), 'Country']
Counter(checker)
#commission and council, none iso, ok

#isolate the gdp series for merging
gdpdata = gdpdata[['GDP (2021) € billion','iso3']]

#import table data for military ALLOCATIONS
data_UST = pd.read_excel('latest UST data.xlsx','allocations month military euro')
#drop euro dummy problematic for cumu sum
data_UST = data_UST.drop('EU member', axis=1)

#produce CUMU VALUE OF MILITARY alloc.
data_UST=data_UST.set_index('Country', append=True).cumsum(axis=1).reset_index(level='Country')

#add iso
iso3 = [countrynames.to_code_3(r,fuzzy=True) for r in data_UST['Country']]
Counter(iso3)
data_UST['iso3'] = iso3 
checker=data_UST.loc[data_UST.iso3.isna(), 'Country']
Counter(checker)

#merge in GDP data
data_UST = data_UST.merge(gdpdata,on='iso3',how='left')

# CREATE GEODATAFRAME
data_UST = gdf.merge(data_UST, left_on='iso', right_on='iso3', how='left', suffixes=('_shape', ''),indicator=True)
#check
data_UST._merge.value_counts()
#both==41, ok as it should be

# Create a custom polygon
polygon = Polygon([(-25,35.225), (50.5,35.225), (50.5,72.5),(-25,75)])

poly_gdf = gpd.GeoDataFrame([1], geometry=[polygon], crs=data_UST.crs)
# Clip polygon from the map of Europe
europe = gpd.clip(data_UST, polygon)

#for the loop, Extract column names (months)
monthlist = ['January (2022)', 'February (2022)', 'March (2022)', 'April (2022)', 'May (2022)', 'June (2022)', 'July (2022)', 'August (2022)', 'September (2022)', 'October (2022)', 'November (2022)', 'December (2022)', 'January (2023)', 'February (2023)', 'March (2023)',
 'April (2023)', 'May (2023)', 'June (2023)', 'July (2023)', 'August (2023)', 'September (2023)',
 'October (2023)', 'November (2023)', 'December (2023)', 'January, 15th (2024)']

# MAP 1 % military ALLOCATIONS over time

#using a loop to make n graphs and save them

# save all the maps in the charts folder
output_path = 'output/military alloc maps'

# set the min and max range for the choropleth map
#values should be based on data
vmin, vmax = 0, 25

#set a loop variable for saving in correct order for gif
i = 1
for month in monthlist:
        
    fig, ax = plt.subplots(1, 1)
    ax.axis('off')
    ax.margins(x=0.0)
    fig.set_size_inches(16, 10)
    mpl.rc('hatch', color='black', linewidth=0.20)

    europe[europe.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

    #COLUMN TO PLOT IS THE MONTH COLUMN
    europe.plot(column=month, ax=ax, legend=False, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, vmin=vmin, vmax=vmax, norm=plt.Normalize(vmin=vmin, vmax=vmax))

    # Add values on top of the map, excluding "nan"
    for idx, row in europe.iterrows():
        x, y = row.geometry.centroid.x, row.geometry.centroid.y
        value = row[month]
        if not math.isnan(value):
            text = ax.annotate(f'{value:.2f}', xy=(x, y), xytext=(-15, 0), textcoords="offset points", fontsize=10, color='black',weight='bold')
            text.set_path_effects([withStroke(linewidth=2, foreground='white')])


    title_font = fm.FontProperties(family='Copperplate Gothic Bold', style='normal', size=16)
    ax.set_title("Military Allocations, Total bilateral", fontproperties=title_font,loc='left')

    # Add a subtitle
    subtitle_font = fm.FontProperties(family='Copperplate Gothic Light', style='italic', size=9)
    ax.text(0.5, 0.95, "Total military allocations as of "  + month, ha='right', va='center', fontproperties=subtitle_font, transform=ax.transAxes)

    # Add a footnote
    footnote_font = fm.FontProperties(family='Calibri', style='normal', size=8)
    ax.text(0.5, 0.02, "Note: Short and multi-year. Does not include EU aid. In billion Euro.", ha='right', va='center', fontproperties=footnote_font, transform=ax.transAxes)

    #CHANGE ACCORDINGLY
    filepath = os.path.join(output_path,"{}_{}_cumu_mil_alloc.png".format(i, month))
    plt.savefig(filepath, bbox_inches='tight',dpi = 300)
    #increment
    i = i+1


# MAP 2 % military ALLOCATIONS over time as GDP

# save all the maps in the charts folder
output_path = 'output/military alloc maps gdp'

# set the min and max range for the choropleth map
#values should be based on data UPDATE ACCORDINGLY
vmin, vmax = 0, 5
#set a loop variable for saving in correct order for gif
i = 1
#duplicate the dataset because i need to overwrite it
europegdp = europe.copy()

for month in monthlist:

    #convert to % GDP
    percgdp = [(a/b)*100 for (a,b) in zip(europegdp[month],europegdp['GDP (2021) € billion'])]

    europegdp[month] = percgdp 
        
    fig, ax = plt.subplots(1, 1)
    ax.axis('off')
    ax.margins(x=0.0)
    fig.set_size_inches(16, 10)
    mpl.rc('hatch', color='black', linewidth=0.20)

    europegdp[europegdp.iso == 'UKR'].plot(ax=ax, edgecolor='black', linewidth=0.125, color='lightgrey', hatch='//////', legend=False, zorder=2)

    #COLUMN TO PLOT IS THE MONTH COLUMN
    europegdp.plot(column=month, ax=ax, legend=False, cmap='OrRd', edgecolor='gray', linewidth=0.15, missing_kwds={'color': 'gainsboro'}, vmin=vmin, vmax=vmax, norm=plt.Normalize(vmin=vmin, vmax=vmax))

    # Add values on top of the map, excluding "nan"
    for idx, row in europegdp.iterrows():
        x, y = row.geometry.centroid.x, row.geometry.centroid.y
        value = row[month]
        if not math.isnan(value):
            text = ax.annotate(f'{value:.2f}', xy=(x, y), xytext=(-15, 0), textcoords="offset points", fontsize=10, color='black',weight='bold')
            text.set_path_effects([withStroke(linewidth=2, foreground='white')])


    title_font = fm.FontProperties(family='Copperplate Gothic Bold', style='normal', size=16)
    ax.set_title("Military Allocations, % 2021 GDP", fontproperties=title_font,loc='left')

    # Add a subtitle
    subtitle_font = fm.FontProperties(family='Copperplate Gothic Light', style='italic', size=9)
    ax.text(0.5, 0.95, "Total military allocations as of "  + month, ha='right', va='center', fontproperties=subtitle_font, transform=ax.transAxes)

    # Add a footnote
    footnote_font = fm.FontProperties(family='Calibri', style='normal', size=8)
    ax.text(0.5, 0.02, "Note: Short and multi-year. Does not include EU aid.", ha='right', va='center', fontproperties=footnote_font, transform=ax.transAxes)

    #CHANGE ACCORDINGLY
    filepath = os.path.join(output_path,"{}_{}_cumu_mil_alloc_gdp.png".format(i, month))
    plt.savefig(filepath, bbox_inches='tight',dpi = 300)
    #increment
    i = i + 1

#--------------CONVERTING TO GIFS
from PIL import Image
import os
import imageio

#save as jpg
def convert_png_to_jpg(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get the list of PNG files in the input folder
    png_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]

    # Loop through each PNG file and convert to JPG
    for png_file in png_files:
        png_path = os.path.join(input_folder, png_file)
        output_path = os.path.join(output_folder, os.path.splitext(png_file)[0] + '.jpg')

        # Open and convert the image
        with Image.open(png_path) as img:
            img.convert('RGB').save(output_path, 'JPEG')

#military alloc maps
input_folder = "output/military alloc maps"
output_folder = "output/military alloc maps/jpg"
convert_png_to_jpg(input_folder, output_folder)

#military alloc maps gdp
input_folder = "output/military alloc maps gdp"
output_folder = "output/military alloc maps gdp/jpg"
convert_png_to_jpg(input_folder, output_folder)


#convert to gif

def create_gif(folder_path, output_gif_path, fps=.5,repeat_indefinitely=True):
    images = []

    # Get the list of JPG files in the folder
    jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

    # Sort the files to ensure correct order
    sorted_list = sorted(jpg_files, key=lambda x: int(x.split('_')[0]))

    # Read each image and append to the list
    for jpg_file in sorted_list:
        image_path = os.path.join(folder_path, jpg_file)
        images.append(imageio.imread(image_path))

    # Create the GIF
    imageio.mimsave(output_gif_path, images, fps=fps,loop=0)

#military alloc maps
folder_path = "output/military alloc maps/jpg"
output_gif_path = "output/military_allocs.gif"
create_gif(folder_path, output_gif_path)


#military alloc maps gdp
folder_path = "output/military alloc maps gdp/jpg"
output_gif_path = "output/military_allocs_gdp.gif"
create_gif(folder_path, output_gif_path)
