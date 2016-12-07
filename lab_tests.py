# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 10:46:46 2016

@author: dietrich

Functions to move into Jupyter eventually
"""

import pandas as pd

from scrape import Iridium


# if __name__ == "__main__":

units_tested = ['0132', '0186']

# search for data within a range
days_in_past = 5

t_start = '11/28/2016 00:00'
t_end = '12/10/2016 00:00'

# now back to the start of the day specified by 'days_in_past'
t_end = pd.to_datetime('now')
t_start = pd.to_datetime('today') - pd.Timedelta('%s days' % days_in_past)

# alternately, just use the pasted date range
if days_in_past is None:
    
    # determine time range to filter on
    t_start = pd.to_datetime(t_start)
    t_end = pd.to_datetime(t_end)

# instance Iridium data class
i = Iridium(form='ma')  # ma = mapco2, wg = waveglider

# set system serial numbers to process
i.unit_files(units=units_tested)

#print(i.data_names)
#print(i.data_urls_modtime)

fdl = i.download_files()

print('New files downloaded:', fdl)

df = pd.DataFrame(data=i.data_names,
                  columns=['unit', 'filename'])
df['file_local_modtime_str'] = i.data_urls_modtime_str
df['file_local_datetime'] = pd.DatetimeIndex(df.file_local_modtime_str)

# filter files down to those within the search time
df = df[(df.file_local_datetime >= t_start) &
        (df.file_local_datetime <= t_end)]

multiDict = {}
    # for n in df:
    #    multiDict[df_local_datetime] = df from Indexer.run()