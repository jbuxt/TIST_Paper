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
# ee.Authenticate()
# ee.Initialize()
credentials, project_id = google.auth.default()
ee.Initialize(credentials, project='ee-maddiehenderson12')

## createshapes 
#Get a rectangle that encompasses the region of interest
ROI = ee.Geometry.Rectangle([36.11092694867859, -0.9639821313886587, 38.47870637456082, 0.8877151637669112])
box_col = ee.FeatureCollection([ROI])

task = batch.Export.table.toDriveShapefile(collection = box_col, folder='Shape_FINAL')


# ##################################
# # FUNCTIONS
# #################################/
# clip to area
def clip_img(image):
    return image.clip(ROI)

# calculate and add an NDVI band
def addNDVI(image):
    return image.addBands(image.normalizedDifference(['B8', 'B4']).rename('NDVI'))
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

  return image.updateMask(mask).divide(10000)

# # method for adding earth engine image tiles to folium map
# def add_ee_layer(self, ee_image_object, vis_params, name):
#     map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
#     folium.raster_layers.TileLayer(
#         tiles=map_id_dict['tile_fetcher'].url_format,
#         attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
#         name=name,
#         overlay=True,
#         control=True
#     ).add_to(self)

# Add Earth Engine drawing method to folium.
# folium.Map.add_ee_layer = add_ee_layer 

# #create monthly totals from input image collection and convert to DF
# def monthlySum(collection, yrs, mos, geom, scale):
#     totals_imgs = []
#     # totals_arr = []
#     for year in yrs:
#         for mo in mos: 
#             #Creates an image that is reduced for the month
#             month_sum = collection.filter(ee.Filter.calendarRange(year, year, 'year'))\
#                                   .filter(ee.Filter.calendarRange(mo, mo, 'month'))\
#                                   .sum()\
#                                   .set({'month': mo, 
#                                         'year': year, 
#                                         'system:time_start': ee.Date.fromYMD(year, mo, 1).millis()})
#             #add that image to the list
#             totals_imgs.append(month_sum) #list of images 
#             #convert that image to array and append to the array 
#             #very convoluted way - make image collection from single image
#             #then use the get region to turn it into a lat,lon, time, bands array
#     #Return image collection        
#     img_col = ee.ImageCollection.fromImages(totals_imgs)

#     return img_col

#create monthly max from input image collection 
def monthlyMax(collection, yrs, mos):
    maxes = []
    for year in yrs:
        for mo in mos: 
            #sum each pixel over the month
            month_max = collection.filter(ee.Filter.calendarRange(year, year, 'year'))\
                                  .filter(ee.Filter.calendarRange(mo, mo, 'month'))\
                                  .max()\
                                  .set({'month': mo, 
                                        'year': year, 
                                        'system:time_start': ee.Date.fromYMD(year, mo, 1).millis()})
            maxes.append(month_max) #list of images of each month

    img_col = ee.ImageCollection.fromImages(maxes)

    return img_col 

##############################
# VIS PARAMS
##############################
# precipitationVis = {
#   'min': 1.0,
#   'max': 17.0,
#   'palette': ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000'],
# }

# ndviVis = {
#   'min': -1, 
#   'max': 1, 
#   'palette': ['blue', 'white', 'green'] # sets the color ramp for displaying it 
# }

# rgbVis = {
#  'bands': ['SR_B4', 'SR_B3', 'SR_B2'], # these are the RGB layers for landsat
#   'min': 0.0,
#   'max': 0.3
# }

###################################
#Begin
###################################

start_date = '2015-07-01' #inclusive
end_date = '2016-01-01' #exclusive
#get to 2023 07 01
startyr = 2015
endyr = 2016
# yrs = ee.List.sequence(startyr, endyr)
mos = range(1,13)
yrs = [2015]
'''
# ADD chirps precip data 
dataset = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY').filterDate(start_date, end_date)
precipitation = dataset.select('precipitation').map(clip_img)
# clipped = dataset.map(lambda image: image.clip(box))
#select median image for simplicity for display
# my_map.add_ee_layer(precipitation.median(), precipitationVis, 'Precipitation')

#get image collection or the dataframe out 
precip = monthlySum(precipitation, yrs, mos, box, 30) 
#scale is 5566m because native resolution -  could upsample to get at the same 30m as landsat? 
tasks = batch.Export.imagecollection.toDrive(collection= precip, 
                                             folder='GEE_Precip', 
                                             namePattern= '{system_date}',
                                             region=box, scale=30,
                                             crs = 'EPSG:4326',
                                             datePattern='yyyyMMdd')


# precip_poi = monthlyPrecip_img.getRegion(box, 5566).getInfo() #this is a list
# precip_df_from_img= pd.DataFrame(precip_poi)
# precip_df_from_img = pd.DataFrame(precip_df_from_img.values[1:], columns=headers)

#id, longitude, latitude, time, precipitation
# Convert the time field into a datetime as additional column .
# precip_df['datetime'] = pd.to_datetime([d.get('value') for d in precip_df.time], unit='ms', origin = 'unix')

# plt.figure()
# plt.bar(precip_df.datetime, precip_df.precipitation)
# plt.title('Monthly precipitation at point')
# plt.show()
# plt.savefig('precip.png')
# print(monthlyPrecip.map(lambda image: image.clip(point)).getInfo())
'''
###############################################################################   
#ADD NDVI and GET MONTHLY VALUES     

#Import Sentinel 2, mask clouds
s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED").filterDate(start_date, end_date)\
    .map(clip_img).map(maskS2clouds)
 
ndvi = s2.map(addNDVI).select('NDVI')

landcover = ee.ImageCollection("ESA/WorldCover/v100").first().clip(ROI)
##ADD TO MAP
# my_map.add_ee_layer(ndvi.select('NDVI').median(), ndviVis, 'NDVImedian')
# my_map.add_ee_layer(ndvi.select('MSAVI2').median(), ndviVis, 'MSAVI2median')
# my_map.add_ee_layer(ndvi_noclouds.select('NDVI').median(), ndviVis, 'NDVImedian_NC')
# my_map.add_ee_layer(ndvi_noclouds.select('MSAVI2').median(), ndviVis, 'MSAVI2median_NC')
# my_map.add_child(folium.LayerControl())
# my_map.save('my_map.html')

 
#taken monthly maximums of NDVI as additional filter

#need to specify the scale because it doesn't automatically keep that 
# for sentinel2, the scale is 10 m and projection is epsg 32628
veg = monthlyMax(ndvi, yrs, mos) 

#START HERE
tasks = batch.Export.imagecollection.toDrive(collection=veg, 
                                             folder='GEE_Veg_S2', 
                                             namePattern= '{system_date}',
                                             region=ROI, scale=10,
                                             crs = 'EPSG:4326',
                                             datePattern='yyyyMMdd') 


#plot monthly max NDVI+MSAVI2 over years  
# plt.figure(1)
# plt.plot(veg_df.datetime.dt.month, veg_df.NDVI, 'r', veg_df.datetime.dt.month, veg_df.MSAVI2, 'b')
# plt.title('Monthly ndvi/msavi2 at point')
# plt.xlabel('months')
# plt.ylabel('index')
# plt.legend()
# plt.show()
# #   #plot monthly ndvi over time
# plt.figure(2)
# plt.plot(veg_df.datetime, veg_df.NDVI, 'r', veg_df.datetime, veg_df.MSAVI2, 'b')
# plt.title('Monthly ndvi/msavi2 at point over time')
# plt.xlabel('months')
# plt.ylabel('index')
# plt.legend()
# plt.show()
#   #plot monthly ndvi by region
#plot NDVI and Precip together