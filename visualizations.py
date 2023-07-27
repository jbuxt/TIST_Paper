# For making maps generally
# And also for assessing number of missing pixels 

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt
from df_to_map import df_to_map
import pickle

def longest_nan(s):
    nans = s.isnull().astype(int).groupby(s.notnull().astype(int).cumsum()).cumsum()
    return nans.max(), nans.idxmax()

with open('veg_meta.pkl', 'rb') as file:
    ndvi_meta, ndvi_bound =pickle.load(file)

county = input('Input the county to process: ')
ndvi = pd.read_csv('ndvi_pixels_'+county+'.csv') #TEMP for testing , nrows=10000
# Calculate the number of missing 
ndvi['Pct_Missing']=ndvi.isna().sum(axis= 1).divide(120)
ndvi[['Longest_Missing_Streak','StartDate_Longest_Missing']] = ndvi.apply(longest_nan, axis=1, result_type='expand')

img = df_to_map(ndvi, ['N_Missing', 'Longest_Missing_Streak'], savefile=True, 
                fname='ndvi_missing_'+county+'.tif', meta=ndvi_meta)


#make histograms
# ndvi['N_Missing'].hist( bins = range(0,100)) #by=ndvi['tist'],
# plt.title('Missing Months per Pixel ('+county+')')
# plt.ylabel('count of pixels')
# plt.xlabel('Number missing months')
# plt.legend()
# plt.savefig('./visuals/n_missing_'+county+'.png')

# ndvi['Longest_Missing_Streak'].hist( bins=range(0,25)) #by=ndvi['tist'],
# plt.title('Longest Missing Streak per Pixel ('+county+')')
# plt.ylabel('count')
# plt.xlabel('number missing pixels in longest streak')
# plt.legend()
# plt.savefig('./visuals/missing_streaks_'+county+'.png')

# ndvi['StartDate_Longest_Missing'].value_counts().plot(kind='bar')
# # ndvi['StartDate_Longest_Missing'].hist(by=ndvi['tist'], bins=120)
# plt.title('Start Date of Longest Missing Streak per Pixel ('+county+')')
# plt.ylabel('count')
# plt.xlabel('start date of longest missing streak')
# plt.legend()
# plt.savefig('./visuals/start_date_missing_'+county+'.png')

# plt.figure()
# plt.imshow(img[:,:, 0])
# plt.title('N Missing '+county)
# plt.colorbar()
# plt.savefig('./visuals/n_missing_map_'+county+'.png')

# plt.figure()
# plt.imshow(img[:,:, 1])
# plt.title('Longest Missing Streak '+county)
# plt.colorbar()
# plt.savefig('./visuals/missing_streak_map_'+county+'.png')
print('done')

## Summary stats on the ndvi 
# print('total % pix missing: ', ndvi.isna().sum().sum() / (120*ndvi.shape[0])) #for all pix

# how many pixels are missing by month generally
# for m in range(1,13):
#     mo = '-'+str(m).zfill(2)
#     missing = ndvi.filter(like=mo, axis=1).isna().sum().sum() #number of missing for that month over the 10 years
#     print(mo, ' missing % : ', missing/(2500*10))