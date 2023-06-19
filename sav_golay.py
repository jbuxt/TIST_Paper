# From 
# https://gis.stackexchange.com/questions/173721/ ...
# reconstructing-modis-time-series-applying-savitzky-golay-filter-with-python-nump/173747#173747
# Applies the method from Chen et al 2004 for NDVI time series reconstruction
# slightly modified for my purposes

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter

def savitzky_golay_filtering(timeseries, wnds=[7, 4], orders=[2, 3], debug=False):                                     
    # interp_ts = pd.Series(timeseries)
    ## Step 1: interopolate linearly between any missing points
    interp_ts = timeseries.interpolate(method='linear', limit=14)
    ## missing: doesn't go through and replace any dramatic jumps of 0.4 or more
    # smooth_ts = interp_ts  
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
    smoother_ts = savgol_filter(interp_ts, window_length=wnd, polyorder=order)                                     
    diff = smoother_ts - interp_ts
    sign = diff > 0 # any places where the smoothed trend is higher than og trend  
    max_diff = np.max(np.abs(diff))                                                                                                                  

    ## Step 3 Calculate the weights
    #weight where the og trend is higher than the smoothed trned (diff < 0)
    # are given higher weight
    W = [(1 if (d<0)  else (1- abs(d)/max_diff)) for d in diff]
    # print(W)                                                                                                                            
    
    wnd, order = wnds[1], orders[1]
    while (new_F < old_F) and (iter < 1000):
        # Step 4: generate new series, replacing the things in 
        # interp_ts with the things from the smoothed trend that are higher at 
        # each point 
        ##REPEAT FROM HERE
        smooth_ts = smoother_ts * sign + interp_ts * (1 - sign)
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
        diff = smoother_ts - interp_ts # Find the difference again                                
        old_F = new_F
        new_F = np.sum(np.abs(diff) * W)
        iter +=1
        sign = diff > 0 ## have to update the sign st that new trend is filled right 
                                                                                          
        # print(iter, ' : ', new_F)
        #then repeat again unless the new F score is bigger than the last one
        # indicating a worse fit, in which case values are not replaced and exits


    if debug:
        return smooth_ts, interp_ts
    return smooth_ts