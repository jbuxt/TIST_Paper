#Make masks out of shp files and save them for applying in Intake Veg and make pix lists

import pickle
import geopandas as gp 
import rasterio as rs
from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
#import numpy.ma as ma 


with open('relevant_tist.pkl', 'rb') as file:
    TIST = pickle.load(file)

with open('relevant_counties.pkl', 'rb') as file:
    counties = pickle.load(file)

with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bound = pickle.load(file)

# with open('veg_meta_8day.pkl', 'rb') as file:
#     meta_8day, bound_8day = pickle.load(file)

# rows = 6871 #in original ROI
# cols = 8786
# rows = 7747 #in the 8day ls/modis pics
# cols = 7422
# int(meta_8day['height']), int(meta_8day['width'])
# (7307, 7329) is the actual number of pix in one ls image


# mod_shp = gp.read_file('./mod_shp/mod_shp.shp')  #The modis-ls 8day shape (shape of 1 ls scene)

# mod_mask = features.rasterize(
#     ## make a mask of the valid data within the tif files of the ls/modis scenes
#             mod_shp.geometry,
#             out_shape=[rows, cols], #CANT use the metadata for height/width
#             #transform=meta_8day['transform'], #can't use this either hmmmm
#             all_touched = True)

# #####################################################
# # Make an outline of the entire study area 
# # counties['roi_col'] = 1
# # roi = counties.dissolve(by='roi_col')


# # counties.plot()
# # roi.plot()
# # plt.show()
# ######################################################
# Create an np array mask of the counties 
county_mask = features.rasterize(
    ## The numbers in mask correspond to counties as follows
    ## 0 = no county
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Embu (29)

             [(counties.loc[0, 'geometry'], 1), (counties.loc[1, 'geometry'], 2),
               (counties.loc[2, 'geometry'], 3), (counties.loc[3, 'geometry'], 4),
               (counties.loc[5, 'geometry'], 5)],
            # out_shape=[int(veg_meta['height']), int(veg_meta['width'])],
            out_shape=[rows, cols],
            transform=veg_meta['transform'], #how to get this to workkkkk 
            all_touched = True)

plt.imshow(county_mask)
plt.show()
# rows = 6871 #in total picture
# cols = 8786
with open ('county_mask_8day.pkl', 'wb') as file:
    pickle.dump(county_mask, file)

TIST_mask = features.rasterize(
    ## make a mask of all pixels in TIST groves
            TIST.geometry,
            out_shape=[veg_meta['height'], veg_meta['width']], #EDIT
            transform=veg_meta['transform'],
            all_touched = True)
plt.imshow(TIST_mask)
plt.show()


with open ('TIST_mask_8day.pkl', 'wb') as file:
    pickle.dump(TIST_mask, file)

############################################################################
eco = gp.read_file('eco_shp/eco_shp.shp') 

eco_mask = features.rasterize(
    ## The numbers in mask correspond to ecoregions as follows
    ## 57 = Southern Acacia-Commiphora bushlands and thickets
    ## 51 =  Northern Acacia-Commiphora bushlands and thickets
    ## 78 = East African montane moorlands
    ## 8 =  East African montane forests
            zip(eco['geometry'], eco['label']),
            out_shape=[int(veg_meta['height']), int(veg_meta['width'])], #EDIT
            transform=veg_meta['transform'],
            all_touched = True)

plt.imshow(eco_mask)
plt.show()

with open ('eco_mask_8day.pkl', 'wb') as file:
    pickle.dump(eco_mask, file)

#have to redownload the ecoregions and landcover with the mod_shp

print('done')
