## Maddie Henderson - July 2023
## Make an interactive map to export to html
'''
### TODO
# https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points?? could be very fun 
# add colorbar that's not ugly
# popup color https://stackoverflow.com/questions/62789558/is-it-possible-to-change-the-popup-background-colour-in-folium

'''
# import pandas as pd 
import folium as f
from folium.features import GeoJsonPopup, GeoJsonTooltip
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rs
import geopandas as gp
import numpy as np
from matplotlib.colors import ListedColormap
import pickle

###################################
# Define the center of map
lon, lat = 37.61, 0.18 
my_map = f.Map(location=[lat, lon], zoom_start=8)

#for all the bounding boxes of images in the ROI
t_bounds = [[-0.9639821313886587, 36.11092694867859], [0.8877151637669112, 38.47870637456082]]

###############################
#STYLE 

# Viridis = mpl.colormaps['viridis']

Greens = mpl.colormaps['Greens']
temp3 = Greens(np.linspace(0,1, 256))
temp3[:, 3] = 0.7 #set everything kinda transparent
temp3[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
Greens  = ListedColormap(temp3)

Purples = mpl.colormaps['Purples'] 
temp1 = Purples(np.linspace(0,1,256))
temp1[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
missing_cm = ListedColormap(temp1)


YlOrRd = mpl.colormaps['YlOrRd'] 
temp2 = YlOrRd(np.linspace(0,1,256))
temp2[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
missing_pct_cm = ListedColormap(temp2) 

##########################################################
##Make the pngs that get loaded later (only need to do once)
##landcover = rs.open('landcover_WorldCoverv100_reprojected(1).tif')
##ecoregions = rs.open('ecoregions_rasterized.tif')

# with open('county_mask.pkl', 'rb') as file:
#    county_mask= pickle.load(file)
# new = county_mask != 0 
# county_mask = new * 1


# with rs.open('RESULTS/Missing/ndvi_missing_Meru.tif') as im:
#   meru = im.read() #outside of county is zero
# with rs.open('RESULTS/Missing/ndvi_missing_Tharaka.tif') as im:
#   thar = im.read() #outside of county is zero
# with rs.open('RESULTS/Missing/ndvi_missing_Nyeri.tif') as im:
#   nyeri = im.read() #outside of county is zero
# with rs.open('RESULTS/Missing/ndvi_missing_Laikipia.tif') as im:
#   lai = im.read() #outside of county is nan
#   np.nan_to_num(lai, copy=False, nan=0.0)
# with rs.open('RESULTS/Missing/ndvi_missing_Embu.tif') as im:
#   embu = im.read() #outside of county is nan
#   np.nan_to_num(embu, copy=False, nan=0.0)

# # # let zeros be the nodata value that i will make clear 
# # could set all nodata to -1 for these which would get mapped as clear if i moved the range up by one 
# missing_streak = meru[1,:,:] +  thar[1,:,:] +  nyeri[1,:,:] + embu[1,:,:] + lai[1,:,:] 
# missing_months = meru[0,:,:] +  thar[0,:,:] +  nyeri[0,:,:] + embu[0,:,:] + lai[0,:,:]
# #should probably also save this in one image / csv for spotfire analysis 

# #change nan to 0 for the picture 
# # np.nan_to_num(missing_streak, copy=False, nan=0.0)
# # np.nan_to_num(missing_months, copy=False, nan=0.0)

# # # #normalize and colorize
# missing_months_colors = missing_pct_cm( np.round(((missing_months - 0) * (1/(1 - 0) * 255)), 0).astype('int16')) #I know the max missing months % is 1
# missing_streak_colors = missing_cm( np.round(((missing_streak - 0) * (1/(36 - 0) * 255)), 0).astype('int16')) # I know the max missing streak is like 50
# # # #Save as png 
# mpl.image.imsave('missing_mo_for_map.png', missing_months_colors)
# mpl.image.imsave('missing_streak_for_map.png', missing_streak_colors)

### NDVI example############################
# with rs.open('ndvi_pic.tif') as im:
#   ndvi = im.read(1) #should have several layers 
# ndvi = np.nan_to_num(ndvi, copy=True, nan=-1, posinf=None, neginf=None)

# ndvi =ndvi[1:-1, 1:] * county_mask
# ndvi[ndvi ==0] = -1 #set the ones we just masked to -1
# ndvi_colors = Greens( np.round(((ndvi +1) * 0.5 * 255), 0).astype('int16')) # range -1 to 1

# mpl.image.imsave('ndvi_ex.png', ndvi_colors)
## ISSUE: The things that are zero within the image are also getting masked aside from the zeros outside the image

############################################################
# TIST groves and counties

with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

# select = np.round(np.random.rand(5000) * 30000, 0).astype('int16')# get 5000 random tist groves
 #reduced for putting on web
# tist_gp = tist_gp.loc[select, ['Trees', 'Name', 'geometry']]
counties_gp = counties_gp.loc[:, ['geometry', 'COUNTY']]

tist_popup = GeoJsonPopup(
    fields=['Trees', "Name"],
    aliases=['Number of Trees', "Grove Name"],
    localize=True,
    labels=True,
)
count_popup = GeoJsonPopup(
    fields=['COUNTY'],
    aliases=['County'],
    localize=True,
    labels=True,
)

colormap = {'Meru': '#ffcccc', 
     'Embu':"#ffe5cc", 
    "Nyeri": "#ffffcc",
    "Kirinyaga": "#ccffcc", 
    "Tharaka": "#ccffff", 
    "Laikipia": "#e5ccff"}

#add counties first so it's on the bottom (actually think this might put them on top? unclear)
f.GeoJson(counties_gp, name='Counties of Interest',
          style_function=lambda x: {
            "fillColor": colormap[x["properties"]["COUNTY"]],
            "color": colormap[x["properties"]["COUNTY"]],
            "weight": 2,
            "fillOpacity": 0.3},
          popup=count_popup).add_to(my_map)

f.GeoJson(tist_gp, name='TIST Groves',
        style_function= lambda x: {"fillColor": "#00cc66", "fillOpacity": 0.3,"weight": 1, "color": "#000000"},
        popup=tist_popup).add_to(my_map)


##################################################################################3
# RASTER LAYERS

f.raster_layers.ImageOverlay('missing_streak_for_map.png', #LONGEST MISSING STREAK 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'Longest missing streak (months) in Landsat data',
                  ).add_to(my_map)


f.raster_layers.ImageOverlay('missing_mo_for_map.png',
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]
                  name = '% Months missing from Landsat data',
                  ).add_to(my_map)


# f.raster_layers.ImageOverlay('ndvi_ex.png',
#                   bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]
#                   name = 'NDVI from Landsat 8',
#                   ).add_to(my_map)
###############################################################
# FINISH AND SAVE
#colormaps since folium doesn't seem to play well with matplotlib
cm1 = f.LinearColormap(colors = [tuple(row) for row in temp2], 
                       index = np.linspace(0, 1, num=255),
                       vmin = 0, 
                       vmax = 1, 
                       caption='Percent of months missing from Landsat-8 data (2013-23)') #probably need to edit this to correspond max/min of usecase
cm2 = f.LinearColormap(colors = [tuple(row) for row in temp1],
                       index = np.linspace(0, 36, num=255),
                       vmin = 0, 
                       vmax = 36, 
                       caption='Number of missing months in longest missing streak')
# cm3 = f.LinearColormap(colors = [tuple(row) for row in temp3],
#                        index = np.linspace(-1, 1, num=255),
#                        vmin = -1, 
#                        vmax = 1, #IDIOT 
#                        caption='NDVI (Vegetation Greeness)')

#add a background to the colorbar - hacky and stolen from
#https://stackoverflow.com/questions/44887461/how-to-add-a-background-color-of-a-colormap-in-a-folium-map
cmap_HTML = cm1._repr_html_()
cmap_HTML = cmap_HTML.replace('<svg height="50" width="400">','<svg id="cmap" height="50" width="400">',1)
cmap_style = '<style>#cmap {background-color: green;}</style>'

cmap2_HTML = cm2._repr_html_()
cmap2_HTML = cmap2_HTML.replace('<svg height="50" width="400">','<svg id="cmap" height="50" width="400">',1)
cmap2_style = '<style>#cmap {background-color: green;}</style>'

# cmap3_HTML = cm3._repr_html_()
# cmap3_HTML = cmap3_HTML.replace('<svg height="50" width="400">','<svg id="cmap" height="50" width="400">',1)
# cmap3_style = '<style>#cmap {background-color: green;}</style>'



my_map.get_root().header.add_child(f.Element(cmap_style))
my_map.get_root().header.add_child(f.Element(cmap2_style))
# my_map.get_root().header.add_child(f.Element(cmap3_style))

f.map.LayerControl().add_to(my_map)

my_map.get_root().html.add_child(f.Element(cmap_HTML))
my_map.get_root().html.add_child(f.Element(cmap2_HTML))
# my_map.get_root().html.add_child(f.Element(cmap3_HTML))


# my_map.add_child(f.LayerControl())
my_map.save('TEST_map.html')

print('donezo')


#https://leafletjs.com/reference.html#path
#all the style things 

# counties_gp['style'] = [
#     {"fillColor": "#ffcccc", "fillOpacity": 0.3, "weight": 2, "color": "black"},
#     {"fillColor": "#ffe5cc", "fillOpacity": 0.3,"weight": 2, "color": "black"},
#     {"fillColor": "#ffffcc", "fillOpacity": 0.3,"weight": 2, "color": "black"},
#     {"fillColor": "#ccffcc", "fillOpacity": 0.3,"weight": 2, "color": "black"},
#     {"fillColor": "#ccffff", "fillOpacity": 0.3,"weight": 2, "color": "black"},
#     {"fillColor": "#e5ccff", "fillOpacity": 0.3,"weight": 2, "color": "black"}
# ]

'''
tooltip = GeoJsonTooltip(
    fields=["name", "medianincome", "change"],
    aliases=["State:", "2015 Median Income(USD):", "Median % Change:"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)

'''
# colormaps
#https://github.com/python-visualization/folium/blob/main/examples/Colormaps.ipynb