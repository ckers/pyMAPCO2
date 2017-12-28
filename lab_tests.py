# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 10:46:46 2016

@author: Colin Dietrich
"""

import glob
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    marks = config.mpl_obvious_markers * ((len(config.mpl_obvious_markers) % len(us))+1)
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


def collate(systems_mapco2, t_start, t_end,
            systems_waveglider=None, systems_asv=None,
            update=False,
            #plot=False,
            verbose=False):
    """Hack because we can't just use unique IDs on our systems.  Wraps _collate
    to handle the 3 rudics directories co2 data is being savied WITH duplicate system IDs.
    Appends ID string to unit number to keep things straight based on:
        Allowed datatypes are:
        'm' : mapco2
        'w' : waveglider
        'a' : asv
    See iridium.frame_co2 for where these identifiers are applied.

    Parameters
    ----------
    systems_mapco2 : list of str, id of each system i.e. '0179'
    t_start : pd.Datetime, start time of data to collate
    t_end : pd.Datetime, end time of data to collate
    update : bool, scrape new data from the Iridium server
    plot : bool, show datetime vs index plot
    waveglider_system : same format as mapo2_system, for waveglider systems
    systems_asv : same format as mapco2_system, for asv co2 systems

    Returns
    -------
    dff :

    """

    dff_w = None
    dff_a = None

    dff = _collate(systems_tested=systems_mapco2, datatype='mapco2',
                   t_start=t_start, t_end=t_end,
                   update=update,
                   #plot=plot,
                   verbose=verbose)
    dff['datatype'] = 'm'

    if systems_waveglider is not None:
        dff_w = _collate(systems_tested=systems_waveglider, datatype='waveglider',
                         t_start=t_start, t_end=t_end,
                         update=update,
                         #plot=plot,
                         verbose=verbose)
        dff_w['datatype'] = 'w'
        dff = pd.concat([dff, dff_w], axis=0, join='outer', ignore_index=True)

    if systems_asv is not None:
        dff_a = _collate(systems_tested=systems_asv, datatype='asv',
                         t_start=t_start, t_end=t_end,
                         update=update,
                         #plot=plot,
                         verbose=verbose)
        dff_a['datatype'] = 'a'
        dff = pd.concat([dff, dff_a], axis=0, join='outer', ignore_index=True)

    #if plot:
    #    plot_units(dff, title='Data Rows vs. Dates - Filtered to date range')

    return dff


def _collate(systems_tested,  datatype,
             t_start, t_end,
             update=False,
             #plot=False,
             verbose=False):
    """Scrape and collate relevent rudics files from one system type folder and download
    from the rudics server.

    Parameters
    ----------
    systems_tested : list of str, system serial numbers, i.e. '0120', to collect data for
    t_start : pd.Datetime, start time of data to collate
    t_end : pd.Datetime, end time of data to collate
    update : bool, scrape new data from the Iridium server
    plot : bool, show datetime vs index plot

    Returns
    -------
    f_list : list, absolute filepath to files to load data from
    dff : pd.DataFrame, all information on files to load data from
    """

    if (datatype is None) or (datatype == 'mapco2'):
        local_target = config.local_mapco2_data_directory
        url_source = config.url_mapco2
    if datatype == 'waveglider':
        local_target = config.local_waveglider_data_directory
        url_source = config.url_waveglider
    if datatype == 'asv':
        local_target = config.local_asv_data_directory
        url_source = config.url_asv
    #else:
    #    local_target = config.local_mapco2_data_directory
    #    url_source = config.url_mapco2

    if update:
        # downloads files based on t_start, t_end
        # does NOT pass file info on, local files are filtered on again later
        # to establish which files to load
        fdl = scrape.run(units=systems_tested,
                         url_source=url_source,
                         local_target=local_target,
                         t_start=t_start,
                         t_end=t_end,
                         #plot=plot
                         )

    # begin local collection of available data files
    f_list = []
    u_list = []
    for system in systems_tested:
        if verbose:
            print('lab_tests._collate>> system local data being loaded: {}'.format(system))
        # print(system)
        f_list_system = glob.glob(local_target + '\\' + system + '\\*')
        f_list = f_list + f_list_system
        u_list = u_list + [system] * len(f_list_system)

    # if verbose:
    #     print('File List to Load')
    #     print('-'*20)
    #     for _f in f_list:
    #         print(_f)

    bf_list = [f.encode('utf-8') for f in f_list]
    dff = pd.DataFrame.from_dict({'filepath': bf_list,
                                  'unit': u_list})

    # no data files where found for the input system
    if len(dff) == 0:
        return dff

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

    if plot & len(dffs) > 0:
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
    f_type = list(dffs.datatype)
    df = load.file_batch(f_list, datatype=f_type, verbose=verbose)
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

    h, g, e, co2 = iridium.batch_co2(df, verbose=verbose)

    if verbose:
        print('lab_tests.import_all>> All systems loaded:')
        print(co2.system.unique())

    co2.drop_duplicates(subset=['cycle', 'datetime64_ns', 'system'], inplace=True)

    co2 = co2[co2.xCO2.apply(lambda x: False if isinstance(x, list) else True)]

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


def log_entry(systems):
    mn = 300
    wn = 30
    an = 30

    mh = ['m_{0:04d}'.format(n) for n in range(1, mn+1)]
    wh = ['w_{0:05d}'.format(n) for n in range(1, wn+1)]
    ah = ['a_{0:05d}'.format(n) for n in range(1, an+1)]
    h = ['YYYY-MM-DDThh:mm:ssZ', 'YYYY/MM/DD hh:mm:ss'] + mh + wh + ah

    m = [''] * mn
    w = [''] * wn
    a = [''] * an

    for x in systems:
        xtype, number = x.split('_')
        if xtype == 'm':
            m[int(number)-1] = 1
        if xtype == 'w':
            w[int(number)-1] = 1
        if xtype == 'a':
            w[int(number)-1] = 1

    _d = m + w + a
    _d = [str(n) for n in _d]

    t = [datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'), datetime.utcnow().strftime('%Y/%m/%d %H:%M:%S')]
    d = t + _d
    return h, d
