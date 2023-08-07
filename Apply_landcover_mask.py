# Maddie Henderson 
## 2023
## apply the ecoregion and landcover masks 
## to result dfs so that csvs can be used in spotfire 
## will remove rows that are not in the landcover of interest 

# also apply and save as tif and rearrange the results tifs 
# into separate tifs by drought so that QGIS likes them better 

import pandas as pd 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import pickle
##### create masks (1 time only)######################3333
# im = rs.open('landcover_WorldCoverv100_reprojected.tif')
# landcover= im.read(1)
# landcover_meta = im.meta
# plt.imshow(landcover)
# im.close()
# Know that due to the mode reduction from 10m to 30m, this ended up with +1 pix on all sides except east/right 
# landcover = np.delete(landcover, [0, -1], 0) # delete first and last row
# landcover = np.delete(landcover, 0, 1) #delete first column

# with open ('landcover_mask.pkl', 'wb') as file:
#     pickle.dump(landcover, file)

#################################################
county = input('Input the county to process: ')
# tif vs df 
# tif = True 

# if tif: 
#     infile = './RESULTS/V2/ndvi_results_'+county+'_V2.tif' 

#     with open('landcover_mask.pkl', 'rb') as file:
#         lc_mask = pickle.load(file)

#     lc_mask = lc_mask <= 40
#     lc_mask = lc_mask * 1

#     im = rs.open('./RESULTS/V2/ndvi_results_Tharaka_V2.tif')
#     res= im.read()
#     res_bands = im.descriptions
#     meta = im.meta
#         #remember - rasterio does layers, rows, cols instead of rows, cols, depth 
#     im.close() 

#     n_layers = len(res_bands)

#     for n in range(n_layers):
#         layer = res[n, :, :] * lc_mask #single layer masked by landcover 


#         meta['count'] = 3

#         with rs.open(fname,"w",**meta) as f:
#             #python array is row, cols, depth
#             # rasterio expects band, row, col
#             #can do a 2d with indexes=1
#             for b in range(1, n_layers+1):

#                 f.write(array[:,:,b-1], indexes=b)
#             # set layer descriptions 
#             f.descriptions=tuple(col_names)


# else: 
infile = 'ndvi_results_'+county+'_V2.csv'

result_df = pd.read_csv(infile)
result_df.drop(columns = result_df.filter(like = '20').columns.to_list(), inplace = True)


#################################################
# Import masks 
#################################################

with open('landcover_mask.pkl', 'rb') as file:
    lc_mask = pickle.load(file)

with open('eco_mask.pkl', 'rb') as file:
    eco_mask = pickle.load(file)

#########################################################
# Get the locations of each lc and eco type and add those to df 

#### landcover 
#only keeping grassland, shrubland, cropland, and forest
#which removes built up things, water, etc 
#this was a dumb way to do it but it worked 
df_40 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(lc_mask == 40))
df_40['landcover'] = 40
df_30 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(lc_mask == 30))
df_30['landcover'] = 30
df_20 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(lc_mask == 20))
df_20['landcover'] = 20
df_10 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(lc_mask == 10))
df_10['landcover'] = 10

#concat
lc_df = pd.concat([df_40, df_30, df_20, df_10], axis=0)

val_lc_results = result_df.merge(lc_df, how='inner', on=['row', 'col'])

#### ecoregions 
# Ecoregion: East African montane moorlands
# Eco ID: 78
# Ecoregion: East African montane forests
# Eco ID: 8
# Ecoregion: Northern Acacia-Commiphora bushlands and thickets
# Eco ID: 51
# Ecoregion: Southern Acacia-Commiphora bushlands and thickets
# Eco ID: 57

df_78 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(eco_mask == 78))
df_78['eco'] = 78
df_8 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(eco_mask == 8))
df_8['eco'] = 8
df_51 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(eco_mask == 51))
df_51['eco'] = 51
df_57 = pd.DataFrame(columns = ['row', 'col'], data = np.argwhere(eco_mask == 57))
df_57['eco'] = 57

eco_df = pd.concat([df_78, df_8, df_51, df_57], axis=0)
final_results = val_lc_results.merge(eco_df, how='inner', on=['row', 'col'])

final_results.to_csv('ndvi_results_w_landcover'+county+'.csv', encoding='utf-8', index=False)

print('applied landcover and eco masks for '+county)                   
