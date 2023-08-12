#make nice graphs of recoveries 

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd
import numpy as np 
 
#################################################3

#import the drought classifications####################################33333
NDMA = pd.read_csv('NDMA_droughts.csv', index_col=0, parse_dates=['Date']) 
# NDMA.index = pd.to_datetime(NDMA.index, format='%Y-%m-%d') #index is datetime

#extend to include the dates there are no NMDA classifications for
extra = pd.DataFrame(columns = NDMA.columns, index = pd.date_range(start='2013-05-01', periods=40, freq='MS'))
extra.fillna
NDMA = pd.concat([NDMA, extra]).sort_index()

date_list = NDMA.index
date_plus = pd.date_range(start='5/1/2013', periods=121, freq='MS') #need one that's +1 in length for the color graph 

color_dict = {'Recovery':2, 'Alert':1, 'Alarm':0,'Normal':3}
CMAP = ListedColormap(['red', 'orange', 'yellow', 'green'])
bounds=[0,1,2,3]
norm = BoundaryNorm(bounds, CMAP.N)
#############################################
county = input('Enter county: ')
r_range = int(input('Enter approx row: '))
c_range = int(input('Enter approx col: '))

ndvi_results = pd.read_csv('./RESULTS/V2/ndvi_results_'+county+'_V2.csv')
ndvi_results =ndvi_results.loc[(ndvi_results['row'] <= (r_range +50)) & (ndvi_results['row'] >= (r_range - 50))]
results =ndvi_results.loc[(ndvi_results['col'] <= (c_range +50)) & (ndvi_results['col'] >= (c_range - 50))]

ndvi_res  = pd.read_csv('./RESULTS/V2/ndvi_residuals_'+county+'_V2.csv') 
ndvi_res =ndvi_res.loc[(ndvi_res['row'] <= (r_range +50)) & (ndvi_res['row'] >= (r_range - 50))]
ndvi_res =ndvi_res.loc[(ndvi_res['col'] <= (c_range +50)) & (ndvi_res['col'] >= (c_range - 50))]

# graph lots of things#################################################
while True: 
        
        row = int(input('Row: '))
        col = int(input('Col: '))
        
        results =ndvi_results.loc[(ndvi_results['row'] == row) & (ndvi_results['col'] == col)]
        res =ndvi_res.loc[(ndvi_res['row'] == row) & (ndvi_res['col'] == col)]
        sample_result = results.iloc[0, :].filter(like='20')
        sample_pixel = res.iloc[0, :].filter(like='20')

        if results.iloc[0, 2] == 1:
                tist_tf = 'TIST'
        else:  
                tist_tf = 'Non-TIST'

        vals = results.filter(like='_')
        n_recovs = int(vals.shape[1] / 3) #have recovs, mins, rsq
        recov_nums = [x[11:] for x in vals.filter(like='recov').columns.to_list()]

        recovs= [int(x) for x in recov_nums]
        starts = [x-5 for x in recovs]
        stops = [x +6 for x in recovs]
        # convert to date time for plot

        start_dates = [pd.to_datetime('05-01-2013')+pd.DateOffset(months = x) for x in starts]
        stop_dates = [pd.to_datetime('05-01-2013')+pd.DateOffset(months = x) for x in stops]
        
        fig, ax = plt.subplots(figsize=(9, 6))
        fig.tight_layout()

        ax.set_ylim(sample_pixel.min()-0.02, sample_pixel.max()+0.02)
        ax.plot(date_list, sample_pixel, 'k*', label='NDVI Residual')
        
        #start date of the whole thing
        ax.plot(date_list, sample_result, 'g-', label='Fitted recovery')
        ax.grid(axis='x', which='both')
        
        ax.pcolor(date_plus, ax.get_ylim(), 
                NDMA[county].map(color_dict).values[np.newaxis], 
                cmap=CMAP, norm=norm, alpha=0.4, linewidth=0.1, antialiased = True)
        
        plt.vlines(start_dates, ax.get_ylim()[0], ax.get_ylim()[1], color = 'blue',
                   label='Potential recov. starts', linewidth=1)
        plt.vlines(stop_dates, ax.get_ylim()[0], ax.get_ylim()[1], color = 'purple',
                   label='Potential recov. stops', linewidth=1)
        ax.set_title('Drought recovery ('+str(row)+\
                ', '+str(col)+'), '+tist_tf)
        ax.set_ylabel('NDVI residual')

        fig.legend()
        # fig.autofmt_xdate(which='both') #change to major for years only

        # plt.gcf().text(0.1,0.01, recs, fontsize=10)
        plt.subplots_adjust(left= 0.1, bottom=0.4)
        ax.table(cellText = [['%0.2f' %x for x in vals.iloc[0, 0:n_recovs].values], ['%0.2f' %x for x in vals.iloc[0, n_recovs:n_recovs*2].values]],
                 rowLabels = ['Recovery Rate', 'Rsquared'], 
                 colLabels = ['Recovery Month %s' % x for x in recov_nums],
                 loc = 'bottom', bbox=[0.2, -0.5, 0.8, 0.275])

        cbar=fig.colorbar(cm.ScalarMappable(cmap=CMAP), ax=ax, 
                location='top', shrink = 0.5,
                pad=0.1, alpha=0.4, 
                label='NDMA Drought Status')
        cbar.set_ticks([0.12, 0.35, 0.62, 0.87])
        cbar.set_ticklabels(['Alarm', 'Alert', 'Recovery', 'Normal'])

        fig.show()
        print('x')
        # fig.savefig(county+'_example_recovery_rate.png')

print('donezo')