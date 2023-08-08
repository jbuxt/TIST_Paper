# do some statistical comparison
# boy howdy do i wish i'd made the leap to jupyter or other notebook but i haven't so here we are

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np 

######################################################33
# import
county =  'Tharaka'
res = pd.read_csv('./RESULTS/V2/ndvi_results_w_everything'+county+'.csv')

'''row,col,tist,county,mean,stdev,recov_rate_59,recov_rate_77,
rsq_59,rsq_77,mins_59,mins_77,
landcover,eco,mean_ndvi,stdev_ndvi,alt,tist_neighbors'''

recov_nums = [x[-2:] for x in res.filter(like='recov').columns.to_list()] #strings
n_recovs = len(recov_nums)

##################################################################3333
# Spearmans rank correlation 
# Do for recovery rates (only ones that have calculated)
# and for mean/std ndvi, mean/std residual, altitude

# can i also do it for landcover/ecoregion? how? 
# can i also do it for categorical calc/no calc/no disturbance? 
