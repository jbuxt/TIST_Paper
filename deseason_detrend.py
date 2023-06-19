#take a few lists of pixels and deseason and detrend 

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

with open ('precip_pixels_sample.pkl', 'rb') as file:
    precip_df, precip_meta, precip_bound = pickle.load(file)

# precip_df.to_csv('precip_pixels_sample.csv', encoding='utf-8', index=False)

with open ('ndvi_pixels_sample.pkl', 'rb') as file:
    ndvi_df, ndvi_meta, ndvi_bound = pickle.load(file)

# ndvi_df.to_csv('ndvi_pixels_sample.csv', encoding='utf-8', index=False)

## Summary stats on the ndvi 
print('total % pix missing: ', ndvi_df.isna().sum().sum() / (120*ndvi_df.shape[0])) #for all pix

#how many pixels are missing by month generally
for m in range(1,13):
    mo = '-'+str(m).zfill(2)
    missing = ndvi_df.filter(like=mo, axis=1).isna().sum().sum() #number of missing for that month over the 10 years
    # print(mo, ' missing % : ', missing/(2500*10))

#apply smoothing function to each timeseries (rows, axis =1)
#this takes a minute
#would be nice to vectorize this but not sure that's possible
smoothed_ndvi_df = ndvi_df.filter(like='20', axis =1).astype("float32").apply(sgf, axis = 1, result_type='broadcast') #

# for idx, row in ndvi_df.iterrows():
#     # use df.apply, with result_type='broadcast'
#     ts = ndvi_df.at[idx].filter(like='20', axis =1)
#     ts_smoothed = sgf(ts, debug = False)
    ## consider: the wrapping? not sure why this is skipping some bits entirely 

for i in range(1,5):
    plt.subplot(4, 1, i)
    plt.plot(smoothed_ndvi_df.columns, smoothed_ndvi_df.iloc[i], 'bo', smoothed_ndvi_df.columns, 
           ndvi_df.filter(like='20', axis =1).iloc[i], 'g*')
    plt.title('pixel '+str(i))
plt.suptitle('ndvi with sgf smoothing')
plt.show()

#############################################
## Deseason and detrend with STL

# period = 12 #since monthly data with yearly seasons
# smooth_length = 7 #ns from STL - might have to fiddle with this 
# p1_res = stl.robust_stl(p1_smoothed, period, smooth_length)

#just for debugging - get a few example plots 
for i in range(1,5):
    plt.figure(i)
    decomp = stl.robust_stl(smoothed_ndvi_df.iloc[i], period = 12, smooth_length = 7)
    decomp.plot()
    plt.title('STL')
    plt.show()


#returns object - just get .resid out of it 
def get_resid(s):
    decomp = stl.robust_stl(s, period = 12, smooth_length = 7)
    return decomp.resid

ndvi_res = smoothed_ndvi_df.apply(get_resid, axis=1, result_type='broadcast')

#copy over the rows and columns etc
ndvi_res[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]


print('done')
# is this going to work well to scale up? tbd lmao 


