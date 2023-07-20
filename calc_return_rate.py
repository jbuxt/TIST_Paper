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
import pickle
# import numpy.ma as ma 
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

county = input('Input the county to process: ')

with open(county+'_ss.pkl', 'rb') as file:
   ss, ss_rows, ss_cols= pickle.load(file)
ss_rows = ss_rows.astype('int')
   
ndvi_res  = pd.read_csv('ndvi_residuals_'+county+'.csv', index_col=0) #only has 1000 rows atm 
#keep the index column as that is what the ss_rows corresponds to: 
    

#### Calculate the recovery rates based on NDMA drought classification dates #####################
# The dates of recovery/normal after drought periods 
if county == 'Laikipia':
    recovery_idx = np.array([54, 59, 78])#ignore 119, too recent
elif county == 'Meru':
    recovery_idx = np.array([42, 54, 59, 77]) #ignore 119 
elif county == 'Tharaka':
    recovery_idx = np.array([59, 77])#Apr 18, Oct 19, Jan 23 (ignored  104, 107, 116 because those are kinda blips in the middle of drought or too close to end )
elif county == 'Nyeri':
    recovery_idx = np.array([54, 59, 77]) #ignore 119
# elif county == 'Kirinyaga':
#     recovery_idx = np.array([])#none - no drought classifications -- do not try this
elif county == 'Embu':
    recovery_idx = np.array([54, 59, 77, 104, 114]) #ignore 119 
else: 
    print('incorrect county entered')
    #program will crash later lol

n_recovs = len(recovery_idx)

recov_start = recovery_idx-5 #look 5 months back for the start of the recovery period
# most of the minimums at the end of the drought happen pretty close to the stated end of the drought
recov_stop = recovery_idx+6 #look up to 6 months ahead to account for delay in veg greening 
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
ndvi_results.drop(columns='empty', inplace= True)
hlist1 = ['recov_rate_'+str(h) for h in recovery_idx]
hlist2 = ['rsq_'+str(h) for h in recovery_idx]
hlist1 = hlist1+ hlist2
ndvi_results[hlist1] = np.nan

for z in range(n_recovs):
    print('starting recovery calculation for recovery number '+str(z))
    valid_rows = ss_rows[ss_overlap[:,z]]#these are the rows to look at for the first recovery period 
    n_valid_rows = len(valid_rows)
    # Grab the slices of the ndvi that we care about 
    valid_slices = ndvi_res.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5] # +4 because there are 4 extra columns at the front end of the df
    # and +5 because want the recovery stop to be inclusive  
    
    #get the means for those rows (can use loc and iloc interchangeably still because no deleted rows yet)
    valid_means = ndvi_res.loc[valid_rows, 'mean']

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
        # concat the mean of the residuals to the end of the sample to make sure it recovers to the 'normal' state
        # and to deal with any recoveries that are very high residuals 
        temp = np.zeros(12)
        temp[:] = valid_means.iloc[n]
        sample = pd.concat([sample, pd.Series(temp)]) 
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

            plt.plot(x, sample, 'r*')
            plt.plot(x, y_curvefitted, 'b-')
            plt.show()

        except Exception as e: 
            # print(e)
            # if you can't calculate for some reason set to 10 (nan signifies empty/not attempted)
            r= 10
            rsquared = 10
            y_curvefitted = 10


        # print('recovery rate: ', r, '\nRsq: ', rsquared)

        recov_rates[n] = r
        Rsq[n] = rsquared
        fits[n, local_min:] = y_curvefitted[0:-12] #don't keep the extra 12 mo for the plotting 

    # Save the lists for each recovery date to the final df 
    ndvi_results.loc[valid_rows, 'recov_rate_'+str(recovery_idx[z])] = recov_rates
    ndvi_results.loc[valid_rows, 'rsq_'+str(recovery_idx[z])] = Rsq
    ndvi_results.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5]= fits 
    print('recovery done- '+str(z))

ndvi_results.dropna(axis=0, thresh=8, inplace=True, ignore_index=False) #drop any rows that don't have at least 8 non empty cells (4 for the labels and 4+ results)
# keep the index labels- MUST USE LOC FROM HERE ON OUT 
#Save to a csv 
ndvi_results.to_csv('ndvi_results_'+county+'.csv', encoding='utf-8', index=True)

print('donezo')
