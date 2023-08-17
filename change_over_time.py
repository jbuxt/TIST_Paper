# Maddie Henderson 
## 2023
## put the % change in recov rate over time into a map 

import pandas as pd 
import matplotlib.pyplot as plt
import rasterio as rs
import numpy as np
import pickle
from rasterio import features
from df_to_map import df_to_map


# get neighboring tist #######################
final = pd.DataFrame()
for county in ['Tharaka', 'Meru', 'Nyeri', 'Meru']:

    infile = './RESULTS/V2/ndvi_all_results_'+county+'.csv'
    result_df = pd.read_csv(infile)

    valid = result_df.loc[((result_df['recov_rate_59'] <10) & (result_df['recov_rate_77'] <10)), ['row', 'col', 'recov_rate_59', 'recov_rate_77']]
    valid['pct_change_rate'] = (valid['recov_rate_77'] - valid['recov_rate_59']) / valid['recov_rate_59']
    final = pd.concat([final, valid], axis = 0)

# save for maps ##############################
with open('veg_meta.pkl', 'rb') as file:
    veg_meta, veg_bounds = pickle.load(file)


df_to_map(final, ['pct_change_rate'], savefile = True, fname = 'rate_change.tif', meta = veg_meta)



print('donezo')                   
