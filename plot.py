# -*- coding: utf-8 -*-
"""
Tools to plot data in any library
Created on 2017-04-25
@author: Colin Dietrich
"""

import numpy as np
from pandas import notnull
from seaborn import color_palette, cubehelix_palette, palplot
import seaborn.apionly as sns
sns.reset_orig()
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

"""
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
"""


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


def pivot_year(df):
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

    # independent axis x for plots
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

    if 'pH' in df.columns:
        ph_my = df.pivot(index='datetime64_ns',
                         columns='year',
                         values='pH')
    else:
        ph_my = None

    return day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my


def pivot_co2_system(df):
    """Pivot data based on system and datetime64_ns for comparison plots

    Parameters
    ----------
    df : Pandas DataFrame

    Returns
    -------
    dt_ms : Pandas DataFrame or None, day of year for each year
    xco2_air_ms : Pandas DataFrame or None
    sw_ms = Pandas DataFrame or None
    sst_ms = Pandas DataFrame or None
    sss_ms = Pandas DataFrame or None
    ph_ms = Pandas DataFrame or None
    """

    d_list = []
    for system in df.system.unique():
        print(system)

        _df = df[df.system == system].copy()
        _df = _df.drop_duplicates()
        _df.reset_index(inplace=True, drop=True)

        _ds = _df.pivot(index='datetime64_ns',
                          columns='system',
                          values='xCO2')
        d_list.append(_ds)

    """
    xco2_air_ms = df.pivot(index='datetime64_ns',
                           columns='system',
                           values='xCO2_Air_dry')

    xco2_sw_ms = df.pivot(index='datetime64_ns',
                          columns='year',
                          values='xCO2_SW_dry')

    sst_ms = df.pivot(index='datetime64_ns',
                      columns='year',
                      values='SST')

    sss_ms = df.pivot(index='datetime64_ns',
                      columns='year',
                      values='SSS')

    ph_ms = df.pivot(index='datetime64_ns',
                     columns='year',
                     values='pH')

    return day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my
    """
    return d_list


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


