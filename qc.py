# -*- coding: utf-8 -*-
"""
Quality Control Tools
Created on Wed Apr 26 2017
@author: Colin Dietrich
"""

import pandas as pd

from time import strftime
from numpy import std

from . import config
from . import plot_plt
from .algebra import timestamp_rounder, common_key


def import_merged(f, unit):
    """Import Merged data worksheet from an Excel Workbook
    Assumes there is a worksheet named 'Merged'

    Parameters
    ----------
    f : str, absolute file path to .xlsx workbook
    unit : str, system id number or serial number

    Returns
    -------
    Pandas DataFrame
    """

    _df = pd.read_excel(f, sheetname='Merged', names=config.xlsx_merged_header)
    _df['datetime64_ns'] = _df.Date.copy()
    _df['datetime'] = _df.Date.copy()
    _df['datetime'] = _df.datetime.astype(str)
    _df['unit'] = str(unit)
    _df['common_key'] = _df.apply(common_key, axis=1)
    return _df


def sss_sami_export(df, filepath, description=''):
    """Export SSS for SAMI ph QC program

    Parameters
    ----------
    df : Pandas DataFrame with columns:
        'datetime64_ns', 'SSS'

    filepath : str, absolute filepath to location to save .csv
    description : str, name of data for .csv filename

    Returns
    -------
    Pandas DataFrame of data written to file
    """

    _df = df.copy()
    _df['date_str'] = _df.datetime64_ns.dt.strftime('%m/%d/%y')
    _df['time_str'] = _df.datetime64_ns.dt.strftime('%H:%M:%S')
    _df = df[['date_str', 'time_str', 'SSS']]
    t = strftime('%Y_%m_%d_%H_%M_%S')

    if description != '':
        description += '_'

    _f = filepath + description + 'sss_for_sami_' + t + '.csv'
    _df.to_csv(_f, sep='\t', header=False, index=False)

    return _df


def sss_seafet_export(df):
    pass


def co2sys_xls_export(df, filepath,
                      p_dbar_in=0.5, p_dbar_out=0.5,
                      total_P=0, total_Si=0,
                      tco2='', pH='', fco2='', sst_out='',
                      description=''):
    """Export data for insertion to co2sys.xls
    Assumes the following columns are in df:
        'datetime',
        'datetime64_ns',
        'SSS',
        'SST',
        'TA',
        'pCO2_SW_sat'

    Note: when run in co2sys.xls be practice is (2017) to use:
        Set of Constants = Ki, K2 from Lueker et al. 2000
        KHSO4 = Dickson
        pH Scale = Total scale (mol/kg-SW)
        [B]T = Uppstrom, 1974

    TODO: find units for total_P, total_Si

    Parameters
    ----------
    df : Pandas DataFrame
    filepath : str, absolute filepath to location to save .csv
    p_dbar_in : float, pressure of input data
    p_dbar_out : float, pressure of output calculated values
    total_P : float, total Phosphorous
    total_Si : float, total Silica
    tco2 : float, '' for None
    pH : float, '' for None
    fco2 : float, '' for None
    sst_out : float, '' for None
    description : str, name of data for .csv filename

    Returns
    -------
    Pandas DataFrame of data written to file
    """

    _df = df[['datetime64_ns',
              'SSS', 'SST',
              'TA', 'pCO2_SW_sat']].copy()

    _df['p_dbar_in'] = p_dbar_in
    _df['p_dbar_out'] = p_dbar_out
    _df['total_P'] = total_P
    _df['total_Si'] = total_Si
    _df['tco2'] = tco2
    _df['pH'] = pH
    _df['fco2'] = fco2
    _df['SST_out'] = sst_out

    _df = _df[config.co2sys_column_names_in]

    _df.dropna(axis=0, how='any', inplace=True)

    if description != '':
        description += '_'

    t = strftime('%Y_%m_%d_%H_%M_%S')
    _f = filepath + description + 'data_for_co2sys_' + t + '.csv'

    _df.to_csv(_f, sep=',', header=True, index=False)

    return _df


def import_co2sysxls(f, unit):
    """Import Merged data worksheet from an Excel Workbook
    Assumes there is a worksheet named 'Merged'

    Parameters
    ----------
    f : str, absolute file path to .xlsx workbook
    unit : str, system id number or serial number

    Returns
    -------
    Pandas DataFrame
    """

    _df = pd.read_excel(f, sheetname='DATA',
                        skiprows=[0, 1],
                        names=config.co2sysxls_column_names)
    _df['unit'] = str(unit)
    return _df


