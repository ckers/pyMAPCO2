# -*- coding: utf-8 -*-
"""Algebra for CO2 data processing

Colin Dietrich 2017
colin.dietrich@noaa.gov
"""


import numpy as np
from datetime import datetime, timedelta


def linear(x, a, b):
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


def inverse_linear(y, a, b):
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


def natural_log(x, a, b):
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
    date_time : DateTime object

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
    if c == 0.0:
        return 0.0
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


def timestamp_rounder(t):
    """Round a DatetimeIndex to a 30 minute interval"""
    return t.replace(minute=30 * (t.minute // 30), second=0, microsecond=0)


def timestamp_sec_rounder(t):
    """Round a DatetimeIndex to a 1 second interval"""
    return t.replace(microsecond=0)


def common_key(system, datetime64_ns):
    return system + '_' + timestamp_rounder(datetime64_ns).strftime('%Y-%m-%dT%H:%M:%SZ')


def common_key_row(row):
    """Create a common key value.

    Parameters
    ----------
    row : Pandas DataFrame row with:
        'datetime64_ns' and 'unit' columns

    Returns
    -------
    str : common key formatted as:
        'xxxx_'%Y-%m-%dT%H:%M:%SZ'' with time rounded to the half hour
    """

    #ck = (row.unit + '_' + #TODO delete if old method
    #      timestamp_rounder(row.datetime64_ns).strftime('%Y-%m-%dT%H:%M:%SZ'))
    ck = common_key(system=row.system, datetime64_ns=row.datetime64_ns)
    return ck


def m1_algebraic(x, y, x_m=None, y_m=None):
    """Find the geometric center of data

    Parameters
    ----------
    x : array-like, values
    y : array-like, values same length as x
    x_m : float, center of x values, optional
    y_m : float, center of y values, optional

    Returns
    -------
    xc : float, x center value
    yc : float, y center value
    Ri : array-like, distance from center for each (x, y)
    R : float, mean value of Ri
    res : float, residual sum of squares
    res2 : float, sum of squared residual squares (better name?)
    """

    # coordinates of the barycenter
    if x_m is None:
        x_m = np.mean(x)
    if y_m is None:
        y_m = np.mean(y)

    # calculation of the reduced coordinates
    u = x - x_m
    v = y - y_m

    # linear system defining the center in reduced coordinates (uc, vc):
    #    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
    #    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
    Suv  = sum(u*v)
    Suu  = sum(u**2)
    Svv  = sum(v**2)
    Suuv = sum(u**2 * v)
    Suvv = sum(u * v**2)
    Suuu = sum(u**3)
    Svvv = sum(v**3)

    # Solving the linear system
    A = np.array([ [ Suu, Suv ], [Suv, Svv]])
    B = np.array([ Suuu + Suvv, Svvv + Suuv ])/2.0
    uc, vc = np.linalg.solve(A, B)

    xc = x_m + uc
    yc = y_m + vc

    # Calculation of all distances from the center (xc, yc)
    Ri      = np.sqrt((x - xc)**2 + (y - yc)**2)
    R       = np.mean(Ri)
    residu  = np.sum((Ri-R)**2)
    residu2 = np.sum((Ri**2-R**2)**2)

    return xc, yc, Ri, R, residu, residu2


def lsq_circle(x, y, x_m=None, y_m=None):
    """Fit a circle to x,y data
    TODO: more docstring

    Parameters
    ----------
    x : array of float
    y : array of float
    x_m : float, center of x values, optional
    y_m : float, center of y values, optional
    """
    xc, yc, ri, r, residu, residu2 = m1_algebraic(x, y, x_m=x_m, y_m=y_m)
    theta_fit = np.linspace(-np.pi, np.pi, 180)
    x_fit = xc + r * np.cos(theta_fit)
    y_fit = yc + r * np.sin(theta_fit)
    return xc, yc, x_fit, y_fit, ri, r, residu, residu2
