# Calculate the recovery rate for pixels at specified times according to the NDMA classifications 
# Inputs: df of ndvi residuals 
#       start/stop indexes for the continuous sections of cleaned data
#       NDMA csv if graphing wanted 
# Outputs: df of ndvi results saved to csv
#           results are: recovery rate and Rsq and fitted values 
#                       for each recovery time period for all available data 
#

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import pickle
# import numpy.ma as ma 
from scipy.optimize import curve_fit


# with open ('precip_pixels_sample.pkl', 'rb') as file:
#     precip_df, precip_meta, precip_bound = pickle.load(file)

# with open ('ndvi_sample_res.pkl', 'rb') as file:
#     ndvi_res, ndvi_meta, ndvi_bound = pickle.load(file)

with open('Tharaka_ss.pkl', 'rb') as file:
   ss, ss_rows, ss_cols= pickle.load(file)
ss_rows = ss_rows.astype('int')
   
ndvi_res  = pd.read_csv('NDVI_residuals_Tharaka.csv') #only has 1000 rows atm 
precip_df = pd.read_csv('precip_pixels_Tharaka.csv', nrows = 1000) 

#import the drought classifications 
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

#one sample pixel 
pix =  ndvi_res.iloc[967,65:124]#.filter(like='20') 
pix.index = pd.to_datetime(pix.index, format='%Y-%m')
precip = precip_df.iloc[967].filter(like='20')
precip.index = pd.to_datetime(precip.index, format='%Y-%m')

#### Calculate the recovery rates based on NDMA drought classification dates #####################
# The dates of recovery/normal after drought periods 
recovery_idx_Th = np.array( [59, 77, 116] )#Apr 18, Oct 19, Jan 23 (ignored  104, 107, because those are kinda blips in the middle of drought)
# add for other counties 
n_recovs = len(recovery_idx_Th)

recov_start = recovery_idx_Th-5 #look 5 months back for the start of the recovery period
# most of the minimums at the end of the drought happen pretty close to the stated end of the drought
recov_stop = recovery_idx_Th+6 #look up to 6 months ahead to account for delay in veg greening 
recov_stop[recov_stop > 119] = 119 #in case there's any that are close to the end 

#Make an array with columns that show which ss pairs/rows are valid for each of the recovery periods 
ss_overlap = np.empty((len(ss_rows), n_recovs))
for x in range(n_recovs):
   ss_overlap[:, x] = (ss_cols[:, 0]<= recov_start[x]) & (ss_cols[:,1] >= recov_stop[x]) #Boolean 
ss_overlap = ss_overlap.astype('bool')

####### Calculate the recovery rates for each designated recovery period ############################

# initialize a df for results 
ndvi_results = ndvi_res.copy()
ndvi_results.iloc[:,4:] = np.nan
ndvi_results = ndvi_results.drop(columns='empty')
hlist1 = ['recov_rate_'+str(h) for h in recovery_idx_Th]
hlist2 = ['rsq_'+str(h) for h in recovery_idx_Th]
hlist1 = hlist1+ hlist2
ndvi_results[hlist1] = np.nan

