# -*- coding: utf-8 -*-
"""
Parse SSTC Data
Reindex TAO SSTC data to 3hr or arbitrary interval

@author: Colin Dietrich
"""

import numpy as np
import pandas as pd
from time import strftime
from io import StringIO

from . import config


def clean_flash(data_list):
    """Clean a list of MAPCO2 flash SSTC data

    Parameters
    ----------
    data_list : list of string lines

    Returns
    -------
    """

    # truncate lines to just met/sstc data
    # (pH data is next thing
    if 'Sami Data' in data_list:
        _line = 'Sami Data'
    elif 'Seafet Data' in data_list:
         _line = 'Seafet Data'
    data_list = data_list[:data_list.index(_line)]

    # remove blank lines
    data_list = [x for x in data_list if x != '']


    return data_list


def save_ssts_sami(df, filepath, verbose=False):
    """Save a .csv of salinity to import to the SAMI QC program

    Parameters
    ----------
    df : Pandas DataFrame with columns:
        datetime64_ns : datetime64_ns object
        SSS : float
    filepath : str, absolute path to save SSS data file to
    verbose : bool, show plots and dataframe head

    Returns
    -------
    Pandas DataFrame of data exported to .csv containing:
        date_str : str
        time_str : str
        SSS : float
    """

    _df = df[['datetime64_ns', 'SSS']].copy()
    _df['date_str'] = _df.datetime64_ns.dt.strftime('%m/%d/%y')
    _df['time_str'] = _df.datetime64_ns.dt.strftime('%H:%M:%S')
    _df = _df[['date_str', 'time_str', 'SSS']]
    _df = _df.dropna(subset=['SSS'], axis=0)
    t = strftime('%Y_%m_%d_%H_%M_%S')
    _f = filepath + '_' + t +'.csv'
    _df.to_csv(_f,
                                  sep='\t',
                                  header=False,
                                  index=False)
    return _df


def to_stringIO(f):
    
    fio = StringIO()
    _f = open(f, 'r')
    for _line in _f:
        try:
            int(_line[0:8])
            fio.write(_line)
        except ValueError:
            continue
    _f.close()
    
    fio.seek(0)
    return fio


