# Maddie Henderson 
## 2023
## import tif files
## and put pixels into an object with info stored
## apply tist and county mask and mark pixels appropriately 
## and then put those pixels into separate lists 
## then save them for loading later 

import pandas as pd 
# import folium 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import os
import pickle
from datetime import datetime as dt    

#################################################
# Import county and tist masks 
#################################################

with open('county_mask.pkl', 'rb') as file:
    county_mask= pickle.load(file)
    ## 0 = no county -- outside of ROI
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Kirinyaga (28) 
    ## 6 = Embu (29)
# Get lists of where each county is by index
# Lai_idx = np.argwhere(county_mask == 1)
# Mer_idx = np.argwhere(county_mask == 2)
# Tha_idx = np.argwhere(county_mask == 3)
Nye_idx = np.argwhere(county_mask == 4)
# Kir_idx = np.argwhere(county_mask == 5)
# Emb_idx = np.argwhere(county_mask == 6)

del county_mask #save space

with open('tist_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)


#################################################
# Import tifs 
#################################################

#start and end months we want to work with
#filenames are yyyyMMdd
#study time range is 2013 05 01 to 2023 04 01 inclusive
start_yr = 2013
end_yr = 2023

# #Number of pixels in each county: 
n_Laikipia = 10837687 
n_Meru = 7720270
n_Theraka = 2990072
n_Nyeri = 3733796
n_Kirinyaga = 1652252
n_Embu = 3170195

rows = 6871 #in total picture
cols = 8786

# n_ROI = 30104272 #all counties 
n_months = 120 

#Precipitation #####################################################3 
# dirname = './GEE_Precip'
date_list = pd.date_range(start='5/1/2013', periods=120, freq='MS')
col_names = ['row','col', 'tist', 'county']+([date.strftime('%Y-%m') for date in date_list])

'''
precip_df= pd.DataFrame(index=range(n_Theraka),columns=col_names)

im_count = 0

for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
            pass #don't have those times 
        else:
            im_count += 1
            print('im_count: ', im_count)
            date = str(y)+'-'+str(m).zfill(2) #Use this to match the column names in the dataframe
            fname = str(y)+str(m).zfill(2)+'01'+ '.tif'#files are named by the month 
            im = rs.open(os.path.join(dirname, fname))
            precip_meta = im.meta
            precip_bound = im.bounds
            im_array = np.float16(im.read(1)) 
            #for precip data, don't care about 4 decimal places in mm per month
            # one or two decimals is fine
            im.close()
            # does float 16 work for ndvi? mayhaps
            
            # rows, cols = np.shape(im_array)
            # p = 0 #pixel count 
            # for i in range(3000, 3050): #rows
            #     for j in range(5000, 5050): #cols
            for p in range(n_Theraka):
                i, j = Tha_idx[p] #go through the list indices of Meru points
                # j = ind[1]
                # if county_mask[i, j] != 0: #if it's in region of interest
                if im_count == 1: #this is the first image
                    #initialize the row with row, col, county, tist, and first timestep 
                    precip_df.at[p, 'row'] = i
                    precip_df.at[p, 'col'] = j
                    precip_df.at[p, 'county'] = 3 #county_mask[i, j] #CHANGE THIS per county
                    precip_df.at[p, 'tist'] = tist_mask[i, j]
                    precip_df.at[p, date] = im_array[i, j]
                    
                else: #not the first image processed
                    # add the timestep to the column based on date and the pixel based on pixel index
                    precip_df.at[p, date] = im_array[i, j]
                    
                # p += 1
                    
#save by county for easier processing 
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Kirinyaga (28) 
    ## 6 = Embu (29)

# with open('precip_Laikipia.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 1], precip_meta, precip_bound], f)

# with open('precip_Meru.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 2], precip_meta, precip_bound], f)

# with open('precip_Tharaka.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 3], precip_meta, precip_bound], f)

# with open('precip_Nyeri.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 4], precip_meta, precip_bound], f)
    
# with open('precip_Kirinyaga.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 5], precip_meta, precip_bound], f)

# with open('precip_Embu.pkl', 'wb') as f:
#     pickle.dump([precip_df.loc[precip_df['county'] == 6], precip_meta, precip_bound], f)

precip_df.to_csv('precip_pixels_Theraka.csv', encoding='utf-8', index=False)

# with open('precip_pixels_Theraka.pkl', 'wb') as file:
#     pickle.dump([precip_df, precip_meta, precip_bound], file)

print('done with precip theraka')                   
'''
# now veg 


# #Veg indices 
dirname = './GEE_Veg_new'
ndvi_df= pd.DataFrame(index=range(n_Nyeri),columns=col_names)

im_count = 0

for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
            pass #don't have those times 
        else:
            im_count += 1
            print('im_count: ', im_count)
            date = str(y)+'-'+str(m).zfill(2) #Use this to match the column names in the dataframe
            fname = str(y)+str(m).zfill(2)+'01'+ '.tif'#files are named by the month 
            im = rs.open(os.path.join(dirname, fname))
            ndvi_meta = im.meta
            ndvi_bound = im.bounds
            im_array = im.read(1) #1 is ndvi, 2 is msavi2
            # np.float16( --  probably fine, preserves 4 decimal places, but won't for now
            #CHECK float 16
            im.close()

            
            p = 0 #pixel count 
            for i in range(3000, 3050): #rows
                for j in range(5000, 5050): #cols
                    if county_mask[i, j] != 0: #if it's in region of interest
                        if im_count == 1: #this is the first image
                            #initialize the row with row, col, county, tist, and first timestep 
                            ndvi_df.at[p, 'row'] = i
                            ndvi_df.at[p, 'col'] = j
                            ndvi_df.at[p, 'county'] = county_mask[i, j]
                            ndvi_df.at[p, 'tist'] = tist_mask[i, j]
                            ndvi_df.at[p, date] = im_array[i, j]
                           
                        else: #not the first image processed
                            # add the timestep to the column based on date and the pixel based on pixel index
                            ndvi_df.at[p, date] = im_array[i, j]
                            
                        p += 1
                    # else pass
                # end j
            # end i 
    #end m 
#end y 


# with open('ndvi_pixels_sample.pkl', 'wb') as file:
#     pickle.dump([ndvi_meta, ndvi_bound], file)

ndvi_df.to_csv('ndvi_pixels_Nyeri.csv', encoding='utf-8', index=False)

print('done with ndvi for Nyeri')                   
