# -*- coding: utf-8 -*-
"""
Parse final published data from MAPCO2
Created on Wed Sep 21 17:17:47 2016
@author: Colin Dietrich
"""

import sys
import numpy as np
import pandas as pd
from os import walk
from datetime import datetime
from io import StringIO
from collections import OrderedDict

from . import config
from .config import column_names, column_names_original, column_mapper
from . import algebra, utils

#from utils.general import pad_date

# names of final data .csv columns
float_names = column_names[:]  # simple copy rather than ref
for _c in ['Date', 'Time', 'Mooring']:
    float_names.remove(_c)


def load(all_files, version='CRD', verbose=False):
    """Load all finalized .csv files into a Pandas DataFrame"""
    return read_files(all_files, version=version, verbose=verbose)


def read_files(all_files, verbose=False, version='CRD'):
    """Read all MAPCO2 files into a Pandas DataFrame

    Parameters
    ----------
    all_files : list, absolute path to .csv source files
    refactor : bool, reformat header variables to CRD format
        useful for any further Python processing,
        as the names are variable safe strings
    verbose : bool

    Returns
    -------
    Pandas DataFrame
    """

    df_list = []
    if isinstance(all_files, str):
        all_files = [all_files]
    for file in all_files:
        if verbose:
            print('Loading: ', str(file))
        _df_n = read_file(file, verbose=verbose, version=version)
        df_list.append(_df_n)

    _df = df_list[0]
    for dfi in df_list[1:]:
        _df = pd.concat([_df, dfi], axis=0)

    _df.reset_index(drop=True, inplace=True)

    return _df


def read_file(file, verbose=False, version='CRD'):
    """Read one MAPCO2 file into a Pandas DataFrame

    Parameters
    ----------
    file : list, absolute path to .csv source files
    refactor : bool, reformat header variables to CRD format
        useful for any further Python processing,
        as the names are variable safe strings
    verbose : bool

    Returns
    -------
    Pandas DataFrame
    """

    dp_n = 'dp number not in filename'
    if 'dp' in file:
        dpix = file.index('dp')
        dp_n = file[dpix + 2:dpix + 4]
        if verbose:
            print('Deployment #:', dp_n)

    # open file once to find if SOCAT header is there
    line_number_of_header = 0
    with open(file, 'r') as _f:
        for line in _f:
            if line[0:7] == 'Mooring':
                break
            else:
                line_number_of_header += 1

    # open file a second time to find if two column header is present
    line_number_of_units = 1
    with open(file, 'r') as _f:
        for line in _f:
            try:
                line = line.split(',')
                if line[1] == 'Dec_Deg':
                    break
                else:
                    line_number_of_units += 1
            except:
                continue

    _df = pd.read_csv(file, index_col=None, dtype=str,
                      header=line_number_of_header,
                      #skiprows=line_number_of_units,
                      sep=',', comment='#')
    _df.reset_index(drop=True, inplace=True)

    if 'Mooring Name' in _df.columns:
        _df.rename(columns=column_mapper, inplace=True)

        new_column_order = []
        for col in _df.columns:
            if col in config.column_names:
                new_column_order.append(col)

        _df = _df[new_column_order]

    _df['dp_n'] = dp_n

    return _df


def format_time(_df):
    _datetime64_ns = (_df.Date.astype(str) + ' ' + _df.Time.astype(str))

    _df['datetime64_ns'] = pd.to_datetime(_datetime64_ns)
    _df['year'] = _df.datetime64_ns.dt.year
    _df['dayofyear'] = _df.datetime64_ns.dt.dayofyear
    _df['time'] = _df.datetime64_ns.dt.time
    _df['day'] = _df.datetime64_ns.apply(algebra.day_of_year)

    return _df


