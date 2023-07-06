#Maddie Henderson
# take a df of pixels through time, linearly fill gaps up to 2 months
# grab only sections that are continuous for more than 4 years
# use STL to decomp those sections and keep residual 

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import STL_Fitting as stl


# Load the veg data #############################################
ndvi_df = pd.read_csv('ndvi_pixels_Theraka.csv', nrows=100) #TEMP for testing 

nrows, dum = ndvi_df.shape
# dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')

#interpolate up to 3 missing points
smoothed_ndvi_df = ndvi_df.iloc[:, 4:].astype("float32").interpolate(method='linear', limit=2, axis = 1, limit_area='inside')

# del ndvi_df # save space 
#add a nan column to the end after interpolation so that it always splits on that 
smoothed_ndvi_df['empty']=np.nan
mask  = np.empty((nrows, 121)).flatten() #make a mask the size of the data 
mask[:] = np.nan 

# for i in range(nrows): #
#https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values
#POTENTIAL ISSUE - precision - goes to float 64
flat_ndvi = smoothed_ndvi_df.values.flatten()
m = np.concatenate(( [True], np.isnan(flat_ndvi), [True] ))  
ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits - for the whole df flattened to 1D
#get any sections longer than 48 pts in this row because need a few years for good seasonal decomp
ss = ss[((ss[:,1] - ss[:,0]) >= 48)]

#set everything outside of these intervals to NaN
for start, stop in ss:
    mask[start:stop] = 1

#apply mask - now all 'rows' have either 1 or 2 longer runs 
flat_ndvi = flat_ndvi * mask


# STL decomp ###########################################
ndvi_res_flat = np.empty((nrows, 121)).flatten()
ndvi_res_flat[:] = np.nan

for start, stop in ss: 
    sample = flat_ndvi[start:stop] #get the continuous slice 
    #apply the decomp and get residual
    decomp = stl.robust_stl(sample, period = 12, smooth_length = 21)
    ndvi_res_flat[start:stop] = decomp.resid


    # decomp.plot()
    # plt.xticks(rotation=90)
    # plt.suptitle('STL')
    # plt.show()
    
smoothed_ndvi_df.loc[:,:] = ndvi_res_flat.reshape(nrows, 121)
# smoothed_ndvi_df = smoothed_ndvi_df.drop(columns='empty')

#copy over the rows and columns etc
smoothed_ndvi_df[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]
# del smoothed_ndvi_df #save space

#Save to CSV 
smoothed_ndvi_df.to_csv('ndvi_residuals_Theraka.csv', encoding='utf-8', index=False)
#Save the ss !!
#np save ss to csv ?? 

print('done')
