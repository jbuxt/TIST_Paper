# Maddie Henderson 
## 2023
## import tif files
## and put pixels into a df through time
## apply tist, and county mask and mark pixels appropriately 
## and then put those pixels into separate dfs and save for later 
## DIFFERENCE: This is for working with the 8day modis+landsat composites 
## these files instead of being one tif with one layer for the ndvi for that month
## is instead a tif for the year with 46 bands, each of which correspods to an 8day composite

import pandas as pd 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import os
import pickle
# from datetime import datetime as dt    

#################################################
# Import masks 
#################################################
county = input('Input the county to process: ')
# county = 'Nyeri'
if county == 'Laikipia':
    county_int = 1
elif county == 'Meru':
    county_int = 2
elif county == 'Tharaka':
    county_int = 3
elif county == 'Nyeri':
    county_int = 4
elif county == 'Embu':
    county_int = 5
else: 
    print('incorrect county entered')
    #program will crash later lol

#CHANGE: Have to make new mask i think to deal with new shape
with open('county_mask.pkl', 'rb') as file:
    county_mask= pickle.load(file)
    ## 0 = no county -- outside of ROI
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Embu
with open('tist_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)

# landcover_mask
with open('landcover_mask.pkl', 'rb') as file:
    landcover_mask = pickle.load(file)
#ecoregion_mask
with open('eco_mask.pkl', 'rb') as file:
    ecoregion_mask = pickle.load(file)

# Get lists of where each county is by index AND where landcover <= 40 
#only keeping grassland, shrubland, cropland, and forest
#not sure if this works or need to do in 2 steps 
#county_idx = np.argwhere(county_mask == county_int) #and (landcover_mask <= 40))
lc_in_county = landcover_mask*(county_mask == county_int)
lc_in_county_40 = lc_in_county*(lc_in_county<=40) #get only the landcover types we care about 
final_idx = np.argwhere(lc_in_county_40 != 0) #index of pixels with lc <=40 in the specified county


del county_mask, lc_in_county_40, lc_in_county#save space


#################################################
# Import tifs 
#################################################

#start and end months we want to work with
#filenames are yyyy - with 46 bands 
#study time range is 2013 05 01 to 2023 04 30 inclusive
start_yr = 2013
end_yr = 2023

# #Number of pixels in each county: (CHANGE)
# n_Laikipia = 10837687 
# n_Meru = 7720270
# n_Theraka = 2990072
# n_Nyeri = 3733796
# n_Kirinyaga = 1652252
# n_Embu = 3170195

# rows = 6871 #in total picture (CHANGE)
# cols = 8786

# n_ROI = 30104272 #all counties - CHANGE 
n_8days = 46*10 #CHANGE THIS _ WILL BE LESS 

n_county, dummy = np.shape(final_idx)

# date_list = pd.date_range(start='5/1/2013', periods=n_months, freq='MS') 
col_names = ['row','col', 'tist', 'county']
# col_names = ['row','col', 'tist', 'county', 'landcover', 'ecoregion']+([date.strftime('%Y-%m') for date in date_list])

# now veg #####################################################################


dirname = './GEE_ls_and_modis'
#ndvi_df= pd.DataFrame(index=range(n_county),columns=range(n_8days))
ndvi_df= pd.DataFrame(0, index=range(10000),columns=col_names+list(range(n_8days)), dtype = 'int') #TEMPORARY FOR TESTING: n_county

im_count = 0
layer_count = 0
for y in range(start_yr, end_yr+1):

    im_count += 1
    print('im_count: ', im_count)
    #fname = str(y)+'.tif'#files are named by year (hopefully) 
    fname = 'ndvi_8day_2016_tiny.tif'
    im = rs.open(os.path.join(dirname, fname))
    ndvi_meta = im.meta
    ndvi_bound = im.bounds
    im_array = im.read() #returns 3d matrix. 
    #Normally python is row, col, depth. This gives layer, row, col 
    # so have to think about that 
    im.close()

    layers, rows, cols = im_array.shape
    #so for one pixel through time, need 
    p = 0
    for i in range(rows): #TEMPORARY for tiny tif
        for j in range(cols):
    #for p in range(n_county): # number pixels in this county 
            # i, j = final_idx[p] #TEMPORARY
                
            if im_count == 1: #this is the first image
                #initialize the row with row, col, county, tist, and first timestep 
                ndvi_df.loc[p, 'row'] = int(i)
                ndvi_df.loc[p, 'col'] = int(j)
                ndvi_df.loc[p, 'county'] = int(county_int)
                ndvi_df.loc[p, 'tist'] = int(tist_mask[i, j])
                ndvi_df.loc[p, 'landcover'] = landcover_mask[i, j]
                ndvi_df.loc[p, 'ecoregion'] = ecoregion_mask[i, j]
                ndvi_df.iloc[p,4+layer_count:4+layer_count+layers] = im_array[:, i, j]#this is a list that is layers long
                #put the timeseries eg if this is first image 4+0 to 4+0+layers
                #second image 4+46 to 4+46+46
                
            else: #not the first image processed
                # add the timestep to the column based on date and the pixel based on pixel index
                ndvi_df.iloc[p,4+layer_count:4+layer_count+layers] = im_array[:, i, j]
            p+=1 #TEMPORARY

    layer_count = layer_count + layers

# with open('ndvi_meta.pkl', 'wb') as file:
#     pickle.dump([ndvi_meta], file)

ndvi_df.to_csv('ndvi_pixels_'+county+'_8day.csv', encoding='utf-8', index=True)

print('done with ndvi for '+county)                   
