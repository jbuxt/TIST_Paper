# do some statistical comparison
# boy howdy do i wish i'd made the leap to jupyter or other notebook but i haven't so here we are

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np 
import seaborn as sb

######################################################33
# import
county = input('Input the county to process: ')
# county =  'Tharaka'
res = pd.read_csv('./RESULTS/V2/ndvi_all_results_'+county+'.csv')
res.rename(columns={"mean": "mean_res", "stdev": "stdev_res", 'alt':'altitude'}, inplace = True)


'''row,col,tist,county,mean,stdev,recov_rate_59,recov_rate_77,
rsq_59,rsq_77,mins_59,mins_77,
landcover,eco,mean_ndvi,stdev_ndvi,alt,tist_neighbors, yearly_precip_avg'''

recov_cols = res.filter(like='recov').columns.to_list()
# recov_nums = [x[11:] for x in recov_cols #strings
# n_recovs = len(recov_nums)

# make a bool col for the ones that are 10 and 15 (no calc and no disturbance)
# new_col_names = ['not_calc_'+x for x in recov_nums]
not_calc_mask = res[recov_cols] >= 10
#mask out the 10s and 15s
res[recov_cols] = res[recov_cols].mask(not_calc_mask, np.nan) #mask replaces values that are True (nan)

res[recov_cols] = res[recov_cols].abs() # Change the recovery to be positive

cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

##################################################################3333
# Spearmans rank correlation 
# Do for recovery rates (only ones that have calculated)
# and for mean/std ndvi, mean/std residual, altitude, and precip (the continuous vars)

# can i also do it for landcover/ecoregion? how? 
# can i also do it for categorical calc/no calc/no disturbance? 
# do i want this separated by county? i think yes that's fine 

# f, axs = plt.subplots(1, n_recovs, gridspec_kw=dict(width_ratios=[4, 4]))

#ignores nans
spearmans = res.loc[:, recov_cols+cols_to_corr].corr(method = 'spearman')
print(spearmans)
plt.figure()
sb.heatmap(spearmans, vmin=-1.0, vmax=1.0, cmap='PRGn', annot=True, 
            fmt=".2f")
plt.xticks(rotation=45) 
plt.yticks(rotation=45) 
plt.title('Spearmans Correlation for Recoveries in '+county)
plt.tight_layout()
plt.show()

print('donezo')