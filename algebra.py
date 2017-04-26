"""Algebra for CO2 data processing"""


import numpy as np
from datetime import datetime, timedelta


def linear_fit(x, a, b):
    """Linear equation of a line as:
    y = ax + b

    Parameters
    ----------
    x : float
    a : float
    b : float

    Returns
    -------
    float, y
    """

    return a * x + b


def inverse_linear_fit(y, a, b):
    """Inverse linear equation of a line as:
    y = ax + b

    Parameters
    ----------
    x : float
    a : float
    b : float

    Returns
    -------
    float, x
    """
    return (y - b) / a


def natural_log_fit(x, a, b):
    """Natural logarithm equation as:
    y = a * ln(x) + b

    Parameters
    ----------
    x : float
    a : float
    b : float

    Returns
    -------
    float, x
    """
    return a * np.log(x) + b


def day_of_year(date_time):
    """Calculate the decimal days since the begining of the year

    Parameters
    ----------
    datetime : DateTime object

    Returns
    -------
    day : float
    """

    day = date_time.dayofyear
    hour = date_time.hour / 24.0
    minute = date_time.minute / 1440.0
    second = date_time.second / 86400.0
    microsecond = date_time.microsecond / 8.64e+10
    nanosecond = date_time.nanosecond / 8.64e+13

    day = day + hour + minute + second + microsecond + nanosecond
    return day


def float_year_to_datetime(fy):
    """Convert floating point year to datatime
    type(element) = pandas.tslib.Timestamp

    Parameters
    ----------
    fy : float

    Returns
    -------
    result : Pandas Timedelta
    """

    year = int(fy)
    rem = fy - year
    base = datetime(year, 1, 1)
    result = base + timedelta(seconds=(base.replace(year=base.year + 1)
                              - base).total_seconds() * rem)
    return result


def decimal_degrees(c):
    """Take a decimal minutes angular measurement and return a decimal
    degrees angular measurement.

    GPS units typically output in latitude ddmm.mmmm and longitude dddmm.mmmm
    and for calculations, need in latitude dd.dddddd or longitude ddd.dddddd.

    Note: does not check extent of input (i.e. 0 <= c <= 180)

    Parameters
    ----------
    c : string or float of coordinate latitude in ddmm.mmmm or
        longitude in dddmm.mmmm

    Returns
    -------
    decimal : float, latitude in dd.dddddd or longitude in ddd.dddddd
    """

    if isinstance(c, str):
        c = float(c)

    degree = np.int(c / 100)
    decimal = degree + ((c - (degree * 100)) / 60)
    return decimal


def get_mbl(df, m):
    """Get the time series CO2 data for a specific latitude.

    n > 90 = 90, n < -90 = -90 but that shouldn't

    Parameters
    ----------
    df : Pandas DataFrame, contains formatted MBL data
    n : float, latitude of interest

    Returns
    -------
    lat : float, latitude of MBL returned
    data : Pandas Series, MBL time series for lat
    """

    if (m > 90) or (m < -90):
        raise ValueError("Cannot be >90 or <-90")

    lat_sin = np.linspace(-1.0, 1.0, 41)

    n = lat_sin[np.argmin(np.abs(lat_sin - np.sin(np.deg2rad(m))))]
    n = '{:.2f}'.format(n)
    n_uncert = n + '_uncert'

    df_temp = df[['datetime_mbl', n, n_uncert]]
    df_temp.columns = ['datetime_mbl', 'xCO2', 'xCO2_uncert']
    return n, df_temp


def subtropic_TA(sss, sst):
    """TA to sss and sst relationship
    TODO: citation
    
    Parameters
    ----------
    sss : float
    sst : float
    
    Return
    ------
    ta : float
    """
    ta = (2305 + 
          58.66 * (sss-35) + 
          2.32 * (sss-35)**2 - 
          1.41 * (sst-20) + 
          0.04 * (sst-20)**2)
    return ta

