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
dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')
#apply smoothing and filling function (Chen 2004) to each timeseries (rows, axis =1)
#this takes a minute
#would be nice to vectorize this but not sure that's possible
#right now limit to fill is 3 because a season is 3 months so dont want to miss 
#any holes larger than 3 months are not filled and left as NaN
#And only the longest three continuous sections are kept and smoothed after filling 

'''
smoothed_ndvi_df = ndvi_df.filter(like='20', axis =1).astype("float32").apply(sgf, axis = 1, result_type='broadcast') #
'''

# What if we just linearly interpolate, don't think i have enough resolution 
# to really bother with this thing

smoothed_ndvi_df = ndvi_df.filter(like='20', axis =1).astype("float32").interpolate(method='linear', limit=3, axis = 1, limit_area='inside')
smoothed_ndvi_df[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]
# del ndvi_df # save space 

final_ts = interp_ts.copy()
final_ts.iloc[:]=np.nan
 
# are there any holes still missing? If so,
# get any portions of data longer than 48 pts (should be only 1 or 2 sections since only 120 pts)
# Extract out relevant column from dataframe as array
m = np.concatenate(( [True], np.isnan(interp_ts.values), [True] ))  # Mask
#kinda assuming there are no completely empty pixels 
#https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values

ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits
intervals, dum = np.shape(ss) #how many intervals are there 
#get any sections longer than 48 pts 
ss = ss[((ss[:,1] - ss[:,0]) >= 48)] #check this 
#set everything outside of these two intervals to NaN
mask = 
# if intervals > 2: #if more than 3 pick the top 3
#     # ss = ss[np.argpartition((ss[:,1] - ss[:,0]), -3)[-3:]]
#     ss = ss[((ss[:,1] - ss[:,0]) >= 48)]
#     intervals = 3

# start,stop = ss[(ss[:,1] - ss[:,0]).argmax()]  # Get max interval, interval limits
for x in range(0,intervals):
    start, stop = ss[x, :] #get idx of the interval 
    temp_ts = interp_ts.iloc[start:stop]
    #assign the smoothed section to the output series then repeat for other intervals
    final_ts.iloc[start:stop] = smooth_ts


for i in range(1,5):
    plt.subplot(4, 1, i)
    plt.plot(dates, smoothed_ndvi_df.filter(like='20').iloc[i], 'bo', dates, 
           ndvi_df.filter(like='20').iloc[i], 'g*')
    # plt.title('pixel '+str(i))
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