for z in range(n_recovs):

    valid_rows = ss_rows[ss_overlap[:,z]]#these are the rows to look at for the first recovery period 
    n_valid_rows = len(valid_rows)
    # Grab the slices of the ndvi that we care about 
    valid_slices = ndvi_res.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5] # +4 because there are 4 extra columns at the front end of the df
    # and +5 because want the recovery stop to be inclusive  

    # Initialize an array to hold the resulting recovery rates and Rsq and fitted eqs for graphing 
    recov_rates = np.empty(n_valid_rows)
    recov_rates[:] = np.nan
    Rsq = np.empty(n_valid_rows)
    Rsq[:] = np.nan
    fits = np.empty(np.shape(valid_slices)) #this is the n_valid_rows by length of recov period (12 mo)
    fits[:] = np.nan

    a_guess, b_guess, c_guess = -0.1, -0.3, 0.05 #Might need to edit this

    for n in range(n_valid_rows): 
        row = valid_slices.iloc[n, :]
        local_min = row.values.argmin()
        sample = row[local_min:] #Find the min within this time and start there 
        x = range(sample.size) #make fake time data for this sample 
        try:
            popt, pcov = curve_fit(lambda t, a, b, c: a*np.exp(b*t)+c, x, sample, 
                            p0=(a_guess, b_guess, c_guess))
        # note that have to remove any values of sample that are zero along with corresponding x -- see if that's an issue 

            a = popt[0]
            r = popt[1] #recovery rate
            c = popt[2]
            #for plotting and finding residual
            y_curvefitted = a*np.exp(r*x)+c 
            # curve_series = pd.Series(y_curvefitted, index=sample.index) #not sure this is right 

            #Calculate the residual between the fitted curve and data 
            ss_res = np.nansum((sample - y_curvefitted)**2)
            ss_tot = np.nansum((sample - sample.mean())**2)
            rsquared = 1 - (ss_res/ss_tot)
        except Exception as e: 
            print(e)
            # if you can't calculate for some reason set to zero (nan signifies empty/not attempted)
            r= 0
            rsquared = 0
            y_curvefitted = 0


        # print('recovery rate: ', r, '\nRsq: ', rsquared)

        recov_rates[n] = r
        Rsq[n] = rsquared
        fits[n, local_min:] = y_curvefitted

        

    ##########Plot ############################
        # # fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=False)
        # ax = plt.plot(row, 'r*', label='ndvi res')
        # # ax2 = host.twinx()
        # # ax1.set_xlabel('month')
        # # ax1.set_ylabel('monthly precip mm/mo' )
        # # # ax1.set_ylim(0, 600)
        # # ax1.bar(x=precip.index, height=precip, width=20, label='monthly precip mm')


        # # ax.set_ylabel('NDVI residual')
        # plt.ylabel('ndvi_residual')
        # # ax2.set_ylim(-0.25, 0.25)
        # rec = 'fitted recovery, r='+str(round(r, 3))+' Rsq='+str(round(rsquared, 2))
        # plt.plot(fits[n], 'g-', label=rec)
        # # fig.legend()
        # # ax.grid(axis='x', which='major')
        # # ax.grid(axis='x', which='major')
        # plt.legend()
        # # ax1.pcolor(date_plus, ax1.get_ylim(), 
        # #         NDMA['Tharaka'].map(color_dict).values[np.newaxis], 
        # #         cmap=CMAP, alpha=0.4,
        # #         linewidth=0, antialiased = True)
        # #lol don't know how to do this to both at once
        # # ax2.pcolor(date_plus, ax2.get_ylim(), 
        # #         NDMA['Tharaka'].map(color_dict).values[np.newaxis], 
        # #         cmap=CMAP, alpha=0.4,
        # #         linewidth=0, antialiased = True)

        # # plt.autofmt_xdate(rotation=45)
        # #fix this -- set the
        # # cbar=fig.colorbar(cm.ScalarMappable(cmap=CMAP), ax=ax1, 
        # #                 location='top', shrink = 0.5,
        # #                 pad=0.2,
        # #                 label='NDMA Drought Status')
        # # cbar.set_ticks([0.12, 0.35, 0.62, 0.87])
        # # cbar.set_ticklabels(['Alarm', 'Alert', 'Recovery', 'Normal'])
        # plt.show()
        # pass

    # Save the lists for each recovery date to the final df 
    ndvi_results.loc[valid_rows, 'recov_rate_'+str(recovery_idx_Th[z])] = recov_rates
    ndvi_results.loc[valid_rows, 'rsq_'+str(recovery_idx_Th[z])] = Rsq
    ndvi_results.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5]= fits 
    print('recovery done- '+str(z))

ndvi_results.dropna(axis=0, thresh=8, inplace=True, ignore_index=False) #drop any rows that don't have at least 8 non empty cells (4 for the labels and 4+ results)
# keep the index labels 
#Save to a csv 
ndvi_results.to_csv('ndvi_results_Tharaka.csv', encoding='utf-8')
print('donezo')
