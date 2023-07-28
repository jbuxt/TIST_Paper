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

with open('county_mask.pkl', 'rb') as file:
    county_mask= pickle.load(file)
    ## 0 = no county -- outside of ROI
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)

#IMPORT ECOREGIONS AND LANDCOVER MASK -- not used until later rn 
#landcover_mask
# with open('landcover_mask.pkl', 'rb') as file:
#     landcover_mask = pickle.load(file)
# #ecoregion_mask
# with open('ecoregion_mask.pkl', 'rb') as file:
#     ecoregion_mask = pickle.load(file)

# Get lists of where each county is by index AND where landcover <= 40 
#only keeping grassland, shrubland, cropland, and forest
#not sure if this works or need to do in 2 steps 
county_idx = np.argwhere(county_mask == county_int) #and (landcover_mask <= 40))

del county_mask #save space

with open('tist_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)


#################################################
# Import tifs 
#################################################

#start and end months we want to work with
#filenames are yyyyMMdd
#study time range is 2013 05 01 to 2023 04 30 inclusive
start_yr = 2013
end_yr = 2023

# #Number of pixels in each county: 
# n_Laikipia = 10837687 
# n_Meru = 7720270
# n_Theraka = 2990072
# n_Nyeri = 3733796
# n_Kirinyaga = 1652252
# n_Embu = 3170195

rows = 6871 #in total picture
cols = 8786

# n_ROI = 30104272 #all counties 
n_months = 120 

n_county, dummy = np.shape(county_idx)

#Precipitation #####################################################
#NOT DOING PRECIP ANYMORE AT LEAST RIGHT NOW 
# dirname = './GEE_Precip'
date_list = pd.date_range(start='5/1/2013', periods=n_months, freq='MS') 
col_names = ['row','col', 'tist', 'county']+([date.strftime('%Y-%m') for date in date_list])
# col_names = ['row','col', 'tist', 'county', 'landcover', 'ecoregion']+([date.strftime('%Y-%m') for date in date_list])

# precip_df= pd.DataFrame(index=range(n_county),columns=col_names)

# im_count = 0

# for y in range(start_yr, end_yr+1):
#     for m in range(1, 13):
#         if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
#             pass #don't have those times 
#         else:
#             im_count += 1
#             print('im_count: ', im_count)
#             date = str(y)+'-'+str(m).zfill(2) #Use this to match the column names in the dataframe
#             fname = str(y)+str(m).zfill(2)+'01'+ '.tif'#files are named by the month 
#             im = rs.open(os.path.join(dirname, fname))
#             precip_meta = im.meta
#             precip_bound = im.bounds
#             im_array = np.float16(im.read(1)) 
#             #for precip data, don't care about 4 decimal places in mm per month
#             # one or two decimals is fine
#             im.close()
            
#             for p in range(n_county):
#                 i, j = county_idx[p] #go through the list indices of county points

#                 if im_count == 1: #this is the first image
#                     #initialize the row with row, col, county, tist, and first timestep 
#                     precip_df.at[p, 'row'] = i
#                     precip_df.at[p, 'col'] = j
#                     precip_df.at[p, 'county'] = county_int #county_mask[i, j] 
#                     precip_df.at[p, 'tist'] = tist_mask[i, j]
#                     precip_df.at[p, date] = im_array[i, j]
                    
#                 else: #not the first image processed
#                     # add the timestep to the column based on date and the pixel based on pixel index
#                     precip_df.at[p, date] = im_array[i, j]


# precip_df.to_csv('precip_pixels_'+county+'.csv', encoding='utf-8', index=False)

# with open('precip_meta.pkl', 'wb') as file:
#     pickle.dump([precip_meta, precip_bound], file)

# print('done with precip for '+ county)                   

# now veg #####################################################################


# #Veg indices 
dirname = './GEE_Veg_new'
ndvi_df= pd.DataFrame(index=range(n_county),columns=col_names)

im_count = 0

for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2015) and (m < 7)) or ((y == 2023) and (m > 6)):
            pass #don't have those times 
        else:
            im_count += 1
            print('im_count: ', im_count)
            date = str(y)+'-'+str(m).zfill(2) #Use this to match the column names in the dataframe
            fname = str(y)+str(m).zfill(2)+'01'+ '.tif'#files are named by the month 
            im = rs.open(os.path.join(dirname, fname))
            ndvi_meta = im.meta
            ndvi_bound = im.bounds
            im_array = im.read(1) #only band is ndvi

            im.close()

            for p in range(n_county): #pixels
                i, j = county_idx[p]
                    
                if im_count == 1: #this is the first image
                    #initialize the row with row, col, county, tist, and first timestep 
                    ndvi_df.at[p, 'row'] = i
                    ndvi_df.at[p, 'col'] = j
                    ndvi_df.at[p, 'county'] = county_int
                    ndvi_df.at[p, 'tist'] = tist_mask[i, j]
                    # ndvi_df.at[p, 'landcover'] = landcover_mask[i, j]
                    # ndvi_df.at[p, 'ecoregion'] = ecoregion_mask[i, j]
                    ndvi_df.at[p, date] = im_array[i, j]
                    
                else: #not the first image processed
                    # add the timestep to the column based on date and the pixel based on pixel index
                    ndvi_df.at[p, date] = im_array[i, j]


with open('ndvi_meta.pkl', 'wb') as file:
    pickle.dump([ndvi_meta], file)

ndvi_df.to_csv('ndvi_pixels_'+county+'.csv', encoding='utf-8', index=False)

print('done with ndvi for '+county)                   
