import pickle
import rasterio as rs

with open ('imported_monthly_veg_14-15.pkl', 'rb') as f:
    veg_meta, veg_bound, ndvi, msavi2, start_yr, end_yr = pickle.load(f)
print(veg_meta)