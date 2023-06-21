#take a few lists of pixels and deseason and detrend 

# import geopandas as gp 
import pandas as pd
# import rasterio as rs
# from rasterio import features
import numpy as np 
import matplotlib.pyplot as plt 
import pickle
import numpy.ma as ma 
from scipy.optimize import curve_fit


with open ('precip_pixels_sample.pkl', 'rb') as file:
    precip_df, precip_meta, precip_bound = pickle.load(file)

with open ('ndvi_sample_res.pkl', 'rb') as file:
    ndvi_res, ndvi_meta, ndvi_bound = pickle.load(file)

#import the drought classifications 
NDMA = pd.read_csv('NDMA_droughts.csv', index_col=0, parse_dates=['Date']) 
# NDMA.index = pd.to_datetime(NDMA.index, format='%Y-%m-%d') #index is datetime

#extend to include the data we don't know anything about
extra = pd.DataFrame(columns = NDMA.columns, index = pd.date_range(start='2013-05-01', periods=40, freq='MS'))
extra.fillna
NDMA = pd.concat([NDMA, extra]).sort_index()

date_list = NDMA.index
date_plus = pd.date_range(start='5/1/2013', periods=121, freq='MS') #need one that's +1 in length for the color graph 

colors = {'Recovery':2, 'Alert':1, 'Alarm':0,'Normal':3}

pix =  ndvi_res.iloc[20].filter(like='20') #get one sample from a pixel
precip = precip_df.iloc[20].filter(like='20')

########### Calc recovery rate sample ##############3
#pix is a pd series
sample = pix['2019-01':'2020-06-01'].astype("float32") #get relevant bit and flip over x axis

sample = sample[sample.values.argmin():-1] #get everything from minimum to the end  
x = range(sample.size) #make fake time data

#potentially need to edit this 
a_guess, b_guess, c_guess = 1, -0.01, 1

popt, pcov = curve_fit(lambda t, a, b, c: a*np.exp(b*t)+c, x, sample, 
                       p0=(a_guess, b_guess, c_guess))

# note that have to remove any values of sample that are zero along with corresponding x -- see if that's an issue 
a = popt[0]
r = popt[1] #recovery rate
c = popt[2]
#for plotting
y_curvefitted = a*np.exp(r*x)+c 




##########Plot ############################
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, sharey=False)
# ax2 = host.twinx()
ax1.set_xlabel('month')
ax1.set_ylabel('monthly precip mm/mo' )
# ax1.set_ylim(0, 600)
ax1.bar(x=date_list, height=precip, width=20, label='monthly precip mm')


ax2.set_ylabel('NDVI residual')
# ax2.set_ylim(-0.25, 0.25)
ax2.plot(date_list, pix, 'r*', label='ndvi res')
fig.legend()
ax1.grid(axis='x', which='major')
ax2.grid(axis='x', which='major')

ax1.pcolor(date_plus, ax1.get_ylim(), 
           NDMA['Tharaka'].map(colors).values[np.newaxis], 
           cmap='RdYlGn', alpha=0.4,
           linewidth=0, antialiased = True)
#lol don't know how to do this to both at once
ax2.pcolor(date_plus, ax2.get_ylim(), 
           NDMA['Tharaka'].map(colors).values[np.newaxis], 
           cmap='RdYlGn', alpha=0.4,
           linewidth=0, antialiased = True)

fig.autofmt_xdate(rotation=45)

plt.show()

print('done')
