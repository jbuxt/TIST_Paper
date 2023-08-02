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
#################################################
county = input('Input the county to process: ')
infile = 'ndvi_results_w_landcover'+county+'.csv'
pix_file = 'ndvi_pixels_'+county+'.csv'

pix= pd.read_csv(pix_file)


with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bounds = pickle.load(file)

mean = pix.iloc[:, 4:].mean(axis = 1).astype('float32') #mean excluding nan of all the ndvi originals 
stdev = pix.iloc[:, 4:].std(axis = 1).astype('float32')
ndvi_mean = pd.concat([pix.loc[:, ['row', 'col']], mean.rename('mean_ndvi'), stdev.rename('stdev_ndvi')], axis = 1)
del pix
#add to results 
result_df = pd.read_csv(infile)
result_df = result_df.merge(ndvi_mean, how='left', on=['row', 'col'])

# save as a tif for all pix in county
df_to_map(ndvi_mean, ['mean_ndvi', 'stdev_ndvi'], savefile = True, fname = 'ndvi_mean_'+county+'.tif', meta = veg_meta)

###################################################################
# altitude 

im = rs.open('altitude.tif')
alt_array= im.read(1)
plt.imshow(alt_array)
im.close()

#because it came with 2 extra rows and one extra column thanks to some imperfection in roi 
#checked which rows were extra in qgis
#now the indexes match up 
alt_array = np.delete(alt_array, [0, -1], 0) # delete first and last row
alt_array = np.delete(alt_array, 0, 1) #delete first column

result_df = pd.read_csv(infile)
# relevant values 
result_df['alt'] = alt_array[result_df['row'], result_df['col']]

###############################################
# get neighboring tist 

with open('TIST_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)

#find neighbors within 1 pixel 
kernel = np.ones((3, 3), dtype='uint8')
neighbors = cv2.dilate(tist_mask, kernel)

tist_mask = neighbors + tist_mask 
# now the center pixels are 2 and and the neighbor pixels are 1 and others are 0 

# relevant values 
result_df['tist_neighbors'] = tist_mask[result_df['row'], result_df['col']]

# save for qgis 
# tist_meta = veg_meta
# tist_meta['dtype'] = 'int8'
# tist_meta['count'] = 1

# with rs.open('tist_neighbors.tif',"w", **tist_meta) as f:
#     #python array is row, cols, depth
#     # rasterio expects band, row, col
#     #can do a 2d with indexes=1
#     f.write(tist_mask, indexes=1)
#     # set layer descriptions 

################## save
result_df.to_csv('ndvi_results_w_everything'+county+'.csv', encoding='utf-8', index=False)

print('add mean ndvi, alt, and tist neighbors for '+county)                   
