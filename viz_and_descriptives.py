#all data viz and summary stats computed here


#------------ number and amount pre and post geocode for aid categories
  
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#----all projects
full_crs = pd.read_csv('data/full_crs.csv', encoding='utf-8')

#donor names
with open("SELECT_DONORS.csv") as f_in:
    next(f_in)
    selecteddonorlist = (line.split(sep=',')[1] if line.split(sep=',')[0]=="X" else "" for line in f_in)
    selecteddonorlist = list(line for line in selecteddonorlist if line) # Non-blank lines in a list
f_in.close()

selected_donors = full_crs[full_crs['DonorName'].isin(selecteddonorlist)]
selected_donors.rawmergebackid.nunique()
#1475067 is the number of projects for the 18 donors

#---geocoded project dataset
rawdata = pd.read_csv('data/output/EU_projs_rawdata.csv',encoding='utf-8')
#generate the project ids
rawdata['projid'] = rawdata['rawmergebackid'].astype(str) + rawdata['location']

#FIRST: do some basic summary stats on number of projects geocoded

rawdata.rawmergebackid.nunique()
    #1134804 is the number of unique projects in the selected donor dataset pre-entity extraction

#--count the projects which have 1 geolocation
#select the projects where at least 1 location != country
temp = rawdata[(rawdata.coords!='POINT EMPTY') & (rawdata.iscountry!=1)]
#number of unique, geocoded projects
temp.rawmergebackid.nunique()
#216518
#number of unique, geocoded proj-locations
temp.projid.nunique()

#get those projects where the only location returned is the centroid 
temp2 = rawdata.groupby('rawmergebackid')['iscountry'].min()
#these are the number of 
temp2.value_counts()
#121,738 projects where the only returned location is the centroid

#---now descriptives statistics on the strings

#by donor, number of empty strings
temp = rawdata[rawdata.ProjectTitle.isna()]
empty_titles_by_donor = temp.groupby('DonorName').agg(empty_titles = ('rawmergebackid','nunique')).reset_index()

temp = rawdata[rawdata.ShortDescription.isna()]
empty_short_by_donor = temp.groupby('DonorName').agg(empty_short = ('rawmergebackid','nunique')).reset_index()

temp = rawdata[rawdata.LongDescription.isna()]
empty_long_by_donor = temp.groupby('DonorName').agg(empty_long= ('rawmergebackid','nunique')).reset_index()
#total projects --need this to make the share 
tot_projs = rawdata.groupby('DonorName').agg(total_projects= ('rawmergebackid','nunique')).reset_index()

#graph it 
graph_df = empty_titles_by_donor.merge(empty_short_by_donor,on='DonorName',how='inner',validate="1:1")

graph_df = graph_df.merge(empty_long_by_donor,on='DonorName',how='inner',validate="1:1")

graph_df = graph_df.merge(tot_projs,on='DonorName',how='inner',validate="1:1")

graph_df['Title_share_missing'] = graph_df['empty_titles']/graph_df['total_projects']
graph_df['Short_share_missing'] = graph_df['empty_short']/graph_df['total_projects']
graph_df['Long_share_missing'] = graph_df['empty_long']/graph_df['total_projects']

graph_df[['DonorName','Title_share_missing','Short_share_missing','Long_share_missing']].set_index('DonorName').plot(kind='bar',xlabel="")

#average string length by donor across non-missings
temp = rawdata[rawdata.ProjectTitle.notna()]
temp['title_len'] = [len(str(a)) for a in temp.ProjectTitle]
title_len = temp.groupby('DonorName').agg(title_len= ('title_len','mean')).reset_index()
temp = rawdata[rawdata.ShortDescription.notna()]
temp['short_len'] = [len(str(a)) for a in temp.ShortDescription]
short_len = temp.groupby('DonorName').agg(short_len= ('short_len','mean')).reset_index()
temp = rawdata[rawdata.LongDescription.notna()]
temp['long_len'] = [len(str(a)) for a in temp.LongDescription]
long_len = temp.groupby('DonorName').agg(long_len= ('long_len','mean')).reset_index()

graph_df = title_len.merge(short_len,on='DonorName',how='inner',validate="1:1")
graph_df = graph_df.merge(long_len,on='DonorName',how='inner',validate="1:1")

graph_df.set_index('DonorName').plot(kind='bar',xlabel="")


#now use the csv file with the sector codings to create new sector codings
codingdf = pd.read_csv('data/other_data/aidsectors.csv')
rawdata = rawdata.merge(codingdf,how='left',on='SectorName',validate='m:1')

#commitments - pregeocode
rawdata['temp'] = rawdata.fillna({'USD_Commitment':0}).groupby(['broadsec'],dropna=False)['USD_Commitment'].transform(lambda x: x.unique().sum())   
rawdata['com-pre-geocode'] = rawdata.groupby(['broadsec'])['temp'].transform('max') 
#commitments - postgeocode
rawdata['temp'] = rawdata.fillna({'USD_Commitment':0}).where(~rawdata['location'].isna()).groupby(['broadsec'],dropna=False)['USD_Commitment'].transform(lambda x: x.unique().sum())   
rawdata['com-post-geocode'] = rawdata.groupby(['broadsec'])['temp'].transform('max') 

plotdf = rawdata.groupby(['broadsec']).agg({'com-pre-geocode':'max','com-post-geocode':'max'}).reset_index()

plt.figure()
ax = plotdf.plot.bar(x='broadsec',rot=45,mark_right = False, color = ['blue', 'lightblue'])
ax.set_xlabel('Aid sector')
ax.set_ylabel("Amount (million USD)")
ax.set_xticklabels(['Multisector','Social Inf.','Econ. Inf.','Commodity/Emergency'])
ax.legend(['Com. pre-geocode','Com. post-geocode'])

#-----dont do number...
#number - pregeocode
rawdata['temp'] = rawdata.groupby(['newsecname'])['rawmergebackid'].transform('nunique')
rawdata['proj-pre-geocode'] = rawdata.groupby(['newsecname'])['temp'].transform('max') 
#number - postgeocode
rawdata['temp'] = rawdata.groupby(['newsecname'])['projid'].transform('nunique')   
rawdata['proj-post-geocode'] = rawdata.groupby(['newsecname'])['temp'].transform('max') 

plotdf = rawdata.groupby(['newsecname']).agg({'com-pre-geocode':'max','com-post-geocode':'max','proj-pre-geocode':'max','proj-post-geocode':'max'}).reset_index()

plt.figure()
ax = plotdf.plot.bar(x='newsecname',rot=45,secondary_y=['proj-pre-geocode', 'proj-post-geocode'],mark_right = False, color = ['blue', 'lightblue', 'red', 'salmon'])
ax.set_xlabel('Aid sector')
ax.set_ylabel("Amount (million USD)")
ax.right_ax.set_ylabel("Number")
ax.set_xticklabels(['Budget/general','Debt','Econ. Inf.', 'Emergency', 'Multisector','Miscellaneous', 'Production','Social Inf.', 'Unspecified'])
ax.legend(['Com. pre-geocode','Com. post-geocode'])
ax.right_ax.legend(['Numb. pre-geocode','Numb. post-geocode'],loc='upper right')

#---------------


#-------------------CHLOROPLETH multiple countries
#first plots will be aid, second plots will be leader birthplace
#plot macro regions in separate plots
import geopandas as gpd
import pandas as pd
import os
import matplotlib
import glob
from shapely.geometry import Polygon
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#merge in the regional identifiers
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3

projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')