def import_xlsx_cycle(df_dict, name, verbose=False):
    """Import one sheet from a VBA imported data set

    Parameters
    ----------
    df_dict : dictionary of Pandas DataFrames, one for each worksheet
    name : str, worksheet name to modify
    verbose : bool, print debug statements

    Returns
    -------
    Pandas DataFrame, reformatted data from 'name' worksheet
    """

    _df = df_dict[name]
    _df = _df.reset_index()

    _df = _df.ix[:, ['Time', 'Calculated xCO2 from Averaged Data',
                     'index', 'Mode', 'Raw1', 'Raw2']]

    renames = {'Time': 'cycle_datetime64_ns',
               'Calculated xCO2 from Averaged Data': 'xCO2',
               'index': 'mode', 'Mode': 'cycle'}
    _df = _df.rename(columns=renames)
    _df = _df.dropna(how='all', axis=0)
    _df = _df[_df['mode'] != 'DEPL']
    _df = _df.drop('mode', axis=1)
    _df['cycle'] = config.cycle_names[name]
    _df['datetime64_ns'] = _df.apply(lambda x: timestamp_rounder(x.cycle_datetime64_ns), axis=1)

    return _df


def batch_reformat(df_dict, verbose=False):
    """Batch reformat all worksheet data as a dictionary of Pandas DataFrames
    Note: this makes a copy and could be slow...
    """

    new_df_dict = {}
    for k, v in config.cycle_names.items():
        if verbose:
            print('Working on:', k, v)
        _df = import_xlsx_cycle(df_dict, k)
        new_df_dict[v] = _df.copy()

    # new column names needed later for merges
    new_df_dict['apof']['xCO2_Air'] = new_df_dict['apof']['xCO2']
    new_df_dict['epof']['xCO2_SW'] = new_df_dict['epof']['xCO2']

    return new_df_dict


def std_outlier_detecter(data_series, std=1):
    """Identify outlier values in a timeseries

    Parameters
    ----------
    series : Array-like, timeseries data
    std : float, number of standard deviations to high pass on

    Returns
    -------
    Array-like, timeseries values greater than std
    """

    return data_series > std * np.std(data_series)


def dt_std_outlier_detector(df, timeseries, std_in=(0.5, 1, 2, 3, 4)):
    """Finds outlier data in col_name of df, based on standard deviations
    passed in std_in using the first derivative of the data.

    Parameters
    ----------
    df : Pandas DataFrame
    timeseries : str, name of column of timeseries data
    std_in : list, standard deviation values to filter on
    plot : bool, create a plot of the std

    Returns
    -------
    Pandas DataFrame with columns:
        timeseries_dt : derivative of timeseries
        timeseries_dtfx : data that was outside of x std
    """

    # differentiate one values interval
    df[timeseries + '_dt'] = df[timeseries].diff(1)

    # std of dt
    dt_std = df[timeseries + '_dt'].std()
    dt_abs = df[timeseries + '_dt'].abs()
    # filter on std
    for std_n in std_in:
        df[timeseries + '_dtf'+str(std_n)] = dt_abs > std_n * dt_std

    return df


