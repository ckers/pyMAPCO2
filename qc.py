# -*- coding: utf-8 -*-
"""
Quality Control Tools
Created on Wed Apr 26 2017
@author: Colin Dietrich
"""

from time import strftime
from pandas import read_excel

from . import config
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

    _df = read_excel(f, sheetname='Merged', names=config.xlsx_merged_header)
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
    t = time.strftime('%Y_%m_%d_%H_%M_%S')

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

    _df = df[['datetime', 'datetime64_ns',
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

    _df = read_excel(f, sheetname='DATA',
                     skiprows=[0, 1, 2],
                     names=config.co2sysxls_column_names)
    # _df['datetime64_ns'] = _df.Date.copy()
    # _df['datetime'] = _df.Date.copy()
    # _df['datetime'] = _df.datetime.astype(str)
    _df['unit'] = str(unit)
    # _df['common_key'] = _df.apply(common_key, axis=1)
    return _df


def import_xlsx_cycle(df, name):
    """Import one sheet from a VBA imported data set"""

    _df = df[name]
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
