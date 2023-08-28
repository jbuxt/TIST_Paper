## Maddie Henderson 
## 2023
## basic pre-process and download from GEE to Google Drive

import ee
import google.auth
from geetools import batch

# have to have used the GEE_start.py before hand to get the authenticaiton and initialization going 
credentials, project_id = google.auth.default()
ee.Initialize(credentials, project='ee-maddiehenderson12')


#ROI
box = ee.Geometry.Rectangle([36.11092694867859, -0.9639821313886587, 38.47870637456082, 0.8877151637669112])
box_col = ee.FeatureCollection([box])

task = batch.Export.table.toDriveShapefile(collection = box_col, folder='Shape_FINAL')


# ##################################
# # FUNCTIONS
# #################################/
# clip to area
def clip_img(image):
    return image.clip(box)

# Applies scaling factors for landsat 8 .
def applyScaleFactors(image):
    opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(opticalBands, None, True).addBands(thermalBands, None, True)

# calculate and add an NDVI band for landsat 8
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

''' ## SENTINEL 2 FUNCTIONS

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
''' 
### FOR CHIRPS PRECIPITATION TO CREATE MONTHLY SUMS
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
#Import Landsat 8 
ls = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterDate(start_date, end_date)\
    .map(clip_img).map(applyScaleFactors)

ndvi = ls.map(addNDVI).map(addmsavi2)
#mask clouds
ndvi_noclouds = ndvi.map(mask_clouds_landsat8).select('NDVI', 'MSAVI2')

#taken monthly maximums of NDVI as additional filter
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