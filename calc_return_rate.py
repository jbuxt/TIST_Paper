# Calculate the recovery rate for pixels at specified times according to the NDMA classifications 
# Inputs: df of ndvi residuals 
#       OLD: start/stop indexes for the continuous sections of cleaned data
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
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# county = input('Input the county to process: ')
county = 'Tharaka'
n_obvs = 9 #number of vals out of 12 to accept for recovery calculation 

# with open('./intermediate_landsat/'+county+'_ss.pkl', 'rb') as file:
#    ss, ss_rows, ss_cols= pickle.load(file)
# ss_rows = ss_rows.astype('int')
   
#CHGNE TO BE FROM INTERMEDIATE FOLDER IF NECESSARY
#ADD INDX COL = 0 BACK IN BEFORE DOING ON SERVER
ndvi_res  = pd.read_csv('ndvi_residuals_'+county+'_V2.csv', index_col=0, nrows = 5000) 
#keep the index column as that is what the ss_rows corresponds to: 


#TEMPORARY FOR NROWS LIMIT
# ss_cols = ss_cols[ss_rows < 5000]
# ss_rows = ss_rows[ss_rows < 5000]


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
elif county == 'Embu':
    recovery_idx = np.array([54, 59, 77, 104, 114]) #ignore 119 
else: 
    print('incorrect county entered')
    #program will crash later lol

n_recovs = len(recovery_idx)

recov_start = recovery_idx-5 #look 5 months back for the start of the recovery period
# most of the minimums at the end of the drought happen pretty close to the stated end of the drought
recov_stop = recovery_idx+6 #look up to 6 months ahead to account for delay in veg greening (effectively means that min has to be within 3 mo of the recovery date)
#extending this makes it too hard to find the right local min
recov_stop[recov_stop > 119] = 119 #in case there's any that are close to the end 

# r59 =  ndvi_df.iloc[:, (59-5):(59+6)]
# print('% pix missing for r59: ', r59.isna().sum().sum() / (r59.size))
# r77 =  ndvi_df.iloc[:, (77-5):(77+6)]

'''
#Make an array with columns that show which ss pairs/rows are valid for each of the recovery periods 
ss_overlap = np.empty((len(ss_rows), n_recovs))
for x in range(n_recovs):
   ss_overlap[:, x] = (ss_cols[:, 0]<= recov_start[x]) & (ss_cols[:,1] >= recov_stop[x]) #Boolean 
ss_overlap = ss_overlap.astype('bool')
'''
####### Calculate the recovery rates for each designated recovery period ############################

# initialize a df for results 
ndvi_results = ndvi_res.copy()
ndvi_results.iloc[:,4:-2] = np.nan #keep the mean and stdev 
#ndvi_results.drop(columns='empty', inplace= True)
hlist1 = ['recov_rate_'+str(h) for h in recovery_idx]
hlist2 = ['rsq_'+str(h) for h in recovery_idx]
#keep the local mins for later analysis
hlist3 = ['mins_'+str(h) for h in recovery_idx]
hlist1 = hlist1+ hlist2 + hlist3
ndvi_results[hlist1] = np.nan

#for use in loop
temp = np.zeros(6) #how many of the mean to add 
a_guess, b_guess, c_guess = -0.05, -0.2, .05  #Somewhat optimized with testing 

