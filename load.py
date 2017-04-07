# -*- coding: utf-8 -*-
"""
Parse summary data frames from MAPCO2
Created on Mon Jul 25 14:30:25 2016
@author: Colin Dietrich
"""

import unicodedata
import pandas as pd

import config


data_types = ['mapco2', 'sami_ph', 'seafet_ph', 'sbe16']


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
    out = [['']*4 for _ in range(5000)]

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
    _df.sami_ph = _df.sami_ph.shift(-1)
    _df.seafet_ph = _df.seafet_ph.shift(-1)
    _df.sbe16 = _df.sbe16.shift(-1)
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


def create_start_end(index_df, data_len):

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

    _len = len(index_df['datetime'])

    for name in data_types:
        index_df[name + '_end'] = index_df[name + '_start'].shift(-1)
        index_df[name + '_end'] -= 1
        _end_i = index_df[name + '_end'].ix[_len-2] + index_df[name + '_end'].diff().mean()
        index_df.ix[_len-1, name + '_end'] = min(_end_i, data_len)
        index_df[name + '_end'] = index_df[name + '_end'].astype(int)
        index_df = index_df.replace(-1000, -999)

    return index_df


def iridium_single(f):
    """Laoad indexes for a single iridium file
    Parameters
    ----------
    f : str, filepath to file to parse

    Returns
    -------
    Pandas Dataframe
    """

    l = file_to_list(f)
    lc, errors, blanks = cleaner(data_list=l)
    d = index_data(lc)
    df = create_index_dataframe(d)
    df['datetime'] = get_start_timestamp(data_list=lc, index_df=df)
    df['datetime64_ns'] = pd.to_datetime(df.datetime, format='%Y/%m/%d_%H:%M:%S')
    df = df.replace('', -999)
    df = create_start_end(index_df=df, data_len=len(lc))
    return df


def unicode_check(line):
    """Try to decode each line to Unicode

    Parameters
    ----------
    line : bytes or str, data to be encoded to 'utf-8'
    """

    try:
        line.decode('utf-8')
        return True
    except UnicodeDecodeError:
        return False


def whitespace(line):
    """Try to remove whitespace from line

    Parameters
    ----------
    line : str, line of text to remove whitespace from
    """
    try:
        return line.rstrip().lstrip()
    except:
        return False


def remove_control_characters(s):
    """Use category identification to remove control characters

    This function might need some bytes level handling too...

    Parameters
    ----------
    s : str, to look for control characters
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

    line_starts = []

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

        if n < limit:
            # collate data lines for identification
            line_starts.append(line[0:line_len])

            # strip whitespace from start & end
        _y = whitespace(line)
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
