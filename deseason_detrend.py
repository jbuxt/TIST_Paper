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
mask  = np.empty((nrows, 120)) #make a mask the size of the data 
mask[:] = np.nan 
all_ss = pd.DataFrame(columns=['ss'], index= range(nrows))
for i in range(nrows):
    #https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values
    m = np.concatenate(( [True], np.isnan(smoothed_ndvi_df.iloc[i].values), [True] ))  
    ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits
    #get any sections longer than 48 pts in this row because need a few years for good seasonal decomp
    ss = ss[((ss[:,1] - ss[:,0]) >= 48)]
    all_ss.loc[i, 'ss'] = ss
    # (should be only 1 or 2 sections since only 120 pts)
    # intervals, dum = np.shape(ss) #how many intervals are there

    #set everything outside of these two intervals to NaN
    for start, stop in ss:
        mask[i, start:stop] = 1

#apply mask - now all rows have either 1 or 2 longer runs 
smoothed_ndvi_df.loc[:,:]= smoothed_ndvi_df.values * mask 
smoothed_ndvi_df['ss'] = all_ss
'''should i do this line by line? could I find the indices of the right sections of the whole
array at once and apply a mask that way?
-- how to tell it to only get things that are more than 48 long within each row without
going row by row? 
also should i apply the STL decomp at the same time since i will already have the indices of 
start and stop? 

could i apply a land cover mask to the county data or even while retrieving it from the tif files? 
that could reduce pixels by some amoount 

also, if i get server access, maybe it's just not a problem and i can move on and stop worrying
'''

#kinda assuming there are no completely empty pixels 

for i in range(1,5):
    plt.subplot(4, 1, i)
    plt.plot(dates, smoothed_ndvi_df.iloc[i], 'bo', dates, 
           ndvi_df.filter(like='20').iloc[i], 'g*')
    # plt.title('pixel '+str(i))
plt.suptitle('Sample NDVI pixels with Linear Interpolation, short gap filling')
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

ndvi_res = smoothed_ndvi_df.apply(get_resid, axis=1, result_type='broadcast')
#copy over the rows and columns etc
ndvi_res[['row','col','tist', 'county']]=ndvi_df[['row','col','tist', 'county']]
# del smoothed_ndvi_df #save space

#Save to CSV 
ndvi_res.to_csv('ndvi_residuals_Theraka.csv', encoding='utf-8', index=False)

print('done')
