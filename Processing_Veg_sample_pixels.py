# Maddie Henderson 
## 2023
## import tif files and stack them into arrays, choosing only a few sample pixels 
## then save them for loading later 

import pandas as pd 
import folium 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import os
import pickle
import Import_saved_files as ws
from datetime import datetime as dt

#################################################
# Import from tif file 
#################################################
#start and end months we want to work with
#filenames are yyyyMMdd
#study time range is 2013 05 01 to 2023 04 01 inclusive
start_yr = 2013
end_yr = 2023

### Random pixels to use as tests 
# 1 : 3000,3000
# 2:  (3000, 6000) (might be vv, check?)
#3: (6000, 5000)
# 4: (2000, 2000)


#Precipitation 
dirname = './GEE_Precip'
precip = np.array([])
date_list = []
# for i in range(0, len(os.listdir(dirname))):
for y in range(start_yr, end_yr+1):
    for m in range(1, 13):
        if ((y == 2013) and (m < 5)) or ((y == 2023) and (m > 4)):
            pass
        else:
            #to make sure they come in in order
            date = str(y)+str(m).zfill(2)+'01'
            fname = date + '.tif'#files are named by the month 
            date = dt.strptime(date, '%Y%m%d')
            date_list.append(date)
            im = rs.open(os.path.join(dirname, fname))
            precip_meta = im.meta
            precip_bound = im.bounds
            array = im.read(1) #only one band in precip data - if wanted can specify band as read(1)
            pix = [array[3000, 3000], array[2000, 2000], array[6000, 5000], array[3000,6000]] # get 4 test pixels
            #damn i've forgotten how to do ANYTHING in python
            if np.size(precip) == 0:
                precip = pix #because i don't know the size of the array already
            else:
                precip = np.row_stack((precip, pix)) #stack the frames 
            im.close()

del array
# now have precip that is columns of each pixel through time. will take


#Veg indices 
dirname = './GEE_Veg_new' # EDIT THIS IF NEEDED
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