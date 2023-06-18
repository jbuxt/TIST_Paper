def robust_stl(series, period, smooth_length=7):
    from statsmodels.tsa.seasonal import STL
    def nt_calc(f,ns):
        '''Calcualte the length of the trend smoother based on
        Cleveland et al., 1990'''
        nt = (1.5*f)/(1-1.5*(1/ns)) + 1 #Force fractions to be rounded up
        if int(nt) % 2. == 1:
            return int(nt)
        elif int(nt) % 2. == 0:
            return int(nt) + 1            
    def nl_calc(f):
        '''Calcualte the length of the low-pass filter based on
        Cleveland et al., 1990'''
        if int(f) % 2. == 1:
            return int(f)
        elif int(f) % 2. == 0:
            return int(f) + 1
    ### REFERENCE FOR LOESS PARAMS BASED ON ORIGINAL FORTRAN CODE ###
    # np = f              # period of seasonal component
    # ns = 7              # length of seasonal smoother
    # nt = nt_calc(f,ns)  # length of trend smoother
    # nl = nl_calc(f)     # length of low-pass filter
    # isdeg = 1           # Degree of locally-fitted polynomial in seasonal smoothing.
    # itdeg = 1           # Degree of locally-fitted polynomial in trend smoothing.
    # ildeg = 1           # Degree of locally-fitted polynomial in low-pass smoothing.
    # nsjump = None       # Skipping value for seasonal smoothing.
    # ntjump = 1          # Skipping value for trend smoothing. If None, ntjump= 0.1*nt
    # nljump = 1          # Skipping value for low-pass smoothing. If None, nljump= 0.1*nl
    # robust = True       # Flag indicating whether robust fitting should be performed.
    # ni = 1              # Number of loops for updating the seasonal and trend  components.
    # no = 3              # Number of iterations of robust fitting. The value of no should
    #                       be a nonnegative integer. If the data are well behaved without 
    #                       outliers, then robustness iterations are not needed. In this case
    #                       set no=0, and set ni=2-5 depending on how much security you want
    #                       that the seasonal-trend looping converges. If outliers are present 
    #                       then no=3 is a very secure value unless the outliers are radical, 
    #                       in which case no=5 or even 10 might be better. If no>0 then set ni 
    #                       to 1 or 2. If None, then no is set to 15 for robust fitting, 
    #                       to 0 otherwise.
    #seasonal_jump=1,trend_jump=1, low_pass_jump=1,
    res = STL(series, period, seasonal=smooth_length, trend=nt_calc(period,smooth_length), low_pass=nl_calc(period), seasonal_deg=1, trend_deg=1, low_pass_deg=1, robust=True)
    return res.fit() #ni, no optional