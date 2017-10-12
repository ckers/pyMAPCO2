"""Import and process General Oceanics Underway pCO2 data

Colin Dietrich 2017
colin.dietrich@noaa.gov
"""

import pandas as pd


keepers = ['ATM', 'EQU', 'STD5z', 'STD1', 'STD2', 'STD3', 'STD4']
keeper_colors = dict(zip(keepers, ['cyan', 'blue', 'red', 'orange', 'green', 'purple', 'black']))


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


def load_files(_f_list, verbose=False):
    """
    Parameters
    ----------
    _f_list : list of str, absolute paths to tab delimited files to load

    Returns
    -------
    Pandas Dataframe
    """

    if verbose:
        print('Working on file:', _f_list[0])
    _df = pd.read_csv(_f_list[0], sep='\t')
    _df = rename_and_format(_df)
    for _f in _f_list[1:]:
        if verbose:
            print('Working on file:', _f)
        _dfi = pd.read_csv(_f, sep='\t')
        _dfi = rename_and_format(_dfi)
        _df = pd.concat([_df, _dfi], axis=0)
    _df.reset_index(drop=True, inplace=True)
    return _df


def mapco2_format(df, hours_offset=0):
    """Format GO data for MAPCO2 comparison
    """

    dfgo = df.copy()
    dfgo['xCO2'] = dfgo['co2_um/m']
    dfgo['system'] = 'GO5'
    dfgo = dfgo[['datetime64_ns', 'xCO2', 'type', 'system']]
    dfgo = dfgo[(dfgo['type'] == 'EQU') | (dfgo['type'] == 'ATM')]
    dfgo['cycle'] = dfgo['type'].apply(lambda x: {'ATM': 'apof', 'EQU': 'epof'}[x])
    dfgo.drop(labels='type', axis=1, inplace=True)
    dfgo.datetime64_ns = df.datetime64_ns - pd.to_timedelta('{} hours'.format(hours_offset))
    return dfgo
