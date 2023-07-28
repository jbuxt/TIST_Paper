# Maddie Henderson 
## 2023
## apply the ecoregion masks -- tbd at what stage in process. ignore for now 

import pandas as pd 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import os
import pickle
from datetime import datetime as dt    

#################################################
# Import masks 
#################################################
# county = input('Input the county to process: ')
county = 'Tharaka'
if county == 'Laikipia':
    county_int = 1
elif county == 'Meru':
    county_int = 2
elif county == 'Tharaka':
    county_int = 3
elif county == 'Nyeri':
    county_int = 4
elif county == 'Embu':
    county_int = 5
else: 
    print('incorrect county entered')
    #program will crash later lol

with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bound = pickle.load(file)

im = rs.open('ecoregions_rasterized_correct_crs.tif')
ecoregion = im.read(1)
eco_meta = im.meta
plt.imshow(ecoregion)
im.close()

with open ('ecoregion_mask.pkl', 'wb') as file:
    pickle.dump(ecoregion, file)

im = rs.open('landcover_WorldCoverv100_reprojected.tif')
landcover= im.read(1)
landcover_meta = im.meta
plt.imshow(landcover)
im.close()

with open ('landcover_mask.pkl', 'wb') as file:
    pickle.dump(landcover, file)

#FIX THIS 
ndvi_df = pd.read_csv('./intermediate_landsat/ndvi_pixels_'+county+'.csv', nrows=1000) #TEMP for testing , nrows =1000


# Get lists of where landcover <= 40 
#only keeping grassland, shrubland, cropland, and forest
#not sure if this works or need to do in 2 steps 
# landcover_idx = np.argwhere(landcover_mask <= 40)

ndvi_df['landcover'] = landcover(ndvi_df['row'], ndvi_df['col'])

# ndvi_df.at[p, 'landcover'] = landcover_mask[i, j]
# ndvi_df.at[p, 'ecoregion'] = ecoregion_mask[i, j]

# #Number of pixels in each county: 
# n_Laikipia = 10837687 
# n_Meru = 7720270
# n_Theraka = 2990072
# n_Nyeri = 3733796
# n_Kirinyaga = 1652252
# n_Embu = 3170195

rows = 6871 #in total picture
cols = 8786

# n_ROI = 30104272 #all counties 
n_months = 120 


# #Veg indices 
dirname = './GEE_Veg_new'




ndvi_df.to_csv('ndvi_pixels_w_landcover'+county+'.csv', encoding='utf-8', index=False)

print('done with landcover for '+county)                   
