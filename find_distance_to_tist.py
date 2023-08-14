# Maddie Henderson 
## 2023
## apply diff additional pieces of info to the dfs for spotfire
## and then also maybe make some TIFs for qgis 
## to result dfs so that csvs can be used in spotfire 

import pandas as pd 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import pickle
from rasterio import features
from df_to_map import df_to_map
from scipy.ndimage import distance_transform_edt as edt


# get neighboring tist #######################

with open('TIST_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)


## EDT in scipy works by finding distance to closest 'background' pixel (zeros
# so need to invert image first 
dists = edt(np.logical_not(tist_mask))
#calculates euclidean distance to closest 0 pixel
# note that this is in distance of pixels
#convert to meters 
dists = dists * 30 
# plt.imshow(dists)
# plt.show()

# save for maps ##############################
with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bounds = pickle.load(file)

tist_meta = veg_meta
tist_meta['dtype'] = 'float32'
tist_meta['count'] = 1

with rs.open('tist_distance.tif',"w", **tist_meta) as f:
    #python array is row, cols, depth
    # rasterio expects band, row, col
    #can do a 2d with indexes=1
    f.write(dists, indexes=1)
    # set layer descriptions 

# SAVE To result csvs############################# 

for county in ['Tharaka', 'Meru', 'Nyeri', 'Meru']:

    infile = './RESULTS/V2/ndvi_all_results_'+county+'.csv'
    result_df = pd.read_csv(infile)
    
    result_df['tist_distance'] = dists[result_df['row'], result_df['col']]

    result_df.to_csv(infile, encoding='utf-8', index=False)

print('added distance to TIST grove in m')                   
