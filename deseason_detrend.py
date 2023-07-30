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
#import pickle


# Load the veg data #############################################
county = input('Input the county to process: ')
# county = 'Tharaka'

ndvi_df = pd.read_csv('ndvi_pixels_'+county+'.csv') #TEMP for testing nrows

## Summary stats on the ndvi 
# print('total % pix missing: ', ndvi_df.isna().sum().sum() / (120*ndvi_df.shape[0])) #for all pix

nrows, dum = ndvi_df.shape
dates = pd.date_range(start='5/1/2013', periods=120, freq='MS')

#V1/V2 - find avg of months per pixel (only on orig data) 
avgs = pd.DataFrame(columns = range(1,13))
for m in range(1,13):
     mo = '-'+str(m).zfill(2)
     avgs.loc[:, m] = ndvi_df.filter(like=mo, axis=1).mean(axis = 1) #mean through each row across col 
#this is a stupid way to do it but i don't care
#make 10 years worth from May 2013 through APril 2023
all_avg = pd.concat([avgs.loc[:, 5:], avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs, avgs.loc[:, :4]], axis = 1)
all_avg = pd.concat([ndvi_df[['row','col','tist', 'county']], all_avg], axis = 1)
all_avg.columns = ndvi_df.columns

# V0 / V2
#interpolate up to 2 /1 missing points since a season is usually 3 months
ndvi_df.iloc[:, 4:].astype("float32").interpolate(method='linear', limit=1, axis = 1, limit_area='inside',  inplace= True)
# smoothed_ndvi_df = pd.concat([ndvi_df[['row','col','tist', 'county']], smoothed_ndvi_df], axis = 1)

#grab the slices that would matter for the tharaka recov periods oto get an estimate 
# r59 =  smoothed_ndvi_df.iloc[:, (59-5+4):(59+6+4)] #account for the 4 intro cols 
# print('% pix missing for r59: ', r59.isna().sum().sum() / (r59.size))
# r77 =  smoothed_ndvi_df.iloc[:, (77-5+4):(77+6+4)]
# print('% pix missing for r77: ', r77.isna().sum().sum() / (r77.size))
# r59.dropna(axis=0, thresh=9, inplace=True, ignore_index=False)
# print('% rows with more than 9 mo r59: ', r59.shape[0] )
# r77.dropna(axis=0, thresh=9, inplace=True, ignore_index=False)
# print('% rows with more than 9 mo r77: ', r77.shape[0])  

# Save a mask of the empty months for later AFTER the filling of 1 month
empty_mask =  ndvi_df.isna() #nan = true, not nan = false
# empty_orig_mask = ndvi_df.isna()

#Now fill the empty pix with the average established for that month for that pixel 
ndvi_df.mask(empty_mask, all_avg, inplace= True) #mask replaces values that are True (nan)
# only_filled = ndvi_df.mask(empty_orig_mask, all_avg)
### Get an example plot################
# plt.plot(dates, smoothed_ndvi_df.iloc[3000, 4:], 'r*', label='interpolated 1 month')
# plt.plot(dates, ndvi_df.iloc[3000, 4:], 'go', label='original')
# plt.plot(dates, filled.iloc[3000, 4:], 'b-', label='interpolated and filled with avgs')
# plt.plot(dates, only_filled.iloc[3000, 4:], 'c--', label = 'no interpolation, only filled with avgs')
# plt.title('Example: gap filling and temporary filling with averages')
# plt.xlabel('date')
# plt.ylabel('NDVI')
# plt.legend()
# plt.show()

ndvi_res = ndvi_df.copy()
ndvi_res.iloc[:, 4:] = 0


ndvi_array = np.array(ndvi_df.iloc[:, 4:].astype('float32'))


for i in ndvi_res.index:
    decomp = stl.robust_stl(ndvi_array[i, :], period = 12, smooth_length = 21)
    ndvi_array[i, :] = decomp.resid
    # decomp.plot()
    # plt.xticks(rotation=90)
    # plt.show()

ndvi_res.iloc[:, 4:] = ndvi_array.astype('float32')
    

###### Now remove the values that were originally nan and not interpolated
ndvi_res.mask(empty_mask, np.nan, inplace=True)

#find the mean and std dev of the residuals after decomposing 
mean = ndvi_res.iloc[:, 4:].mean(axis = 1)
stdev = ndvi_res.iloc[:, 4:].std(axis = 1)
ndvi_res = pd.concat([ndvi_res, mean.rename('mean'), stdev.rename('stdev')], axis = 1)


#do NOT delete rows without enough data yet- makes it annoying to deal with loc instead of iloc 

#Save to CSV - writes indices to col 0
ndvi_res.to_csv('ndvi_residuals_'+county+'_V2.csv', encoding='utf-8', index=True)


print('donezo')
