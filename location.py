

import algebra


"""This module assumes a dataframe format of:
index             datetime64_ns
-----
datetime_str     datetime64[ns]
lat                     float64
lon                     float64
datetime64_ns    datetime64[ns]

TODO: centralize flag codes, messages
"""


def flag_off_station(row, t_start, t_end, flag_ok=2.0, flag_bad=4.10):
    if (((row.datetime64_ns < t_start) or (row.datetime64_ns > t_end)) and
       row.flag == flag_ok):
        return flag_bad
    else:
        return flag_ok


def gps_std_filter(df_gps, t_start, t_end, target_lon, target_lat, max_std):

    gps = df_gps.copy()

    gps['flag'] = 2.0
    gps['flag_note'] = ''

    # flag outside time range = 4.10
    # gps['flag'] = gps.apply(lambda x: 4.10 if ((x.datetime64_ns < t_start) or
    #                                            (x.datetime64_ns > t_end)) and
    #                                             x.flag == 2.0
    #                                        else x.flag,
    #                         axis=1)

    gps['flag'] = gps.apply(lambda row: flag_off_station(row, t_start, t_end),
                            axis=1)

    message = 'Outside deployment start and end dates'
    gps['flag_note'] = gps.apply(lambda x: message if x.flag == 4.10
                                                   else x.flag_note,
                                 axis=1)


