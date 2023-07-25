#Make masks out of shp files and save them for applying in Intake Veg and make pix lists

import pickle
import geopandas as gp 
import rasterio as rs
from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
#import numpy.ma as ma 


with open('relevant_tist.pkl', 'rb') as file:
    TIST = pickle.load(file)

with open('relevant_counties.pkl', 'rb') as file:
    counties = pickle.load(file)

with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bound = pickle.load(file)

im = rs.open('ecoregions_rasterized.tif')
ecoregion = im.read(1)
eco_meta = im.meta
plt.imshow(ecoregion)

im = rs.open('landcover_WorldCoverv100_reprojected.tif')
landcover= im.read(1)
landcover_meta = im.meta
plt.imshow(landcover)

with open ('ecoregion_mask.pkl', 'wb') as file:
    pickle.dump(ecoregion, file)

with open ('landcover_mask.pkl', 'wb') as file:
    pickle.dump(landcover, file)

#####################################################
# Make an outline of the entire study area 
# counties['roi_col'] = 1
# roi = counties.dissolve(by='roi_col')


# counties.plot()
# roi.plot()
# plt.show()
######################################################
# Create an np array mask of the counties 
county_mask = features.rasterize(
    ## The numbers in mask correspond to counties as follows
    ## 0 = no county
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Embu (29)

             [(counties.loc[0, 'geometry'], 1), (counties.loc[1, 'geometry'], 2),
               (counties.loc[2, 'geometry'], 3), (counties.loc[3, 'geometry'], 4),
               (counties.loc[5, 'geometry'], 5)],
            out_shape=[int(veg_meta['height']), int(veg_meta['width'])],
            transform=veg_meta['transform'],
            all_touched = True)

plt.imshow(county_mask)
plt.show()
# rows = 6871 #in total picture
# cols = 8786
with open ('county_mask.pkl', 'wb') as file:
    pickle.dump(county_mask, file)

TIST_mask = features.rasterize(
    ## make a mask of all pixels in TIST groves
            TIST.geometry,
            out_shape=[veg_meta['height'], veg_meta['width']],
            transform=veg_meta['transform'],
            all_touched = True)
plt.imshow(TIST_mask)
plt.show()

## Get rid of precip values outside the counties of interest 
# outside = ma.make_mask(county_mask)
# tist_not = ma.make_mask(TIST_mask)
# precip = precip * tist_not

with open ('TIST_mask.pkl', 'wb') as file:
    pickle.dump(TIST_mask, file)




print('done')
