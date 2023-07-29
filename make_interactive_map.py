## Maddie Henderson - July 2023
## Make an interactive map to export to html
'''
### TODO
# https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points?? could be very fun 
# add colorbar
# popup color https://stackoverflow.com/questions/62789558/is-it-possible-to-change-the-popup-background-colour-in-folium

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

# with rs.open('RESULTS/ndvi_missing_Meru.tif') as im:
#   meru = im.read() #should have several layers 

# with rs.open('RESULTS/ndvi_missing_Tharaka.tif') as im:
#   thar = im.read() #should have several layers 
# with rs.open('RESULTS/ndvi_missing_Nyeri.tif') as im:
#   nyeri = im.read() #should have several layers 

# # let zeros be the nodata value that i will make clear 
# missing_streak = meru[1,:,:] +  thar[1,:,:] +  nyeri[1,:,:] #add the others when they are done
# missing_months = meru[0,:,:] +  thar[0,:,:] +  nyeri[0,:,:]

# #normalize and colorize
# missing_months_colors = missing_pct_cm( np.round(((missing_months - 0) * (1/1 - 0) * 255), 0).astype('int8')) #I know the max missing months % is 1
# missing_streak_colors = missing_cm( np.round(((missing_streak - 0) * (1/(50 - 0) * 255)), 0).astype('int8')) # I know the max missing streak is like 50

# ## ISSUE: The things that are zero within the image are also getting masked aside from the zeros outside the image

# #Save as png 
# mpl.image.imsave('missing_mo_for_map.png', missing_months_colors)
# mpl.image.imsave('missing_streak_for_map.png', missing_streak_colors)

# ANd then also an example NDVI 

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
        style_function= lambda x: {"fillColor": "#00cc66", "fillOpacity": 0.3,"weight": 1, "color": "#00cc66"},
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
###############################################################
# FINISH AND SAVE
#colormaps
cm1 = f.LinearColormap(colors = [tuple(row) for row in temp2], 
                       index = np.linspace(0, 1, num=255),
                       vmin = 0, 
                       vmax = 1) #probably need to edit this to correspond max/min of usecase
cm2 = f.LinearColormap(colors = [tuple(row) for row in temp1],
                       index = np.linspace(0, 50, num=255),
                       vmin = 0, 
                       vmax = 50)
cm1.caption = 'Percent of months missing from Landsat data'
cm2.caption = 'Number of missing months in longest missing streak'

cmap_HTML = cm1._repr_html_()
cmap2_HTML = cm2._repr_html_()
cmap_HTML = cmap_HTML.replace('<svg height="50" width="500">','<svg id="cmap" height="50" width="500">',1)
cmap2_HTML = cmap2_HTML.replace('<svg height="50" width="500">','<svg id="cmap" height="50" width="500">',1)
cmap_style = '<style>#cmap {background-color: green;}</style>'
cmap2_style = '<style>#cmap {background-color: green;}</style>'

my_map.get_root().header.add_child(f.Element(cmap_style))
my_map.get_root().header.add_child(f.Element(cmap2_style))
f.map.LayerControl().add_to(my_map)
my_map.get_root().html.add_child(f.Element(cmap_HTML))
my_map.get_root().html.add_child(f.Element(cmap2_HTML))
# my_map.add_child(cm1)
# my_map.add_child(cm2)

# my_map.add_child(f.LayerControl())
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