# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 10:46:46 2016

@author: dietrich

Functions to move into Jupyter eventually
"""

import pandas as pd

import datatypes
import iridium

from scrape import Iridium
from load import Cleaner, Indexer

# if __name__ == "__main__":

#units_tested = ['0132', '0176', '0002', '0005', '0019', '0168']

units_tested = ['0009']


# search for data within a range
days_in_past = 11

t_start = '03/06/2016 00:00'
t_end = '01/09/2017 00:00'

verbose = True

# determine time range to filter on
t_start = pd.to_datetime(t_start)
t_end = pd.to_datetime(t_end)

# now back to the start of the day specified by 'days_in_past'
if days_in_past is not None:
    t_end = pd.to_datetime('now')
    t_start = pd.to_datetime('today') - pd.Timedelta('%s days' % days_in_past)

# instance Iridium data class
i = Iridium(form='ma')  # ma = mapco2, wg = waveglider

# set system serial numbers to process
i.unit_files(units=units_tested)

if verbose:
    print(i.data_names)
    print(i.data_urls_modtime)

fdl = i.download_files()

if verbose:
    print('New files downloaded:', fdl)

df = pd.DataFrame({'unit': i.data_sn,
                   'filename': i.data_filename})

df['file_local_modtime_str'] = i.data_urls_modtime_str
df['file_local_datetime'] = pd.DatetimeIndex(df.file_local_modtime_str)
df['new_filename'] = i.data_new_filename

# filter files down to those within the search time
df = df[(df.file_local_datetime >= t_start) &
        (df.file_local_datetime <= t_end)]
        
df.reset_index(inplace=True)


def get(f, verbose=False):
    """Get all iridium data from a file

    Parameters
    ----------
    f : str, filepath to iridium data file
    verbose : bool, print debug statements

    Returns
    -------
    status : bool, whether any frames of data where found in the file
    h : Pandas DataFrame, header data
    g : Pandas DataFrame, GPS data
    e : Pandas DataFrame, engineering data
    aux : Pandas DataFrame, auxilary data (pH - not implemented yet)
    sbe16 : Pandas DataFrame, SBE16 data
    """

    if verbose:
        print('get>> file = ', f)

    # get indices of data frame separators
    indexer = Indexer(file=f, terminal=False)

    if indexer.df is None:
        return False, None, None, None, None, None, None
    
    indexer.df.reset_index(inplace=True)

    # clean the data
    # z : list, cleaned data
    # y : list, unicode error indexes
    # x : list, blank lines
    cleaner = Cleaner()
    z, y, x = cleaner.run(indexer.file_to_list(f))

    if verbose:
        print('Header>> ', datatypes.MAPCO2Header().data_names)
        print('GPS>>    ', datatypes.MAPCO2GPS().data_names)
        print('ENGR>>   ', datatypes.MAPCO2Engr(data_type='iridium').data_names)
        print('indexer.df.head() >>', indexer.df.head())

    _h, _g, _e, _co2, _aux, _sbe16 = iridium.concat(data=z,
                                                   start=indexer.df.start.values,
                                                   end=indexer.df.end.values,
                                                   verbose=verbose)

    return True, _h, _g, _e, _co2, _aux, _sbe16

# dictionary for multi-index data
co2_dict = {}

# first filename in list
n = 0
f = df.ix[n, 'new_filename']
u = df.ix[n, 'unit']
if verbose:
    print('first filename to parse:', f)
fn = i.local_data_directory + '\\' + u + '\\' + f

# logic bug if status of n = 0 is False... fix!
status, h, g, e, co2, aux, sbe16 = get(fn, verbose=verbose)

# increment through the rest of the files
for n in range(1, len(df.filename)):
    f = df.ix[n, 'new_filename']
    u = df.ix[n, 'unit']
    fn = i.local_data_directory + '\\' + u + '\\' + f

    if verbose:
        print('file #:', n)
        print('filepath to open:', fn)

    status, h_n, g_n, e_n, co2_n, aux_n, sbe16_n = get(fn, verbose=verbose)

    if status is True:
        h = pd.concat([h, h_n])
        g = pd.concat([g, g_n])
        e = pd.concat([e, e_n])
        co2 = pd.concat([co2, co2_n])


df_epof = co2[co2.cycle == 'epof'].copy()
df_apof = co2[co2.cycle == 'apof'].copy()

df_epof.reset_index(inplace=True)
df_apof.reset_index(inplace=True)

df_epof.drop_duplicates(inplace=True)
df_apof.drop_duplicates(inplace=True)

p_epof = df_epof.pivot(index='datetime', columns='system', values='xCO2')
p_apof = df_apof.pivot(index='datetime', columns='system', values='xCO2')

# create a MultiIndex based on datetime and cycle values
co2m = co2.set_index(['datetime', 'cycle'])

print('Done!')
print('='*40)
