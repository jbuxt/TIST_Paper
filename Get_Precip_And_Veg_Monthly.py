## Maddie Henderson 
## 2023
## basic pre-process and download from GEE to Google Drive

import pandas as pd 
# from IPython.display import display
#import folium 
import ee
import google.auth
import matplotlib.pyplot as plt
from geetools import batch

credentials, project_id = google.auth.default()
ee.Initialize(credentials, project='ee-maddiehenderson12')

## createshapes 
#Get a rectangle that encompasses the region of interest
ROI = ee.Geometry.Rectangle([37.418438390871614, -0.46499883273351506, 38.291851476809114, 0.4303777575597561])
box_col = ee.FeatureCollection([ROI])

# task = batch.Export.table.toDriveShapefile(collection = box_col, folder='Shape_FINAL')


# ##################################
# # FUNCTIONS
# #################################/
# clip to area
def clip_img(image):
    return image.clip(ROI)

# calculate and add an NDVI band
def addNDVI(image):
    return image.addBands(image.normalizedDifference(['B8', 'B4'])\
                          .rename('NDVI')).copyProperties(image, ['system:time_start'])
#B8 is surface reflectance near infrared, B4 is red sentinel


# Mask clouds on sentinel 
def maskS2clouds(image):
  # Bits 10 and 11 are clouds
  cloudsBitMask = (1<<10) #ee.Number(2).pow(3).int()# 1000 in base 2
  cirrusCloudBitMask = (1<<11)

  # Get the pixel QA band
  qa = image.select('QA60')

  # Both flags should be set to zero, indicating clear conditions
  mask = qa.bitwiseAnd(cloudsBitMask).eq(0).And(
      qa.bitwiseAnd(cirrusCloudBitMask).eq(0))

  return image.updateMask(mask).divide(10000).copyProperties(image, ['system:time_start'])

def mask_col(image):
    return image.updateMask(crop_mask)

#create monthly max from input image collection 
def monthlyMax(collection, yrs, mos):
    maxes = []
    for year in yrs:
        for mo in mos: #this part is still good 
            #sum each pixel over the month
            month_max = collection.filter(ee.Filter.calendarRange(year, year, 'year'))\
                                  .filter(ee.Filter.calendarRange(mo, mo, 'month'))\
                                  .max()\
                                  .set({'month': mo, 
                                        'year': year, 
                                        'system:time_start': ee.Date.fromYMD(year, mo, 1).millis()})\
                                   .setDefaultProjection('EPSG:32635', [10,0,499980,0,-10,8200020])
            maxes.append(month_max) #list of images of each month

    img_col = ee.ImageCollection.fromImages(maxes)

    return img_col 

def reduce(image):
    return image.reduceResolution(reducer= ee.Reducer.mean(),
    #Force the next reprojection to aggregate instead of resampling.
            maxPixels=20) # reducing 4 pix to one)

##############################
# VIS PARAMS
##############################

###################################
#Begin
###################################

start_date = '2015-12-01' #inclusive
end_date = '2017-01-01' #exclusive
#get to 2023 07 01
startyr = 2015
endyr = 2017
mos = range(1,13)
yrs = range(startyr, endyr)

###############################################################################   
#ADD NDVI and GET MONTHLY VALUES     

#Import Sentinel 2, mask clouds
s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterDate(start_date, end_date)\
    .map(clip_img).map(maskS2clouds)
 


landcover = ee.ImageCollection("ESA/WorldCover/v100").first().clip(ROI)
''''type': 'Image', 'bands': [{'id': 'Map', 'data_type': {'type': 'PixelType', 'precision': 'int', 'min': 0, 'max': 255}, 'dimensions': [10483, 10747], 'origin': [2609020, 1002834], 'crs': 'EPSG:4326', 'crs_transform': [8.333333333333333e-05, 0, -180, 0, -8.333333333333333e-05, 84]}], 'version': 1685065671563344, 'id': 'ESA/WorldCover/v100/2020', 'properties': {'system:footprint': {'type': 'Polygon', 'coordinates': [[[37.418438390871614, -0.46499883273351506], [38.291851476809114, -0.46499883273351506], [38.291851476809114, 0.4303777575597561], [37.418438390871614, 0.4303777575597561], [37.418438390871614, -0.46499883273351506]]]},'''
crop_mask = landcover.lte(40)
'''crop_mask : {'type': 'Image', 'bands': [{'id': 'Map', 'data_type': 
{'type': 'PixelType', 'precision': 'int', 'min': 0, 'max': 1}, 
'dimensions': [10483, 10747], 'origin': [2609020, 1002834], 'crs': 'EPSG:4326', 
'crs_transform': [8.333333333333333e-05, 0, -180, 0, -8.333333333333333e-05, 84]}]}'''

ndvi = s2.map(addNDVI).select('NDVI').map(mask_col) # up to here is fine for values
#get rid of anything land type wise unwanted

#taken monthly maximums of NDVI as additional filter

#need to specify the scale because it doesn't automatically keep that 
# for sentinel2, the scale is 10 m and projection is epsg 32628
veg = monthlyMax(ndvi, yrs, mos) #printing this deadlocks 
''' [{'id': 'NDVI', 'data_type': {'type': 'PixelType', 'precision': 'float', 'min': -1, 'max': 1}, 'crs': 'EPSG:32635', 'crs_transform': [10, 0, 499980, 0, -10, 8200020]'''
veg_30m = veg.map(reduce) #take mean of pixels to get desired res
#START HERE
tasks = batch.Export.imagecollection.toDrive(collection=veg_30m, 
                                             folder='GEE_Veg_S2_20m', 
                                             namePattern= '{system_date}',
                                             region=ROI, scale=20, #reduce by 1/2 for memory purposes
                                             crs = 'EPSG:4326',
                                             datePattern='yyyyMMdd') 


print('donezo')