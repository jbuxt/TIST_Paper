# do some statistical comparison
# boy howdy do i wish i'd made the leap to jupyter or other notebook but i haven't so here we are

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np 
import seaborn as sb
from scipy.stats import spearmanr
from scipy import stats

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
recov_nums = [x[11:] for x in recov_cols] #strings
n_recovs = len(recov_nums)
new_col_names = ['cat_'+x for x in recov_nums]

## assign categories for each recovery column 
res[new_col_names] = 'calc'
for n in range(n_recovs):
    x = recov_cols[n]
    y = new_col_names[n]
    res.loc[(res[x] == 10.0), y] = 'no_calc'
    res.loc[(res[x] == 15.0), y] = 'no_disturb'
    res.loc[(res[x].isna()), y] = 'null'

##############################################33
# make a bool col for the ones that are 10 and 15 (no calc and no disturbance)

# not_calc_mask = res[recov_cols] >= 10
# #mask out the 10s and 15s
# res[recov_cols] = res[recov_cols].mask(not_calc_mask, np.nan) #mask replaces values that are True (nan)

# res[recov_cols] = res[recov_cols].abs() # Change the recovery to be positive

# cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

##################################################################3333
# Spearmans rank correlation 
# Do for recovery rates (only ones that have calculated)
# and for mean/std ndvi, mean/std residual, altitude, and precip (the continuous vars)

# can i also do it for landcover/ecoregion? how? 
# can i also do it for categorical calc/no calc/no disturbance? 
# do i want this separated by county? i think yes that's fine 

# f, axs = plt.subplots(1, n_recovs, gridspec_kw=dict(width_ratios=[4, 4]))

#ignores nans
# spearmans = res.loc[:, recov_cols+cols_to_corr].corr(method = 'spearman')
# print(spearmans)
# plt.figure()
# sb.heatmap(spearmans, vmin=-1.0, vmax=1.0, cmap='PRGn', annot=True, 
#             fmt=".2f")
# plt.xticks(rotation=45) 
# plt.yticks(rotation=45) 
# plt.title('Spearmans Correlation for Recoveries in '+county)
# plt.tight_layout()
# plt.show()


# spearmanr = spearmanr(res.loc[:, recov_cols+cols_to_corr], nan_policy = 'omit')

# plt.figure()
# sb.heatmap(spearmanr.statistic, vmin=-1.0, vmax=1.0, cmap='PRGn', annot=True, 
#             fmt=".2f")
# plt.xticks(rotation=45) 
# plt.yticks(rotation=45) 
# plt.title('Spearmans (SciPy) Correlation for Recoveries in '+county)
# plt.tight_layout()
# plt.show()

# plt.figure()

# sb.heatmap(spearmanr.pvalue, vmin=0, vmax=1.0, cmap='Greens', annot=True, 
#             fmt=".2f")
# plt.xticks(rotation=45) 
# plt.yticks(rotation=45) 
# plt.title('PValues from SciPy for Recoveries in '+county)
# plt.tight_layout()
# plt.show()
###############################################################################
# Chi squared test of independence
# use for categorical influence on categorical: so landcover and eco on calc/no calc/no disturbance 

# Add categorical tags 
# case [eco] when 78 then "Montane moorlands" when 8 then "Montane forests" when 51 then "N. Acacia bushland" when 57 then "S. Acacia bushland" else "null" end
#case [landcover] when 10 then "Trees" when 20 then "Shrubs" when 30 then "Grass" when 40 then "Crops" else "null" end

# need to get rid of the montane moorlands anyways - not super applicable here and is just going to mess with it 
# and also the null values 

for y in ['eco', 'landcover']:
    for x in new_col_names:
        print(y, x)
        cross = pd.crosstab(res.loc[res[x] != 'null', x], res.loc[res[x] != 'null', y])
        print(cross)
        # get rid of the null values as they are not applicable 
        chi2, p, dof, ex = stats.chi2_contingency(cross)
        print('Chi2: {}, pvalue: {}, dof: {}'.format(chi2, p, dof))

print('donezo')