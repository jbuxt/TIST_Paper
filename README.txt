Author: Madeleine Henderson 
Date: May-Sept 2023
Purpose: MSc Thesis, University of Exeter 
Title: Impact of community agroforestry on resilience to drought in Kenya 

Scripts for estimating recovery rates: 
1. Initialize google earth engine authorization: GEE_start.py
1a. Create masks for the counties and TIST groves: Import_Shapefiles.py and Clip_Rasters.py
2. Download monthly composite and cloud masked TIF files of NDVI to Google Drive 
   (have to edit dates to do in batches). Each TIF is one month: Get_Precip_And_Veg_Monthly.py
3. Turn the downloaded TIF files into CSVs with the pixels through time for 
   each county (N pixels x 120 months): Intake_Veg_and_make_pix_lists.py
4. Fill, deseason, and detrend the NDVI. Creates CSVs of residuals (N pixels x 120 months): Intake_Veg_and_make_pix_lists.py
4a. Utilizes STL_Fitting.py from Smith, Traxl, and Boers 2022. 
5. Estimate the recovery rate at the indicated times. Saves CSV of curve fit estimations, 
   estimated rate, Rsquared, and local minimum for each recovery period for each pixel with enough
   valid data to be attempted: calc_return_rate.py

Scripts for analyzing data, adding additional columns for analysis, and creating visualizations: 
- Apply_landcover_mask.py
- Creates tif files from dataframes: results_to_maps.py and df_to_map.py
- Plots residual and fitted recovery rate for input pixel location: make_figures_recoveries.py
- Folium web maps: make_interactive_map_results.py and make_interactive_map.py
- find_distance_to_tist.py
- change_over_time.py
- apply_other_masks.py
- interpretation.py
- visualizations.py
- Statistical testing: stats.py
- yearly_avg_precip.py

Scripts from previous versions of methodology: 
- sav_golay.py
- Intake_Veg_and_make_pix_lists_8DAY.py
- Import_saved_files.py
