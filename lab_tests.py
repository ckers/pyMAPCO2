# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 10:46:46 2016

@author: Colin Dietrich
"""

#import sys
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#import plotly.offline as ply
#import plotly.graph_objs as go

#from bs4 import BeautifulSoup

from . import scrape, load, iridium, config, plot_plt


def t_range(t_start, t_end, days_in_past):
    """Determine the range of data to process based on three values.
    All string inputs are formatted str, time in mm/dd/yyyy hh:mm
    days_in_past overrides t_start and t_end values

    Parameters
    ----------
    t_start : str, date and time of start of interval
    t_end : str, date and time of end of interval
    days_in_past : int, days from present

    Returns
    -------
    t_start :
    t_end :
    """

    if days_in_past is not False:
        t_end = pd.to_datetime('now')
        t_start = t_end - pd.Timedelta('%s days' % days_in_past)
    return t_start, t_end


def plot_units(df, title=''):
    us = df.unit.unique()
    marks = config.mpl_obvious_markers * ((len(config.mpl_obvious_markers)%len(us))+1)
    us = df.unit.unique()
    fig, ax = plt.subplots()
    mc = 0
    for u in df.unit.unique():
        _fdl = df[df.unit == u].copy()
        ax.plot(_fdl.index, _fdl.datetime64_ns,
                marker=marks[mc], label=u)
        mc += 1
    ax.legend()
    ax=plt.gca()
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.yaxis.set_major_formatter(xfmt)
    plt.title(title)
    plot_plt.show()


def collate(systems_tested,  t_start, t_end, local_target=None, plot=False, verbose=False):
    """Scrape and collate relevent rudics files and download them from the rudics server

    Parameters
    ----------
    systems_tested : list of str, system serial numbers, i.e. '0120', to collect data for
    t_start : pd.Datetime, start time of data to collate
    t_end : pd.Datetime, end time of data to collate
    plot : bool, show datetime vs index plot

    Returns
    -------
    f_list : list, absolute filepath to files to load data from
    dff : pd.DataFrame, all information on files to load data from
    """

    if local_target is None:
        local_target = config.local_mapco2_data_directory
    # TODO: handle ASV data

    fdl = scrape.run(units=systems_tested,
                     t_start=t_start,
                     t_end=t_end,
                     plot=plot)

    f_list = []
    u_list = []
    for system in systems_tested:
        # print(system)
        f_list_system = glob.glob(local_target + '\\' + system + '\\*')
        f_list = f_list + f_list_system
        u_list = u_list + [system] * len(f_list_system)

    if verbose:
        print('File List to Load')
        print('-'*20)
        for _f in f_list:
            print(_f)

    bf_list = [f.encode('utf-8') for f in f_list]
    dff = pd.DataFrame.from_dict({'filepath': bf_list,
                                  'unit': u_list})

    def get_date(bfp):
        """
        Parameters
        ----------
        bfp : bytes, bytes filepath

        Returns
        -------
        datetime_str : str, datetime of file
        """

        fp_list = bfp.split(b'\\')
        fa = fp_list[-1]
        fb = fa.split(b'.')[0]
        fc = fb.split(b'_')
        fd = fc[1:]
        if len(fd) == 4:
            fd = fd[:-1]
        fe = b'-'.join(fd)
        datetime_str = fe.decode('utf-8')
        return datetime_str

    dff['datetime_str'] = dff.filepath.apply(get_date)
    dff.filepath = dff.filepath.str.decode('utf-8')
    dff['datetime64_ns'] = pd.to_datetime(dff.datetime_str)

    if plot:
        plot_units(dff, title='Data Rows vs. Dates - Filtered to date range')

    return dff


def time_filter(dff, t_start, t_end, plot=False):
    """Filter DataFrame of files to time range of interest

    Parametres
    ----------
    dff : DataFrame, data file information
    t_start : pd.Datetime, start time of data to collate
    t_end : pd.Datetime, end time of data to collate
    plot : bool, show datetime vs index plot

    Returns
    -------
    dffs : DataFrame, filtered on t_start, t_end datetime range
    """

    dffs = dff[(dff.datetime64_ns >= t_start) & (dff.datetime64_ns <= t_end)]

    if plot:
        plot_units(dffs, title='Date of Each File Being Loaded')

    return dffs


def load_data(dffs, verbose=False):
    """Load data from all files in the file list DataFrame

    Parameters
    ----------
    dffs : DataFrame, formatted output from collate
    verbose : print verbose information

    Returns
    -------
    DataFrame, parsed mapco2 data with nested lists
    """
    if verbose:
        print('lab_tests.load_data>> Files being loaded:')
    f_list = list(dffs.filepath)
    df = load.file_batch(f_list, verbose=verbose)
    df.reset_index(inplace=True, drop=True)

    return df


def import_all(df, verbose=False):
    """Import all co2 related data in to DataFrames

    Parameters
    ----------
    df : DataFrame, with unparsed list data for each timestamp
    verbose : print verbose information

    Returns
    -------
    h : DataFrame, header data
    g : DataFrame, gps data
    e : DataFrame, engineering line data
    co2 : DataFrame, co2 measurement data
    """

    h, g, e, co2 = iridium.batch_co2_list(df.co2_list, verbose=verbose)

    if verbose:
        print('lab_tests.import_all>> All systems loaded:')
        print(co2.system.unique())

    co2.drop_duplicates(subset=['cycle', 'datetime64_ns', 'system'], inplace=True)

    if verbose:
        print('lab_tests.import_all>> Systems being parsed:')
        print(co2.system.unique())

    co2_list = []
    for system in co2.system.unique():
        for cycle in co2.cycle.unique():
            key = system + '_' + cycle
            _df = co2[(co2.system == system) & (co2.cycle == cycle)].copy()
            _df.sort_values(by='datetime64_ns', inplace=True)
            _df.reset_index(inplace=True, drop=True)
            co2_list.append((system, cycle, _df))

    return h, g, e, co2

