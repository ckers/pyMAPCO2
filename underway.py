"""Import and process General Oceanics Underway pCO2 data

Colin Dietrich 2017
colin.dietrich@noaa.gov
"""
import os
import numpy as np
import pandas as pd

from .utils import file_ops

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


def time_reformat(line):
    """Reformat to consistent dates"""
    line = line.split('\t')
    #print(line)
    date = line[2]
    date = date.split('/')
    d = date[0]
    m = date[1]
    y = date[2]

    if len(y) == 2:
        y = '20' + y

    date = y + '/' + m + '/' + d
    line[2] = date
    return ','.join(line)


def concat_txt(data_path, verbose=False):
    """Concatenate all data into one .csv file to be loaded using Cathy's VBA program
    
    Parameters
    ----------
    data_path : str, path to folder containing GO data
    
    Returns
    -------
    .csv file of data
    """
    
    # build list of files to load
    #abs_dir = go_data_path + sys_id + '\\'
    #files = file_ops.files_in_directory(abs_dir, hint='dat.txt', skip=None)
    #_f_list = [abs_dir + f for f in files]

    # build list of files to load
    files = file_ops.files_in_directory(data_path, hint='dat.txt', skip=None)
    _f_list = [data_path + '\\' + f for f in files]
    
    
    if verbose:
        print('Working on file:', _f_list[0])

    lines_out = []
    # load the first, or only file
    with open(_f_list[0]) as f:
        h = f.readline()

    if 'tank T' in h:
        h = h.replace('tank T', 'SST')
    
    h = h.replace('\t', ',')
    lines_out.append(h)

    for fn in _f_list:
        with open(fn) as f:
            for line in f:
                if line[0:4] == 'Type':
                    continue
                if ('DRAIN' in line[0:10]) or ('DOWN' in line[0:10]):
                    continue
                else:
                    lines_out.append(time_reformat(line))

    fp = data_path + '\\compiled_GO_data.csv'
    with open(fp, 'w') as f:
        for i in lines_out:
            f.write(i)
            
    return os.path.normpath(fp)
        

def load_system(data_path, verbose=False):
    """Load all files for one Underway pCO2 system into a DataFrame

    Parameters
    ----------
    #sys_id : list of str, id of each system to be used for abs path to data
    data_path : str, path to folder containing GO data
    #_f_list : list of str, absolute paths to tab delimited files to load
    verbose : bool, print debug information

    Returns
    -------
    Pandas Dataframe, all data collected
    """

    # build list of files to load
    #abs_dir = go_data_path + sys_id + '\\'
    #files = file_ops.files_in_directory(abs_dir, hint='dat.txt', skip=None)
    files = file_ops.files_in_directory(data_path, hint='dat.txt', skip=None)
    #_f_list = [abs_dir + f for f in files]
    _f_list = [data_path + '\\' + f for f in files]

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
    #_df['system'] = sys_id
    return _df

    
def select_file():
    """Stand alone file selection function"""
    import tkinter
    from tkinter import filedialog
    
    root = tkinter.Tk()
    fp = filedialog.askopenfilename()
    root.destroy()
    return os.path.normpath(fp)
    
def select_folder():
    """Stand alone folder selection function"""
    
    import tkinter
    from tkinter import filedialog
    
    root = tkinter.Tk()
    fp = filedialog.askdirectory()
    root.destroy()
    return os.path.normpath(fp)
    
def concat_txt_window():
    """Produces a window to ask for directory containing GO data, then calls concat_txt()
    """

    return concat_txt(select_folder(), verbose=False)
    
    
def load_system_window():
    """Produces a window to ask for directory containing GO data, then calls concat_txt()
    """
    fp = select_folder()
    return load_system(fp, verbose=False), fp
    
    
def mapco2_format(df, hours_offset=0):
    """Format GO data for MAPCO2 comparison
    Might need to refactor or nuke...
    """

    dfgo = df.copy()
    dfgo['xCO2'] = dfgo['co2_um/m']
    dfgo = dfgo[['datetime64_ns', 'xCO2', 'type', 'system']]
    dfgo = dfgo[(dfgo['type'] == 'EQU') | (dfgo['type'] == 'ATM')]
    dfgo['cycle'] = dfgo['type'].apply(lambda x: {'ATM': 'apof', 'EQU': 'epof'}[x])
    dfgo.drop(labels='type', axis=1, inplace=True)
    dfgo.datetime64_ns = df.datetime64_ns - pd.to_timedelta('{} hours'.format(hours_offset))
    return dfgo
