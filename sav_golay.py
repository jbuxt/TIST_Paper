# From 
# Applies the method from Chen et al 2004 for NDVI time series reconstruction
# slightly modified for my purposes
## NOT USED IN FINAL IMPLEMENTATION

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter

def savitzky_golay_filtering(timeseries, wnds=[5, 4], orders=[2, 3], limit = 3, debug=False):                                     

    ## Step 1: interopolate linearly between up to 3 missing points but not outside that 
    interp_ts = timeseries.interpolate(method='linear', limit=limit, limit_area='inside')
    final_ts = interp_ts.copy()
    final_ts.iloc[:]=np.nan #create output series with right shape and nans in right places

    ## missing: doesn't go through and replace any dramatic jumps of 0.4 or more. That's fine for my purposes.

    ## Step 1.1 -  are there any holes still missing? If so,
    # get the three longest portions of continuous data

    # nans = interp_ts.isna()
    # runs = nans.groupby(nans.cumsum()).agg({'index': ['count', 'min', 'max']})
    # nans = interp_ts.isnull().astype(int).groupby(interp_ts.notnull().astype(int).cumsum()).cumsum()

    # Extract out relevant column from dataframe as array
    m = np.concatenate(( [True], np.isnan(interp_ts.values), [True] ))  # Mask
    #kinda assuming there are no completely empty pixels 
    #https://stackoverflow.com/questions/41494444/pandas-find-longest-stretch-without-nan-values

    ss = np.flatnonzero(m[1:] != m[:-1]).reshape(-1,2)   # Start-stop limits
    intervals, dum = np.shape(ss) #how many intervals are there 
    #get the three longest by index
    if intervals > 3: #if more than 3 pick the top 3
        ss = ss[np.argpartition((ss[:,1] - ss[:,0]), -3)[-3:]]
        intervals = 3
    
    # start,stop = ss[(ss[:,1] - ss[:,0]).argmax()]  # Get max interval, interval limits
    for x in range(0,intervals):
        start, stop = ss[x, :] #get idx of the interval 
        temp_ts = interp_ts.iloc[start:stop]

    
    #apply the smoothing on each of these sections 
        #put them all back together and return 


        ## wnds = m, orders = d from paper 
        ## Step 1.5?: selects the combo of m and d that has best fit
        # according to the least squares (NOT IMPLEMENTED)                                                                                          
        wnd, order = wnds[0], orders[0]
        old_F = 1e8
        new_F = 1e7 
        W = []
        iter = 0 

        #STep 2: smooth with the SG filter to get the long term trend
        # can use mode = 'wrap' -- check the notes and see if cyclic is good option
        smoother_ts = savgol_filter(temp_ts, window_length=wnd, polyorder=order)                                     
        diff = smoother_ts - temp_ts
        sign = diff > 0 # any places where the smoothed trend is higher than og trend  
        max_diff = np.max(np.abs(diff))                                                                                                                  

        ## Step 3 Calculate the weights
        #weight where the og trend is higher than the smoothed trned (diff < 0)
        # are given higher weight
        W = [(1 if (d<0)  else (1- abs(d)/max_diff)) for d in diff]
        # print(W)                                                                                                                            
        
        wnd, order = wnds[1], orders[1]
        while (new_F < old_F) and (iter < 10):
            # Step 4: generate new series, replacing the things in 
            # interp_ts with the things from the smoothed trend that are higher at 
            # each point 
            ##REPEAT FROM HERE
            smooth_ts = smoother_ts * sign + temp_ts * (1 - sign)
            '''
            Ni(new) = interp_ts when interp > smoother, latest when interp < smoother
            '''
            # print('smoother: ', smoother_ts)
            # print('interp: ', interp_ts)
            # print('result (smooth): ', smooth_ts)

            # Step 5: Fit new NDVI with SG filter
            # set new m and d -  smaller m and larger d are recommended
            # Chen 2004 used m=4 and d=6 
            #except this savgol filter cannot hander an order higher than the window size 
            smoother_ts = savgol_filter(smooth_ts, window_length=wnd, polyorder=order)
            
            ## Step 6: Calculate fitting effect index 
            # how well do fitted values approach the more highly weighted og points
            diff = smoother_ts - temp_ts # Find the difference again                                
            old_F = new_F
            new_F = np.sum(np.abs(diff) * W)
            iter +=1
            sign = diff > 0 ## have to update the sign st that new trend is filled right 
                                                                                            
            # print(iter, ' : ', new_F)
            #then repeat again unless the new F score is bigger than the last one
            # indicating a worse fit, in which case values are not replaced and exits
        
        #assign the smoothed section to the output series then repeat for other intervals
        final_ts.iloc[start:stop] = smooth_ts

    if debug:
        return final_ts, interp_ts
    return final_ts