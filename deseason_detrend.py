#Maddie Henderson
# V0
# take a df of pixels through time, linearly fill gaps up to 2 months
# grab only sections that are continuous for more than 4 years
# use STL to decomp those sections and keep residual 

# V1
# take a df of pixels through time
# Find the average value of each month (eg avg Jan, avg Feb, etc)
# Save a mask of the missing values for whole df 
# Use those averages to fill holes in timeseries   
# use STL to decomp those sections and keep residual
# Then mask out the gaps you filled 
# Check: how many have 10 or 11 out of 12 months for a recovery year? 
# Option: go back to linearly filling for 1 or 2 months also 

import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import STL_Fitting as stl
import pickle


# Load the veg data #############################################
# county = input('Input the county to process: ')
county = 'Tharaka'

ndvi_df = pd.read_csv('./intermediate_landsat/ndvi_pixels_'+county+'.csv', nrows =5000) #TEMP for testing 

## Summary stats on the ndvi 
# print('total % pix missing: ', ndvi_df.isna().sum().sum() / (120*ndvi_df.shape[0])) #for all pix

#grab the slices that would matter for the tharaka recov periods
# r59 =  ndvi_df.iloc[:, (59-5):(59+6)]
# print('% pix missing for r59: ', r59.isna().sum().sum() / (r59.size))
# r77 =  ndvi_df.iloc[:, (77-5):(77+6)]
# print('% pix missing for r77: ', r77.isna().sum().sum() / (r77.size))
# r59.dropna(axis=0, thresh=6, inplace=True, ignore_index=False)
# print('% rows with more than 6 mo r59: ', r59.shape[0] )
# r77.dropna(axis=0, thresh=6, inplace=True, ignore_index=False)
# print('% rows with more than 6 mo r77: ', r77.shape[0])  

nrows, dum = ndvi_df.shape
dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')

# V0
#interpolate up to 2 missing points since a season is usually 3 months
# will lose about 20% ? of pixels this way 
# smoothed_ndvi_df = ndvi_df.iloc[:, 4:].astype("float32").interpolate(method='linear', limit=2, axis = 1, limit_area='inside')

#V1 - find avg of months per pixel 
avgs = pd.DataFrame(columns = range(1,13))
for m in range(1,13):
     mo = '-'+str(m).zfill(2)
     avgs.loc[:, m] = ndvi_df.filter(like=mo, axis=1).mean(axis = 1) #mean through each row across col 
all_avg = pd.concat([avgs.loc[:, 5:], avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs.loc[:, :4]], axis = 1)
all_avg = pd.concat([ndvi_df[['row','col','tist', 'county']], all_avg], axis = 1)
all_avg.columns = ndvi_df.columns

# Save a mask of the empty months for later
empty_mask =  ndvi_df.isna() #nan = true, not nan = false

#Now fill the empty pix with the average established for that month for that pixel 
smoothed_ndvi_df = ndvi_df.mask(empty_mask, all_avg) #mask replaces values that are True (nan)

### Get an example plot################
# plt.plot(dates, smoothed_ndvi_df.iloc[55, 4:], 'b-', label='filled')
# plt.plot(dates, ndvi_df.iloc[55, 4:], 'go', label='original')
# plt.title('Example: replaced missing months with pixel average for that month')
# plt.xlabel('date')
# plt.ylabel('NDVI')
# plt.legend()
# plt.show()

'''
#add a nan column to the end after interpolation so that it always splits on that 
smoothed_ndvi_df['empty']=np.nan
mask  = np.empty((nrows, 121)).flatten() #make a mask the size of the data 
mask[:] = np.nan 


#https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values

flat_ndvi = smoothed_ndvi_df.values.flatten().astype('float32')
m = np.concatenate(( [True], np.isnan(flat_ndvi), [True] ))  
ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits - for the whole df flattened to 1D
#get any sections longer than 48 pts in this row because need a few years for good seasonal decomp
ss = ss[((ss[:,1] - ss[:,0]) >= 48)]

#set everything outside of these intervals to NaN
for start, stop in ss:
    mask[start:stop] = 1

#apply mask - now all 'rows' have either 1 or 2 longer continuous runs 
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
'''
ndvi_res = ndvi_df.copy()
ndvi_res.iloc[:, 4:] = 0

ndvi_array = np.array(smoothed_ndvi_df.iloc[:, 4:].astype('float32'))

for i in smoothed_ndvi_df.index:
    decomp = stl.robust_stl(ndvi_array[i, :], period = 12, smooth_length = 21)
    ndvi_res.iloc[i, 4:] = decomp.resid

    # decomp.plot()
    # plt.xticks(rotation=90)
    # plt.show()

###### Now remove all the values that were originally nan 
ndvi_res.mask(empty_mask, np.nan, inplace=True)

#find the mean and std dev of the residuals after decomposing 
mean = ndvi_res.iloc[:, 4:].mean(axis = 1)
stdev = ndvi_res.iloc[:, 4:].std(axis = 1)
ndvi_res = pd.concat([ndvi_res, mean.rename('mean'), stdev.rename('stdev')], axis = 1)

'''
#copy over the rows and columns etc
smoothed_ndvi_df = pd.concat([ndvi_df[['row','col','tist', 'county']], smoothed_ndvi_df], axis = 1)

#get the rows and cols of array that the ss is referring to once ndvi is reshaped 
ss_cols = ss % 121 #this now more closely aligns with the date 
ss_rows = np.floor(ss[:,0] / 121) #gives the row of the dataframe that it corresponds to 
'''
#do NOT delete rows without enough data yet- makes it annoying to deal with loc instead of iloc 

#Save to CSV - writes indices to col 0
ndvi_res.to_csv('ndvi_residuals_'+county+'_V1.csv', encoding='utf-8', index=True)

'''
#Save the ss !!
with open(county+'_ss.pkl', 'wb') as file:
    # A new file will be created
    pickle.dump([ss, ss_rows, ss_cols], file)
'''

print('donezo')
