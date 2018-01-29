

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


def mapco2_to_ddm(x):
    """MAPCO2 Degrees Minutes format to Degrees Decimal Minutes
    ...because who cares about format?

    Parameters
    ----------
    x : str
    Returns
    -------
    x_int, str: Degrees
    x_min, str: Decimal Minutes
    """
    a, b = x.split('.')
    x_int = a[:-2]
    x_min = a[-2:] + '.' + b
    return x_int, x_min


def dms2dd(degrees, minutes, seconds, direction):
    """Degrees Minutes Seconds Direction to Decimal Degrees"""
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction == 'W' or direction == 'S':
        dd *= -1
    return dd


def mapco2_to_dd(lat_raw, ns, lon_raw, ew):
    """Convert raw MAPCO2 Latitude and Longitude to Decimal Degrees
    Parameters
    ----------
    lat_raw, str : MAPCO2 latitude
    ns, str : 'N' or 'S' direction
    lon_raw, str : MAPCO2 longitude
    ew, str : 'E' or 'W' direction

    Returns
    -------
    lat, float : latitude in decimal degrees
    lon, float : longitude in decimal degrees
    """
    lat_deg, lat_min = mapco2_to_ddm(lat_raw)
    lon_deg, lon_min = mapco2_to_ddm(lon_raw)
    lat = dms2dd(degrees=lat_deg, minutes=lat_min, seconds=0, direction=ns)
    lon = dms2dd(degrees=lon_deg, minutes=lon_min, seconds=0, direction=ew)
    return lat, lon


def mapco2_to_dd_mapper(row, lat_raw='lat_raw', ns='NS', lat='lat',
                             lon_raw='lon_raw', ew='EW', lon='lon'):
    """Convert raw MAPCO2 Latitude and Longitude to Decimal Degrees

    Parameters
    ----------
    row, Pandas DataFrame row
    lat_raw, str : column name for raw MAPCO2 latitude
    ns, str : column name for 'N' or 'S' direction
    lon_raw, str : column name for raw MAPCO2 longitude
    ew, str : column name for 'E' or 'W' direction

    Returns
    -------
    lat, float : latitude
    lon, float : longitude
    """

    _lat, _lon = mapco2_to_dd(lat_raw=row[lat_raw], ns=row[ns], lon_raw=row[lon_raw], ew=row[ew])
    row[lat] = _lat
    row[lon] = _lon
    return row