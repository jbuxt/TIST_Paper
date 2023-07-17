# take output recovery rates / Rsq etc and see what things look like 
#

# import geopandas as gp 
import pandas as pd
import rasterio as rs
# from rasterio import features
import numpy as np 
import pickle
import matplotlib.pyplot as plt 
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap

####################################################################
# Import results 

county = 'Tharaka'

df = pd.read_csv('./RESULTS/ndvi_results_'+county+'.csv', index_col=0)
#this has columns for the fits as well as the results 
df.drop(columns = df.filter(like='20').columns.tolist(), inplace=True)

###################################################################
# get some counts

## How many pixels with any results out of the total? 
# #Number of pixels in each county: 
# n_Laikipia = 10837687 
# n_Meru = 7720270
n_Tharaka = 2990072
# n_Nyeri = 3733796
# n_Kirinyaga = 1652252
# n_Embu = 3170195

nrows, ncols = df.shape
nrecovs = int((ncols-4)/2)

print('Pixels with any results calculated out of total for {0:s}: {1:0.2f}'.format(county, nrows/n_Tharaka))

n_attempted = np.zeros(nrecovs,)
print('Percent pixels where recovery calculation attempted: ')
for n in range(nrecovs):
    n_attempted[n] = df.iloc[:, 4+n].count()#counts not NA values 
    print('recovery {0:d}: {1:0.2f}'.format( n, n_attempted[n]/n_Tharaka))

n_successful = np.zeros(nrecovs,)   
print('Percent pixels where recovery calculation successful: ')
for n in range(nrecovs):
    n_successful[n] = n_attempted[n] - (df.iloc[:, 4+n] == 10.0000).sum() #unsuccessful attemps set to 10 
    print('recovery {0:d}: {1:0.2f}', n, n_successful[n]/n_Tharaka)

###########################################################
# Make some histograms 

#Histogram of each recovery and sorted by tist vs non tist
df[df == 10.00] = np.nan #Get rid of all the 10s now that we know how many there were 


# hist1 = df.filter(like='recov').hist(layout=[nrecovs, 1], bins=range(-60, 20), by=df['tist']) #by=ndvi['tist'],

for n in range(nrecovs):
    plt.subplot(nrecovs, 1, n+1)
    plt.hist((df[df.tist == 1].iloc[:, n+4], df[df.tist == 0].iloc[:, n+4]), 
             bins=range(int(df.iloc[:, n+4].min()), int(df.iloc[:, n+4].max())))
    plt.legend(loc = 'upper right')
    plt.title(df.columns[n+4])



plt.suptitle('Recovery rates in ('+county+')')
plt.ylabel('count')
plt.xlabel('Recovery rate')
# plt.legend()



print('donezo')