# Maddie Henderson 
## 2023
## get the yearly precip avg for each pixel for study period so we can check that 

import pandas as pd 
import numpy as np

#################################################
county = input('Input the county to process: ')
pix_file = 'precip_pixels_'+county+'.csv'

pix= pd.read_csv(pix_file)
'''row, col, county, tist, 120 cols of dates'''

yearly = pix.iloc[:, 4:].sum(axis = 1).astype('float16') / 10  #sum the monthly rainfall then divide by number of years 

precip = pd.concat([pix.loc[:, ['row', 'col']], yearly.rename('yearly_precip_avg')], axis = 1)

#add to results 
# result_df = pd.read_csv(infile)
# result_df = result_df.merge(ndvi_mean, how='left', on=['row', 'col'])

# save as a tif for all pix in county
# df_to_map(ndvi_mean, ['mean_ndvi', 'stdev_ndvi'], savefile = True, fname = 'ndvi_mean_'+county+'.tif', meta = veg_meta)

################## save
precip.to_csv('yearly_precip'+county+'.csv', encoding='utf-8', index=False)

print('added yearly precip for '+county)                   
