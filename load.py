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
import xarray as xr

from io import StringIO

from . import config
from .algebra import float_year_to_datetime, common_key_row, timestamp_rounder
from utils.main import flatten


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

    _df = pd.DataFrame(index_list, columns=config.frame_data_types)
    _df.ph_sami = _df.ph_sami.shift(-1)
    _df.ph_seafet = _df.ph_seafet.shift(-1)
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

    for name in config.frame_data_types:
        index_df[name + '_end'] = index_df[name + '_start']
        index_df[name + '_end'] = index_df[name + '_end'].astype(int)
        index_df[name + '_end'] += config.frame_default_number_of_list_lines
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


def load_file(f, datatype, system=None, verbose=False):
    """Load all available data types in a file
    Note: data types are determined by delimiter definitions, which 
    are hardcoded below.
    
    Parameters
    ----------
    f : str, filepath to file to parse
    datatype : str, system type... all because we duplicated serial numbers between
        mapco2, asv and waveglider... sigh.  A global reassignment might be better.
        For now a simple convention: 'm' = mapco2, 'a' = asv, 'w' = waveglider
    system : str, electronics system serial number.  Primarily used for single flash
        imports. Example: System 0176 = '0176'
    verbose : bool, print verbose statements

    Returns
    -------
    df: Pandas Dataframe, data of all identified data types
    TODO: document columns and types
    """

    if verbose:
        print(f)

    l = file_to_list(f)

    lc, errors, blanks = cleaner(data_list=l)

    # acknowledgement record, i.e. SS =3 or reboot to fast
    if len(lc) < 10:
        return pd.DataFrame([])

    for line in lc[0:8]:
        # system status transmission
        # removed due to some files having status AND data
        # will likely break when there's a status in the MIDDLE of the file
        # Thanks firmware!
        # no data test transmission
        if line[0:4] == 'Each':
            return pd.DataFrame([])

    df = format_index_dataframe(lc)

    # files that don't have any data (i.e. RECV frames)
    if len(df) == 0:
        return pd.DataFrame([])

    df['source'] = os.path.normpath(f).split('\\')[-1]
    if system is None:
        df['system'] = datatype + '_' + df.source.str[1:5]
    else:
        df['system'] = str(system)

    df['common_key'] = df.apply(common_key_row, axis=1)

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


def file_batch(f_list, datatype, verbose=False):
    """Load multiple iridium files using frames_all
    
    Parameters
    ----------
    f_list : list of str, filepath to file to parse
    verbose : bool, show debug statements
    
    Returns
    -------
    Pandas Dataframe, data of all identified data types
    """

    if verbose:
        print('load.file_batch>>')
    _df_list = []
    for n in range(0, len(f_list)):
        _df = load_file(f=f_list[n], datatype=datatype[n], verbose=verbose)
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


def repeat_finder(s, min_count=16, verbose=False):
    """Find repeated characters that are likely a firmware bug
    i.e. '000000000000000'

    Parameters
    ----------
    s : str, line of data
    min_count : int, number of sequential characters required to
        trigger a removal
    verbose : bool, print debug info

    Returns
    -------
    str, stripped of most common repeated character
    """

    c = -1
    removals = {}
    indexes = list(range(len(s)))[:-1]
    if verbose:
        print('load.repeat_stripper>> indexes:', indexes)

    for n in indexes:

        ns0 = s[n-1]
        ns1 = s[n]

        if ns0 == ns1:
            c += 1
        else:
            c = -1
        if verbose:
            print('load.repeat_finder>> n:{} ns0:{} ns1:{} c:{}'.format(n, ns0, ns1, c))

        if c > min_count:
            if ns1 in removals:
                removals[ns1][1] = n
            else:
                removals[ns1] = [n-c, n]

    if len(removals) == 0:
        if verbose:
            print('load.repeat_finder>> Length of removals =', len(removals))
        return False

    return removals


def repeat_stripper(s, min_count=16, verbose=False, limit=100):
    """Remove repeated characters that are likely a firmware bug
    i.e. '000000000000000'


    Parameters
    ----------
    s : str, line of data
    min_count : int, number of sequential characters required to
        trigger a removal
    verbose : bool, print debug info
    limit : int, max number of characters to check (prevents runaway)

    Returns
    -------
    str, stripped of most common repeated character
    """

    result = True
    line_out = None
    c = 0
    while True:
        result = repeat_finder(s=s, min_count=min_count, verbose=verbose)
        if verbose:
            print(result, type(result), result is False)
        if result is False:
            break
        else:
            ixs = [v for k, v in result.items()]
            ixs = sorted(ixs)
            ixs = list(flatten(ixs))
            ixs = [0] + ixs + [len(ixs)+1]
            new_s = config.repeat_flag  # Repeat stripped placeholder
            for ix in range(0, len(ixs)-2, 2):
                new_s = new_s + s[ixs[ix]:ixs[ix+1]]
            s = new_s
        if c > limit:
            break
        c += 1
    return s


def cleaner(data_list, limit=700, line_len=10, strip_stars=False, verbose=False):
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
        
        # strip whitespace from start & end
        _y = rsls_whitespace(line)

        if strip_stars:
            # remove all '*' characters
            _y = remove_star(_y)
        
        # remove repeat characters
        _y = repeat_stripper(_y)

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
    dfmbl.rename(columns={'xCO2': 'mbl_xCO2',
                          'xCO2_uncert': 'mbl_xCO2_uncert'}, inplace=True)
    dfmbl['mbl_xCO2_low_uncert'] = dfmbl.mbl_xCO2 - dfmbl.mbl_xCO2_uncert
    dfmbl['mbl_xCO2_high_uncert'] = dfmbl.mbl_xCO2 + dfmbl.mbl_xCO2_uncert
    dfmbl['datetime64_ns'] = pd.to_datetime(dfmbl.datetime_mbl)
    dfmbl.datetime64_ns = dfmbl.datetime64_ns.dt.round('1 min')
    return dfmbl