def add_flagged_columns(_df):
    """Add plot data for flagged points
    Parameters
    ----------
    _df : Pandas DataFrame with 'xCO2_Air_dry', 'xCO2_SW_dry' and 'pH_QF' columns
        note: these are CRD column headers, not originals...
    """

    if 'xCO2_Air_QF' in _df.columns:
        _df['xCO2_Air_dry_flagged_3'] = _df.apply(lambda x: x.xCO2_Air_dry if x.xCO2_Air_QF == 3.0
                                              else np.nan,
                                              axis=1)
    if 'xCO2_SW_QF' in _df.columns:
        _df['xCO2_SW_dry_flagged_3'] = _df.apply(lambda x: x.xCO2_SW_dry if x.xCO2_SW_QF == 3.0
                                             else np.nan,
                                             axis=1)
    if 'pH_QF' in _df.columns:
        _df['pH_flagged_3'] = _df.apply(lambda x: x.pH if x.pH_QF == 3.0
                                           else np.nan, axis=1)
    return _df


def reformat_final(file, name='', refactor=False, version='original',
                   ph=False, verbose=True, inplace=True):
    """Reformat a published .csv MAPCO2 file.
    Fixes historical formatting errors.

    Parameters
    ----------
    file : list, absolute path to .csv source files
    name : str, rename mooring id if not ''
    version : str, original header format or CRD clean version
    ph : bool or Pandas DataFrame,
        False: do nothing
        True: fill 'pH' = -999.0 and 'pH_QF' = 5
        DataFrame: insert pH data and QF flags
            Note DataFrame must have same number of rows and columns
            'pH' and 'pH_QF'
    inplace : bool, overwrite input file
    verbose : bool

    Returns
    -------
    saves back to .csv file with 'reformated YYYY-MM-DD_HH:MM:SS'
        inserted into filename
    """

    if version == 'original':
        n = 1
    else:
        n = 2

    header = extract_lines(file, n=n, verbose=verbose)
    _df = read_file(file)

    try:
        _df['new_date_1'] = pd.to_datetime(_df.Date, errors='coerce')
        _df['new_date_2'] = _df.new_date_1.apply(lambda x: x.strftime('%m/%d/%Y') if pd.notnull(x) else '')
    except ValueError:
        _type, value, traceback = sys.exc_info()
        print('Date reformat error %s: %s' % (str(_type), value))
        return

    try:
        _df['new_time_1'] = pd.to_datetime(_df.Time, errors='coerce')
        _df['new_time_2'] = _df.new_time_1.apply(lambda x: x.strftime('%H:%M') if pd.notnull(x) else '')
    except ValueError:
        _type, value, traceback = sys.exc_info()
        print('Time reformat error %s: %s' % (str(_type), value))
        return
    #except:
    #print('Trouble reformatting times in file ', file)
    #print(_df.Date)
    #print(_df.Time)
        #return

    _df.Date = _df.new_date_2
    _df.Time = _df.new_time_2

    _df.drop(labels=['new_date_1', 'new_date_2', 'new_time_1', 'new_time_2'],
             axis=1, inplace=True)

    if name != '':
        _df['Mooring'] = name

    if isinstance(ph, pd.DataFrame):
        _df['pH'] = ph.pH
        _df['pH_QF'] = ph.pH_QF
    elif ph:
        _df.pH_QF = 5
        _df.pH = -999.0

    for column in _df.columns:
        if 'QF' in column:
            _df[column] = _df[column].astype(int)

    if not inplace:
        t_now = datetime.now().strftime('%Y-%m-%dT%H_%M_%S')
        f_name = file[:-4]
        f_extension = file[-4:]
        f_out = f_name + '_' + t_now + '_' + f_extension
    else:
        f_out = file

    sio_all = StringIO()
    for line in header:
        sio_all.write(line)
    sio_data = StringIO()
    _df.to_csv(sio_data, header=False, index=False,
               float_format="%.3f")

    sio_all.write(sio_data.getvalue())

    with open(f_out, 'w') as f_sio:
        f_sio.write(sio_all.getvalue())

    sio_data.close()
    sio_all.close()
    if verbose:
        print('Done reformatting:')
        print(f_out)
    return _df, header