for z in range(n_recovs): #Z goes through the recoveries 
    print('starting recovery calculation for recovery number '+str(z))
    '''
    valid_rows = ss_rows[ss_overlap[:,z]]#these are the rows to look at for the first recovery period 
    n_valid_rows = len(valid_rows)
    '''
    #grab any rows that have at least n_obvs observations in the recovery window 
    # +4 because there are 4 extra columns at the front end of the df
    # and +5 because want the recovery stop to be inclusive  
    valid_rows = ndvi_res[ndvi_res.iloc[:, recov_start[z]+4:recov_stop[z]+5].count(axis=1) >= n_obvs].index
    n_valid_rows = len(valid_rows)

    # Grab the slices of the ndvi that we care about 
    valid_slices = ndvi_res.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5] 
    
    #get the means/stdevs for those rows (can use loc and iloc interchangeably still because no deleted rows yet)
    valid_means = ndvi_res.loc[valid_rows, 'mean']
    valid_stdevs = ndvi_res.loc[valid_rows, 'stdev'] #index is true to the original df 

    # Initialize an array to hold the resulting recovery rates and Rsq and fitted eqs for graphing 
    recov_rates = np.empty(n_valid_rows)
    recov_rates[:] = np.nan
    Rsq = np.empty(n_valid_rows)
    Rsq[:] = np.nan
    fits = np.empty(np.shape(valid_slices)) ##this is the n_valid_rows by length of recov period (12 mo)
    fits[:] = np.nan
    #save the value of the local minimums for later too 
    mins = np.empty(n_valid_rows)
    mins[:] = np.nan

    for n in range(n_valid_rows): # N is going through the number of valid rows 
        row = valid_slices.iloc[n, :] #Have to use iloc because loc has the original index 
        local_min = row.argmin(skipna = True)
        min_val = row[local_min] 

        #check that the mean is at least 1 std dev from the mean 
        #in order to try
        if min_val < (valid_means.iloc[n] - valid_stdevs.iloc[n]): #iloc good 
            
            sample = row[local_min:] #Find the min within this time and start there 
            
            # concat the mean of the residuals to the end of the sample to make sure it recovers to the 'normal' state
            # and to deal with any recoveries that are very high pos residuals 
            #need to have at least 3 of the orig pts to get anything - if not it will error out 
            #(THis could be changed if I did a diff fitting method - using the default scipy curvefit option rn)
            #but have to have a check here so it doesn't get covered up by adding 12 means afterwards
            #if len(sample) >=3: 
            if sample.count() >=3: #require at least 3 real data points incl the min to fit 
                temp[:] = valid_means.iloc[n] #iloc good
                sample = pd.concat([sample, pd.Series(temp)]) 
            
            x = np.array(range(sample.size)) #make fake time data for this sample - can't just be a range for the curve_fit

            try:
                popt, pcov = curve_fit(lambda t, a, b, c: a*np.exp(b*t)+c, x, sample, 
                                p0=(a_guess, b_guess, c_guess), nan_policy= 'omit') #ignores nan values


                a = popt[0]
                r = popt[1] #recovery rate
                c = popt[2]
                
                #for plotting and finding residual
                y_curvefitted = a*np.exp(r*x)+c 

                #PLOTTING FOR TESTING
                # plt.plot(x, sample, 'r*')
                # plt.plot(x, y_curvefitted, 'b-')
                # # std1 = valid_means.iloc[n] - valid_stdevs.iloc[n]
                # # std2 = valid_means.iloc[n] - 2* valid_stdevs.iloc[n]
                # # plt.plot([0, 1, 2, 3, 4,5], [std1, std1,std1,std1,std1,std1 ], 'y-')
                # # plt.plot([0, 1, 2, 3, 4,5], [std2, std2,std2,std2,std2,std2 ], 'g-')
                # plt.show()

                #Calculate the residual between the fitted curve and data, ignoring the final 'fake' data
                y_curvefitted = y_curvefitted[0:-6] #don't keep the last 6
                sample = sample.iloc[0:-6]
                ss_res = np.nansum((sample - y_curvefitted)**2)
                ss_tot = np.nansum((sample - sample.mean())**2)
                rsquared = 1 - (ss_res/ss_tot)
                
                #Rsqared outside of 0-1 indicates nonsensical result/wrong model
                #Shifting more than -1 or +0.5 also indicates a v bad model since all data is in the +/- 0.3 range 
                #Having a positive a is also bad model since should be a negative 
                #These will get set to 10 as attempted fit but bad model 
                if (rsquared < 0) or (rsquared > 1) or (c< -1) or (c>0.5) or (a > 0.1) : 
                    raise Exception('nonsensical model')
                
            except Exception as e: 
                print(e)
                # if you can't calculate for some reason set to 10 (nan signifies empty/not attempted)
                #could be not enough data/min at the end of the sample 
                r= 10
                rsquared = 10
                y_curvefitted = 10
        else: #IF the min wasn't low enough- no disturbance/recovery -- saving for looking at resistance later
            r= 15
            rsquared = 15
            y_curvefitted = 15 

        # print('recovery rate: ', r, '\nRsq: ', rsquared)

        recov_rates[n] = r
        Rsq[n] = rsquared
        fits[n, local_min:] = y_curvefitted
        mins[n] = min_val #for testing only

    # Save the lists for each recovery date to the final df 
    #loc or iloc is fine here 
    ndvi_results.loc[valid_rows, 'recov_rate_'+str(recovery_idx[z])] = recov_rates
    ndvi_results.loc[valid_rows, 'rsq_'+str(recovery_idx[z])] = Rsq
    ndvi_results.iloc[valid_rows, recov_start[z]+4:recov_stop[z]+5]= fits 
    ndvi_results.loc[valid_rows, 'mins_'+str(recovery_idx[z])] = mins
    print('recovery done- '+str(z))

ndvi_results.dropna(axis=0, thresh=8, inplace=True, ignore_index=False) #drop any rows that don't have at least 8 non empty cells (4 for the labels and 4+ results)
# keep the index labels- MUST USE LOC FROM HERE ON OUT 
#Save to a csv 
ndvi_results.to_csv('ndvi_results_'+county+'TESTING_V2.csv', encoding='utf-8', index=True)

print('donezo')
