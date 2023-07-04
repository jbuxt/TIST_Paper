# For making maps generally

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt
from df_to_map import df_to_map

def longest_nan(s):
    nans = s.isnull().astype(int).groupby(s.notnull().astype(int).cumsum()).cumsum()
    return nans.max(), nans.idxmax()

ndvi = pd.read_csv('ndvi_pixels_Theraka.csv') #TEMP for testing , nrows=10000
# Calculate the number of missing 
ndvi['N_Missing']=ndvi.isna().sum(axis= 1)
ndvi[['Longest_Missing_Streak','StartDate_Longest_Missing']] = ndvi.apply(longest_nan, axis=1, result_type='expand')

img = df_to_map(ndvi, ['N_Missing', 'Longest_Missing_Streak'])


#make histograms
ndvi['N_Missing'].hist(by=ndvi['tist'], bins = range(0,100))
plt.title('Missing Months per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('number missing pixels')
plt.legend()
plt.savefig('./visuals/n_missing_tharaka.png')

ndvi['Longest_Missing_Streak'].hist(by=ndvi['tist'], bins=range(0,25))
plt.title('Longest Missing Streak per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('number missing pixels in longest streak')
plt.legend()
plt.savefig('./visuals/missing_streaks_tharaka.png')

ndvi['StartDate_Longest_Missing'].value_counts().plot(kind='bar')
# ndvi['StartDate_Longest_Missing'].hist(by=ndvi['tist'], bins=120)
plt.title('Start Date of Longest Missing Streak per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('start date of longest missing streak')
plt.legend()
plt.savefig('./visuals/start_date_missing_tharaka.png')

plt.figure()
plt.imshow(img[:,:, 0])
plt.title('N Missing Tharaka')
plt.colorbar()
plt.savefig('./visuals/n_missing_map_tharaka.png')

plt.figure()
plt.imshow(img[:,:, 1])
plt.title('Longest Missing Streak Tharaka')
plt.colorbar()
plt.savefig('./visuals/missing_streak_map_tharaka.png')
print('done')