def build_ply_flag_df(df_dict, df_flags):
    """Build a Pandas DataFrame for plotting flags from a dictionary of DataFrames
    where keys are 'apon', 'apof' etc

    Parameters
    ----------
    df_dict : dict of Pandas DataFrames

    Returns
    -------
    Pandas DataFrame
    """

    _dfa = df_dict['apof']
    _dfa = _dfa[['datetime64_ns', 'xCO2_Air']].reset_index()
    _dfa = _dfa.drop('index', axis=1)

    _dfe = df_dict['epof']
    _dfe = _dfe[['datetime64_ns', 'xCO2_SW']].reset_index()
    _dfe = _dfe.drop('index', axis=1)

    plt_flags_qfa4 = df_flags[df_flags['QF_air'] == 4]
    plt_flags_qfa4 = plt_flags_qfa4[['datetime64_ns', 'xCO2_Air']].reset_index()
    plt_flags_qfa4 = plt_flags_qfa4.rename(columns={'xCO2_Air': 'xCO2_Air_dry_flagged_4'})
    plt_flags_qfa4 = plt_flags_qfa4.drop('index', axis=1)

    plt_flags_qfa3 = df_flags[df_flags['QF_air'] == 3]
    plt_flags_qfa3 = plt_flags_qfa3[['datetime64_ns', 'xCO2_Air']].reset_index()
    plt_flags_qfa3 = plt_flags_qfa3.rename(columns={'xCO2_Air': 'xCO2_Air_dry_flagged_3'})
    plt_flags_qfa3 = plt_flags_qfa3.drop('index', axis=1)

    plt_flags_qfs4 = df_flags[df_flags['QF_sw'] == 4]
    plt_flags_qfs4 = plt_flags_qfs4[['datetime64_ns', 'xCO2_SW']].reset_index()
    plt_flags_qfs4 = plt_flags_qfs4.rename(columns={'xCO2_SW': 'xCO2_SW_dry_flagged_4'})
    plt_flags_qfs4 = plt_flags_qfs4.drop('index', axis=1)

    plt_flags_qfs3 = df_flags[df_flags['QF_sw'] == 3]
    plt_flags_qfs3 = plt_flags_qfs3[['datetime64_ns', 'xCO2_SW']].reset_index()
    plt_flags_qfs3 = plt_flags_qfs3.rename(columns={'xCO2_SW': 'xCO2_SW_dry_flagged_3'})
    plt_flags_qfs3 = plt_flags_qfs3.drop('index', axis=1)

    dff = _dfa.merge(_dfe, on='datetime64_ns')
    dff = dff.merge(plt_flags_qfa4, on='datetime64_ns', how='outer')
    dff = dff.merge(plt_flags_qfa3, on='datetime64_ns', how='outer')
    dff = dff.merge(plt_flags_qfs4, on='datetime64_ns', how='outer')
    dff = dff.merge(plt_flags_qfs3, on='datetime64_ns', how='outer')

    dff = dff.rename(columns={'xCO2_SW': 'xCO2_SW_dry', 'xCO2_Air': 'xCO2_Air_dry'})

    return dff


def extracter(df, sheet, name, t_col, d_col):
    """Generic data extractor for xlsx sourced dict of DataFrames

    Parameters
    ----------
    df : dict of Pandas DataFrames
    sheet : str, key to df for DataFrame
    name : str, column name to label output data
    t_col : int, index of datatime64_ns timestamp column
    d_col : int, index of data column

    Returns
    -------
    Pandas DataFrame with:
        reset index
        name : data column
        datetime64_ns : timestamp in datetime64[ns] format
    """

    _df = df[sheet]
    _df = pd.DataFrame({'t': _df.iloc[:, t_col],
                        name: _df.iloc[:, d_col]})
    _df = _df.reset_index()
    _df = _df.dropna(how='all', axis=0)
    _df['datetime64_ns'] = _df.apply(lambda x: timestamp_rounder(x.t),
                                     axis=1)
    _df = _df.drop(['index', 't'], axis=1)
    return _df


##### All Below are used together to import data FROM .xlsx files #####

def mapco2_xlsx_extractor(path_in):
    """Load a previously compiled (in VBA) Excel workbook of mapco2 data

    Parameters
    ----------
    path_in : str, path to .xlsx file

    Returns
    -------
    dict, of Pandas DataFrames
    """

    worksheets = ['Zero Pump On',
                  'Zero Pump Off',
                  'Zero Post Cal',
                  'Span Pump On',
                  'Span Pump Off',
                  'Span Post Cal',
                  'Equil Pump On',
                  'Equil Pump Off',
                  'Air Pump On',
                  'Air Pump Off']

    df_xlsx = pd.read_excel(io=path_in,
                            sheetname=worksheets,
                            header=0,
                            skiprows=1)
    return df_xlsx


def format_xlsx_import(_df, t_start, t_end):
    _df['datetime64_ns'] = pd.to_datetime(_df.datetime_str)
    _df.datetime64_ns = _df.datetime64_ns.apply(timestamp_rounder)
    _df.index = _df.datetime64_ns
    _df.index.name = 'datetime64_ns'
    _df = _df[(_df.datetime64_ns >= t_start) & (_df.datetime64_ns <= t_end)]
    _df = _df[pd.notnull(_df.index)]
    return _df


