## Maddie Henderson 
## Make an interactive map to export to html

import pandas as pd 
import folium as f
from folium.features import GeoJsonPopup, GeoJsonTooltip
import matplotlib.pyplot as plt
import rasterio as rs
import geopandas as gp
import numpy as np
import pickle

# Define the center of map
lon, lat = 37.61, 0.18 
my_map = f.Map(location=[lat, lon], zoom_start=8)


# how to change colors
# add some rasters of ndvi, landcover, ecoregion 
# what is displayed with clicking? 




# tpath = 'relevant_tist_groves/Relevant_Tist_groves.shp'
# cpath = 'relevant_counties/Relevant_Counties.shp'

# tist_gp = gp.read_file(tpath) #
# counties_gp = gp.read_file(cpath) #EPSG4326
with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

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
# tist_gjson = tist_gp.to_json()
# counties_gjson = counties_gp.to_json()

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
# counties = f.features.GeoJson(counties_gjson, name='Counties of Interest',
#                               style=counties_gjson['style'],
#                               popup=count_popup).add_to(my_map)

f.GeoJson(tist_gp, name='TIST Groves',
        # style_function={"fillColor": "#00cc66", "fillOpacity": 0.3,"weight": 1, "color": "#00cc66"},
        popup=tist_popup).add_to(my_map)


# my_map.add_child(counties)
# my_map.add_child(tist_farms)
# for farm in 

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
