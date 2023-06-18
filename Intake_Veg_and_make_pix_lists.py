# Maddie Henderson 
## 2023
## import tif files
## and put pixels into an object with info stored
## apply tist and county mask and mark pixels appropriately 
## and then put those pixels into separate lists 
## then save them for loading later 

# import pandas as pd 
# import folium 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import os
import pickle
from datetime import datetime as dt

#################################################
# Define pixel through time class 
#################################################
class Pix:

    def __init__(self, row, col, county, tist, first_ts_pt):
        self.row = row
        self.col = col
        self.county = county
        self.tist = tist
        self.ts = [first_ts_pt]

    def add(self, new_val):
        self.ts.append(new_val)
    

#################################################
# Import county and tist masks 
#################################################

with open('county_mask.pkl', 'rb') as file:
    county_mask= pickle.load(file)
    ## 0 = no county
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Kirinyaga (28) 
    ## 6 = Embu (29)
with open('tist_mask.pkl', 'rb') as file:
    tist_mask = pickle.load(file)
# plt.imshow(tist_mask)
# plt.show()

#################################################
# Import tifs 
#################################################

#start and end months we want to work with
#filenames are yyyyMMdd
#study time range is 2013 05 01 to 2023 04 01 inclusive
start_yr = 2013
end_yr = 2023

#Precipitation 
dirname = './GEE_Precip'
date_list = []
im_count = 0
#can really only do one at a time. CHANGE THIS and names to save to 
sel_county = 3
precip_pix = []
for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
            pass #don't have those times 
        else:
            im_count += 1
            date = str(y)+str(m).zfill(2)+'01'
            fname = date + '.tif'#files are named by the month 
            date = dt.strptime(date, '%Y%m%d')
            date_list.append(date)
            im = rs.open(os.path.join(dirname, fname))
            precip_meta = im.meta
            precip_bound = im.bounds
            im_array = np.float16(im.read(1)) #only one band in precip data - if wanted can specify band as read(1) to get 2d array
            #for precip data, don't care about 4 decimal places in mm per month
            # one or two decimals is fine
            im.close()
            # does float 16 work for ndvi? mayhaps
            # PRE_DEFINE THE LIST SIZE? or tell it what region to start looking in? 
            
            rows, cols = np.shape(im_array)
            p = 0 #pixel count 
            for i in range(rows):
                for j in range(cols):
                    if county_mask[i, j] == sel_county: #if it's inside a relevant county -- change this back to != 0 if do mult counties 
                        if im_count == 1: #this is the first image
                            #check that this is correct
                            x = Pix(i, j, sel_county, tist_mask[i,j], im_array[i, j])
                            precip_pix.append(x)
                            # x = Pix(self, row, col, county, tist, first_ts_pt)
                            # Create a Pix instance, initialize values 
                           

                        else: #not the first image processed
                            # just append the new timeseries value to the appropriate pixel 
                            precip_pix[p].add(im_array[i, j])
                            
                        p += 1
                    # else pass
                # end j
            # end i 
    #end m 
#end y 

#CHANGE FILE NAME
with open ('precip_pix_Tharaka.pkl', 'wb') as file:
    pickle.dump([precip_pix, precip_meta, precip_bound, date_list], file)
print('done with precip')                   

# now veg 


#Veg indices 
dirname = './GEE_Veg_new'
ndvi = np.array([])
msavi2 = np.array([])
for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
            pass
        else:
            fname = str(y)+str(m).zfill(2)+'01.tif'
            #files are named by the month 
            im = rs.open(os.path.join(dirname, fname))
            veg_meta = im.meta
            veg_bound = im.bounds
            array1 = im.read(1) #band 1 is ndvi 
            array2 = im.read(2) #band 2 msavi2
            # a, b = np.shape(array1)
            # array1 = np.reshape(array1, (1, a, b)) #make 3d since it's not when you select only 1 band
            pix1 = [array1[3000, 3000], array1[2000, 2000], array1[6000, 5000], array1[3000,6000]] 
            # array2 = np.reshape(array2, (1, a, b))
            pix2 = [array2[3000, 3000], array2[2000, 2000], array2[6000, 5000], array2[3000,6000]] 
            #damn i've forgotten how to do ANYTHING in python
            if np.size(ndvi) == 0:
                ndvi = pix1
                msavi2 = pix2
            else:
                ndvi= np.row_stack((ndvi, pix1)) #stack the frames through time
                msavi2 = np.row_stack((msavi2, pix2))
            im.close()
        # array size is frames, rows, columns  

# #################################################
# # Save to file for reloading in other scripts
# #################################################
del array1, array2

p0 = np.column_stack((precip[:, 0], ndvi[:, 0], msavi2[:, 0]))
p1 = np.column_stack((precip[:, 1], ndvi[:, 1], msavi2[:, 1]))
p2 = np.column_stack((precip[:, 2], ndvi[:, 2], msavi2[:, 2]))
p3 = np.column_stack((precip[:, 3], ndvi[:, 3], msavi2[:, 3]))

with open ('test_pix.pkl', 'wb') as file:
    pickle.dump([p0, p1, p2, p3, start_yr, end_yr, date_list], file)
print('done')