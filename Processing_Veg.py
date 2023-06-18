# Maddie Henderson 
## 2023
## import tif files and stack them into arrays 
## then save those arrays to be loaded again later 

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
start_yr = 2014
end_yr = 2015
start_mo = 1
end_mo = 12

#Precipitation 

dirname = './GEE_Precip'
precip = np.array([])
date_list = []
# for i in range(0, len(os.listdir(dirname))):
for y in range(start_yr, end_yr+1):
    for m in range(start_mo, end_mo +1):
    #to make sure they come in in order
        date = str(y)+str(m).zfill(2)+'01'
        fname = date + '.tif'#files are named by the month 
        date = dt.strptime(date, '%Y%m%d')
        date_list.append(date)
        im = rs.open(os.path.join(dirname, fname))
        precip_meta = im.meta
        precip_bound = im.bounds
        array = im.read() #only one band in precip data - if wanted can specify band as read(1)
        #damn i've forgotten how to do ANYTHING in python
        if np.size(precip) == 0:
            precip = array #because i don't know the size of the array already
        else:
            precip = np.concatenate((precip, array), axis = 0) #stack the frames 
        im.close()

with open ('imported_monthly_precip_14-15.pkl', 'wb') as file:
    pickle.dump([precip_meta, precip_bound, precip, date_list], file)

print('done')
##Veg indices 
# dirname = './GEE_Veg_new/GEE_Veg1' # EDIT THIS IF NEEDED
# ndvi = np.array([])
# msavi2 = np.array([])
# for y in range(start_yr, end_yr+1):
#     for m in range(start_mo, end_mo +1):

#         fname = str(y)+str(m).zfill(2)+'01.tif'
#         #files are named by the month 
#         im = rs.open(os.path.join(dirname, fname))
#         veg_meta = im.meta
#         veg_bound = im.bounds
#         array1 = im.read(1) #band 1 is ndvi 
#         array2 = im.read(2) #band 2 msavi2
#         a, b = np.shape(array1)
#         array1 = np.reshape(array1, (1, a, b)) #make 3d since it's not when you select only 1 band
#         array2 = np.reshape(array2, (1, a, b))
#         #damn i've forgotten how to do ANYTHING in python
#         if np.size(ndvi) == 0:
#             ndvi = array1
#             msavi2 = array2
#         else:
#             ndvi= np.concatenate((ndvi, array1), axis = 0) #stack the frames through time
#             msavi2 = np.concatenate((msavi2, array2), axis = 0)
#         # array size is frames, rows, columns  

# # #################################################
# # # Save to file for reloading in other scripts
# # #################################################

# with open ('imported_monthly_veg_14-15.pkl', 'wb') as file:
#     pickle.dump([veg_meta, veg_bound, ndvi, msavi2, start_yr, end_yr], file)


