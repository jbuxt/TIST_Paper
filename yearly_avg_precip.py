# Maddie Henderson 
## 2023
## get the yearly precip avg for each pixel for study period so we can check that 

import pandas as pd 
import numpy as np
from df_to_map import df_to_map
import pickle

#################################################
# county = input('Input the county to process: ')
# res_file = './RESULTS/V2/ndvi_results_w_everything'+county+'.csv'
# precip_file = './yearly_precip/yearly_precip'+county+'.csv'

# # pix_file = 'precip_pixels_'+county+'.csv'

# # pix= pd.read_csv(pix_file)
# # '''row, col, county, tist, 120 cols of dates'''

# # yearly = pix.iloc[:, 4:].sum(axis = 1).astype('float16') / 10  #sum the monthly rainfall then divide by number of years 

# # precip = pd.concat([pix.loc[:, ['row', 'col']], yearly.rename('yearly_precip')], axis = 1)

# #add to results#########################3 
# result_df = pd.read_csv(res_file)
# precip = pd.read_csv(precip_file)
# result_df = result_df.merge(precip, how='left', on=['row', 'col'])

# save as a tif for all pix######################
with open('veg_meta.pkl', 'rb') as file:
    ndvi_meta, ndvi_bound =pickle.load(file)

precip_file1 = './yearly_precip/yearly_precipTharaka.csv'
precip_file2 = './yearly_precip/yearly_precipMeru.csv'
precip_file3 = './yearly_precip/yearly_precipEmbu.csv'
precip_file4 = './yearly_precip/yearly_precipNyeri.csv'
pix1= pd.read_csv(precip_file1)
pix2= pd.read_csv(precip_file2)
pix3= pd.read_csv(precip_file3)
pix4= pd.read_csv(precip_file4)
precip = pd.concat([pix1, pix2, pix3, pix4], axis =0)
df_to_map(precip, ['yearly_precip_avg'], savefile = True, fname = 'yearly_precip_avg.tif', meta = ndvi_meta)

################## save
# precip.to_csv('yearly_precip'+county+'.csv', encoding='utf-8', index=False)
# result_df.to_csv('./RESULTS/V2/ndvi_all_results_'+county+'.csv', encoding='utf-8', index=False)
# print('added yearly precip for '+county)                   
