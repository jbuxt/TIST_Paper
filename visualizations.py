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

ndvi = pd.read_csv('ndvi_pixels_Theraka.csv', nrows=10000) #TEMP for testing 
ndvi['N_Missing']=ndvi.isna().sum(axis= 1)
ndvi[['Longest_Missing_Streak','StartDate_Longest_Missing']] = ndvi.apply(longest_nan, axis=1, result_type='expand')

img = df_to_map(ndvi, ['N_Missing', 'Longest_Missing_Streak'])
#make histogram 
ndvi['N_Missing'].hist(by=ndvi['tist'], bins = range(0,100))
plt.title('Missing Months per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('number missing pixels')
plt.legend()
plt.show()

ndvi['Longest_Missing_Streak'].hist(by=ndvi['tist'], bins=range(0,25))
plt.title('Longest Missing Streak per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('number missing pixels in longest streak')
plt.legend()
plt.show()

ndvi['StartDate_Longest_Missing'].value_counts().plot(kind='bar')
# ndvi['StartDate_Longest_Missing'].hist(by=ndvi['tist'], bins=120)
plt.title('Start Date of Longest Missing Streak per Pixel (Tharaka)')
plt.ylabel('count')
plt.xlabel('start date of longest missing streak')
plt.legend()
plt.show()

plt.subplot(2,1,1).imshow(img[:,:, 0])
plt.title('N_Missing')
plt.subplot(2,1,2).imshow(img[:,:, 1])
plt.title('Longest_Missing_Streak')
plt.show()
print('done')