#make nice graphs of recoveries 

import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pandas as pd
import numpy as np 
 
#################################################3
county = 'Tharaka'

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

#################import data
ndvi_results = pd.read_csv('./RESULTS/ndvi_results_'+county+'.csv',index_col=0)
ndvi_results = ndvi_results[ndvi_results.loc[:, 'tist']== 1]

precip_df = pd.read_csv('precip_pixels_'+county+'.csv') #skiprows=57204, nrows = 1000

precip_df = precip_df.loc[ndvi_results.index.to_list(), :]

ndvi_res  = pd.read_csv('ndvi_residuals_'+county+'.csv') 
ndvi_res = ndvi_res.loc[ndvi_results.index.to_list(), :]

#pick a row to plot
for row in ndvi_results.index: #since the results has rows deleted

        sample_result = ndvi_results.loc[row, :].filter(like='20')
        sample_pixel = ndvi_res.loc[row, :].filter(like='20')
        sample_precip = precip_df.loc[row, :].filter(like='20')
        if ndvi_results.loc[row, 'tist'] == 1:
                tist_tf = 'TIST'
        else:  
                tist_tf = 'Non-TIST'

        results = ndvi_results.loc[row].filter(like='_')
        # results.index[0]+'
        recs = 'r1 = '+str(round(results[0],3))+' Rsq = '+str(round(results[3],2))+'; '+\
        'r2 = '+str(round(results[1],3))+' Rsq = '+str(round(results[4],2))+'; '+\
        'r3 = '+str(round(results[2],3))+' Rsq = '+str(round(results[5],2))
        ##########Plot ############################
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=False)
        # fig, ax = plt.subplots()
        ax2.plot(date_list, sample_pixel, 'r*', label='NDVI Residual')

        # ax1.set_xlabel('month')
        ax1.set_ylabel('monthly precipitation (mm/mo)' )
        ax1.set_ylim(0, 700)
        ax1.bar(x=date_list, height=sample_precip, width=20, label='monthly precip mm')
        ax2.set_ylabel('NDVI residual')
        ax2.set_xlabel('date')
        ax2.set_ylim(-0.3, 0.3)
        ax2.plot(date_list, sample_result, 'g-', label='Fitted recovery')
        # fig.legend()
        ax2.grid(axis='x', which='major')
        ax1.grid(axis='x', which='major')
        fig.legend()
        ax1.pcolor(date_plus, ax1.get_ylim(), 
                NDMA[county].map(color_dict).values[np.newaxis], 
                cmap=CMAP, alpha=0.4,
                linewidth=0, antialiased = True)
        #lol don't know how to do this to both at once
        ax2.pcolor(date_plus, ax2.get_ylim(), 
                NDMA[county].map(color_dict).values[np.newaxis], 
                cmap=CMAP, alpha=0.4,
                linewidth=0, antialiased = True)

        fig.autofmt_xdate(which='both')

        plt.gcf().text(0.1,0.01, recs, fontsize=10)
        plt.subplots_adjust(bottom=0.15)

        cbar=fig.colorbar(cm.ScalarMappable(cmap=CMAP), ax=ax1, 
                        location='top', shrink = 0.5,
                        pad=0.2,
                        label='NDMA Drought Status')
        cbar.set_ticks([0.12, 0.35, 0.62, 0.87])
        cbar.set_ticklabels(['Alarm', 'Alert', 'Recovery', 'Normal'])
        fig.suptitle('Example recoveries ('+str(ndvi_results.loc[row, 'row'])+\
                     ', '+str(ndvi_results.loc[row, 'col'])+'), '+tist_tf)
        fig.show()
        # fig.savefig(county+'_example_recovery_rate.png')

print('donezo')