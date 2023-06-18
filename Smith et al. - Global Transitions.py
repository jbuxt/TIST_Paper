# -*- coding: utf-8 -*-

import numpy as np
import scipy.stats, scipy.signal
import pandas as pd

### Code for Transition Detection and Recovery Fitting ###
p0 = [-1, -0.1]
bounds = ([-np.inf, -np.inf], [0, 0])

def exp_fit(x, a, b):
    return a*np.exp(b*x)

def exp_jac(x, a, b):
    jac = np.array([np.exp(b*x), a*x*np.exp(b*x)]).T
    return jac

def get_rsq(ser, popt):
    residuals = ser.values - exp_fit(np.arange(ser.shape[0]), *popt)
    ss_res = np.nansum(residuals**2)
    ss_tot = np.nansum((ser.values - np.nanmean(ser.values))**2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared

def transition(x, win_size, pct=99, ret=False):
    av_derivative = np.empty(x.shape)
    av_derivative.fill(np.nan)
    half_window = int(win_size / 2)
    ln = x.shape[0]
    for i in range(half_window, ln - half_window):
        av_derivative[i] = np.nanmean(x[i - half_window : i]) - np.nanmean(x[i : i + half_window])
    
    #Simple and quick peak-perserving smoothing
    av_derivative = scipy.signal.savgol_filter(av_derivative, 7, 1, deriv=0)
    
    #Drop values below a threshold 
    av_derivative_masked = av_derivative.copy()
    av_derivative_masked[av_derivative < np.nanpercentile(av_derivative, pct)] = 0 
    
    transition_times = scipy.signal.argrelmax(av_derivative_masked, order=1)[0] 
    
    #Get the width of peaks
    av = av_derivative_masked.copy()
    av[av > 0] = 1    
    av[np.isnan(av)] = 0
    cs = pd.Series(av).rolling(18).sum()
    
    widths = []
    for t in transition_times:
        width = np.nanmax(cs.values[t - 9:t + 9])  
        widths.append(width)

    av_derivative_masked[av_derivative_masked == 0] = np.nan

    return transition_times, widths

def fit_to_transition(transition_date, detrended, raw):
    #detrended is the detrended and deseasoned data
    #raw is the raw time series
    
    end_date = pd.Timestamp(transition_date) + pd.Timedelta('5Y')
    prev_date = pd.Timestamp(transition_date) - pd.Timedelta('5Y')
    if end_date <= detrended.index.max():
        fitting = detrended.copy()[np.logical_and(detrended.index >= transition_date, detrended.index <= end_date)]
        fitting_raw = raw.copy()[np.logical_and(detrended.index >= transition_date, detrended.index <= end_date)]
        
        #Find the closest local minima to start the fitting from
        armin = np.argmin(fitting.values[:8])
        fitting_min = fitting[armin:]
        
        #See how far the data drops during the transition (to catch spurious transitions)
        raw_drop = fitting_raw[0] - fitting_raw[armin]
       
        #Get the fit statistics
        try:
            trange = np.arange(fitting_min.shape[0])
            popt, _ = curve_fit(exp_fit, trange, fitting_min.values - np.nanmean(fitting_min.values), p0=p0, jac=exp_jac, bounds=bounds)
            rsq = get_rsq(fitting_min - np.nanmean(fitting_min.values), popt)
            fit = popt[1]
        except:
            fit = np.nan
            rsq = np.nan
            
        #Get the before/after mean/std
        subser = raw[np.logical_and(raw.index >= transition_date, raw.index <= end_date)]
        prevser = raw[np.logical_and(raw.index < transition_date, raw.index >= prev_date)]
        submn = np.nanmean(subser)
        subvar = np.nanstd(subser)
        prevmn = np.nanmean(prevser)
        prevvar = np.nanstd(prevser)

        #Add KS Statistic
        try:
            ks, pval = scipy.stats.ks_2samp(prevser.values, subser.values)
        except:
            ks, pval = np.nan, np.nan
        
    return raw_drop, fit, rsq, submn, subvar, prevmn, prevvar, ks, pval


### Global theoretical recovery rates from AC1/variance ###
def calc_kappa(x):
    dx = x[1:] - x[:-1]
    kappa, b = np.polyfit(x[:-1], dx, 1)
    return kappa

def compute_lam(x, dt):
    dx = (x[1:] - x[:-1]) / dt
    return scipy.stats.linregress(x[:-1], dx)[0]

def compute_sigma(x, dt):
    dx = (x[1:] - x[:-1]) / dt
    lamb = compute_lam(x, dt)
    diff = dx - lamb * x[:-1]
    return np.std(diff) * np.sqrt(dt)

def theory_variance(x, dt):
    lam = compute_lam(x, dt)
    sigma = compute_sigma(x, dt)
    return -sigma**2 / (2 * lam)

def theory_ac1(x, dt):
    lam = compute_lam(x, dt)
    return 1 + lam * dt

def check_ts(x, dt=1):
    l = compute_lam(x, dt)
    s = compute_sigma(x, dt)
    v = np.nanvar(x)
    tv = theory_variance(x, dt)
    ac1 = np.corrcoef(x[1:], x[:-1])[0,1]
    tac1 = theory_ac1(x, dt)
    
    return l, s, v, tv, ac1, tac1

### Code for Trend Estimation ###
def calc_ar1(x):
    return np.corrcoef(x[:-1], x[1:])[0,1]

def sliding_window_calc(x, win_size):
    var = np.empty(x.shape)
    var.fill(np.nan)
    ar1 = np.empty(x.shape[0])
    ar1.fill(np.nan)
    half_window = int(win_size / 2)
    ln = x.shape[0]
    for i in range(half_window, ln - half_window):
        subset = x[i - half_window : i + half_window]
        try:
            ar1_ = calc_ar1(subset)
            var_ = np.nanvar(subset)
        except:
            ar1_ = np.nan
            var_ = np.nan
        ar1[i] = ar1_
        var[i] = var_
    ar1 = np.array(ar1)
    var = np.array(var)
    return ar1, var

def fourrier_surrogates(ts, ns):
    ts_fourier  = np.fft.rfft(ts)
    random_phases = np.exp(np.random.uniform(0, 2 * np.pi, (ns, ts.shape[0] // 2 + 1)) * 1.0j)
    ts_fourier_new = ts_fourier * random_phases
    new_ts = np.real(np.fft.irfft(ts_fourier_new))
    return new_ts

def score_at_pct(ts, tau, ns):
    tsf = ts - np.nanmean(ts) #Center on zero
    tsf = tsf[~np.isnan(tsf)] #Strip NaN (5-year rolling winndows leave NaN on either end of the TS)
    tlen = tsf.shape[0] #Get shape
    new_ser = fourrier_surrogates(tsf, ns) #Create surrogates via phase shifting
    stat = np.zeros(ns)
    for i in range(ns):
        stat[i] = scipy.stats.kendalltau(range(tlen), new_ser[i,:], nan_policy='omit')[0] #Calc KT for shuffled series
    p = scipy.stats.percentileofscore(stat, tau)
    return p

def estimate_resilience(residual_denoised, mw, ns):
    #residual_denoised is data without long-term trend or seasonality
    #mw is moving window
    #ns is number of phase surrogates (for significance testing)
    
    k, ar, var = sliding_window_calc(residual_denoised, mw)
    tau_ar = scipy.stats.kendalltau(range(len(ar)), ar, nan_policy='omit')[0]
    tau_var = scipy.stats.kendalltau(range(len(var)), var, nan_policy='omit')[0]
    
    try:
        pval_ar = score_at_pct(ar, tau_ar, ns)
    except:
        pval_ar = np.nan
    try:
        pval_var = score_at_pct(var, tau_var, ns)
    except:
        pval_var = np.nan
    
    return tau_ar, pval_ar, tau_var, pval_var