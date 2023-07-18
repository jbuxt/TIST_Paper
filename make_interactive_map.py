## Maddie Henderson 
## Make an interactive map to export to html

import pandas as pd 
import folium as f
import matplotlib.pyplot as plt
import rasterio as rs
import geopandas as gp
import numpy as np

# Define the center of map
lat, lon = 37.61, 0.18
my_map = f.Map(location=[lat, lon], zoom_start=10)

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


tpath = 'relevant_tist_groves/Relevant_Tist_groves.shp'
cpath = 'relevant_counties/Relevant_Counties.shp'

tist_shp = gp.read_file(tpath) #
counties_shp = gp.read_file(cpath) #EPSG4326

my_map.add_child(f.LayerControl())
my_map.save('intro_map.html')