def daily_to_3h(filepath, f_sst, f_ssc, t0, t1,
                time_filter_results, interval_filter_results,
                plot_data, save_data, title):
        
    # import SST data from hand cleaned file
    f_sst = filepath + f_sst
    io_sst = to_stringIO(f=f_sst)
    
    io_list = []
    for line in io_sst:
        out = line.split(" ")
        io_list.append(out)
    
    sst_column_names = ["YYYYMMDD", "HHMMSS", "temp", "Q", "M"]
    
    df_sst = pd.DataFrame(io_list,
                       columns=sst_column_names)
    
    df_sst.YYYYMMDD = df_sst.YYYYMMDD.astype(str)
    df_sst.HHMMSS = df_sst.HHMMSS.astype(str)
    
    df_sst["t"] = df_sst.YYYYMMDD + " " + df_sst.HHMMSS
    df_sst["t"] = pd.to_datetime(df_sst.t, format="%Y%m%d %H%M%S")
    
    df_sst = df_sst[["t", "temp"]]
    
    # import SSC data from hand cleaned file
    f_ssc = filepath + f_ssc
    io_ssc = to_stringIO(f=f_ssc)
    
    io_list = []
    for line in io_ssc:
        one = line.split(" ")
        l = len(one)
        if l < 12:
            add_l = 12 - l
            out = one[:-2] + ["-9.999"]*add_l + one[-2:]
        else:
            out = one
        io_list.append(out)
    
    ssc_column_names = ["YYYYMMDD", "HHMMSS", "sal", 
                        "S5", "S10", "S25", "S50", "S75", 
                        "S100", "S125", "Q", "M"]
    
    df_sal = pd.DataFrame(io_list,
                       columns=ssc_column_names)
    
    df_sal.YYYYMMDD = df_sal.YYYYMMDD.astype(str)
    df_sal.HHMMSS = df_sal.HHMMSS.astype(str)
    
    df_sal["t"] = df_sal.YYYYMMDD + " " + df_sal.HHMMSS
    df_sal["t"] = pd.to_datetime(df_sal.t, format="%Y%m%d %H%M%S")
    df_sal = df_sal[["t", "sal"]]
    
    df_sal.sal = df_sal.sal.astype("float32")
    df_sst.temp = df_sst.temp.astype("float32")
    
    ## make 3hr interval
    hr3t = pd.date_range(t0, t1, freq="3H")
    
    if time_filter_results:
        # use the t0 and t1 values defined above to filter to this deployment
        df_sal = df_sal[(df_sal.t >= t0) & (df_sal.t <= t1)]
        df_sst = df_sst[(df_sst.t >= t0) & (df_sst.t <= t1)]
        
    if interval_filter_results:
        # only select data on hours that the MAPCO2 also runs [0, 3, 9, 12, 15, 18, 21]
        df_sst["t_hr"] = pd.DatetimeIndex(df_sst.t).hour
        df_sal["t_hr"] = pd.DatetimeIndex(df_sal.t).hour
        df_sst["t_min"] = pd.DatetimeIndex(df_sst.t).minute
        df_sal["t_min"] = pd.DatetimeIndex(df_sal.t).minute
        
        df_sst = df_sst[df_sst.t_min == 0]
        df_sal = df_sal[df_sal.t_min == 0]
        
        selector = [0, 3, 6, 9, 12, 15, 18, 21]
        df_sst = df_sst[df_sst.t_hr.isin(selector)]
        df_sal = df_sal[df_sal.t_hr.isin(selector)]
        
    hr3t = pd.date_range(t0, t1, freq="3H")
    # reindex data to 3:00 hr interval, fill is NaN    
    df_sst = df_sst.set_index("t")
    df_sst = df_sst.reindex(index=hr3t)
    df_sst['n'] = 0
    df_sst.ix[df_sst.index.hour == 0, 'n'] = 1
    df_sst['day'] = df_sst.n.cumsum()
    df_sst = df_sst.drop('n', 1)
    df_sst['filled'] = 0
    df0 = df_sst[df_sst.temp.notnull()]
    for i in df0.day.unique():
        _n = df0.ix[df0.day == i, 'temp']
        #print(i, _n[0])
        df_sst.ix[df_sst.ix[df_sst.day == i].index, 'filled'] = _n[0]
    
    df_sal = df_sal.set_index("t")
    df_sal = df_sal.reindex(index=hr3t)    
    df_sal['n'] = 0
    df_sal.ix[df_sal.index.hour == 0, 'n'] = 1
    df_sal['day'] = df_sal.n.cumsum()
    df_sal = df_sal.drop('n', 1)
    df_sal['filled'] = 0
    df0 = df_sal[df_sal.sal.notnull()]
    for i in df0.day.unique():
        _n = df0.ix[df0.day == i, 'sal']
        #print(i, _n[0])
        df_sal.ix[df_sal.ix[df_sal.day == i].index, 'filled'] = _n[0]
        
    if save_data:
    
        df_sal.to_csv("..\\" + title + "_ssc.csv", sep=",")
        df_sst.to_csv("..\\" + title + "_sst.csv", sep=",")    
        
    if plot_data:
        import matplotlib.pyplot as plt
        
        # this nuked all interpolated values, not sure why I did this... CRD
#        df_sst = df_sst[df_sst.temp > 0.0]
#        df_sal = df_sal[df_sal.sal > 0.0]
        
        df_sal_plot = df_sal[df_sal.sal.notnull()]
        plt.plot(df_sal_plot.index, df_sal_plot.sal,
                 marker="o", markeredgecolor="blue", markerfacecolor="None", linestyle="-",
                 color="blue",
                 label="sal 12:00")
        plt.plot(df_sal.index, df_sal.filled, markerfacecolor="None", linestyle="-",
                 marker="x", markeredgecolor="orange",
                 color="orange", 
                 label="sal applied to day")
    
        
        df_sst_plot = df_sst[df_sst.temp.notnull()]
        plt.plot(df_sst_plot.index, df_sst_plot.temp,
                 marker=">", markeredgecolor="red", markerfacecolor="None", linestyle="-",
                 color="red", label="sst 12:00")
        plt.plot(df_sst.index, df_sst.filled,
                 marker = "<", markeredgecolor="green", markerfacecolor="None", linestyle="-",
                 color="green", label="sst applied to day")
        plt.legend()
        plt.show()

    return df_sal, df_sst


def clean_sbe16(list_data):
    """Clean list data in an iridium frame of SBE16 data

    Parameters
    ----------
    list_data : list

    """

    ld = [x for x in list_data if 'SBE' not in x]
    ld = ' '.join(ld)
    ld = ld.split(' ')
    ld = [x for x in ld if x != '']

    # deal with uneven nan fill 9 characters
    # rather than .replace_nan with floats of varying decimals later...
    _ld = []
    for x in ld:
        if x in config.nan_9s:
            x = np.nan
        else:
            x = np.float64(x)
        _ld.append(x)
    return _ld