#africa
africa = projdata.loc[projdata['africa']==1]
recipientlist = list(africa['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
africa = africa.groupby(['shapeID_adm1']).sum()
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = africa.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'left', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

africa_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#prep as a geodataframe
africa_with_geoms = gpd.GeoDataFrame(data=africa_with_geoms, geometry='geometry',crs='wgs84')
#plot
africa_with_geoms.plot(column = 'totalcom_adm1',cmap='BuPu',norm=matplotlib.colors.LogNorm()).set_axis_off()

#asia
asia = projdata.loc[projdata['asia']==1]
recipientlist = list(asia['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
asia = asia.groupby(['shapeID_adm1']).sum()
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = asia.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'left', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )  
    geom_dict[c]=merged 

asia_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#prep as a geodataframe
asia_with_geoms = gpd.GeoDataFrame(data=asia_with_geoms, geometry='geometry',crs='wgs84')
#plot full
asia_with_geoms.plot(column = 'totalcom_adm1',cmap='BuPu',norm=matplotlib.colors.LogNorm())
#need to drop that one country which is way out there
polgpd = gpd.GeoDataFrame([Polygon([(25,-25), (25, 70), (160, 70), (160, -25), (25, -25)])],columns=['polygongeom'],crs = 'wgs84',geometry='polygongeom')
clipped = asia_with_geoms.sjoin(polgpd,how='inner')
#plot
clipped.totalcom_adm1 = clipped.totalcom_adm1+0.01
clipped.plot(column = 'totalcom_adm1',cmap='BuPu',norm=matplotlib.colors.LogNorm()).set_axis_off()

#LA
LA = projdata.loc[projdata['LA']==1]
recipientlist = list(LA['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
LA = LA.groupby(['shapeID_adm1']).sum()
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = LA.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'left', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

LA_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#prep as a geodataframe
LA_with_geoms = gpd.GeoDataFrame(data=LA_with_geoms, geometry='geometry',crs='wgs84')
#plot
LA_with_geoms.plot(column = 'totalcom_adm1',cmap='BuPu',norm=matplotlib.colors.LogNorm()).set_axis_off()


#europe - gotta do it different, open geom files and merge 
#i will do this one later because i need to download all the geometry files even for non recipient countries
#for the sake of this map, consider Turkey europe
projdata.loc[projdata['countrycodeiso3']=='TUR','europe']=1
europe = projdata.loc[projdata['europe']==1]
#collapse the yearly data to just regional aggregates
europe = europe.groupby(['shapeID_adm1']).sum()
#need a list of European countries
recipientlist = ['CZE','POL','BGR','UKR','MLT','HRV','MDA','ROU','CYP','ALB','BLR','SRB','MNE','BIH','SVN','SVK','MKD','XKX','GEO','TUR','ARM','AZE', 'GRC','LVA','LTU','EST','RUS','AUT','HUN']
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)
    merged = europe.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'right', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

europe_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#prep as a geodataframe
europe_with_geoms = gpd.GeoDataFrame(data=europe_with_geoms, geometry='geometry',crs='wgs84')
#plot full
europe_with_geoms.plot(column = 'totalcom_adm1',missing_kwds={'color': 'lightgrey'},cmap='BuPu',norm=matplotlib.colors.LogNorm()).set_axis_off()

#need to drop that one country which is way out there
polgpd = gpd.GeoDataFrame([Polygon([(10, 30), (10, 60), (48, 60), (48, 30), (10, 30)])],columns=['polygongeom'],crs = 'wgs84',geometry='polygongeom')
clipped = europe_with_geoms.sjoin(polgpd,how='inner')
#plot
clipped.totalcom_adm1 = clipped.totalcom_adm1+0.01
clipped.plot(column = 'totalcom_adm1',missing_kwds={'color': 'lightgrey'},cmap='BuPu',norm=matplotlib.colors.LogNorm()).set_axis_off()


#-------------------CHLOROPLETH multiple countries LEADER BIRTHPLACE

import geopandas as gpd
import pandas as pd
import os
import numpy as np
import matplotlib
import glob
from shapely.geometry import Polygon
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#merge in the regional identifiers
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3

projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')

#africa
africa = projdata.loc[projdata['africa']==1]
recipientlist = list(africa['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
africa = africa.groupby('shapeID_adm1').agg({'inpower':'sum','Year':['min','max']}).reset_index()
africa.columns = africa.columns.droplevel(0)
africa.rename(columns={'':'shapeID_adm1'},inplace=True)
africa['timespan'] = africa['max'] - africa['min']
africa['shareofyears'] = africa['sum']/africa['timespan']
#small inputations to deal with lots of 0's
africa["shareofyears"] = africa["shareofyears"] + 0.1
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = africa.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'right', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

africa_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#prep as a geodataframe
africa_with_geoms = gpd.GeoDataFrame(data=africa_with_geoms, geometry='geometry',crs='wgs84')
#plot
africa_with_geoms.plot(column = 'shareofyears',cmap='OrRd',missing_kwds={'color': 'lightgrey'},norm=matplotlib.colors.LogNorm()).set_axis_off()

#asia
asia = projdata.loc[projdata['asia']==1]
recipientlist = list(asia['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
asia = asia.groupby('shapeID_adm1').agg({'inpower':'sum','Year':['min','max']}).reset_index()
asia.columns = asia.columns.droplevel(0)
asia.rename(columns={'':'shapeID_adm1'},inplace=True)
asia['timespan'] = asia['max'] - asia['min']
asia['shareofyears'] = asia['sum']/asia['timespan']
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = asia.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'right', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

asia_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#small inputations to deal with lots of 0's
asia_with_geoms.shareofyears.fillna(0.01,inplace=True)
#prep as a geodataframe
asia_with_geoms = gpd.GeoDataFrame(data=asia_with_geoms, geometry='geometry',crs='wgs84')
#plot full
asia_with_geoms.plot(column='shareofyears',cmap='OrRd',norm=matplotlib.colors.LogNorm()).set_axis_off()

#need to drop that one country which is way out there
polgpd = gpd.GeoDataFrame([Polygon([(25,-25), (25, 70), (160, 70), (160, -25), (25, -25)])],columns=['polygongeom'],crs = 'wgs84',geometry='polygongeom')
clipped = asia_with_geoms.sjoin(polgpd,how='inner')
#plot
clipped.shareofyears = clipped.shareofyears+0.01
clipped.plot(column = 'shareofyears',cmap='OrRd',norm=matplotlib.colors.LogNorm()).set_axis_off()

#LA
LA = projdata.loc[projdata['LA']==1]
recipientlist = list(LA['countrycodeiso3'].unique())
#collapse the yearly data to just regional aggregates
LA = LA.groupby('shapeID_adm1').agg({'inpower':'sum','Year':['min','max']}).reset_index()
LA.columns = LA.columns.droplevel(0)
LA.rename(columns={'':'shapeID_adm1'},inplace=True)
LA['timespan'] = LA['max'] - LA['min']
LA['shareofyears'] = LA['sum']/LA['timespan']
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = LA.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'right', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

LA_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#small inputations to deal with lots of 0's
LA_with_geoms.replace(np.inf,0,inplace=True)
LA_with_geoms.shareofyears.fillna(0.01,inplace=True)
#prep as a geodataframe
LA_with_geoms = gpd.GeoDataFrame(data=LA_with_geoms, geometry='geometry',crs='wgs84')
#plot
LA_with_geoms.plot(column='shareofyears',cmap='OrRd').set_axis_off()

#europe
projdata.loc[projdata['countrycodeiso3']=='TUR','europe']=1
europe = projdata.loc[projdata['europe']==1]
recipientlist = ['CZE','POL','BGR','UKR','MLT','HRV','MDA','ROU','CYP','ALB','BLR','SRB','MNE','BIH','SVN','SVK','MKD','XKX','GEO','TUR','ARM','AZE', 'GRC','LVA','LTU','EST','RUS','AUT','HUN']
#collapse the yearly data to just regional aggregates
europe = europe.groupby('shapeID_adm1').agg({'inpower':'sum','Year':['min','max']}).reset_index()
europe.columns = europe.columns.droplevel(0)
europe.rename(columns={'':'shapeID_adm1'},inplace=True)
europe['timespan'] = europe['max'] - europe['min']
europe['shareofyears'] = europe['sum']/europe['timespan']
#add the geometry files 
geom_dict ={}
for c in recipientlist:
    filename = 'data/geodata/geometry_files/adm1/' + c +'_ADM1.geojson'
    countrygeom = gpd.read_file(filename)   
    merged = europe.merge(countrygeom[['geometry','shapeID']],left_on ='shapeID_adm1', right_on = 'shapeID', how = 'right', validate = "1:1" )
    merged.dropna(subset=['geometry'],inplace=True )   
    geom_dict[c]=merged 

europe_with_geoms =pd.concat(geom_dict.values(),ignore_index=True)
#0's?
#europe_with_geoms.shareofyears.fillna(0.01,inplace=True)
#prep as a geodataframe
europe_with_geoms = gpd.GeoDataFrame(data=europe_with_geoms, geometry='geometry',crs='wgs84')
#plot full
europe_with_geoms.plot(column='shareofyears',cmap='OrRd',missing_kwds={'color': 'lightgrey'}).set_axis_off()

#need to drop that one country which is way out there
polgpd = gpd.GeoDataFrame([Polygon([(10, 30), (10, 60), (48, 60), (48, 30), (10, 30)])],columns=['polygongeom'],crs = 'wgs84',geometry='polygongeom')
clipped = europe_with_geoms.sjoin(polgpd,how='inner')
#plot
clipped.shareofyears = clipped.shareofyears+0.01
clipped.plot(column = 'shareofyears',missing_kwds={'color': 'lightgrey'},cmap='OrRd',norm=matplotlib.colors.LogNorm()).set_axis_off()


#--------switches in treatment (leader birthplace)
#have to do it by macro regions? probably yes

import pandas as pd
import numpy as np
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#merge in the regional identifiers
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3

projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')


#compute, by region, the amount of switches. Also compute the average share of years per macroregion that a leader stays in power. Then collapse to the macro region level

LA = projdata.loc[projdata['LA']==1]
africa = projdata.loc[(projdata['africa']==1) | (projdata['middleeast']==1)]
asia = projdata.loc[projdata['asia']==1]
europe = projdata.loc[projdata['europe']==1]

for df in [africa,asia,LA,europe]:
    reg = df.copy()
    #switches
    print((reg[['inpower']].diff(axis=0) != 0).sum(axis=0))
    #share of years
    reg['maxyear'] = reg.groupby(['shapeID_adm1'],dropna=False)['Year'].transform('max')
    reg['minyear'] = reg.groupby(['shapeID_adm1'],dropna=False)['Year'].transform('min')
    reg['totalinpower'] = reg.groupby(['shapeID_adm1'],dropna=False)['inpower'].transform('sum')
    reg['timespan'] = reg['maxyear'] - reg['minyear']
    reg['shareofyears'] = reg['totalinpower']/reg['timespan']
    #sometimes inf occurs because 0/0
    reg.shareofyears.replace(np.inf,0,inplace=True)
    #there are some dumb mistakes, like if a leader is in power 2003 and 2004, it is 2 years so 2004-2003 = 1 == 2/1 == 2
    reg['shareofyears'] = [1 if x > 1 else x for x in reg['shareofyears']]
    print(reg.shareofyears.describe())


#Sankey graph - color intensity - commitment averages
from floweaver import *
import pandas as pd 
import numpy as np

full_crs = pd.read_pickle('output/full_crs.pickle')
selecteddonorlist = ['Italy','France','Germany','Belgium','Spain','Sweden','Norway','Denmark','Luxembourg','Iceland','Ireland','Greece','Switzerland','United Kingdom','Finland','Austria','Portugal','Netherlands']

#keep selected 18 donors
selected_donors = full_crs[full_crs['DonorName'].isin(selecteddonorlist)]
#replace 0's in commitments with NaN
selected_donors['USD_Commitment'].replace(0, np.nan, inplace=True)
#drop panel dups - just works better when calculating commitment averages
#selected_donors = selected_donors.drop_duplicates(subset=['panelid'],keep=False)

#remove "regional and unspecified"
index_names = selected_donors[ (selected_donors['RegionName'] == "Regional and Unspecified")].index
# drop these given rows
selected_donors.drop(index_names, inplace = True)
selected_donors.RegionName.unique()
selected_donors.dropna(subset=['RegionName'], inplace = True)

#group macro regional projects
selected_donors.loc[selected_donors['RegionName'] == 'Africa', 'RegionName'] = 'Africa, regional'
selected_donors.loc[selected_donors['RegionName'] == 'Asia', 'RegionName'] = 'Asia, regional'
selected_donors.loc[selected_donors['RegionName'] == 'America', 'RegionName'] = 'America, regional'
#drop macro regional
index_names = selected_donors[ (selected_donors['RegionName'] == "Africa, regional") |(selected_donors['RegionName'] == "Asia, regional")| (selected_donors['RegionName'] == "America, regional")].index
# drop these given rows
selected_donors.drop(index_names, inplace = True)


#generate grouped data (stats)
flows = (
    selected_donors.groupby(["DonorName", "RegionName"])
    .agg({"USD_Commitment": "mean"})
    .dropna()
    .reset_index()
    .rename(
        columns={
            "DonorName": "source",
            "RegionName": "target",
            "USD_Commitment": "value",
        }
    )
)


#start here chart
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

weave(sdd, flows, link_color=QuantitativeScale('value')).to_widget().auto_save_svg("sankey_comms.svg")


#-----------------same as above one but number of projs
from floweaver import *
import pandas as pd 
import numpy as np

full_crs = pd.read_pickle('output/full_crs.pickle')
selecteddonorlist = ['Italy','France','Germany','Belgium','Spain','Sweden','Norway','Denmark','Luxembourg','Iceland','Ireland','Greece','Switzerland','United Kingdom','Finland','Austria','Portugal','Netherlands']

#keep selected 18 donors
selected_donors = full_crs[full_crs['DonorName'].isin(selecteddonorlist)]

#drop panel dups 
#selected_donors = selected_donors.drop_duplicates(subset=['panelid'],keep=False)

#remove "regional and unspecified"
index_names = selected_donors[ (selected_donors['RegionName'] == "Regional and Unspecified")].index
# drop these given rows
selected_donors.drop(index_names, inplace = True)
selected_donors.RegionName.unique()
selected_donors.dropna(subset=['RegionName'], inplace = True)

#group macro regional projects
selected_donors.loc[selected_donors['RegionName'] == 'Africa', 'RegionName'] = 'Africa, regional'
selected_donors.loc[selected_donors['RegionName'] == 'Asia', 'RegionName'] = 'Asia, regional'
selected_donors.loc[selected_donors['RegionName'] == 'America', 'RegionName'] = 'America, regional'
#drop macro regional
index_names = selected_donors[ (selected_donors['RegionName'] == "Africa, regional") |(selected_donors['RegionName'] == "Asia, regional")| (selected_donors['RegionName'] == "America, regional")].index
# drop these given rows
selected_donors.drop(index_names, inplace = True)

panelcols = ['DonorName','RecipientName','CrsID']

selected_donors['panelid'] = selected_donors.groupby(panelcols, dropna=True).ngroup()


#generate grouped data (stats)
flows = (
    selected_donors.groupby(["DonorName", "RegionName"])
    .agg({"panelid": "count"})
    .dropna()
    .reset_index()
    .rename(
        columns={
            "DonorName": "source",
            "RegionName": "target",
            "panelid": "value",
        }
    )
)


#start here chart
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

weave(sdd, flows, link_color=QuantitativeScale('value',palette='Blues_9')).to_widget().auto_save_svg("sankey_projs.svg")


#-------------------Summary statistics

import pandas as pd
import numpy as np 

#for basic summary stats at the ADM1  - year level, dont need the dyadic data
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#generate the control variables as in stata
sat_mean = [x if t <=2013 else y for (x,y,t) in zip(projdata['dmsp_mean'],projdata['viirs_to_dmsp_mean'],projdata['Year'])]
projdata['sat_mean'] = sat_mean

projdata['numbports'].fillna(0, inplace=True)

logpop = [np.log(x+0.01) if x==0 else np.log(x) for x in projdata['pop_sum']]
projdata['logpop']=logpop

logsat = [np.log(x+0.01) if x==0 else np.log(x) for x in projdata['sat_mean']]
projdata['logsat']=logsat

logmines = [np.log(x+0.01) if x==0 else np.log(x) for x in projdata['numbmines']]
projdata['logmines']=logmines

#correct commitments and projects, removing 0's
projdata['totalcom_adm1'].fillna(0, inplace=True)
logcom = [np.log(1) if x==0 else np.log(x) for x in projdata['totalcom_adm1']]
projdata['logcom']=logcom

projdata['totalprojs_adm1'].fillna(0, inplace=True)

projdata[['logcom','totalprojs_adm1','logsat','logpop','logmines','numbports','is_capital']].describe()


#doing summary stats for the different aid categories 
for a in ['socialinfprojs_adm1','econinfprojs_adm1','budgdebtemerprojs_adm1', 'otherprojs_adm1']:
    projdata[a].fillna(0, inplace=True)

for a in ['socialinfcom_adm1', 'econinfcom_adm1','budgdebtemercom_adm1', 'othercom_adm1']:
    projdata[a].fillna(0, inplace=True)
    loggedval = [np.log(1) if x==0 else np.log(x) for x in projdata[a]]
    projdata['log{}'.format(a)]=loggedval
    
projdata[['logsocialinfcom_adm1', 'logeconinfcom_adm1','logbudgdebtemercom_adm1', 'logothercom_adm1', 'socialinfprojs_adm1','econinfprojs_adm1','budgdebtemerprojs_adm1', 'otherprojs_adm1']].describe()

#summary stats on the different types of aid channels (implementing type)
for a in ['donorpublicent','recippublicent','ngo','intorg','unis','privsec']:
    projdata[a].fillna(0, inplace=True)
    loggedval = [np.log(1) if x==0 else np.log(x) for x in projdata[a]]
    projdata['log{}'.format(a)]=loggedval

#-------------------------more summary stats on non-collapsed data: project flow types
#need to update this with the geocoded data...? what did i mean by this its already done on the geocoded one
#need to open the raw data for this
import pandas as pd
import numpy as np 

#for basic summary stats at the ADM1  - year level, dont need the dyadic data
#use the raw data keeping only the geocoded projects: collapsing to adm1 i am not sure yet of how good it is
projdata = pd.read_csv('data/output/EU_projs_rawdata.csv',encoding='utf-8')

#do the usual dropping of unecessary things
projdata.dropna(subset=['CrsID'],inplace=True)
projdata.dropna(subset='shapeID_adm1',inplace=True)
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)

#now group by flow type 
projdata.groupby("FlowName")['USD_Commitment'].describe()


#descriptive stats on the biggest projects
import pandas as pd
import numpy as np 

projdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')

#keep only geocoded
#do the usual dropping of unecessary things
projdata.dropna(subset=['CrsID'],inplace=True)
projdata.dropna(subset='shapeID_adm1',inplace=True)
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)


temp = projdata.groupby('DonorName')['USD_Commitment'].nlargest(5).reset_index()
temp.set_index('level_1',inplace=True)

outputdf = projdata.loc[temp.index]


#------visualization for aid channel
    #ideas:
        #number of projects and amount per aid channel type for each year?
            #i think amount is sufficient, forget number of projects
            #forget yearly variation for now
        #also by macro region? 
        #also by donor?
        #the way to put all this together is a connection plot, for each country to each macro region, by channel type

import pandas as pd 
import numpy as np 

#slim down my dataset 
projdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')

#do the usual dropping of unecessary things
projdata.dropna(subset=['CrsID'],inplace=True)
projdata.dropna(subset='shapeID_adm1',inplace=True)
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)

#macroregions
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3
projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')

macroregion = ['Africa' if x==1 else 'Asia' if y ==1 else 'LA' if z ==1 else 'Middle East' if m==1 else 'Europe' if n==1 else np.nan for (x,y,z,m,n) in zip(projdata['africa'],projdata['asia'],projdata['LA'],projdata['middleeast'],projdata['europe'])]
projdata['macroregion'] = macroregion


#add the centroids for recipient regions
projdata['macroregionlat'] = [0.816623 if x ==1 else 10.487812 if y ==1 else 25.279115 if z ==1 else 44.50695 if v==1 else 31.25351 if m==1 else np.nan for (x,y,z,v,m) in zip(projdata['africa'],projdata['LA'],projdata['asia'],projdata['europe'],projdata['middleeast'])]

projdata['macroregionlong'] = [21.68328 if x ==1 else -73.752868 if y==1 else 92.882693 if z==1 else 26.808488 if v==1 else 46.573498 if m==1 else np.nan for (x,y,z,v,m) in zip(projdata['africa'],projdata['LA'],projdata['asia'],projdata['europe'],projdata['middleeast'])] 

#add the centroids for donor countries
projdata['europelat'] = 49.229558
projdata['europelong'] = 7.005221

#broad channel types
projdata['broadchannels'] = ['Donor public ent.' if 10000<=x<12000 else 'Recip. public ent.' if 12000<=x<20000 else 'NGO' if 20000<=x<30000 else 'Int. orgs.' if 40000<=x<50000 else 'Research inst.' if 50000<=x<60000 else 'Private sec.' if ((30000<=x<40000) | (60000<=x<90000)) else np.nan for x in projdata['ChannelCode']]

#now collapse the dataset as total by recipient macro region
df = projdata.groupby(['macroregion','broadchannels']).aggregate({'USD_Commitment': 'sum','europelat': 'max','europelong':'max','macroregionlat':'max','macroregionlong':'max'}).reset_index(inplace=True)

# on  a map? its not great, try with a sankey plot
from floweaver import *
#--------------mid point macroregions

#generate grouped data (stats)
flows = (
    projdata.groupby(['DonorName',"macroregion", "broadchannels"])
    .agg({"USD_Commitment": "sum"})
    .dropna()
    .reset_index().rename(columns={'DonorName':'source','macroregion':'region','broadchannels':'target','USD_Commitment':'value'})
    )
# create region partition
region = Partition.Simple('region', flows['region'].unique())

nodes = {
    'start': ProcessGroup(list(flows['source'].unique())), # one at the start 
    'middle': Waypoint(region),
    'end': ProcessGroup(list(flows['target'].unique())),}

# set the order of the nodes left to right
ordering = [['start'], ['middle'], ['end']]

# set the "bundle" of connections you want to show
bundles = [Bundle('start', 'end', waypoints=['middle'])]

# partition the groups for display
destination = Partition.Simple('target', flows['target'].unique())
nodes['start'].partition = Partition.Simple('source', flows['source'].unique())
nodes['end'].partition = destination

sdd = SankeyDefinition(nodes, bundles, ordering, flow_partition=region)

# display sankey (with color palette) and save as png
weave(sdd, flows).to_widget().auto_save_svg('macro_middle.svg')

#--------------mid point channels

#generate grouped data (stats)
flows = (
    projdata.groupby(['DonorName',"macroregion", "broadchannels"])
    .agg({"USD_Commitment": "sum"})
    .dropna()
    .reset_index().rename(columns={'DonorName':'source','macroregion':'target','broadchannels':'region','USD_Commitment':'value'})
    )
# create region partition
region = Partition.Simple('region', flows['region'].unique())

nodes = {
    'start': ProcessGroup(list(flows['source'].unique())), # one at the start 
    'middle': Waypoint(region),
    'end': ProcessGroup(list(flows['target'].unique())),}

# set the order of the nodes left to right
ordering = [['start'], ['middle'], ['end']]

# set the "bundle" of connections you want to show
bundles = [Bundle('start', 'end', waypoints=['middle'])]

# partition the groups for display
destination = Partition.Simple('target', flows['target'].unique())
nodes['start'].partition = Partition.Simple('source', flows['source'].unique())
nodes['end'].partition = destination

sdd = SankeyDefinition(nodes, bundles, ordering, flow_partition=region)

# display sankey (with color palette) and save as png
weave(sdd, flows).to_widget().auto_save_svg('channels_middle.svg')

#simple channels-recipregion summary stats table
projdata.groupby(["broadchannels", "macroregion"])['USD_Commitment'].sum().unstack()


#--------------sample of names for different channel categories (ngos, public entities, private..)
    #output to an excel list the different names by type 

import pandas as pd 
import numpy as np 

#slim down my dataset 
projdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')

#do the usual dropping of unecessary things
projdata.dropna(subset=['CrsID'],inplace=True)
projdata.dropna(subset='shapeID_adm1',inplace=True)
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)

#create broad channel
projdata['broadchannels'] = ['Donor public ent.' if 10000<=x<12000 else 'Recip. public ent.' if 12000<=x<20000 else 'NGO' if 20000<=x<30000 else 'Int. orgs.' if 40000<=x<50000 else 'Research inst.' if 50000<=x<60000 else 'Private sec.' if ((30000<=x<40000) | (60000<=x<90000)) else np.nan for x in projdata['ChannelCode']]

# Group by 'broadchannels' column and apply value_counts to 'ChannelName' column
grouped_data = projdata.groupby('broadchannels')['ChannelReportedName'].apply(lambda x: x.value_counts())

# Reset the index of each group
grouped_data = grouped_data.reset_index()

# Rename the columns
grouped_data.columns = ['broadchannels', 'ChannelReportedName', 'Count']

# Save the separate dataframe for each broadchannel
with pd.ExcelWriter("data/output/rawchannelnames.xlsx") as writer:
    for school in grouped_data['broadchannels'].unique():
        print(f"broadchannels: {school}")
        outputdf = grouped_data[grouped_data['broadchannels'] == school]
        #print(grouped_data[grouped_data['broadchannels'] == school])
        #print()
        outputdf.to_excel(writer, sheet_name=f"{school}", index=False)

#---------------------------------summary statistics on dyadic
# amount and number by donor and macro region

import pandas as pd
import numpy as np
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls_dyadic.csv',encoding='utf-8')

#merge in the regional identifiers
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3

projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')


#create a column that identifies macro regions
macroregion = ['Africa & M.E' if (x==1 or m==1) else 'Asia' if y ==1 else 'LA' if z ==1 else 'Europe' if v ==1 else 'Others' for (x,y,z,v,m) in zip(projdata['africa'],projdata['asia'],projdata['LA'],projdata['europe'],projdata['middleeast'])]
projdata['macroregion'] = macroregion

#should be some kind of crosstab table 
df_output = projdata[['totalcom_adm1','DonorName','macroregion']].groupby(['DonorName','macroregion']).mean()
df_output.to_csv('data/output/donor_macroregion_crosstab.csv')
#and the other one with project number? ill see later if i wanna do



#------------------------------------MORE SUBNATIONAL REGION DESCRIPTIVES
#first, decompose flows by type, channel, etc for each of the top recipient regions, for each country?
    #maybe could be like 7 graphs: Germany, France, Italy, Spain, Netherlands, UK, and Nordics
    #for each of these a graph that decomposes total flows over a relevant period (2000-2010, then 2011-2021)
        #and for each of those by channel and aid type o

#OR....do it from the recipient side. So select a few of the regions with the most projects and then do a tree chart

#OR....I could replicate the region specific map i made but distinguish the dots by donors, and do two maps side by side to show the evolution over the years
    #to do this i should pick just one region with the most number of projects 

#this is one of the regions with the most projects - i should do for a number of regions, not just one
    #and replicate over two periods (1990-2000, 2011-2020) -- to show how over the years the time has evolved
#IND-ADM1-51497691B65804234 -- adm2: IND-ADM2-76128533B49538664
#COD-ADM1-28894549B87528803 -- COD-ADM2-86626825B98452657
#PSE-ADM1-83478781B80832077 -- PSE-ADM2-87354302B60226836
#BIH-ADM1-56671855B27811889 --BIH-ADM2-47562260B66622354
#BOL-ADM1-26024454B92466198 -- BOL-ADM2-80513517B39687614

import geopandas as gpd
import pandas as pd
import folium

#data with georeferences
projdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')
#do the very basic cleaning 
projdata.dropna(subset=['CrsID'],inplace=True)
#now use the csv file with the sector codings to create new sector codings
codingdf = pd.read_csv('data/other_data/aidsectors.csv')
projdata = projdata.merge(codingdf,how='left',on='SectorName',validate='m:1')
#now make sure im not double counting the committment or proj numb summing
#to do this i'm going to first drop NaN regions - all those non geotagged
projdata.dropna(subset='shapeID_adm1',inplace=True)
#check shapeids assigned correctly
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)

#FOR GRAPHS, make color palettes - for geopandas plot

pointsPalette = {'Italy': 'chartreuse',
                 'France': 'cornflowerblue', 'Germany': 'tan', 'Belgium': 'rosybrown', 'Spain': 'coral', 'Sweden':'palegoldenrod', 'Norway':'lightpink','Denmark':'seashell','Luxembourg':'yellowgreen','Iceland':'lightslategray', 'Ireland':'mediumspringgreen','Greece':'paleturquoise','Switzerland':'violet','United Kingdom':'dimgray','Finland':'snow','Austria':'thistle','Portugal':'bisque','Netherlands':'orange'}

#dataframes for each of the selected regions
#-------------INDIA ADM1 
indiaaid = projdata.loc[projdata['shapeID_adm1'] == 'IND-ADM1-51497691B65804234']
indiaaid_pre = indiaaid.loc[indiaaid['Year'] <= 2000]
indiaaid_post = indiaaid.loc[indiaaid['Year'] >2000]
countrygeom = gpd.read_file('data/geodata/geometry_files/adm1/IND_ADM1.geojson')
#just the country geom
countrygeom = countrygeom.merge(indiaaid, left_on = 'shapeID', right_on = "shapeID_adm1",how = 'inner')

#--Pre plot (only one with legend)
geopdaid_pre = gpd.GeoDataFrame(data=indiaaid_pre,geometry = gpd.points_from_xy(indiaaid_pre.longitude,indiaaid_pre.latitude))
geopdaid_pre.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_pre.plot(ax=base, column='DonorName',markersize= 3,legend=True,cmap='tab20',legend_kwds={"loc": 'lower right'}).set_axis_off()

#---Post plot
geopdaid_post = gpd.GeoDataFrame(data=indiaaid_post,geometry = gpd.points_from_xy(indiaaid_post.longitude,indiaaid_post.latitude))
geopdaid_post.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_post.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()


#-------------INDIA ADM2 
indiaaid = projdata.loc[projdata['shapeID_adm2'] == 'IND-ADM2-76128533B49538664']
indiaaid_pre = indiaaid.loc[indiaaid['Year'] <= 2000]
indiaaid_post = indiaaid.loc[indiaaid['Year'] >2000]
countrygeom = gpd.read_file('data/geodata/geometry_files/adm2/IND_ADM2.geojson')
countrygeom = countrygeom.merge(indiaaid, left_on = 'shapeID', right_on = "shapeID_adm2",how = 'inner')

#--Pre plot
geopdaid_pre = gpd.GeoDataFrame(data=indiaaid_pre,geometry = gpd.points_from_xy(indiaaid_pre.longitude,indiaaid_pre.latitude))
geopdaid_pre.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_pre.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---Post plot
geopdaid_post = gpd.GeoDataFrame(data=indiaaid_post,geometry = gpd.points_from_xy(indiaaid_post.longitude,indiaaid_post.latitude))
geopdaid_post.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_post.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#FOLIUM - NICE
geopdaid_post = gpd.GeoDataFrame(data=indiaaid_post,geometry = gpd.points_from_xy(indiaaid_post.longitude,indiaaid_post.latitude))
geopdaid_post.reset_index(inplace=True)
geopdaid_post.crs = countrygeom.crs  
map = folium.Map(location=[19.15, 72.85], zoom_start=10, tiles="CartoDB positron")
#add layer 
sim_geo = gpd.GeoSeries(countrygeom["geometry"][0])
geo_j = sim_geo.to_json()
geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "#FFE5CC", "fillOpacity": 0.4,'color':'black','dashArray': '5, 5'})
geo_j.add_to(map) 

geo_df_list = [[point.xy[1][0], point.xy[0][0]] for point in geopdaid_post.geometry]

# Iterate through list and add a marker
i = 0
for coordinates in geo_df_list:
    # assign a color marker
    if geopdaid_post.DonorName[i] == "Italy":
        type_color = "green"
    elif geopdaid_post.DonorName[i] == "France":
        type_color = "blue"
    elif geopdaid_post.DonorName[i] == "Germany":
        type_color = "beige"
    elif geopdaid_post.DonorName[i] == "Belgium":
        type_color = "purple"
    elif geopdaid_post.DonorName[i] == "Spain":
        type_color = "pink"
    elif geopdaid_post.DonorName[i] == "Sweden":
        type_color = "black"
    elif geopdaid_post.DonorName[i] == "Norway":
        type_color = "gray"
    elif geopdaid_post.DonorName[i] == "Denmark":
        type_color = "darkpurple"
    elif geopdaid_post.DonorName[i] == "Luxembourg":
        type_color = "red"
    elif geopdaid_post.DonorName[i] == "Iceland":
        type_color = "darkblue"
    elif geopdaid_post.DonorName[i] == "Ireland":
        type_color = "darkgreen"
    elif geopdaid_post.DonorName[i] == "Greece":
        type_color = "cadetblue"
    elif geopdaid_post.DonorName[i] == "Switzerland":
        type_color = "lightred"
    elif geopdaid_post.DonorName[i] == "United Kingdom":
        type_color = "lightgray"
    elif geopdaid_post.DonorName[i] == "Finland":
        type_color = "lightblue"
    elif geopdaid_post.DonorName[i] == "Austria":
        type_color = "lightred"
    elif geopdaid_post.DonorName[i] == "Portugal":
        type_color = "lightgreen"
    else:
        type_color = "orange"

    # Place the markers with the popup labels and data
    map.add_child(
        folium.Marker(
            location=coordinates,
            popup="Donor: "
            + str(geopdaid_post.DonorName[i])
            + "<br>"
            + "Sector: "
            + str(geopdaid_post.broadsec[i])
            + "<br>"
            + "Amount: "
            +str(geopdaid_post.USD_Commitment[i]),
            icon=folium.Icon(color="%s" % type_color),
        )
    )
    i = i + 1
#view and export
map.save("mumbai_example.html")
map


#---------------PALESTINE
pseaid = projdata.loc[projdata['shapeID_adm1'] == 'PSE-ADM1-83478781B80832077']
pseaid_pre = pseaid.loc[pseaid['Year'] <= 2000]
pseaid_post = pseaid.loc[pseaid['Year'] >2000]
countrygeom = gpd.read_file('data/geodata/geometry_files/adm1/PSE_ADM1.geojson')
countrygeom = countrygeom.merge(pseaid, left_on = 'shapeID', right_on = "shapeID_adm1",how = 'inner')

#--Pre plot
geopdaid_pre = gpd.GeoDataFrame(data=pseaid_pre,geometry = gpd.points_from_xy(pseaid_pre.longitude,pseaid_pre.latitude))
geopdaid_pre.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_pre.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---Post plot
geopdaid_post = gpd.GeoDataFrame(data=pseaid_post,geometry = gpd.points_from_xy(pseaid_post.longitude,pseaid_post.latitude))
geopdaid_post.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_post.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()


#--------------CONGO DEM ADM1 - weak evidence
africaaid = projdata.loc[projdata['shapeID_adm1'] == 'COD-ADM1-28894549B87528803']
africaaid_pre = africaaid.loc[africaaid['Year'] <= 2000]
africaaid_post = africaaid.loc[africaaid['Year'] >2000]
countrygeom = gpd.read_file('data/geodata/geometry_files/adm1/COD_ADM1.geojson')
countrygeom = countrygeom.merge(africaaid, left_on = 'shapeID', right_on = "shapeID_adm1",how = 'inner')

#--Pre plot
geopdaid_pre = gpd.GeoDataFrame(data=africaaid_pre,geometry = gpd.points_from_xy(africaaid_pre.longitude,africaaid_pre.latitude))
geopdaid_pre.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_pre.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---Post plot
geopdaid_post = gpd.GeoDataFrame(data=africaaid_post,geometry = gpd.points_from_xy(africaaid_post.longitude,africaaid_post.latitude))
geopdaid_post.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_post.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---------LATIN AMERICA, BOLIVIA
laaid = projdata.loc[projdata['shapeID_adm1'] == 'BOL-ADM1-26024454B92466198']
laaid_pre = laaid.loc[laaid['Year'] <= 2000]
laaid_post = laaid.loc[laaid['Year'] >2000]
countrygeom = gpd.read_file('data/geodata/geometry_files/adm1/BOL_ADM1.geojson')
countrygeom = countrygeom.merge(laaid, left_on = 'shapeID', right_on = "shapeID_adm1",how = 'inner')

#--Pre plot
geopdaid_pre = gpd.GeoDataFrame(data=laaid_pre,geometry = gpd.points_from_xy(laaid_pre.longitude,laaid_pre.latitude))
geopdaid_pre.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_pre.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---Post plot
geopdaid_post = gpd.GeoDataFrame(data=laaid_post,geometry = gpd.points_from_xy(laaid_post.longitude,laaid_post.latitude))
geopdaid_post.crs = countrygeom.crs  
base = countrygeom.plot(color='white',edgecolor='black')
geopdaid_post.plot(ax=base, column='DonorName',markersize= 3,legend=False,cmap='tab20').set_axis_off()

#---other regions i havent done year, dont know if i will
europeaid = projdata.loc[projdata['shapeID_adm1'] == 'BIH-ADM1-56671855B27811889']
europeaid_pre = europeaid.loc[europeaid['Year'] <= 2000]
europeaid_post = europeaid.loc[europeaid['Year'] >2000]

#--------------country specific map plot - OLD
#read in both files: base map and specific recipient country aid data 
#trying different countries....will try first a subsaharan african country
import geopandas as gpd
import pandas as pd

projdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')
#do the very basic cleaning 
projdata.dropna(subset=['CrsID'],inplace=True)
#now use the csv file with the sector codings to create new sector codings
codingdf = pd.read_csv('data/other_data/aidsectors.csv')
projdata = projdata.merge(codingdf,how='left',on='SectorName',validate='m:1')
#now make sure im not double counting the committment or proj numb summing
#to do this i'm going to first drop NaN regions - all those non geotagged
projdata.dropna(subset='shapeID_adm1',inplace=True)
#check shapeids assigned correctly
isocheck = [a[0:3] for a in projdata['shapeID_adm1']]
projdata['isocheck'] = isocheck
projdata.drop(projdata[~(projdata['RecipientISO3']==projdata['isocheck'])].index,inplace=True)

#now pick a recipient country
recipientaid = projdata.loc[projdata['RecipientISO3'] == 'COD']
#reduce it even further, take a single year
recipientaid = recipientaid.loc[recipientaid['Year']==2019]
#country geometry
countrygeom = gpd.read_file('data/geodata/geometry_files/adm1/COD_ADM1.geojson')
#geo pd
geopdaid = gpd.GeoDataFrame(data=recipientaid,geometry = gpd.points_from_xy(recipientaid.longitude,recipientaid.latitude))
geopdaid.crs = countrygeom.crs  
#plot
base = countrygeom.plot(color='lightgreen',edgecolor='black')
geopdaid.plot(ax=base,marker = 'o', color='red',markersize= 3).set_axis_off()

#------------------------------Additional viz stuff, also for other projects

#-------------------by macro geographic regions, share of projects amount and number belonging to social vs econ vs others (stacked bar)
        #i started doing this but matplotlib is just so bad for side by side stacked bar charts, easier to do it in stata 

#first prepare the data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#merge in the regional identifiers
regions = pd.read_csv('data/other_data/macroregions.csv')
countrycodeiso3 = [x[0:3] for x in projdata['shapeID_adm1']]
projdata['countrycodeiso3'] = countrycodeiso3

projdata = projdata.merge(regions,how='left',on = 'countrycodeiso3',validate='m:1')


#create a column that identifies macro regions
macroregion = ['Africa & M.E' if (x==1 or m==1) else 'Asia' if y ==1 else 'LA' if z ==1 else 'Europe' for (x,y,z,m) in zip(projdata['africa'],projdata['asia'],projdata['LA'],projdata['middleeast'])]
projdata['macroregion'] = macroregion


plotdf = projdata.groupby(['macroregion']).agg({'socialinfcom_adm1':'sum','econinfcom_adm1':'sum','budgdebtemercom_adm1':'sum','socialinfprojs_adm1':'sum','econinfprojs_adm1':'sum','budgdebtemerprojs_adm1':'sum'}).reset_index()



#for the end-of-cycle seminar, doing an icicle plot

import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd

full_crs = pd.read_pickle('output/full_crs.pickle')

full_crs.RegionName.unique()
index_names = full_crs[ (full_crs['RegionName'] == "Regional and Unspecified") | (full_crs['RegionName'] =="Africa, regional") | (full_crs['RegionName'] =="Asia, regional") | (full_crs['RegionName'] =="America, regional")].index
# drop these given row
# indexes from dataFrame
full_crs.drop(index_names, inplace = True)
full_crs.RegionName.unique()
full_crs.dropna(subset=['RegionName'], inplace = True)
full_crs.RegionName.unique()
#ok now, keep only one country to simplify
keep = ['Italy']
full_crs = full_crs[full_crs['DonorName'].isin(keep)]
#group the sector names - i took this from the tania file in Aid
sec0 = ['11110',	'11120',	'11130',	'11182',	'11220',	'11230',	'11240',	'11320',	'11330',	'11420',	'11430',	'12110',	'12181',	'12182',	'12191',	'12220',	'12230',	'12240',	'12250',	'12261',	'12262',	'12263',	'12281',	'13010',	'13020',	'13030',	'13040',	'13081',	'14010',	'14015',	'14020',	'14021',	'14022',	'14030',	'14031',	'14032',	'14040',	'14050',	'14081',	'15110',	'15111',	'15112',	'15113',	'15114',	'15130',	'15150',	'15151',	'15152',	'15153',	'15160',	'15170',	'15210',	'15220',	'15230',	'15240',	'15250',	'15261',	'16010',	'16020',	'16030',	'16040',	'16050',	'16062',	'16063',	'16064',	'24010',	'24020',	'24030',	'24040',	'24081',	'25010',	'25020',	'41010',	'41020',	'41030',	'41040',	'41050',	'41081',	'41082',	'51010',	'53030',	'53040',	'60010',	'60020',	'60030',	'60040',	'60061',	'60062',	'72010',	'72040',	'72050',	'73010',	'74010']
sec1 = ['31110',	'31120',	'31130',	'31140',	'31150',	'31161',	'31162',	'31163',	'31164',	'31165',	'31166',	'31181',	'31182',	'31191',	'31192',	'31193',	'31194',	'31195',	'31210',	'31220',	'31261',	'31281',	'31282',	'31291',	'31310',	'31320',	'31381',	'31382',	'31391',	'32161',	'32162',	'32165',	'52010']
sec2 = ['23110',	'23181',	'23182',	'23183',	'23210',	'23220',	'23230',	'23240',	'23250',	'23260',	'23270',	'23310',	'23320',	'23330',	'23340',	'23410',	'23510',	'23630',	'23640',	'32164',	'32167',	'32169',	'32170',	'32210',	'32220',	'32261',	'32262',	'32264',	'32265',	'32266']
sec3 = ['32110',	'32120',	'32130',	'32140',	'32163',	'32168',	'32171',	'32182']
sec4 = ['33110',	'33120',	'33130',	'33140',	'33150',	'33181',	'33210']
sec5 = ['21010',	'21020',	'21030',	'21040',	'21050',	'21061',	'21081',	'22010',	'22020',	'22030',	'22040',	'32166',	'32172',	'32310']
sec6 = ['16061']
sec7 = ['43010',	'43030',	'43040',	'43050',	'43081',	'43082',	'99810',	'99820']

full_crs['PurposeCode'] = full_crs['PurposeCode'].astype("string")
full_crs.insert(1, "groupsector", "")

#makes some issues with the indexing but oh well
full_crs['groupsector'] = full_crs.apply(lambda i: "Non sector allocable" if i['PurposeCode'] in sec0 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Food" if i['PurposeCode'] in sec1 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Mineral" if i['PurposeCode'] in sec2 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Manufacturing" if i['PurposeCode'] in sec3 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Wholesale/retail" if i['PurposeCode'] in sec4 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Infrastructure/IT" if i['PurposeCode'] in sec5 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Other" if i['PurposeCode'] in sec6 else i['groupsector'],axis=1)
full_crs['groupsector'] = full_crs.apply(lambda i: "Other" if i['PurposeCode'] in sec7 else i['groupsector'],axis=1)

#create counts per groups 
icechart = full_crs.groupby(['RegionName', 'groupsector']).size().reset_index(name='counts')

fig = px.icicle(icechart, path=[px.Constant("Italy"), 'RegionName', 'groupsector'], values='counts')
fig.update_traces(root_color="lightgrey")
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.show()

#exclude non sector allocable 
index_names = ['Non sector allocable', 'Other']
# drop these given row
# indexes from dataFrame
reduceddata = full_crs[~full_crs.groupsector.isin(index_names)]

#create counts per groups 
icechart = reduceddata.groupby(['RegionName', 'groupsector']).size().reset_index(name='counts')

fig = px.icicle(icechart, path=[px.Constant("Italy"), 'RegionName', 'groupsector'], values='counts')
fig.update_traces(root_color="lightgrey")
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.show()

#reduce further 

index_names = ['Non sector allocable', 'Other']
reduceddata = full_crs[~full_crs.groupsector.isin(index_names)]
reduceddata['RegionName'] = reduceddata.apply(lambda i: "Other" if i['RegionName'] !="South of Sahara" else i['RegionName'],axis=1)

#create counts per groups 
icechart = reduceddata.groupby(['RegionName', 'groupsector']).size().reset_index(name='counts')

fig = px.icicle(icechart, path=[px.Constant("Italy"),'RegionName' ,'groupsector'], values='counts')
fig.update_traces(root_color="lightgrey")
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
fig.show()


#with repeated values -showing structure
import plotly.graph_objects as go

fig =go.Figure(go.Icicle(
 ids=["Donor",
    "Recipient1", "Recipient2", "Recipient3",'Agency1','Agency2', 'Sector1', 'Sector2','Purpose1','Purpose2' ],
  labels= ["Donor","Recipient1","Recipient2","Recipient3",'Agency1','Agency2','Sector1','Sector2','Purpose1','Purpose2'],
  parents=["",
    "Donor", "Donor", "Donor", "Recipient1",'Recipient1', "Agency1",'Agency1','Sector1','Sector1','Sector2','Purpose1','Purpose2', 'Agency2',"Recipient2",'Recipient3'],
    root_color="lightgrey"
))
fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

fig.show()

#share of unique projects by donor 
full_crs = pd.read_pickle('output/full_crs.pickle')
selecteddonorlist = ['Italy','France','Germany','Belgium','Spain','Sweden','Norway','Denmark','Luxembourg','Iceland','Ireland','Greece','Switzerland','United Kingdom','Finland','Austria','Portugal','Netherlands']

import plotly.express as px
#keep selected 18 donors
selected_donors = full_crs[full_crs['DonorName'].isin(selecteddonorlist)]
#drop panel dups
selected_donors = selected_donors.drop_duplicates(subset=['panelid'],keep=False)

#create counts per groups 
icechart = selected_donors.groupby(['DonorName']).size().reset_index(name='projcounts')
#------------------------
fig = px.pie(icechart, values='projcounts', names='DonorName')
fig.update_traces(textposition='inside', textinfo='percent+label')
fig.show()

#--------------------------------------------------------------------------------------------------------
#share of projects belonging to different sectors
#just open the collapsed one, should be easiest that way
import geopandas as gpd
import pandas as pd

#geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')
#raw data
rawdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')
#now use the csv file with the sector codings to create new sector codings
codingdf = pd.read_csv('data/other_data/aidsectors.csv')
rawdata = rawdata.merge(codingdf,how='left',on='SectorName',validate='m:1')

rawdata['totalcom'] = rawdata['USD_Commitment'].sum()
#Social inf com
rawdata['socialinfcom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==1).sum()
#Econ inf com
rawdata['econinfcom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==2).sum()
#Budget/general com- all
rawdata['budgdebtemercom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==3).sum()
#others 
rawdata['othercom'] = rawdata['totalcom'] - (rawdata['socialinfcom']  +rawdata['econinfcom']  +rawdata['budgdebtemercom'] )

#collapsing the geocoded
sumsdf = projdata.sum().to_frame().T.rename_axis('Total')
otherpost=sumsdf['totalcom_adm1'].iloc[0] - (sumsdf['socialinfcom_adm1'].iloc[0] + sumsdf['econinfcom_adm1'].iloc[0] + sumsdf['budgdebtemercom_adm1'].iloc[0])

#best way is just create a df
plotdf = {'Aid category': ['Social inf.', 'Economic inf.', 'Budget/debt/general','Other'],
        'Post': [sumsdf['socialinfcom_adm1'].iloc[0], sumsdf['econinfcom_adm1'].iloc[0], sumsdf['budgdebtemercom_adm1'].iloc[0], otherpost],
        'Pre': [ rawdata['socialinfcom'].iloc[0], rawdata['econinfcom'].iloc[0], rawdata['budgdebtemercom'].iloc[0], rawdata['othercom'].iloc[0]]}
plotdf = pd.DataFrame(plotdf)
#then create column that gives values in percentage 
percentagespre = [a/rawdata['totalcom'].iloc[0] for a in plotdf['Pre']]
percentagespost = [a/sumsdf['totalcom_adm1'].iloc[0] for a in plotdf['Post']]
plotdf['Pre_geocode'] = percentagespre
plotdf['Post_geocode'] = percentagespost 
plotdf[['Aid category','Pre_geocode','Post_geocode']].plot.bar(x='Aid category',rot=0)

#--------------------------Number and amount by aid type, before AND after geocoding
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

#open geocoded data
projdata = pd.read_csv('data/output/adm1projs_regional_controls.csv',encoding='utf-8')

#get the full summary stats from these values that are at the region-year level
sumsdf = projdata[['totalcom_adm1','socialinfcom_adm1','econinfcom_adm1','budgdebtemercom_adm1','othercom_adm1','totaldis_adm1', 'socialinfdis_adm1', 'econinfdis_adm1', 'budgdebtemerdis_adm1', 'otherdis_adm1','totalprojs_adm1', 'socialinfprojs_adm1', 'econinfprojs_adm1', 'budgdebtemerprojs_adm1', 'otherprojs_adm1',]].sum().to_frame().T.rename_axis('Total')

#do the same for raw data
#raw data
rawdata = pd.read_csv('data/output/projs_rawdata.csv',encoding='utf-8')
rawdata['projid'] = rawdata['rawmergebackid'].astype(str) + rawdata['location']
#now use the csv file with the sector codings to create new sector codings
codingdf = pd.read_csv('data/other_data/aidsectors.csv')
rawdata = rawdata.merge(codingdf,how='left',on='SectorName',validate='m:1')
rawdata['totalcom'] = rawdata['USD_Commitment'].sum()
#Social inf 
rawdata['socialinfcom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==1).sum()
rawdata['socialinfprojs'] = rawdata['projid'].where(rawdata['broadsec']==1).nunique()
#Econ inf 
rawdata['econinfcom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==2).sum()
rawdata['econinfprojs'] = rawdata['projid'].where(rawdata['broadsec']==2).nunique()
#Budget/general 
rawdata['budgdebtemercom'] = rawdata['USD_Commitment'].where(rawdata['broadsec']==3).sum()
rawdata['budgdebtemerprojs'] = rawdata['projid'].where(rawdata['broadsec']==3).nunique()

#best way is just create a df
plotdf = {'Aid category': ['Social inf.', 'Economic inf.', 'Budget/debt/general'],
        'Amount post-geocode': [sumsdf['socialinfcom_adm1'].iloc[0], sumsdf['econinfcom_adm1'].iloc[0], sumsdf['budgdebtemercom_adm1'].iloc[0]],
        'Number post-geocode': [ sumsdf['socialinfprojs_adm1'].iloc[0], sumsdf['econinfprojs_adm1'].iloc[0], sumsdf['budgdebtemerprojs_adm1'].iloc[0]],    'Amount pre-geocode': [ rawdata['socialinfcom'].iloc[0], rawdata['econinfcom'].iloc[0], rawdata['budgdebtemercom'].iloc[0]],    
        'Number pre-geocode': [ rawdata['socialinfprojs'].iloc[0], rawdata['econinfprojs'].iloc[0], rawdata['budgdebtemerprojs'].iloc[0]]}
plotdf = pd.DataFrame(plotdf)

#one axis
plotdf[['Aid category','Amount post-geocode','Amount pre-geocode', 'Number post-geocode', 'Number pre-geocode']].plot.bar(x='Aid category',rot=0)

#two axis all pre and post - but something is off
plt.figure()
ax = plotdf.plot.bar(x='Aid category',secondary_y=['Number post-geocode', 'Number pre-geocode'],mark_right = False, color = ['blue', 'lightblue', 'red', 'salmon'])
ax.set_ylabel("Amount (million USD)")
ax.right_ax.set_ylabel("Number")



#wbes visualizations
import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd

data = pd.read_csv('G:\My Drive\Public data\geocoded_wbes.csv',encoding='utf-8')

#to make a nice graph, just do one region, like SSA