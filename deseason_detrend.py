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

precip_df.to_csv('precip_pixels_sample.csv', encoding='utf-8', index=False)

with open ('ndvi_pixels_sample.pkl', 'rb') as file:
    ndvi_df, ndvi_meta, ndvi_bound = pickle.load(file)

ndvi_df.to_csv('ndvi_pixels_sample.csv', encoding='utf-8', index=False)

## consider: the wrapping? not sure why this is skipping some bits entirely 
p0_smoothed = sgf(p0[:, 1], debug = False) 
p1_smoothed = sgf(p1[:, 1], debug = False) 
p2_smoothed = sgf(p2[:, 1], debug = False) 
p3_smoothed = sgf(p3[:, 1], debug = False) 

plt.subplot(4, 1, 1)
plt.plot(date_list, p2[:, 1], 'bo', date_list, pd.Series(p2[:, 1]).interpolate(method="linear"), 
         'r-', date_list, p2_smoothed, 'g*')
plt.title('p2')
plt.subplot(4, 1, 2)
plt.plot(date_list, p0[:, 1], 'bo',date_list, pd.Series(p0[:, 1]).interpolate(method="linear"), 'r-',
         date_list, p0_smoothed, 'g*')
plt.title('p0')
plt.subplot(4, 1, 3)
plt.plot(date_list, p1[:, 1], 'bo', date_list,pd.Series(p1[:, 1]).interpolate(method="linear"), 'r-',
         date_list, p1_smoothed, 'g*')
plt.title('p1')
plt.subplot(4, 1, 4)
plt.plot(date_list, p3[:, 1], 'bo', date_list,pd.Series(p3[:, 1]).interpolate(method="linear"), 'r-',
         date_list, p3_smoothed, 'g*')
plt.title('p3')
plt.suptitle('ndvi with linear and sgf smoothing')
plt.show()



#############################################
## Deseason


'''#reshape so that each row is a year and each column is a month
reshaped = p1[:, 1].reshape(10,12) #ndvi 

ndvi_season = np.nanmean(reshaped, axis = 0)
# Take the average of each month across the ten years, ignoring nans
# Have a 1x12 array now of the seasonal means (1 row)

#subtract each column - have to transpose one because of np.subtract
#10x12 - 
# 1 x 12 season 
deseasoned = (reshaped - ndvi_season).flatten(order = 'C')
#get back to one column 
plt.figure()
plt.plot(deseasoned)
plt.title('deseasoned with mean')
plt.show()'''

period = 12 #since monthly data with yearly seasons
smooth_length = 7 #ns from STL - might have to fiddle with this 
p1_res = stl.robust_stl(p1_smoothed, period, smooth_length)

p1_res.plot()
plt.title('STL')
plt.show()

print('done')
# is this going to work well to scale up? tbd lmao 


