# -*- coding: utf-8 -*-
"""
Tools to plot data in any library
Created on 2017-04-25
@author: Colin Dietrich
"""

import numpy as np
from pandas import notnull
import matplotlib.pyplot as plt
from seaborn import color_palette, cubehelix_palette, palplot

from . import config


# year range for multiyear pivots and plots
years = np.linspace(config.y0, config.y1,
                    (config.y1 - config.y0) + 1,
                    dtype=int)

generic_p = color_palette("cubehelix", 30)
generic_pdict = dict(zip(years, generic_p))
xco2_air_p = cubehelix_palette(30, start=2.5, rot=0)
xco2_air_pdict = dict(zip(years, xco2_air_p))
xco2_sw_p = cubehelix_palette(30, start=0.5, rot=0)
xco2_sw_pdict = dict(zip(years, xco2_sw_p))
sst_p = cubehelix_palette(30, start=1.5, rot=0)
sst_pdict = dict(zip(years, sst_p))
sss_p = cubehelix_palette(30, start=0.0, rot=0)
sss_pdict = dict(zip(years, sss_p))
ph_p = cubehelix_palette(30, start=2.0, rot=0)
ph_pdict = dict(zip(years, ph_p))


def demo_palletes():
    palplot(generic_p)
    plt.title('Generic', loc='right', fontsize=30)
    palplot(xco2_air_p)
    plt.title('xCO2 Air', loc='right', fontsize=30)
    palplot(xco2_sw_p)
    plt.title('xCO2 SW', loc='right', fontsize=30)
    palplot(sst_p)
    plt.title('SST', loc='right', fontsize=30)
    palplot(sss_p)
    plt.title('SSS', loc='right', fontsize=30)
    palplot(ph_p)
    plt.title('pH', loc='right', fontsize=30)
    plt.show()


def lim_finder(data, margin=0.1, data_type=None, verbose=False):
    """Set axis limits to something based on reality
    data_types accepted are in config.k_limits:
        'datetime64_ns'
        'xco2_sw'
        'xco2_air'
        'xco2'
        'o2_percent'
        'sst'
        'sss'
        'atm_press'
        'ph'

    Parameters
    ----------
    data : array-like, values to look for min/max in
    margin : float, factor (1 = 100% etc) to set limit relative to max/min
    data_type : str, identifying code for data to set limits
    verbose : bool

    Returns
    -------
    kmin : float, min value to set axis
    kmax : float, max value to set axis
    """

    d = np.array(data)
    d = d[notnull(d)]
    d_min = np.min(d)
    d_max = np.max(d)
    d_min = d_min - (d_min * margin)
    d_max = d_max + (d_max * margin)

    limits = config.k_limits[data_type]

    if verbose:
        print('Data type:', data_type)
        print('Static limits:', limits)
        print('Calculated limits:', d_min, d_max)

    return np.max([limits[0], d_min]), \
           np.min([limits[1], d_max])


def pivot(df):
    """Pivot data based on year and day of year for multiyear plots

    Parameters
    ----------
    df : Pandas DataFrame

    Returns
    -------
    day_my : Pandas DataFrame or None, day of year for each year
    xco2_air_my : Pandas DataFrame or None
    sw_my = Pandas DataFrame or None
    sst_my = Pandas DataFrame or None
    sss_my = Pandas DataFrame or None
    ph_my = Pandas DataFrame or None
    """

    # independed axis x for plots
    day_my = df.pivot(index='datetime64_ns',
                      columns='year',
                      values='day')

    xco2_air_my = df.pivot(index='datetime64_ns',
                           columns='year',
                           values='xCO2_Air_dry')

    xco2_sw_my = df.pivot(index='datetime64_ns',
                          columns='year',
                          values='xCO2_SW_dry')

    sst_my = df.pivot(index='datetime64_ns',
                      columns='year',
                      values='SST')

    sss_my = df.pivot(index='datetime64_ns',
                      columns='year',
                      values='SSS')

    ph_my = df.pivot(index='datetime64_ns',
                     columns='year',
                     values='pH')

    return day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my


def write_flag(x):
    """Return data if flag is type"""


def create_flag_columns(df):
    """Create flag columns for plotting flagged points
    """

    df['xCO2_SW_dry_flagged_3'] = df.apply(lambda x: x.xCO2_SW_dry if x.xCO2_SW_QF == 3.0
                                                                   else np.nan, axis=1)
    df['xCO2_SW_dry_flagged_4'] = df.apply(lambda x: x.xCO2_SW_dry if x.xCO2_SW_QF == 4.0
                                                                   else np.nan, axis=1)
    df['xCO2_Air_dry_flagged_3'] = df.apply(lambda x: x.xCO2_Air_dry if x.xCO2_Air_QF == 3.0
                                                                   else np.nan, axis=1)
    df['xCO2_Air_dry_flagged_4'] = df.apply(lambda x: x.xCO2_Air_dry if x.xCO2_Air_QF == 4.0
                                                                   else np.nan, axis=1)
    if 'pH' in df.columns:
        df['pH_flagged_3'] = df.apply(lambda x: x.pH if x.pH_QF == 3.0
                                                     else np.nan, axis=1)
        df['pH_flagged_4'] = df.apply(lambda x: x.pH if x.pH_QF == 4.0
                                                     else np.nan, axis=1)

    return df


