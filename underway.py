"""Import and process General Oceanics Underway pCO2 data

Colin Dietrich 2017
colin.dietrich@noaa.gov
"""
from .utils import file_ops
import numpy as np
import pandas as pd

# TODO: add to config.py
keepers = ['ATM', 'EQU', 'STD5z', 'STD1', 'STD2', 'STD3', 'STD4']
keeper_colors = dict(zip(keepers, ['cyan', 'blue', 'red', 'orange', 'green', 'purple', 'black']))
go_data_path = 'C:\\Users\\dietrich\\code\\mapco2_tests\\go_data\\'





def rename_and_format(_df):
    """Rename columns in GO data files and insert datetime column.
    Assumes str format and that 'pc_date' and 'pc_time' are valid column names
    after renaming header.

    Parameters
    ----------
    _df : Pandas Datafame

    Returns
    -------
    _df : Pandas Dataframe
    """

    _df.columns = [c.strip().lower().replace('  ', ' ').replace(' ', '_') for c in _df.columns]
    _df['datetime64_str'] = _df.pc_date.astype(str) + '_' + _df.pc_time.astype(str)
    _df['datetime64_ns'] = pd.to_datetime(_df.datetime64_str, format='%d/%m/%y_%H:%M:%S')
    return _df


def load_files(sys_ids, verbose=False):
    """Load all files for all Underway pCO2 system IDs specified

    Parameters
    ----------
    sys_ids : list of str, id of each system to be used for abs path to data
    verbose : bool, print debug information

    Returns
    -------
    Pandas Dataframe, all data collected
    """

    # load the first, or only system id
    _df = load_system(sys_ids[0], verbose=verbose)

    # if more than one id passed, concatenate them
    if len(sys_ids) > 1:
        for sys_id in sys_ids[1:]:
            _dfi = load_system(sys_id, verbose=verbose)
            _df = pd.concat([_df, _dfi], axis=0)
        _df.reset_index(drop=True, inplace=True)
    return _df


def load_system(sys_id, verbose=False):
    """Load all files for one Underway pCO2 system

    Parameters
    ----------
    sys_id : list of str, id of each system to be used for abs path to data
    #_f_list : list of str, absolute paths to tab delimited files to load
    verbose : bool, print debug information

    Returns
    -------
    Pandas Dataframe, all data collected
    """

    # build list of files to load
    abs_dir = go_data_path + sys_id + '\\'
    files = file_ops.files_in_directory(abs_dir, hint='dat.txt', skip=None)
    _f_list = [abs_dir + f for f in files]

    if verbose:
        print('Working on file:', _f_list[0])

    # load the first, or only file
    _df = pd.read_csv(_f_list[0], sep='\t')
    _df = rename_and_format(_df)

    # if more than one file, concatenate them
    for _f in _f_list[1:]:
        if verbose:
            print('Working on file:', _f)
        _dfi = pd.read_csv(_f, sep='\t')
        _dfi = rename_and_format(_dfi)
        _df = pd.concat([_df, _dfi], axis=0)

    # reset the row index and add the system specific id
    _df.reset_index(drop=True, inplace=True)
    _df['system'] = sys_id
    return _df


def mapco2_format(df, hours_offset=0):
    """Format GO data for MAPCO2 comparison
    """

    dfgo = df.copy()
    dfgo['xCO2'] = dfgo['co2_um/m']
    dfgo = dfgo[['datetime64_ns', 'xCO2', 'type', 'system']]
    dfgo = dfgo[(dfgo['type'] == 'EQU') | (dfgo['type'] == 'ATM')]
    dfgo['cycle'] = dfgo['type'].apply(lambda x: {'ATM': 'apof', 'EQU': 'epof'}[x])
    dfgo.drop(labels='type', axis=1, inplace=True)
    dfgo.datetime64_ns = df.datetime64_ns - pd.to_timedelta('{} hours'.format(hours_offset))
    return dfgo