def extract_lines(file, n=2, verbose=True):
    """Extract lines up to a set number in a file

    Parameters
    ----------
    file : str, absolute path to .csv source files
    n : int, lines to extract
    verbose : bool

    Returns
    -------
    list, n number of lines from start of file
    """
    lines = []
    with open(file) as f:
        _n = 0
        for line in f:
            lines.append(line)
            _n += 1
            if _n > n - 1:
                break

    return lines


def make_datetime(_df):
    #TODO: moved to load, should be deleted
    """Create datetime column in Pandas DataFrame

    Parameters
    ----------
    _df : Pandas DataFrame, MAPCO2 data with 'Date' and 'Time' columns

    Returns
    -------
    df : Pandas DataFrame, with 'datetime64_ns' column formatted as
        a Pandas DatetimeIndex
    """
    _datetime64_ns = (_df.Date.astype(str)
                      + ' '
                      + _df.Time.astype(str))
    _df['datetime64_ns'] = pd.to_datetime(_datetime64_ns)
    return _df


def format_floats(_df):
    """Format column datatypes and replace NaN values with np.nan

    Parameters
    ----------
    _df : Pandas DataFrame, MAPCO2 data

    Returns
    -------
    df : Pandas DataFrame, data converted to float and NaN replaced
    """
    _df_cols = _df.columns
    for _f in _df_cols:
        try:
            _df[_f] = _df[_f].astype(float)
        except ValueError:
            continue
        except TypeError:
            continue

    _df.replace(to_replace=-999.0, value=np.nan, inplace=True)

    return _df


def refactor(_df, verbose=False):
    # COPIED to load, should be deleted
    """Refactor parts of the imported final data
    Applies make_datetime, format_floats, replaces -999.0 with np.nan,
    adds day of year columns for multiyear plotting

    Parameters
    ----------
    _df : Pandas DataFrame, containing finalized MAPCO2 data

    Returns
    -------
    df : Pandas DataFrame
    """

    # HEADER
    if 'MM/DD/YYYY' in _df.Date.any():
        _df = _df[_df.Date != 'MM/DD/YYYY'].copy()

    _datetime64_ns = (_df.Date + ' ' + _df.Time)

    dt64_ns = []
    for t in _datetime64_ns:
        try:
            dt = pd.to_datetime(t)
        except:
            print('Trouble converting to datetime:', t)
            dt = pd.NaT
        dt64_ns.append(dt)

    #_df['datetime64_ns'] = pd.to_datetime(_datetime64_ns)
    _df['datetime64_ns'] = dt64_ns

    _df['year'] = _df.datetime64_ns.dt.year
    _df['dayofyear'] = _df.datetime64_ns.dt.dayofyear
    _df['time'] = _df.datetime64_ns.dt.time
    _df['day'] = _df.datetime64_ns.apply(algebra.day_of_year)
    _df = format_floats(_df)
    _df.replace(to_replace=-999.0, value=np.nan, inplace=True)

    try:
        _df['xCO2_Air_dry_flagged_3'] = _df.apply(lambda x: x.xCO2_Air_dry if x.xCO2_Air_QF == 3.0
                                                                       else np.nan, axis=1)
        _df['xCO2_SW_dry_flagged_3'] = _df.apply(lambda x: x.xCO2_SW_dry if x.xCO2_SW_QF == 3.0
                                                                     else np.nan, axis=1)
    except AttributeError:
        pass

    try:
        _df['pH_flagged_3'] = _df.apply(lambda x: x.pH if x.pH_QF == 3.0
                                               else np.nan, axis=1)
    except AttributeError:
        pass

    return _df


