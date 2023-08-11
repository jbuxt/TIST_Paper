# do some statistical comparison
# boy howdy do i wish i'd made the leap to jupyter or other notebook but i haven't so here we are

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np 
import seaborn as sb
from scipy import stats

######################################################33
# import
county = input('Input the county to process: ')

res = pd.read_csv('./RESULTS/V2/ndvi_all_results_'+county+'.csv')
res.rename(columns={"mean": "mean_res", "stdev": "stdev_res", 'alt':'altitude'}, inplace = True)


'''row,col,tist,county,mean,stdev,recov_rate_59,recov_rate_77,
rsq_59,rsq_77,mins_59,mins_77,
landcover,eco,mean_ndvi,stdev_ndvi,alt,tist_neighbors, yearly_precip_avg'''

recov_cols = res.filter(like='recov').columns.to_list()
recov_nums = [x[11:] for x in recov_cols] #strings
n_recovs = len(recov_nums)
new_col_names = ['cat_'+x for x in recov_nums]

# assign categories for each recovery column 
res[new_col_names] = 'calc'
for n in range(n_recovs):
    x = recov_cols[n]
    y = new_col_names[n]
    res.loc[(res[x] == 10.0), y] = 'no_calc'
    res.loc[(res[x] == 15.0), y] = 'no_disturb'
    res.loc[(res[x].isna()), y] = 'null'

# get tist and neighbors into same group 
res['tist_TF'] = res['tist_neighbors'] > 0 #true is TIST and neighbors

##############################################33
# mask the 10s and 15s 

# not_calc_mask = res[recov_cols] >= 10
# #mask out the 10s and 15s
# res[recov_cols] = res[recov_cols].mask(not_calc_mask, np.nan) #mask replaces values that are True (nan)

# res[recov_cols] = res[recov_cols].abs() # Change the recovery to be positive



##################################################################3333
# Spearmans rank correlation 
# Do for recovery rates (only ones that have calculated)
# and for mean/std ndvi, mean/std residual, altitude, and precip (the continuous vars)


# f, axs = plt.subplots(1, n_recovs, gridspec_kw=dict(width_ratios=[4, 4]))

# cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

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


# spearmanr = stats.spearmanr(res.loc[:, recov_cols+cols_to_corr], nan_policy = 'omit')

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

# for y in ['tist_TF']: #also 'eco' and 'landcover'
#     for x in new_col_names:
#         print(y, x)
#         cross = pd.crosstab(res.loc[res[x] != 'null', x], res.loc[res[x] != 'null', y])
#         print(cross)
#         # get rid of the null values as they are not applicable 
#         chi2, p, dof, ex = stats.chi2_contingency(cross)
#         print('Chi2: {}, pvalue: {}, dof: {}'.format(chi2, p, dof))

for y in ['tist_TF']: 
    for x in ['eco', 'landcover']:
        print(y, x)
        cross = pd.crosstab(res[x], res[y])
        print(cross)
        chi2, p, dof, ex = stats.chi2_contingency(cross)
        print('Chi2: {:.1f}, pvalue: {:.3f}, dof: {}'.format(chi2, p, dof))

################################################################################
#Kruskal - Wallace H test 
# for testing if 2+ samples come from the same distribution - if we assume 
# that the shape and scale of the distribution is the same then is a test of
# equivalence of medians (which yeah - the recovery rates have a similar shape and scale)
# basically is wilcoxon rank-sum/mann-whitney U for more than 2 groups
#scipy.stats.kruskal(*samples, nan_policy='propagate', axis=0, keepdims=False)
#using this for the recovery rate vs. cat variables like landcover, eco, TIST/non tist 
# also using to look at the continuous IVs vs cat outcome of calc/no calc/no dist 

# be sure to uncomment the masking of 10s and 15s at the top 
# if looking at recovery rate distributions

# y = 'eco' # effetively 2 types - ignore the moorlands 
# for x in recov_cols:
#     print(y, x)
#     # separate into samples 
#     # 8 and 51
#     r1 = res.loc[(res[y] == 8), x]
#     r2 = res.loc[(res[y] == 51), x]
#     # print the medians as well 
#     print('Median of Forest: {:.2f}, Median of Bushland: {:.2f}'.format(r1.median(skipna = True), r2.median(skipna = True)))

#     # get rid of the null values as they are not applicable 
#     h, p = stats.kruskal(r1, r2, nan_policy = 'omit')
#     print('H stat: {:.1f}, pvalue: {}'.format(h, p))

