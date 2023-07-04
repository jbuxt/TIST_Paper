#take a df of pixels through time and deseason and detrend 
# fill trend with NDVI reconstruction chen 2004
# use STL to decomp

import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
import numpy.ma as ma 
import STL_Fitting as stl
from sav_golay import savitzky_golay_filtering as sgf


# Load the veg data #############################################
# with open ('ndvi_pixels_sample.pkl', 'rb') as file:
#     ndvi_df, ndvi_meta, ndvi_bound = pickle.load(file)

ndvi_df = pd.read_csv('ndvi_pixels_Theraka.csv', nrows=100) #TEMP for testing 

#apply smoothing and filling function (Chen 2004) to each timeseries (rows, axis =1)
#this takes a minute
#would be nice to vectorize this but not sure that's possible
smoothed_ndvi_df = ndvi_df.filter(like='20', axis =1).astype("float32").apply(sgf, axis = 1, result_type='broadcast') #
smoothed_ndvi_df [['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]

# del ndvi_df # save space 

## consider: the wrapping? not sure why this is skipping some bits entirely 

for i in range(1,5):
    plt.subplot(4, 1, i)
    plt.plot(smoothed_ndvi_df.columns, smoothed_ndvi_df.iloc[i], 'bo', smoothed_ndvi_df.columns, 
           ndvi_df.filter(like='20', axis =1).iloc[i], 'g*')
    plt.title('pixel '+str(i))
plt.suptitle('Sample NDVI pixels with Reconstruction and Smoothing')
plt.show()

#############################################
## Deseason and detrend with STL

#just for debugging - get a few example plots 
# for i in range(1,5):
#     # plt.figure(i)
#     decomp = stl.robust_stl(smoothed_ndvi_df.iloc[i], period = 12, smooth_length = 7)
#     plt.xticks(rotation=90)
#     decomp.plot()
#     plt.title('STL')
#     plt.show()

# Apply the STL decomposition
#returns object - just get .resid out of it 
def get_resid(s):
    decomp = stl.robust_stl(s, period = 12, smooth_length = 7)
    return decomp.resid

ndvi_res = smoothed_ndvi_df.filter(like='20').apply(get_resid, axis=1, result_type='broadcast')
#copy over the rows and columns etc
ndvi_res[['row','col','tist', 'county']]=smoothed_ndvi_df[['row','col','tist', 'county']]
# del smoothed_ndvi_df #save space

# with open('ndvi_sample_res.pkl', 'wb') as f:
#     pickle.dump([ndvi_res, ndvi_meta, ndvi_bound], f)

#Save to CSV 
ndvi_res.to_csv('ndvi_residuals_Theraka.csv', encoding='utf-8', index=False)

print('done')
