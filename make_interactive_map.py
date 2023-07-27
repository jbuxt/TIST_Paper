## Maddie Henderson 
## Make an interactive map to export to html

import pandas as pd 
import folium as f
from folium.features import GeoJsonPopup, GeoJsonTooltip
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rs
import geopandas as gp
import numpy as np
import numpy.ma as ma
import pickle

# Define the center of map
lon, lat = 37.61, 0.18 
my_map = f.Map(location=[lat, lon], zoom_start=8)

###############################
#STYLE 

recov_cm = mpl.colormaps['viridis']
# Recov Rate (add missing missing and not calculated vals )
missing_cm = mpl.colormaps['Purples'].resampled(120) #up to 120 months missing 
ndvi_cm = mpl.colormaps['Greens']


 

# tpath = 'relevant_tist_groves/Relevant_Tist_groves.shp'
# cpath = 'relevant_counties/Relevant_Counties.shp'

# tist_gp = gp.read_file(tpath) #
# counties_gp = gp.read_file(cpath) #EPSG4326

with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

with open('veg_meta.pkl', 'rb') as file:
   veg_meta, veg_bounds=pickle.load(file)


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

#add counties first so it's on the bottom 
f.GeoJson(counties_gp, name='Counties of Interest',
          style_function=lambda x: {
            "fillColor": colormap[x["properties"]["COUNTY"]],
            "color": colormap[x["properties"]["COUNTY"]],
            "fillOpacity": 0.4},
          popup=count_popup).add_to(my_map)

f.GeoJson(tist_gp, name='TIST Groves',
        # style_function={"fillColor": "#00cc66", "fillOpacity": 0.3,"weight": 1, "color": "#00cc66"},
        popup=tist_popup).add_to(my_map)

# landcover = rs.open('landcover_WorldCoverv100_reprojected(1).tif')
# ecoregions = rs.open('ecoregions_rasterized.tif')

with rs.open('RESULTS/ndvi_missing_Meru.tif') as im:
   meru = im.read() #should have several layers 
  #  deal with nan???
   meru_meta = im.meta
   t_bounds = [[im.bounds[0], im.bounds[1]], [im.bounds[2], im.bounds[3]]]
   t_bands = im.descriptions
# Might need to mask wth np
#data = ma.masked_invalid(meru[:,:,0])
#colored_data = missing_cm(data)
# also might need to normalize data? unclear
#think it has to be 0-255 
# let zeros be the nodata value that i will make clear 

scaled_meru0 = np.round(((meru[0,:,:] - 0) * (1/(meru[0,:,:].max() - 0) * 255)), 0).astype('uint8')
scaled_meru1 = np.round(((meru[1,:,:] - 0) * (1/(meru[1,:,:].max() - 0) * 255)),0).astype('uint8')

f.raster_layers.ImageOverlay(scaled_meru1,
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  colormap = mpl.colormaps['Purples'], #can't call colormap on the array here, also doesn't like colored data in the first part 
                  name = 'Longest missing streak',
                  ).add_to(my_map)
f.raster_layers.ImageOverlay(scaled_meru0,
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  colormap = mpl.colormaps['Greens'], #can't call colormap on the array here, also doesn't like colored data in the first part 
                  name = '% Months missing',
                  ).add_to(my_map)

''' Function of the form [x -> (r,g,b)] or [x -> (r,g,b,a)] for transforming a mono image into RGB. 
It must output iterables of length 3 or 4, with values between 0 and 1. 
Hint: you can use colormaps from matplotlib.cm.'''


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

my_map.add_child(f.LayerControl())
my_map.save('intro_map.html')

print('donezo')
'''
##############################
# VIS PARAMS
##############################
precipitationVis = {
  'min': 1.0,
  'max': 17.0,
  'palette': ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000'],
}

ndviVis = {
  'min': -1, 
  'max': 1, 
  'palette': ['blue', 'white', 'green'] # sets the color ramp for displaying it 
}

rgbVis = {
 'bands': ['SR_B4', 'SR_B3', 'SR_B2'], # these are the RGB layers for landsat
  'min': 0.0,
  'max': 0.3
}
'''
### FUTURE 
#https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points?? could be very fun 


## discrete colormap?
## An alternative could be to specify colors accompanied with the respective values.

# colors = [(0, "white"), (1./3.5, "green"), (1.5/3.5, "green"),
#           (1.501/3.5, "red"), (2.5/3.5, "red"), (2.501/3.5, "gray"), (1, "gray") ]
# mycmap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)
