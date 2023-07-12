#take calculated return rates and turn them into maps / layers 

import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from df_to_map import df_to_map

county = input('Input the county to process: ')
fname = 'ndvi_results_'+county+'.csv'

ndvi_results = pd.read_csv('ndvi_results_'+county+'.csv')

col_names_recov = ndvi_results.filter(like = 'recov').columns()
col_names_rsq = ndvi_results.filter(like = 'rsq').columns()

ndvi_recov_array = df_to_map(ndvi_results, col_names_recov)
ndvi_rsq_array = df_to_map(ndvi_results, col_names_rsq)

#now turn this into like rasterio thing where i can attach metadata and 
#bounds and the names of layers? 