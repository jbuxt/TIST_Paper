#take a few lists of pixels and deseason and detrend 

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
import numpy.ma as ma 


with open ('precip_pixels_sample.pkl', 'rb') as file:
    precip_df, precip_meta, precip_bound = pickle.load(file)

with open ('ndvi_sample_res.pkl', 'rb') as file:
    ndvi_res, ndvi_meta, ndvi_bound = pickle.load(file)


pix =  ndvi_res.iloc[27].filter(like='20') #get one sample
precip = precip_df.iloc[27].filter(like='20')
fig, host = plt.subplots()
ax2 = host.twinx()
host.set_xlabel('date')
host.set_ylabel('NDVI')
ax2.set_ylabel('monthly precip mm/mo')
p1 = host.plot(pix, 'r-', label='ndvi')
p2 = host.plot(precip, 'b*', label='monthly precip mm')
host.legend()
# plt.xticks(rotation=90)
host.autofmt_xdate()
plt.show()
print('done')
