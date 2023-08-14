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
import cv2
from df_to_map import df_to_map
from scipy.ndimage import distance_transform_edt as edt

#################################################
# county = input('Input the county to process: ')

# infile = './RESULTS/V2/ndvi_all_results_'+county+'.csv'
# result_df = pd.read_csv(infile)

# with open('veg_meta.pkl', 'rb') as file:
#     veg_meta, veg_bounds = pickle.load(file)


# get neighboring tist #######################

with open('TIST_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)


# save for maps ##############################
# tist_meta = veg_meta
# tist_meta['dtype'] = 'int32'
# tist_meta['count'] = 1

# with rs.open('tist_neighbors.tif',"w", **tist_meta) as f:
#     #python array is row, cols, depth
#     # rasterio expects band, row, col
#     #can do a 2d with indexes=1
#     f.write(tist_mask, indexes=1)
#     # set layer descriptions 

# SAVE To result csvs############################# 
# result_df['tist_neighbors'] = tist_mask[result_df['row'], result_df['col']]

# result_df.to_csv(infile, encoding='utf-8', index=False)

print('added mean ndvi, alt, pct missing, human modification, and tist neighbors for '+county)                   