# y = 'landcover' # 4 types
# for x in recov_cols:
#     print(y, x)
#     # separate into samples 
#     #10, 20, 30, 40
#     r1 = res.loc[(res[y] == 10), x] #trees
#     r2 = res.loc[(res[y] == 20), x] #shrubs
#     r3 = res.loc[(res[y] == 30), x] # grass
#     r4 = res.loc[(res[y] == 40), x] #crops
#     print('Median of Trees: {:.2f}, Median of Shrubs: {:.2f}, Median of Grass: {:.2f}, Median of Crops: {:.2f}'.format(r1.median(skipna = True), 
#                                                             r2.median(skipna = True),
#                                                             r3.median(skipna=True), 
#                                                             r4.median(skipna = True)))
#     #ignore nan values 
#     h, p = stats.kruskal(r1, r2, r3, r4, nan_policy = 'omit')
#     print('H stat: {:.1f}, pvalue: {}'.format(h, p))

# y = 'tist_neighbors' # calling this 2 types - group TIST and 'neighbors' together types
# for x in recov_cols:
#     print(y, x)
#     # separate into samples 
#     #0 vs 1/2
#     r1 = res.loc[(res[y] == 0), x]
#     r2 = res.loc[(res[y] > 0), x]
#     print('Median of Non-Tist: {:.2f}, Median of Tist/Neighbors: {:.2f}'.format(r1.median(skipna = True), r2.median(skipna = True)))
#     #ignore nan values 
#     h, p = stats.kruskal(r1, r2, nan_policy = 'omit')
#     print('H stat: {:.1f}, pvalue: {}'.format(h, p))

#############################

# MUST REDO THIS 
cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

for y in new_col_names: #the categorical columns of calc/no calc/no dist
    for x in cols_to_corr:
        print(y, x)
        # separate into samples 
        r1 = res.loc[(res[y] == 'calc'), x]
        r2 = res.loc[(res[y] =='no_calc'), x]
        r3 = res.loc[(res[y] =='no_disturb'), x]
        print('Median of Calc: {:.2f}, Median of No Disturb: {:.2f}, Median of No Calc: {:.2f}'.format(r1.median(skipna = True), 
                                                                                                       r3.median(skipna = True),
                                                                                                       r2.median(skipna = True)))
        #ignore nan values 
        h, p = stats.kruskal(r1, r2, r3, nan_policy = 'omit')
        print('H stat: {:.1f}, pvalue: {:0.3f}'.format(h, p))
#########################################
# cols_to_corr = ['mean_ndvi','stdev_ndvi','altitude','mean_res','stdev_res', 'yearly_precip_avg']

# y = 'tist_neighbors' #the categorical column 
# for x in cols_to_corr:
#         print(y, x)
#         # separate into samples 
#         r1 = res.loc[(res[y] == 0), x] #other
#         r2 = res.loc[(res[y] > 0), x] #tist and neighbors 

#         print('Median of Other: {:.2f}, Median of Tist/Neighbors: {:.2f}'.format(r1.median(skipna = True), 
#                                                                             r2.median(skipna = True)))
#         #ignore nan values 
#         h, p = stats.kruskal(r1, r2, nan_policy = 'omit')
#         print('H stat: {:.1f}, pvalue: {:0.3f}'.format(h, p))

##############################################
## Recovery rate compared by county, recovery, and landcover type between TIST/neighbors/other

# mask the 10s and 15s 

not_calc_mask = res[recov_cols] >= 10
#mask out the 10s and 15s
res[recov_cols] = res[recov_cols].mask(not_calc_mask, np.nan) #mask replaces values that are True (nan)

res[recov_cols] = res[recov_cols].abs() # Change the recovery to be positive

y = 'tist_neighbors' #the categorical column 
for x in recov_cols:
    for z in [10, 20, 30, 40]: #landcover types
        print(y, x, z)
        # separate into samples 
        r1 = res.loc[((res[y] == 0) & (res['landcover'] == z)), x] #other
        r2 = res.loc[((res[y] == 1) & (res['landcover'] == z)), x] #neighbors 
        r3 = res.loc[((res[y] == 2) & (res['landcover'] == z)), x] #neighbors 

        print('Median of Other: {:.2f}, Median of Neighbors: {:.2f}, Median of TIST: {:.2f}'.format(r1.median(skipna = True), 
                                                                            r2.median(skipna = True),
                                                                            r3.median(skipna = True)))
        #ignore nan values 
        h, p = stats.kruskal(r1, r2, r3, nan_policy = 'omit')
        print('H stat: {:.1f}, pvalue: {:0.3f}'.format(h, p))

print('donezo')