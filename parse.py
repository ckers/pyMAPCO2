# -*- coding: utf-8 -*-
"""
Parse MAPCO2 data
Created on Thu Jul 28 14:45:54 2016
@author: Colin Dietrich
"""

import time
import re
import numpy as np
import pandas as pd

from . import datatypes


def date_time_convert(dt, ft):
    """Convert date_time value to unix time
    Parameters
    ----------
    dt : date_time string
    ft : format of date_time string

    Returns
    -------
    t : unix time in seconds
    """
    return time.mktime(time.strptime(dt, ft))


def header(line, verbose=False):
    """Parse the header line of the mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    Returns
    -------
    h : class, instance of data class MAPCO2Header with data set
    """

    if verbose:
        print("parse.header>>  ", line)

    h = datatypes.MAPCO2Header()
    h.parse(line=line, verbose=verbose)

    return h


def gps(line, verbose=False):
    """Parse the gps header line of the mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    Returns
    -------
    g : class, instance of data class MAPCO2GPS with data set

    """
    g = datatypes.MAPCO2GPS()
    g.parse(line=line, verbose=verbose)

    return g


def engr(line, verbose=False, data_type='iridium', firmware='6.09'):
    """Parse the engineering header line of a mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    data_type : str, 'iridium', 'flash' or 'terminal'
    firmeware : str, '6.09' or other string float
    
    Returns
    -------
    e : class, instance of data class MAPCO2Engr with data set
    """

    e = datatypes.MAPCO2Engr(data_type=data_type)
    e.parse(line=line, verbose=verbose)
    e.update_names()
    try:
        e.decode_flag()
    # handle the never ending line inconsistencies
    except ValueError:
        print('Error with line:')
        print(line)
        return e
    return e


def co2_line(line, verbose=False):
    """Parse the co2 data line of a mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    Returns
    -------
    c : class, instance of data class MAPCO2Data with data set
    """

    if verbose:
        print("parse_co2    >>  ", line)

    c = datatypes.MAPCO2Data()

    co2 = line.split()

    co2 = float_converter(co2)

    try:
        c.minute = co2[0]
        c.licor_temp = co2[1]
        c.licor_temp_std = co2[2]
        c.licor_press = co2[3]
        c.licor_press_std = co2[4]
        c.xCO2 = co2[5]
        c.xCO2_std = co2[6]
        c.O2 = co2[7]
        c.O2_std = co2[8]
        c.RH = co2[9]
        c.RH_std = co2[10]
        c.RH_temp = co2[11]
        c.RH_temp_std = co2[12]
        c.xCO2_raw1 = co2[13]
        c.xCO2_raw1_std = co2[14]
        c.xCO2_raw2 = co2[15]
        c.xCO2_raw2_std = co2[16]
    except IndexError:
        pass

    return c


def co2_series(line, verbose):
    """Convert line of co2 data into a pandas series
    Parameters
    ----------
    line : str, one line of licor data
    verbose : bool, output print information
    Returns
    -------
    c_series : Series, pandas series object
    """
    c = co2_line(line=line, verbose=verbose)
    c_series = pd.Series(data=c.data(), index=c.data_names)
    return c_series


def float_converter(data_line):
    """Clean and convert all data to floats.  Attempts to find directly,
    regexp find float, regexp find int in that order.

    Parameters
    ----------
    data_line : list, str format of data

    Returns
    -------
    list of floats"""
    line = []
    for n in range(0, len(data_line)):
        x = data_line[n]
        try:
            y = float(x)
        except ValueError:
            try:
                y = re.findall("\d+\.\d+", x)[0]  # find first float
            except IndexError:
                try:
                    y = re.findall("\d+", x)[0]  # find first int
                except IndexError:
                    y = np.nan
#        parse_log.events.append("parse.float_validator>> error converting to float: "
#                                + current_frame)
        line.append(y)
    return line
