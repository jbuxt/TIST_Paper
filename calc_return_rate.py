#Calculate the recovery rate for pixels 
# and ?? 
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


with open ('precip_pixels_sample.pkl', 'rb') as file:
    precip_df, precip_meta, precip_bound = pickle.load(file)

with open ('ndvi_sample_res.pkl', 'rb') as file:
    ndvi_res, ndvi_meta, ndvi_bound = pickle.load(file)

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
pix =  ndvi_res.iloc[20].filter(like='20') 
pix.index = pd.to_datetime(pix.index, format='%Y-%m')
precip = precip_df.iloc[20].filter(like='20')
precip.index = pd.to_datetime(precip.index, format='%Y-%m')

'''
have a df with dates vals and empty column 
have list of idx of filled parts if flattened 

method 1: look for single drop and recovery as in smith 
-- advantage: can just iterate through each thing in a flattened list? 

method 2: look for drop and recovery in date ranges pertaining to specific droughts 

-- what i don't have: a way to connect the list of idx to dates and pixels without flattening and unflattening
could i do math on the list of idx to get it all working for a 2d array which is then easier to connect to dates 
sth like modulo and subtract to get it all back in the 0-120 range 

121
'''

########### Calc recovery rate sample ##############3
#pix is a pd series
sample = pix['2019-01':'2020-06-01'].astype("float32") #get relevant part 
#-- now need to tell it where to look 
#need to probably include clause that if the min isn't more than X% diff, then 
#there was nothing to recover from 

sample = sample[sample.values.argmin():-1] #get everything from minimum to the end  
#change-- specify how long i'm looking for recovery? 
x = range(sample.size) #make fake time data for this sample 

#potentially need to edit this 
a_guess, b_guess, c_guess = 1, -0.01, 1

popt, pcov = curve_fit(lambda t, a, b, c: a*np.exp(b*t)+c, x, sample, 
                       p0=(a_guess, b_guess, c_guess))

# note that have to remove any values of sample that are zero along with corresponding x -- see if that's an issue 
a = popt[0]
r = popt[1] #recovery rate
c = popt[2]
#for plotting and finding residual (do i need to find residual?? )
y_curvefitted = a*np.exp(r*x)+c 
curve_series = pd.Series(y_curvefitted, index=sample.index)

#Calculate the residual between the fitted curve and data 
ss_res = np.nansum((sample - y_curvefitted)**2)
ss_tot = np.nansum((sample - sample.mean())**2)
R_sq = 1 - (ss_res/ss_tot)

print('recovery rate: ', r, '\nRsq: ', R_sq)


##########Plot ############################
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=False)
# ax2 = host.twinx()
ax1.set_xlabel('month')
ax1.set_ylabel('monthly precip mm/mo' )
# ax1.set_ylim(0, 600)
ax1.bar(x=precip.index, height=precip, width=20, label='monthly precip mm')


ax2.set_ylabel('NDVI residual')
# ax2.set_ylim(-0.25, 0.25)
ax2.plot(pix, 'r*', label='ndvi res')
rec = 'fitted recovery, r='+str(round(r, 3))+' Rsq='+str(round(R_sq, 2))
ax2.plot(curve_series, 'g-', label=rec)
# fig.legend()
ax1.grid(axis='x', which='major')
ax2.grid(axis='x', which='major')
ax2.legend()
ax1.pcolor(date_plus, ax1.get_ylim(), 
           NDMA['Tharaka'].map(color_dict).values[np.newaxis], 
           cmap=CMAP, alpha=0.4,
           linewidth=0, antialiased = True)
#lol don't know how to do this to both at once
ax2.pcolor(date_plus, ax2.get_ylim(), 
           NDMA['Tharaka'].map(color_dict).values[np.newaxis], 
           cmap=CMAP, alpha=0.4,
           linewidth=0, antialiased = True)

fig.autofmt_xdate(rotation=45)
#fix this -- set the
cbar=fig.colorbar(cm.ScalarMappable(cmap=CMAP), ax=ax1, 
                  location='top', shrink = 0.5,
                  pad=0.2,
                  label='NDMA Drought Status')
cbar.set_ticks([0.12, 0.35, 0.62, 0.87])
cbar.set_ticklabels(['Alarm', 'Alert', 'Recovery', 'Normal'])
plt.show()

print('done')
