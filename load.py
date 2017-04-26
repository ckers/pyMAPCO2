# -*- coding: utf-8 -*-
"""
Parse summary data frames from MAPCO2
Created on Mon Jul 25 14:30:25 2016
@author: Colin Dietrich
"""

import os
import unicodedata
import numpy as np
import pandas as pd

from . import config
from .algebra import float_year_to_datetime

# TODO: more config info, probably should move to config.py
data_types = ['mapco2', 'ph_sami', 'ph_seafet', 'sbe16', 'met']
default_number_of_list_lines = 30  # how many lines to save if no end line found


def sniff(file):
    """Decide if file is a MAPCO2 flash data file
    
    Parameters
    ----------
    file : str, filepath to file
    
    Returns
    -------
    bool, True if file contains MAPCO2 data
    """
    f = open(file, mode='r', errors='ignore', encoding='utf-8')
    for _line in f:
        _line = _line.lstrip()
        _id = _line[0:4]
        if _id in config.pco2_start_delimiters:
            return True
    return False


def file_to_list(file):
    """Convert string/file data to list, no cleaning
    Parameters
    ----------
    file : str, filepath to file to open

    Returns
    -------
    data : list, lines of data from file
    """
    data = []
    f = open(file, mode='r', errors='ignore', encoding='utf-8')
    for _line in f:
        data.append(_line)
    return data


def index_data(data):
    """Find indexes where an new frame of MAPCO2 data starts,
    as well as where the pH data is saved

    Examples: 'FAST', 'NORM', 'DEPL'

    Parameters
    ----------
    data : list,
    
    Returns
    -------
    out : list, nested list of lines where dataframes start
    """

    c = 0
    i = 0
    out = [['']*5 for _ in range(5000)]

    for _line in data:
        _id = _line[0:4]

        if _id in config.pco2_start_delimiters:
            out[i][0] = c
            i += 1
        if _id in ['Sami', 'PH']:
            out[i][1] = c
        if _id == 'Seaf':
            out[i][2] = c
        if _id == 'SBE1':
            out[i][3] = c
        if _id == 'Met ':  # note single whitespace - bad luck, full line is 'Met Data'
            out[i][4] = c
        c += 1

    out = out[:i+1]
    return out


def create_index_dataframe(index_list):
    """
    Run the indexer on self.data and return values in self.df

    Parameters
    ----------
    index_list : list, nested list of lines where dataframes start

    Returns
    -------
    _df : Pandas Dataframe
    """

    _df = pd.DataFrame(index_list, columns=data_types)
    _df.ph_sami = _df.ph_sami.shift(-1)
    _df.seafet_ph = _df.ph_seafet.shift(-1)
    _df.sbe16 = _df.sbe16.shift(-1)
    _df.met = _df.met.shift(-1)
    _df = _df.dropna(axis=0)

    return _df


def get_start_timestamp(data_list, index_df):
    """Get timestamps for MAPCO2 dataframe indexes

    Parameters
    ----------
    data_list : list, cleaned data lines
    index_df : Pandas DataFrame, index values for all data types

    Returns
    -------
    out : list, of str with timestamp for each mapco2 dataframe index
    """

    indexes = index_df.mapco2.values
    out = []
    for _i in indexes:
        header = data_list[_i].strip().split()
        _t = header[3] + '_' + header[4]
        out.append(_t)

    return out


def create_start_end(index_df):
    """Find the start and end columns from a DataFrame of
    only start indexes

    Parameters
    ----------
    index_df : Pandas DataFrame, start indexes

    Returns
    -------
    Pandas DataFrame of 'name'_start and 'name'_end index data
    """

    rename_columns = []
    for name in index_df.columns:
        if 'datetime' not in name:
            rename_columns.append(name + '_start')
        else:
            rename_columns.append(name)

    index_df.columns = rename_columns

    for name in rename_columns:
        if 'start' in name:
            index_df[name.replace('start', 'end')] = ''

    for name in data_types:
        index_df[name + '_end'] = index_df[name + '_start']
        index_df[name + '_end'] = index_df[name + '_end'].astype(int)
        index_df[name + '_end'] += default_number_of_list_lines
        index_df = index_df.replace(-1000, -999)

    return index_df


def format_index_dataframe(lc):
    """Load indexes for a single iridium file
    Parameters
    ----------
    lc : list, lines of cleaned data

    Returns
    -------
    df : Pandas Dataframe, indexes of all identified data types
    """

    d = index_data(lc)
    df = create_index_dataframe(d)
    df['datetime'] = get_start_timestamp(data_list=lc, index_df=df)
    df['datetime64_ns'] = pd.to_datetime(df.datetime, format='%Y/%m/%d_%H:%M:%S')
    df = df.replace('', -999)
    df = create_start_end(index_df=df)
    return df

    
def frames(lc, start, end, delimiters):
    """Get data of one type from data file.  Type is determined by delimiters
    
    Parameters
    ----------
    lc : list, lines of cleaned data
    start : array-like, indexes of start of data frame in lc
    end : array-like, indexes of end of data frame in lc
    delimiters : list of 2 str, characters to use as start and end of
        section of data
    
    Returns
    -------
    delimiters : list of str, two item long representing the starting
        and ending delimiters of a frame of data
    """
    
    delim_start = delimiters[0]
    delim_end = delimiters[1]

    data = [[] for _ in range(5000)]

    c = 0
    for i in range(len(start)):

        if start[i] == -999:
            data[c] = []
            c += 1
            continue

        _data = lc[start[i]:end[i]]

        i = 0
        _j = []
        save = True
        for j in _data:

            if j[0:len(delim_start)] == delim_start:
                save = True
            if j[0:len(delim_end)] == delim_end:
                save = False
                _j.append(j)
                i += 1
            if save:
                _j.append(j)
        data[c] = _j

        c += 1

    data = data[:c]
    return data


