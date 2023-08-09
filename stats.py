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

recov_nums = [x[-2:] for x in res.filter(like='recov').columns.to_list()] #strings
n_recovs = len(recov_nums)

# make a bool col for calc
for x in recov_nums:
    col_name = 'recov_rate_'+x
    new_col_name = 'calc_'+x
    res[new_col_name] = (res[col_name] < 10) #10 is no calc and 15 is no disturbance
    res[col_name] = res[col_name].abs() # Change the recovery to be positive

cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

##################################################################3333
# Spearmans rank correlation 
# Do for recovery rates (only ones that have calculated)
# and for mean/std ndvi, mean/std residual, altitude

# can i also do it for landcover/ecoregion? how? 
# can i also do it for categorical calc/no calc/no disturbance? 
# do i want this separated by county? i think yes that's fine 

# f, axs = plt.subplots(1, n_recovs, gridspec_kw=dict(width_ratios=[4, 4]))

for x in recov_nums: 
    col_name = 'recov_rate_'+x
    bool_col_name = 'calc_'+x
    spearmans = res.loc[res[bool_col_name], [col_name]+cols_to_corr].corr(method = 'spearman')
    print(spearmans)
    print(x)
    plt.figure()
    sb.heatmap(spearmans, vmin=-1.0, vmax=1.0, cmap='PRGn', annot=True, 
               fmt=".2f")
    plt.xticks(rotation=45) 
    plt.yticks(rotation=45) 
    plt.title('Spearmans Correlation for Recovery '+x+' in '+county)
    plt.tight_layout()
    plt.show()

print('donezo')