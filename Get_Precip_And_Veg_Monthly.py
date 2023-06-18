## Maddie Henderson 
## 2023
## basic pre-process and download from GEE to Google Drive

import pandas as pd 
# from IPython.display import display
import folium 
import ee
import google.auth
import matplotlib.pyplot as plt
from geetools import batch
# ee.Authenticate()
# ee.Initialize()
credentials, project_id = google.auth.default()
ee.Initialize(credentials, project='ee-maddiehenderson12')

## createshapes 
#Get a rectangle that encompasses the 5/6 counties of interest
# point = ee.Geometry.Point(37.61, 0.18)
box = ee.Geometry.Rectangle([36.11106114075685, -0.9637556593236211, 38.47861485169435, 0.8873597041102137])
box_col = ee.FeatureCollection([box])

#task = batch.Export.table.toDriveShapefile(collection = box_col, folder='Shape')

# Define the center of map
# lat, lon = 37.61, 0.18
# my_map = folium.Map(location=[lat, lon], zoom_start=10)

# ##################################
# # FUNCTIONS
# #################################/
# clip to area
def clip_img(image):
    return image.clip(box)
# EDIT THE GEOMETRY IF NEEDED
# must be a better way to do that 

# Applies scaling factors for landsat 8 .
def applyScaleFactors(image):
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

# calculate and add an NDVI band
def addNDVI(image):
    return image.addBands(image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI'))
#SR_B5 is surface reflectance near infrared, B4 is red landsat

# compute MSAVI2 using expression for Landsat 8 
def addmsavi2(image):
    return image.addBands(image.expression(
  '(2 * NIR + 1 - sqrt(pow((2 * NIR + 1), 2) - 8 * (NIR - RED)) ) / 2', 
  {
    'NIR': image.select('SR_B5'), 
    'RED': image.select('SR_B4')
  }).rename('MSAVI2'))

# Mask clouds on Landsat 8 SR 
def mask_clouds_landsat8(image):
  # Bits 1-4 clouds / shadows
  cloudsBitMask = (1<<3) #ee.Number(2).pow(3).int()# 1000 in base 2
  dilatedCloudBitMask = (1<<1)
  cirrusCloudBitMask = (1<<2)
  cloudShadowBitMask = (1<<4)

  # Get the pixel QA band
  qa = image.select('QA_PIXEL')

  # Both flags should be set to zero, indicating clear conditions
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
      qa.bitwiseAnd(cloudsBitMask).eq(0)).And(
      qa.bitwiseAnd(dilatedCloudBitMask).eq(0)).And(
      qa.bitwiseAnd(cirrusCloudBitMask).eq(0))

  return image.updateMask(mask)

# method for adding earth engine image tiles to folium map
def add_ee_layer(self, ee_image_object, vis_params, name):
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
        name=name,
        overlay=True,
        control=True
    ).add_to(self)

# Add Earth Engine drawing method to folium.
folium.Map.add_ee_layer = add_ee_layer 

#create monthly totals from input image collection and convert to DF
def monthlySum(collection, yrs, mos, geom, scale):
    totals_imgs = []
    # totals_arr = []
    for year in yrs:
        for mo in mos: 
            #Creates an image that is reduced for the month
            month_sum = collection.filter(ee.Filter.calendarRange(year, year, 'year'))\
                                  .filter(ee.Filter.calendarRange(mo, mo, 'month'))\
                                  .sum()\
                                  .set({'month': mo, 
                                        'year': year, 
                                        'system:time_start': ee.Date.fromYMD(year, mo, 1).millis()})
            #add that image to the list
            totals_imgs.append(month_sum) #list of images 
            #convert that image to array and append to the array 
            #very convoluted way - make image collection from single image
            #then use the get region to turn it into a lat,lon, time, bands array
            # ic = ee.ImageCollection.fromImages([month_sum])
            # arr = ic.getRegion(geom, scale).getInfo()
            # header = arr.pop(0) #delete the first row that has the headers and everything 
            # totals_arr.extend(arr) 


    #Return image collection        
    img_col = ee.ImageCollection.fromImages(totals_imgs)
    #Return dataframe
    # img_df = pd.DataFrame(totals_arr) #convert list to df
    # img_df.columns = header
    # seems to be a list of arrays 

    return img_col

#create monthly max from input image collection 
def monthlyMax(collection, yrs, mos, geom, scale, crs):
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
            # ic = ee.ImageCollection.fromImages([month_max])
            # arr = ic.getRegion(geom, scale, crs).getInfo()
            # header = arr.pop(0) #delete the first row that has the headers and everything 
            # maxes.extend(arr) 
    img_col = ee.ImageCollection.fromImages(maxes)
    # img_df = pd.DataFrame(maxes) #convert list to df
    # img_df.columns = header
    return img_col 

##############################
# VIS PARAMS
##############################
precipitationVis = {
  'min': 1.0,
  'max': 17.0,
  'palette': ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000'],
}

ndviVis = {
  'min': -1, 
  'max': 1, 
  'palette': ['blue', 'white', 'green'] # sets the color ramp for displaying it 
}

rgbVis = {
 'bands': ['SR_B4', 'SR_B3', 'SR_B2'], # these are the RGB layers for landsat
  'min': 0.0,
  'max': 0.3
}

###################################
#Begin
###################################

start_date = '2017-06-01' #inclusive
end_date = '2017-07-01' #exclusive
#get to 2023 05 01
startyr = 2017
endyr = 2017
# yrs = ee.List.sequence(startyr, endyr)
mos = [6]#range(1,13)
yrs = [2017]
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
#ADD NDVI and MSAVI and GET MONTHLY VALUES     

#Import Landsat 8 
ls = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(start_date, end_date)\
    .map(clip_img).map(applyScaleFactors)
  
ndvi = ls.map(addNDVI).map(addmsavi2)
#mask clouds
ndvi_noclouds = ndvi.map(mask_clouds_landsat8).select('NDVI', 'MSAVI2')

##ADD TO MAP
# my_map.add_ee_layer(ndvi.select('NDVI').median(), ndviVis, 'NDVImedian')
# my_map.add_ee_layer(ndvi.select('MSAVI2').median(), ndviVis, 'MSAVI2median')
# my_map.add_ee_layer(ndvi_noclouds.select('NDVI').median(), ndviVis, 'NDVImedian_NC')
# my_map.add_ee_layer(ndvi_noclouds.select('MSAVI2').median(), ndviVis, 'MSAVI2median_NC')
# my_map.add_child(folium.LayerControl())
# my_map.save('my_map.html')

 
#taken monthly maximums of NDVI as additional filter
#and create dataframe
#need to specify the scale because it doesn't automatically keep that 
# for landsat, the scale is 30 m and projection is epsg 32628
veg = monthlyMax(ndvi_noclouds, yrs, mos, box, 30, 'EPSG:4326') 

#START HERE
tasks = batch.Export.imagecollection.toDrive(collection=veg, 
                                             folder='GEE_Veg', 
                                             namePattern= '{system_date}',
                                             region=box, scale=30,
                                             crs = 'EPSG:4326',
                                             datePattern='yyyyMMdd') 
# print(veg_df.columns)
# #id, longitude, latitude, time, NDVI, MSAVI2
# # Convert the time field into a datetime as additional column .
# veg_df['datetime'] = pd.to_datetime([d.get('value') for d in veg_df.time], unit='ms', origin = 'unix')
# print(veg_df[:5])

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