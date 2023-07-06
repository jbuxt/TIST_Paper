#take a df of pixels through time and deseason and detrend 
# fill trend with NDVI reconstruction chen 2004
# use STL to decomp

import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import numpy.ma as ma 
import STL_Fitting as stl
# from sav_golay import savitzky_golay_filtering as sgf


# Load the veg data #############################################
# with open ('ndvi_pixels_sample.pkl', 'rb') as file:
#     ndvi_df, ndvi_meta, ndvi_bound = pickle.load(file)

ndvi_df = pd.read_csv('ndvi_pixels_Theraka.csv', nrows=100) #TEMP for testing 
nrows, dum = ndvi_df.shape
dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')

#interpolate up to 3 missing points
smoothed_ndvi_df = ndvi_df.iloc[:, 4:].astype("float32").interpolate(method='linear', limit=3, axis = 1, limit_area='inside')

# smoothed_ndvi_df[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]
# del ndvi_df # save space 
#add a nan column to the end after interpolation so that it always splits on that 
smoothed_ndvi_df['empty']=np.nan
mask  = np.empty((nrows, 121)).flatten() #make a mask the size of the data 
mask[:] = np.nan 
# all_ss = pd.DataFrame(columns=['ss'], index= range(nrows)) #still need this? 
# for i in range(nrows): #
#https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values
#POTENTIAL ISSUE - precision - goes to float 64
flat_ndvi = smoothed_ndvi_df.values.flatten()
m = np.concatenate(( [True], np.isnan(flat_ndvi), [True] ))  
ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits - for the whole df flattened to 1D
#get any sections longer than 48 pts in this row because need a few years for good seasonal decomp
ss = ss[((ss[:,1] - ss[:,0]) >= 48)]
# all_ss.loc[i, 'ss'] = ss
# (should be only 1 or 2 sections since only 120 pts +1 nan)
intervals, dum = np.shape(ss) #how many intervals are there

#set everything outside of these two intervals to NaN
for start, stop in ss:
    mask[start:stop] = 1
# mask = mask.reshape((nrows, 121))
#apply mask - now all rows have either 1 or 2 longer runs 
flat_ndvi = flat_ndvi * mask


# STL decomp ###########################################
ndvi_res_flat = np.empty((nrows, 121)).flatten()
ndvi_res_flat[:] = np.nan
i=0
for start, stop in ss: 
    sample = flat_ndvi[start:stop] #get the continuous slice 
    #apply the decomp and get residual
    decomp = stl.robust_stl(sample, period = 12, smooth_length = 7)
    ndvi_res_flat[start:stop] = decomp.resid

    if i < 5:
        plt.xticks(rotation=90)
        decomp.plot()
        plt.title('STL')
        plt.show()
    i+=1

#don't have to do this until the end
# smoothed_ndvi_df.loc[:,:]= smoothed_ndvi_df.values * mask 
smoothed_ndvi_df.loc[:,:] = ndvi_res_flat.reshape(nrows, 121)
smoothed_ndvi_df = smoothed_ndvi_df.drop(columns='empty')
# smoothed_ndvi_df['ss'] = all_ss

'''
could i apply a land cover mask to the county data or even while retrieving it from the tif files? 
that could reduce pixels by some amoount 

also, if i get server access, maybe it's just not a problem and i can move on and stop worrying
'''

# for i in range(1,5):
#     plt.subplot(4, 1, i)
#     plt.plot(dates, smoothed_ndvi_df.iloc[i], 'bo', dates, 
#            ndvi_df.filter(like='20').iloc[i], 'g*')
#     # plt.title('pixel '+str(i))
# plt.suptitle('Sample NDVI pixels with Linear Interpolation, short gap filling')
# plt.show()


# Apply the STL decomposition
#returns object - just get .resid out of it 
# def get_resid(s):
#     decomp = stl.robust_stl(s, period = 12, smooth_length = 7)
#     return decomp.resid

# ndvi_res = smoothed_ndvi_df.apply(get_resid, axis=1, result_type='broadcast')

#copy over the rows and columns etc
smoothed_ndvi_df[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]
# del smoothed_ndvi_df #save space

#Save to CSV 
smoothed_ndvi_df.to_csv('ndvi_residuals_Theraka.csv', encoding='utf-8', index=False)

print('done')
