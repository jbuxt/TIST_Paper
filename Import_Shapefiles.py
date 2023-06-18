#Import shapefiles of Tist groves and kenyan counties
#Clip the TIST groves to the ones within the five counties 
#Maddie Henderson
#2023

import geopandas as gp 
import matplotlib.pyplot as plt
import Import_saved_files as ws
import pickle

tpath = 'TIST_Groves/TIST_Groves.shp'
cpath = 'Kenya_Counties/Kenya_County_Boundaries.shp'

tist = gp.read_file(tpath) #
all_counties = gp.read_file(cpath) #EPSG4326
#select relevant counties 
counties = all_counties[(all_counties.COUNTY).isin(['Meru', 'Kirinyaga', 'Tharaka', 'Embu', 'Laikipia', 'Nyeri'])]

#Get only TIST groves within the relevant counties 
#have to do a spatial join because looking at NxM comparison
#This adds a column specifying the county the grove is in 
#might have a duplicate row if it's on the border between two counties? 
#need to check how many i'm really expecting 
tist_in = gp.sjoin(tist, counties[['COUNTY', 'geometry']], how='inner', op='within')

# tist_in.to_file('Relevant_Tist_groves.shp')
# counties.to_file('Relevant_Counties.shp')


with open('relevant_tist.pkl', 'wb') as file:
      
    # A new file will be created
    pickle.dump(tist_in, file)

with open('relevant_counties.pkl', 'wb') as file:
      
    # A new file will be created
    pickle.dump(counties, file)
    
# plt.figure()
# counties.plot()
# tist_in.plot()
# # plt.legend()
# plt.show()
# print('done')

# ws.save('tist_and_counties', 'tist_in', 'counties')