class FinalCSV(object):
    def __init__(self):
        self.target = None
        """NOTE: USE MODULE METHODS ABOVE - remove this if not used!"""
    def load_df(self, fp):
        """Load MAPCO2 data from final .csv to Pandas DataFrame
        Skips the first row, assuming units are there.

        TODO: write data file specification

        Parameters
        ----------
        fp : str, filepath to .csv file of final MAPCO2 data 
        
        Returns
        -------
        _df : DataFrame, final MAPCO2 data formatted as
            Date                          object
            H2O_AIR                      float64
            H2O_SW                       float64
            Latitude                     float64
            Licor_Atm_Pressure           float64
            Licor_Temp                   float64
            Longitude                    float64
            Mooring                       object
            Percent_O2                   float64
            SSS                          float64
            SST                          float64
            Time                          object
            datetime              datetime64[ns]
            dfCO2                        float64
            dpCO2                        float64
            fCO2_Air_sat                 float64
            fCO2_SW_sat                  float64
            pCO2_Air_sat                 float64
            pCO2_SW_sat                  float64
            xCO2_Air_QF                    int64
            xCO2_Air_dry                 float64
            xCO2_Air_wet                 float64
            xCO2_SW_QF                     int64
            xCO2_SW_dry                  float64
            xCO2_SW_wet                  float64
            dtype: object
        """

        _df = pd.read_csv(fp, sep=',',
                          names=conf)
        _df.Date = _df.Date.map(utils.pad_date)
        _df['datetime'] = _df.Date + ' ' + _df.Time
        _df['datetime'] = pd.to_datetime(_df.datetime)

        return _df

    def get_files(self, fp):
        """Get all files in a directory.  Uses 3.5 os.walk
        Only include files in fp directory that should be loaded.
        
        Parameters
        ----------
        fp : str, directory to walk into
        Returns
        -------
        files_out : list, of str abs filepath locations of all files
        """
        files_out = []
        for root, dirs, files in walk(fp):
            for name in files:
                files_out.append(root + name)
        return files_out

    def load_batch(self, fp_list, verbose=False):
        """Load all files in a directory that are CDIAC VBA MAPCO2 format

        Parameters
        ----------
        fp_list : list, str filepath to .csv files to load
        
        Returns
        -------
        _df : DataFrame, final MAPCO2 data.  See load_df for dtypes
        _dfmbl : DataFrame, mbl data.  See load_mbl for dtypes        
        """
        mapco2_fp_list = []
        mbl_fp = None

        for fp in fp_list:
            if "mbl" in fp:
                mbl_fp = fp
                if verbose:
                    print("MBL found:", mbl_fp)

            else:
                mapco2_fp_list.append(fp)

        _dfmbl = self.load_mbl(mbl_fp)
        if verbose:
            print('MBL data.head:', _dfmbl.head())

        _fp = mapco2_fp_list[0]
        if verbose:
            print('Loading:', _fp)
        _df = self.load_df(_fp)
        for _fp in mapco2_fp_list[1:]:
            if verbose:
                print('Loading:', _fp)
            _df2 = self.load_df(_fp)
            _df = pd.concat([_df, _df2])

        _df = _df.sort_values(by=["datetime"], axis=0)
        _df.reset_index(inplace=True)

        return _df, _dfmbl

    def load_mbl(self, fp):
        """Load a .csv file of location specific MBL data generated from
        Pandas via import_mbl.py
        Parameters
        ----------
        fp : str, file path to .csv file containing precompiled mbl
            data for the location being batched
        
        Returns
        -------
        _df : DataFrame, containing mbl umol/mol CO2 formatted as
            Unnamed: 0              int64
            t              datetime64[ns]
            xCO2                  float64
            xCO2_uncert           float64
            dtype: object
            
        """

        _df = pd.read_csv(fp, sep=',',
                          header=0)
        _df['datetime'] = pd.DatetimeIndex(_df['t'])

        return _df


class CDIACDL(object):
    def __init__(self, target=None):
        """Download data from CDIAC and store locally"""
        pass


class FinalPlot(object):
    def __init__(self):
        pass
