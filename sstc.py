# -*- coding: utf-8 -*-
"""
Parse SSTC Data

@author: Colin Dietrich
"""
from time import strftime
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