def load_file(f):
    """Load all available data types in a file
    Note: data types are determined by delimiter definitions, which 
    are hardcoded below.
    
    Parameters
    ----------
    f : str, filepath to file to parse

    Returns
    -------
    df: Pandas Dataframe, data of all identified data types
    TODO: document columns and types
    """

    l = file_to_list(f)
    lc, errors, blanks = cleaner(data_list=l)
    df = format_index_dataframe(lc)

    df['source'] = os.path.normpath(f).split('\\')[-1]
    df['unit'] = df.source.str[1:5]
    df['common_key'] = (df.unit.astype(str) +
                        '_' +
                        df.datetime.str.replace(':', '_').str.replace('/', '_'))
    df['sbe16_list'] = frames(lc,
                              start=df.sbe16_start,
                              end=df.sbe16_end,
                              delimiters=['SBE16 DATA', 'END SBE16'])
    
    df['ph_sami_list'] = frames(lc,
                                start=df.ph_sami_start,
                                end=df.ph_sami_end,
                                delimiters=['PH', 'END PH'])
    
    df['ph_seafet_list'] = frames(lc,
                                  start=df.ph_seafet_start,
                                  end=df.ph_seafet_end,
                                  delimiters=['Seafet Data', 'End Seafet Data'])

    df['met_list'] = frames(lc,
                            start=df.met_start,
                            end=df.met_end,
                            delimiters=['Met', ''])

    df['co2_list'] = frames(lc,
                            start=df.mapco2_start,
                            end=df.mapco2_end,
                            delimiters=['NORM', 'SW_xCO2(dry)'])
    
    return df


def file_batch(f_list):
    """Load multiple iridium files using frames_all
    
    Parameters
    ----------
    f_list : list of str, filepath to file to parse
    
    Returns
    -------
    Pandas Dataframe, data of all identified data types
    """
    
    _df_list = []
    for _f in f_list:
        _df = load_file(_f)
        _df_list.append(_df)
        
    df = pd.concat(_df_list)
    df.reset_index(inplace=True, drop=True)

    return df

    
def unicode_check(line):
    """Try to decode each line to Unicode

    Parameters
    ----------
    line : bytes or str, data to be encoded to 'utf-8'

    Returns
    -------
    str or bool, decoded line or False
    """

    try:
        line.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


def rsls_whitespace(line):
    """Try to remove whitespace from line

    Parameters
    ----------
    line : str, line of text to remove whitespace from

    Returns
    -------
    str or bool, stripped line or False
    """
    try:
        return line.rstrip().lstrip()
    except:
        return False


def remove_star(line):
    """Try to remove star ('*') characters from a line

    Parameters
    ----------
    line : str, line

    Returns
    -------
    str or bool, line with '*' removed or False
    """
    try:
        return line.replace('*', '')
    except:
        return False


def remove_control_characters(s):
    """Use category identification to remove control characters

    This function might need some bytes level handling too...

    Parameters
    ----------
    s : str, to look for control characters

    Returns
    -------
    str or bool, line with control characters removed or False
    """
    try:
        return ''.join(ch for ch in s if unicodedata.category(ch)[0] != 'C')
    except:
        return False


def cleaner(data_list, limit=700, line_len=10, verbose=False):
    """
    Parameters
    ----------
    data_list : list, subset of data to check for integrity
    verbose : bool,
    limit : int,
    line_len : int,

    Returns
    -------
    z : list, cleaned data
    y : list, unicode error indexes
    x : list, blank lines
    """

    if data_list is None:
        if verbose:
            print('load.cleaner>> No list passed to clean!')
        return None, None, None
    else:
        if verbose:
            print('load.cleaner>> list loaded...')

    a = len(data_list)

    z = [''] * a
    y = [False] * a
    x = [False] * a

    for n in range(0, a):

        line = data_list[n]

        # remove all '*' characters
        _y = remove_star(line)

        # strip whitespace from start & end
        _y = rsls_whitespace(_y)

        if _y is False:
            y[n] = True
        else:
            line = _y

        # remove control characters
        _x = remove_control_characters(line)

        if _x is False:
            x[n] = True
        else:
            line = _x

        z[n] = line

    if verbose:
        print('load.cleaner>> done!')

    return z, y, x


def mbl_source(mbl_file):
    """Load MBL data from .csv

    Parameters
    ----------
    mbl_file : str, filepath to .csv of MBL data from ESRL

    Returns
    -------
    Pandas DataFrame
    """

    # grid latitude
    lat_sin = np.linspace(-1.0, 1.0, 41)
    # create column names
    col_names = ['YYYY.YYYYYY']
    for n in lat_sin:
        col_names.append("{0:.2f}".format(n))
        col_names.append("{0:.2f}".format(n) + "_uncert")
    # read in data
    df = pd.read_table(mbl_file,
                   sep=" ",
                   skipinitialspace=True,
                   dtype=float,
                   comment='#',
                   names=col_names)
    # format datetime
    df['datetime_mbl'] = df['YYYY.YYYYYY'].map(float_year_to_datetime)
    return df


def mbl_site(mbl_file):
    """Load MBL data generated for a specific site
    Note: this could be combined with the original loading

    Parameters
    ----------
    mbl_file : str
    """

    dfmbl = pd.read_csv(mbl_file, sep=',')
    dfmbl['xCO2_low_uncert'] = dfmbl.xCO2 - dfmbl.xCO2_uncert
    dfmbl['xCO2_high_uncert'] = dfmbl.xCO2 + dfmbl.xCO2_uncert
    dfmbl['datetime64_ns'] = pd.to_datetime(dfmbl.datetime_mbl)
    return dfmbl
