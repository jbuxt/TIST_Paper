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
#################################################
county = 'Nyeri' #input('Input the county to process: ')
infile = './RESULTS/V2/ndvi_results_w_landcover'+county+'.csv'
pix_file = './RESULTS/V2/ndvi_pixels_'+county+'.csv'

# pix= pd.read_csv(pix_file, nrows = 5000)

# mean = pix.iloc[:, 4:].mean(axis = 1).astype('float32') #mean excluding nan of all the ndvi originals 
# stdev = pix.iloc[:, 4:].std(axis = 1).astype('float32')
# ndvi_mean = pd.concat([pix['row', 'col'], mean.rename('mean'), stdev.rename('stdev')], axis = 1)
# del pix
# save as a tif! for all pix or just the ones with results? 
#df to map 

###################################################################
# altitude 
'''
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
'''
###############################################

with open('relevant_tist.pkl', 'rb') as file:
    TIST = pickle.load(file)
with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bounds = pickle.load(file)

TIST_mask = features.rasterize(
    ## make a mask of all pixels in TIST groves
            TIST.geometry,
            out_shape=[veg_meta['height'], veg_meta['width']], 
            transform=veg_meta['transform'])

#find neighbors within 1 pixel 
kernel = np.ones((3, 3), dtype='uint8')
neighbors = cv2.dilate(TIST_mask, kernel)

tist_mask = neighbors + TIST_mask 
# now the center pixels are 2 and and the neighbor pixels are 1 and others are 0 

tist_meta = veg_meta
tist_meta['dtype'] = 'int8'
tist_meta['count'] = 1

with rs.open('tist_neighbors.tif',"w", **tist_meta) as f:
    #python array is row, cols, depth
    # rasterio expects band, row, col
    #can do a 2d with indexes=1
    f.write(tist_mask, indexes=1)
    # set layer descriptions 

################## add to outputs 

with_mean = result_df.merge(ndvi_mean, how='left', on=['row', 'col'])



final_results.to_csv('ndvi_results_w_everything'+county+'.csv', encoding='utf-8', index=False)

print('add mean ndvi, x, x, and x for '+county)                   
