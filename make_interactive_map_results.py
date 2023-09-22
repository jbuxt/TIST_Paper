## Maddie Henderson - Aug 2023
## Make an interactive map to export to html
'''
### TODO
# https://stackoverflow.com/questions/58227034/png-image-not-being-displayed-on-folium-map
# Display a graph of the recovery rate at selected points?? could be very fun 
# add colorbar that's not ugly
# popup color https://stackoverflow.com/questions/62789558/is-it-possible-to-change-the-popup-background-colour-in-folium


for final results page want 
- can use existing images for some parts of page - examples, all results 
- for map for use -  could limit to meru and tharaka for speed/size
--- for colormap, do separate layers for valid calc, invalid calc 
- have 59, 77 as toggle layers, background google satellite, sample of TIST groves, and several
  points with example plots that can be pulled up 
'''
# import pandas as pd 
import folium as f
from folium.features import GeoJsonPopup, GeoJsonTooltip
import matplotlib.pyplot as plt
import matplotlib as mpl
import rasterio as rs
import geopandas as gp
import numpy as np
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import pickle

###############################
#STYLE 

Green = mpl.colormaps['Greens']
temp = Green(np.linspace(-1, 5, 256))
temp[0, :] = np.array([1,1,1,0]) #Set anything mapped to the min as transparent
green_cm  = ListedColormap(temp)

other_cm = LinearSegmentedColormap.from_list( 'other_cm', [(0/15,    '#ffff0000'), #first one is transparent
                                              (10/15, '#ffff66'),
                                              (15/15,    '#0000ff')])
# YlOrRd = mpl.colormaps['YlOrRd'] 
# temp2 = YlOrRd(np.linspace(0,1,256))
# temp2[0, :] = np.array([1,1,1,0]) #Set anything mapped to 0 as transparent
# missing_pct_cm = ListedColormap(temp2) 

# #for the problematic ones 
# cmap = plt.get_cmap('PuOr', 2)
# cmap.set_under('#FFFFFF00')


######################## # ##################################
##Make the pngs that get loaded later (only need to do once)

# with rs.open('77_Tharaka.tif') as im:
#   thar77 = im.read() #outside of county is nan
#   meru_bands = im.descriptions

# with rs.open('59_Tharaka.tif') as im:
#   thar59 = im.read() 
#   thar_bands =im.descriptions

# #Goals 
# # 2 images for each recovery - one of the legit vals , one of the 10s and 15s 

# recov77 = thar77[0,:,:] 
# np.nan_to_num(recov77, copy=False, nan=1) #rates are negative 
# others77 = recov77.copy() #for 10s and 15s
# others77[others77 < 10] =  0 #get rid of all others
# recov77[recov77 >= 10] =  1
# recov77 = recov77 * -1 #make rates positive and NAN/10/15 is negative -1
# recov77[recov77 >= 5] =  5 #make everything more than 5 just 5 for the picture

# recov59 = thar59[0,:,:] 
# np.nan_to_num(recov59, copy=False, nan=1) #rates are negative 
# others59 = recov59.copy() #for 10s and 15s
# others59[others59 < 10] =  0 #get rid of all others
# recov59[recov59 >= 10] =  1
# recov59 = recov59 * -1 #make rates positive and NAN/10/15 is negative -1
# recov59[recov59 >= 5] =  5 #make everything more than 5 just 5 for the picture

# # # #normalize and colorize
# recov77_colors = green_cm( np.round(((recov77 - -1) * (1/(5 - -1) * 255)), 0).astype('int16')) #min -1 max 5 
# recov59_colors = green_cm( np.round(((recov59 - -1) * (1/(5 - -1) * 255)), 0).astype('int16')) #min -1 max 5 

# other77_colors = other_cm(others77/15)
# other59_colors = other_cm(others59/15)
# # # #Save as png 
# mpl.image.imsave('77_thar.png', recov77_colors)
# mpl.image.imsave('59_thar.png', recov59_colors)
# mpl.image.imsave('77_other.png', other77_colors)
# mpl.image.imsave('59_other.png', other59_colors)

###################################################################3
# Define the center of map
lon, lat = 37.79, -0.24  #EDIT THIS TO BE ON THARAKA # 37.61, 0.18 for overall map

my_map = f.Map(location=[lat, lon], zoom_start=9)

tile = f.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       ).add_to(my_map)

#for all the bounding boxes of images in the ROI
t_bounds = [[-0.9639821313886587, 36.11092694867859], [0.8877151637669112, 38.47870637456082]]

############################################################
# TIST groves and counties

with open('tist_and_counties_gp.pkl', 'rb') as file:
   tist_gp, counties_gp= pickle.load(file)

# select = np.round(np.random.rand(5000) * 30000, 0).astype('int16')# get 5000 random tist groves
#reduced for putting on web
tist_gp = tist_gp.loc[tist_gp['COUNTY'] == 'Tharaka', ['Trees', 'Name', 'geometry']] #get only those in Tharaka 


f.GeoJson(tist_gp, name='TIST Groves',
        style_function= lambda x: {"fillColor": "#00cc66", "fillOpacity": 0.3,
                                   "weight": 1, "color": "#000000"}).add_to(my_map)


##################################################################################3
# RASTER LAYERS



f.raster_layers.ImageOverlay('59_thar.png', 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'Recovery rate for Recovery 59',
                  overlay = True,
                  control = True
                  ).add_to(my_map)


f.raster_layers.ImageOverlay('77_thar.png',
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]
                  name = 'Recovery rate for Recovery 77',
                  overlay = True,
                  control = True
                  ).add_to(my_map)

f.raster_layers.ImageOverlay('59_other.png', 
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]]
                  name = 'No disturbance / no calculation for Recovery 59',
                  overlay = True,
                  control = True                  
                  ).add_to(my_map)


f.raster_layers.ImageOverlay('77_other.png',
                  bounds=t_bounds, #[[lat_min, lon_min], [lat_max, lon_max]
                  name = 'No disturbance / no calculation for Recovery 77',
                  overlay = True,
                  control = True  
                  ).add_to(my_map)

###############################################################
# FINISH AND SAVE

# add a colormap from a png since there's 2 sep pngs and the colormaps are so hacky 

#add a background to the colorbar - hacky and stolen from
#https://stackoverflow.com/questions/44887461/how-to-add-a-background-color-of-a-colormap-in-a-folium-map
# cmap_HTML = cm1._repr_html_()
# cmap_HTML = cmap_HTML.replace('<svg height="50" width="400">','<svg id="cmap" height="50" width="400">',1)
# cmap_style = '<style>#cmap {background-color: green;}</style>'




# my_map.get_root().header.add_child(f.Element(cmap_style))


f.map.LayerControl().add_to(my_map)

# my_map.get_root().html.add_child(f.Element(cmap_HTML))


my_map.save('tharaka_interactive_map.html')

print('donezo')