def slice_df_co2(df_xlsx, t_start, t_end):
    """Slice co2 data from entire dictionary of DataFrames from the .xlsx file

    Parameters
    ----------
    df_xlsx : dict, of Pandas DataFrames containing worksheets from xlsx source file
    t_start : datetime, start time of deployment
    t_end : datetime, end time of deployment

    Returns
    -------
    Pandas DataFrame, co2 specific data
    """

    df_co2 = pd.DataFrame({'datetime_str': df_xlsx['Air Pump Off'].iloc[:, 2],
                           'zpcl': df_xlsx['Zero Post Cal'].iloc[:, 23],   # xCO2 dry
                           'spcl': df_xlsx['Span Post Cal'].iloc[:, 23],   # xCO2 dry
                           'epof': df_xlsx['Equil Pump Off'].iloc[:, 25],  # xCO2 dry
                           'apof': df_xlsx['Air Pump Off'].iloc[:, 25]},   # xCO2 dry
                          columns=['datetime_str', 'zpcl', 'spcl', 'epof', 'apof'])
    df_co2 = format_xlsx_import(df_co2, t_start, t_end)
    return df_co2


def slice_df_gps(df_xlsx, t_start, t_end):
    """Slice gps data from entire dictionary of DataFrames from the .xlsx file

    Parameters
    ----------
    df_xlsx : dict, of Pandas DataFrames containing worksheets from xlsx source file
    t_start : datetime, start time of deployment
    t_end : datetime, end time of deployment

    Returns
    -------
    Pandas DataFrame, co2 specific data
    """

    df_gps = pd.DataFrame({'datetime_str': df_xlsx['Zero Pump On'].iloc[:, 36],  # AJ
                           'lat': df_xlsx['Zero Pump On'].iloc[:, 37],           # AK
                           'lon': df_xlsx['Zero Pump On'].iloc[:, 38]})          # AL
    df_gps = format_xlsx_import(df_gps, t_start, t_end)
    return df_gps


def slice_df_pressure(df_xlsx, t_start, t_end):
    """Slice pressure data from entire dictionary of DataFrames from the .xlsx file

    Parameters
    ----------
    df_xlsx : dict, of Pandas DataFrames containing worksheets from xlsx source file
    t_start : datetime, start time of deployment
    t_end : datetime, end time of deployment

    Returns
    -------
    Pandas DataFrame, co2 specific data
    """

    df_pressure = pd.DataFrame({'datetime_str': df_xlsx['Air Pump Off'].iloc[:, 2],
                                'zpon': df_xlsx['Zero Pump On'].iloc[:, 5],   # Licor kPa
                                'spon': df_xlsx['Span Pump On'].iloc[:, 5],   # Licor kPa
                                'epon': df_xlsx['Equil Pump On'].iloc[:, 5],  # Licor kPa
                                'apon': df_xlsx['Air Pump On'].iloc[:, 5],    # Licor kPa
                                'apof': df_xlsx['Air Pump Off'].iloc[:, 5]},  # Licor kPa
                               columns=['datetime_str', 'zpon', 'spon', 'epon', 'apon', 'apof'])
    df_pressure = format_xlsx_import(df_pressure, t_start, t_end)
    return df_pressure


def slice_df_cal(df_xlsx, t_start, t_end):
    """Slice calibration data from entire dictionary of DataFrames from the .xlsx file

    Parameters
    ----------
    df_xlsx : dict, of Pandas DataFrames containing worksheets from xlsx source file
    t_start : datetime, start time of deployment
    t_end : datetime, end time of deployment

    Returns
    -------
    Pandas DataFrame, co2 specific data
    """

    df_cal = pd.DataFrame({'datetime_str': df_xlsx['Air Pump Off'].iloc[:, 2],
                           'zpof': df_xlsx['Zero Pump Off'].iloc[:, 8],
                           'zpcal': df_xlsx['Zero Post Cal'].iloc[:, 8],
                           'zpcal_raw1' : df_xlsx['Zero Post Cal'].iloc[:, 17],
                           'zpcal_raw2' : df_xlsx['Zero Post Cal'].iloc[:, 19],

                           'spof': df_xlsx['Span Pump Off'].iloc[:, 8],
                           'spcal': df_xlsx['Span Post Cal'].iloc[:, 8],
                           'spcal_raw1' : df_xlsx['Span Post Cal'].iloc[:, 17],
                           'spcal_raw2' : df_xlsx['Span Post Cal'].iloc[:, 19],

                           'epof': df_xlsx['Equil Pump Off'].iloc[:, 8],
                           'apof': df_xlsx['Air Pump Off'].iloc[:, 8]
                           },
                          columns=['datetime_str', 'zpof', 'zpcal', 'spof', 'spcal',
                                   'zpcal_raw1', 'zpcal_raw2', 'spcal_raw1', 'spcal_raw2',
                                   'epof', 'apof'])
    df_cal = format_xlsx_import(df_cal, t_start, t_end)
    return df_cal

##### see note above #####
