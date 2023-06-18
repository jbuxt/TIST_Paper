#Clip the veg and precip to the counties and save

import pickle
import geopandas as gp 
import rasterio as rs
from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
import numpy.ma as ma 


# #Load the veg and precip data as well as the relevant counties and groves
# with open ('imported_monthly_veg_14-15.pkl', 'rb') as f:
#     veg_meta, veg_bound, ndvi, msavi2, start_yr, end_yr = pickle.load(f)

with open ('imported_monthly_precip_14-15.pkl', 'rb') as f:
    precip_meta, precip_bound, precip, date_list = pickle.load(f)

# with open('relevant_tist.pkl', 'rb') as file:
#     TIST = pickle.load(file)

with open('relevant_counties.pkl', 'rb') as file:
    counties = pickle.load(file)

#####################################################
# Make an outline of the entire study area 
counties['roi_col'] = 1
roi = counties.dissolve(by='roi_col')

# counties.plot()
# roi.plot()
# plt.show()
######################################################
#clip the veg data to roi 


# Create an np array mask of the counties 
county_mask = features.rasterize(
    ## The numbers in mask correspond to counties as follows
    ## 0 = no county
    ## 1 = Laikipia (14) 
    ## 2 = Meru (16)
    ## 3 = Tharaka (22) 
    ## 4 = Nyeri (25)
    ## 5 = Kirinyaga (28) 
    ## 6 = Embu (29)
             [(counties.loc[14, 'geometry'], 1), (counties.loc[16, 'geometry'], 2),
               (counties.loc[22, 'geometry'], 3), (counties.loc[25, 'geometry'], 4),
               (counties.loc[28, 'geometry'], 5), (counties.loc[29, 'geometry'], 6),],
            out_shape=precip[0,:,:].shape,
            transform=precip_meta['transform'],
            all_touched = True)

plt.imshow(county_mask)
plt.show()

with open ('county_mask.pkl', 'wb') as file:
    pickle.dump(county_mask, file)

TIST_mask = features.rasterize(
    ## make a mask of all pixels in TIST groves
            TIST.geometry,
            out_shape=precip[0,:,:].shape,
            transform=precip_meta['transform'],
            all_touched = True)
plt.imshow(TIST_mask)
plt.show()

## Get rid of precip values outside the counties of interest 
outside = ma.make_mask(county_mask)
tist_not = ma.make_mask(TIST_mask)
precip = precip * tist_not
# ndvi = ndvi * outside
# msavi2 = msavi2*outside

plt.imshow(precip[5, :,:])
plt.show()
# # plt.imshow(ndvi[5, :,:])
# plt.show()



# with open ('clipped_precip_14-15.pkl', 'wb') as file:
#     pickle.dump([precip_meta, precip_bound, precip, date_list], file)

# with open ('clipped_veg_14-15.pkl', 'wb') as file:
#     pickle.dump([veg_meta, veg_bound, ndvi, msavi2, start_yr, end_yr], file)

with open ('TIST_mask.pkl', 'wb') as file:
    pickle.dump(TIST_mask, file)


print('done')
