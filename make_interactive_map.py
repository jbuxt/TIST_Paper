## Maddie Henderson 
## Make an interactive map to export to html
'''
### TODO
#https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points?? could be very fun 
'''


import pandas as pd 
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

Viridis = mpl.colormaps['viridis']

Greens = mpl.colormaps['Greens']


Purples = mpl.colormaps['Purples'] 
temp = Purples(np.linspace(0,1,256))
temp[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
missing_cm = ListedColormap(temp) 

YlOrRd = mpl.colormaps['YlOrRd'] 
temp = YlOrRd (np.linspace(0,1,256))
temp[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
missing_pct_cm = ListedColormap(temp) 

############################################################
# TIST groves and counties

with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

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
        style_function={"fillColor": "#00cc66", "fillOpacity": 0.3,"weight": 1, "color": "#00cc66"},
        popup=tist_popup).add_to(my_map)

# landcover = rs.open('landcover_WorldCoverv100_reprojected(1).tif')
# ecoregions = rs.open('ecoregions_rasterized.tif')

with rs.open('RESULTS/ndvi_missing_Meru.tif') as im:
   meru = im.read() #should have several layers 
  #  deal with nan???
   meru_meta = im.meta
  #get the bounding box 
   t_bounds = [[im.bounds[1], im.bounds[0]], [im.bounds[3],im.bounds[2]]]
   t_bands = im.descriptions



# let zeros be the nodata value that i will make clear 
# Import meru, tharaka, nyeri missing
# Add together
# Normalize
#Colorze
#Save as png 

#Do this for misisng months and longest missing streak 
# ANd then also an example NDVI 

# How to add colorbar?

### COULD PROBS SAVE TIME SAVING AS PNG
colors_meru0 = np.round(((meru[0,:,:] - 0) * (1/(meru[0,:,:].max() - 0) * 255)), 0).astype('uint8')
colors_meru1 = missing_cm(np.round(((meru[1,:,:] - 0) * (1/(meru[1,:,:].max() - 0) * 255)),0).astype('uint8'))

# mpl.image.imsave('meru_missing_for_map.png', missing_cm(scaled_meru0))

f.raster_layers.ImageOverlay('meru_missing_for_map.png', #LONGEST MISSING STREAK 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'Longest missing streak (months)',
                  ).add_to(my_map)


f.raster_layers.ImageOverlay(colors_meru0 ,
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]
                  name = '% Months missing from Landsat data',
                  ).add_to(my_map)
###############################################################
# FINISH AND SAVE

my_map.add_child(f.LayerControl())
my_map.save('intro_map.html')

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