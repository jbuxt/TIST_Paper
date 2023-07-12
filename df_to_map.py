# Use this to return the df of each pixel through time to the original map 
# takes df with pixel locations, county, tist, etc and additional columns 
# for values that should be put back in maps 
# put names of columns you want mapped in a list 
#future -  convert to raster file for plotting in GIS 

import numpy as np 
from scipy.sparse import coo_matrix 
import pandas as pd
import rasterio as rs
# import matplotlib.pyplot as plt 

def df_to_map(df, col_names, rows=6871, cols=8786, savefile=False, fname='output_map', meta=None):
    #know rows/cols based on my orginal region of interest

    n_layers = len(col_names) #number of maps to make
    #initialize array of correct size with nan
    array = np.empty((rows, cols, n_layers))
    array[:] = np.nan

    for x in range(n_layers):
        vals = col_names[x]
        s_img = coo_matrix((df[vals], (df.row, df.col)), shape = (rows, cols))
        img = s_img.todense()
        array[:,:, x] = img
        
    
    if savefile:
        meta['count'] = n_layers

        with rs.open(fname,"w",**meta) as f:
            # write the file path (a string) to the content of the raster
            # file (it expects the mentioned array-like object from the
            # error), will not work well, hence the error
            f.write(array)
            print('tif saved to: '+fname)

    return array


# #testing 

# ndvi = pd.read_csv('ndvi_pixels_sample.csv') 
# ndvi['Average']=ndvi.filter(like='20').mean(axis= 1, skipna=True)
# ndvi['Max']=ndvi.filter(like='20').max(axis= 1)
# img = df_to_array_map(ndvi, ['Average', 'Max'])

# plt.imshow(img[:,:, 0])

# plt.imshow(img[:,:, 1])
# print('done')