import pickle 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


with open ('precip_pixels_sample.pkl', 'rb') as f:
    precip_df, precip_meta, precip_bounds = pickle.load(f)

precip_df_calc = precip_df.astype("float32").drop(columns = ['row','col', 'tist', 'county']) #mean of float 16 overflows

#what is average precip per month over time in area 
monthly_av = precip_df_calc.mean(axis = 0)

multiyr_av = pd.DataFrame(columns = range(1, 13))
for m in range(1,13):
    mo = '-'+str(m).zfill(2)
    multiyr_av.at[0, m] = monthly_av.filter(like=mo, axis=0).mean()
print(multiyr_av)
#average by month over all the years 

# could use this to give my normalized deficit 

pass