def netCDF(filepath):
    """Load one netCDF4 file from WHOI
    Uses xarray and Pandas

    Parameters
    ----------
    filepath : str

    Returns
    -------
    Pandas DataFrame
    """

    ds = xr.open_dataset(filepath)

    return ds.to_dataframe()


def netCDF_batch(filepath_list):

    df_list = []

    for f in filepath_list:
        df_list.append(netCDF(f))

    df = pd.concat(df_list)
    return df


def SAMI2_QCd(filepath):
    """Load a Sunburst Sensors SAMI2 QC program output file

    Parameters
    ----------
    filepath : str, path to .csv file output by QC program/MATLAB

    Returns
    -------
    Pandas DataFrame
    """

    # with salinity applied there are more columns...
    try:
        f_sami_names = ['datetime_sami', 'pH', 'SST_sami', 'SSS_sami', 'flags']
        df_sami = pd.read_csv(filepath, header=2, sep='\t', names=f_sami_names,
                              converters={'timestamp': str, 'flags': str})
    # constant salinity case
    except:
        f_sami_names = ['datetime_sami', 'pH', 'SST_sami', 'flags']
        df_sami = pd.read_csv(filepath, header=3, sep='\t', names=f_sami_names,
                              converters={'timestamp': str, 'flags': str})

    df_sami = df_sami.drop_duplicates()
    df_sami.reset_index(inplace=True, drop=True)
    df_sami.flags = df_sami.flags.str.strip()

    df_sami['outlier'] = df_sami.flags.str[3]
    df_sami['pump'] = df_sami.flags.str[2]
    df_sami['sat'] = df_sami.flags.str[1]
    df_sami['blank'] = df_sami.flags.str[0]

    df_sami['datetime64_ns_ph'] = pd.DatetimeIndex(df_sami.datetime_sami)
    df_sami['datetime64_ns'] = df_sami['datetime64_ns_ph'].apply(timestamp_rounder)

    df_sami.pH.replace(to_replace='NaN', value=np.nan, inplace=True)
    df_sami.pH = df_sami.pH.astype(float)

    df_sami['plot_outlier'] = np.where(df_sami.outlier == 1, df_sami.pH, np.nan)
    df_sami['plot_pump'] = np.where(df_sami.pump == 1, df_sami.pH, np.nan)
    df_sami['plot_sat'] = np.where(df_sami.sat == 1, df_sami.pH, np.nan)
    df_sami['plot_blank'] = np.where(df_sami.blank == 1, df_sami.pH, np.nan)

    return df_sami


def ftp_data(filepath):
    """Load FTP realtime data"""

    return pd.read_csv(filepath, header=5, sep=',')


def ndbc_file(fp, verbose=False):
    """Read in Generic NDBC Data from A FILE

    Parameters
    ----------
    fp : str, filepath to .ascii formatted NDBC data

    Returns
    -------
    data : list, nested lines of stripped, split data
    header : list, header names
    """

    sf = open(fp).read()
    a = sf.split('Deployment: ')
    b = [StringIO(n) for n in a]

    dfs_to_concat = []
    for n in b[1:]:
        _df = ndbc_df(n)
        if verbose:
            print(_df.head())
        dfs_to_concat.append(_df)

    df = pd.concat(dfs_to_concat, axis=0, join='outer')
    return df


def ndbc_list(itter):
    """Read in Generic NDBC Data

    Parameters
    ----------
    itter : itterable with .ascii formatted NDBC data
        (file object or StringIO, etc)

    Returns
    -------
    data : list, nested lines of stripped, split data
    header : list, header names
    """

    header = ''
    data = []
    units = None

    for line in itter:
        if line[0:8] == 'YYYYMMDD':
            header = line.split()
        if line[0:5] == 'Depth':
            units = line.split()
        else:
            try:
                _ = int(line[0:8])
                data.append(line.strip().split())
            except:
                continue

    return data, header, units


def ndbc_df(itter, units=None):
    """Load NDBC file into Pandas DataFrame

    Parameters
    ----------
    itter : itterable with .ascii formatted NDBC data
        (file object or StringIO, etc)
    units : bool, optional return units (depth, quality flags)

    Returns
    -------
    _df : Pandas DataFrame with datetime64_ns index
    units : list
    """

    d, h, u = ndbc_list(itter)

    # all because NDBC uses 2 column variable names... sigh
    if u is not None:
        depth = []
        for i in u:
            try:
                i = int(i)
                depth.append(i)
            except ValueError:
                continue

        new_columns = []
        n = 0
        for c in h:
            if 'QQQQ' in c:
                c = 'quality'
            if 'MMMM' in c:
                c = 'mode'
            for label in ['SSS', 'SAL', 'SST', 'TEMP']:
                if label in c:
                    c = c + '_' + str(depth[n])
                    n += 1
            new_columns.append(c)
        h = new_columns

    # create DataFrame using header variable names
    _df = pd.DataFrame(d, columns=h)

    for col in _df.columns:
        for sss in ['SSS', 'SAL', 'SST', 'TEMP']:
            if sss in col:
                _df[col] = _df[col].astype(float)

    _df['datetime_str'] = _df.YYYYMMDD + ' ' + _df.HHMMSS
    _df['datetime64_ns'] = pd.to_datetime(_df.datetime_str, format="%Y%m%d %H%M%S")
    _df.index = _df.datetime64_ns
    _df.index.name = 'datetime64_ns'
    _df.replace(to_replace=-9.999, value=np.nan, inplace=True)
    if units is not None:
        return _df, u
    return _df
