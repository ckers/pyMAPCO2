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

import config

# we're shooting for all this data:
pco2_header = ("location_code", "system_code",
               "unit_time", "unit_unix_time",
               "gps_time", "lat", "lon", "firmware", "mode",
               "cycle",
               "licor_temp", "licor_temp_std",
               "licor_pres", "licor_pres_std",
               "pco2", "pco2_std",
               "o2_percent", "o2_std",
               "rh", "rh_std", "rh_temp", "rh_temp_std",
               "raw1", "raw1_std", "raw2", "raw2_std")


class MAPCO2Base(object):

    def __init__(self):
        pass
    
    def series(self):
        """Single dimension data"""
        return pd.Series(data=self.data(), index=self.data_names)

    def dataframe(self, date_time):
        """Multi dimension timeseries data"""
        self.df = pd.DataFrame(data=self.data(),
#                               index=date_time,
                               columns=self.data_names)


class MAPCO2Header(MAPCO2Base):
    def __init__(self):
        
        self.df = None
        
        self.mode = []
        self.checksum = []
        self.size = []
        self.date_time = []
        self.location = []
        self.system = []
        self.firmware = []

        self.date_time_format = "%Y/%m/%d_%H:%M:%S"
        self.firmware_format = "A.B_%m/%d/%Y"

        self.data_names = ["mode",
                           "checksum",
                           "size",
                           "date_time",
                           "location",
                           "system",
                           "firmware"]

    def data(self):
        _a = [self.mode,
              self.checksum,
              self.size,
              self.date_time,
              self.location,
              self.system,
              self.firmware]
        return _a


class MAPCO2GPS(MAPCO2Base):
    
    def __init__(self):
        
        self.df = None
        
        self.date_time = []
        self.lat_deg = []
        self.lat_min = []
        self.lat_direction = []
        self.lat = []
        self.lon_deg = []
        self.lon_min = []
        self.lon_direction = []
        self.lon = []
        self.fix_time = []  # seconds to find a fix
        self.quality = []  # quality factor, lower is better
        self.time_before_check = []
        self.time_after_check = []
        self.valve_time = []

        self.date_time_format = "%m/%d/%Y_%H:%M:%S"

        self.data_names = ["date_time",
                           "lat_deg", "lat_min", "lat_direction", "lat_ddeg",
                           "lon_deg", "lon_min", "lon_direction", "lon_ddeg",
                           "fix_time", "quality",
                           "time_before_check", "time_after_check",
                           "valve_time"]

    def data(self):
        return [self.date_time,
                self.lat_deg,
                self.lat_min,
                self.lat_direction,
                self.lon_deg,
                self.lon_min,
                self.lon_direction,
                self.fix_time,
                self.quality,
                self.time_before_check,
                self.time_after_check,
                self.valve_time]


class MAPCO2Engr(MAPCO2Base):
    def __init__(self, data_type="iridium"):

        self.df = None

        self.data_type = data_type

        self.v_logic = []
        self.v_trans = []
        self.zero_coeff = []
        self.span_coeff = []
        self.flag = []

        self.sst = []
        self.sst_std = []
        self.ssc = []
        self.ssc_std = []
        self.sss = []
        self.sss_std = []
        self.u = []
        self.u_std = []
        self.v = []
        self.v_std = []
        self.raw_compass = []
        self.raw_vane = []
        self.raw_windspeed = []

        self.data_names = ["v_logic", "v_trans", "zero_coeff", "span_coeff",
                           "flag", "sst", "sst_std", "ssc", "ssc_std",
                           "sss", "sss_std", "u", "u_std", "v", "v_std",
                           "raw_compass", "raw_vane", "raw_windspeed"]

        self.update_names()

    def update_names(self):
        if self.data_type != "iridium":
            self.data_names = self.data_names[:5]

    def data(self):
        _a = [self.v_logic,
              self.v_trans,
              self.zero_coeff,
              self.span_coeff,
              self.flag,
              self.sst,
              self.sst_std,
              self.ssc,
              self.ssc_std,
              self.sss,
              self.sss_std,
              self.u,
              self.u_std,
              self.v,
              self.v_std,
              self.raw_compass,
              self.raw_vane,
              self.raw_windspeed]

        if (self.data_type == "flash") or (self.data_type == "terminal"):
            _a = _a[:5]
        return _a


class MAPCO2DataFinal(MAPCO2Base):

    def __init__(self):
        
        self.dp = []
        self.df = None
        
        self.date_time = []
        self.lat = []
        self.lon = []

        self.licor_press_atm = []
        self.licor_temp_c = []
        self.O2_percent = []
        self.sst = []
        self.sss = []
        
        self.xCO2_air_qf = []
        self.xCO2_air_wet = []
        self.xCO2_air_dry = []
        self.xCO2_air_H2O = []
        self.fCO2_air_sat = []
        
        self.xCO2_sw_qf = []
        self.xCO2_sw_wet = []
        self.xCO2_sw_dry = []
        self.xCO2_sw_H2O = []
        self.fCO2_sw_sat = []

        self.dfCO2 = []

        self.data_names = ["deployment",
                           "date_time",
                           "lat_ddeg",
                           "lon_ddeg",

                           "licor_press",                           
                           "licor_temp",
                           "O2",
                           "sst",
                           "sss",
                           
                           "xCO2_air_qf",
                           "xCO2_air_wet",
                           "xCO2_air_dry",
                           "xCO2_air_H2O",
                           "fCO2_air_sat",
                                
                           "xCO2_sw_qf",
                           "xCO2_sw_wet",
                           "xCO2_sw_dry",
                           "xCO2_sw_H2O",
                           "fCO2_sw_sat",
                        
                           "dfCO2",]
        
    def data(self):
        _a = [self.dp,
              self.date_time,
              self.lat,
              self.lon,
            
              self.licor_press_atm,
              self.licor_temp_c,
              self.O2_percent,
              self.sst,
              self.sss,
            
              self.xCO2_air_qf,
              self.xCO2_air_wet,
              self.xCO2_air_dry,
              self.xCO2_air_H2O,
              self.fCO2_air_sat,
            
              self.xCO2_sw_qf,
              self.xCO2_sw_wet,
              self.xCO2_sw_dry,
              self.xCO2_sw_H2O,
              self.fCO2_sw_sat,
            
              self.dfCO2]
        return _a
        
#    def dataframe(self, date_time):
#        self.df = pd.DataFrame(data=self.data(),
#                               index=self.date_time,
#                               columns=self.data_names)
        
        
class MAPCO2Data(MAPCO2Base):
    def __init__(self):
        
        self.df = None
        
        self.minute = []
        self.licor_temp = []
        self.licor_temp_std = []
        self.licor_press = []
        self.licor_press_std = []
        self.xCO2 = []
        self.xCO2_std = []
        self.O2 = []
        self.O2_std = []
        self.RH = []
        self.RH_std = []
        self.RH_temp = []
        self.RH_temp_std = []
        self.xCO2_raw1 = []
        self.xCO2_raw1_std = []
        self.xCO2_raw2 = []
        self.xCO2_raw2_std = []

        self.data_names = ["minute",
                           "licor_temp",
                           "licor_temp_std",
                           "licor_press",
                           "licor_press_std",
                           "xCO2",
                           "xCO2_std",
                           "O2",
                           "O2_std",
                           "RH",
                           "RH_std",
                           "RH_temp",
                           "RH_temp_std",
                           "xCO2_raw1",
                           "xCO2_raw1_std",
                           "xCO2_raw2",
                           "xCO2_raw2_std"]

    def data(self):
        _a = [self.minute,
              self.licor_temp,
              self.licor_temp_std,
              self.licor_press,
              self.licor_press_std,
              self.xCO2,
              self.xCO2_std,
              self.O2,
              self.O2_std,
              self.RH,
              self.RH_std,
              self.RH_temp,
              self.RH_temp_std,
              self.xCO2_raw1,
              self.xCO2_raw1_std,
              self.xCO2_raw2,
              self.xCO2_raw2_std]
        return _a
        

class CO2Data(object):
    
    def __init__(self):
        self.date_time = []
        self.header = MAPCO2Header()
        self.gps = MAPCO2GPS()
        self.engr = MAPCO2Engr()
        self.data = MAPCO2Data()
        self.final = MAPCO2DataFinal()
        
    def dataframe(self):
        self.header.dataframe(self.date_time)
        self.gps.dataframe(self.date_time)
        self.engr.dataframe(self.date_time)
        self.data.dataframe(self.date_time)
        self.final.dataframe(self.date_time)
        

class MAPCO2ParseLog(object):
    def __init__(self):
        self.events = []


parse_log = MAPCO2ParseLog()
current_frame = ""


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
        parse_log.events.append("parse.float_validator>> error converting to float: "
                                + current_frame)
        line.append(y)
    return line


def parse_iridium_frame(data, start, end, verbose=False, data_type="iridium"):
    # break the data file into samples
    sample = data[start:end]

    current_frame = sample[0]

    h = parse_header(sample[0], verbose=verbose)
    g = parse_gps(sample[1], verbose=verbose)
    e = parse_engr(sample[2], verbose=verbose, data_type=data_type)
    zpon = parse_co2_line(sample[3], verbose=verbose)
    zpof = parse_co2_line(sample[4], verbose=verbose)
    zpcl = parse_co2_line(sample[5], verbose=verbose)
    spon = parse_co2_line(sample[6], verbose=verbose)
    spof = parse_co2_line(sample[7], verbose=verbose)
    spcl = parse_co2_line(sample[8], verbose=verbose)
    epon = parse_co2_line(sample[9], verbose=verbose)
    epof = parse_co2_line(sample[10], verbose=verbose)
    apon = parse_co2_line(sample[11], verbose=verbose)
    apof = parse_co2_line(sample[12], verbose=verbose)

    return h, g, e, zpon, zpof, zpcl, spon, spof, spcl, epon, epof, apon, apof

def clean_flash_line(line):
    """Clean a line of flash data

    Parameters
    ----------
    line : str

    Returns
    -------

    """
    pass

def index_flash_frame(data, verbose=False):
    """Find delimiters between cycles
    Parameters
    ----------
    data : list, str of each line from flash file in this frame
    
    Returns
    -------
    list, index numbers of headers for each data frame
    """
    indexes = []
    minutes = []
    for n in range(0, len(data)):
        if verbose: print(n)
        if data[n][0:5] == "*****":
            indexes.append(n)
            minutes.append(data[n][-2:])
    return indexes, minutes


def find_flash_cycle_sections(sample, verbose=False):
    indexes = []
    names = []
    for n in range(0, len(sample)):
        if verbose: print(n, sample[n][0:2])
        if sample[n][0:2] in ("Li", "O2", "RH", "Rh"):
            indexes.append(n)
            names.append(sample[n])
            print("YES", n, sample[n])
    indexes.append(len(sample))
    return indexes, names

def parse_flash_frame(data, start, end, verbose=False):
    # break the data file into samples
    sample = data[start:end]
#    print("sample>>")
#    print(sample)
    i, m = index_flash_frame(sample)
    print("i>>", i)
    print("m>>", m)
    i_end = i[1:] + [len(sample)]
    cycle = sample[i[0]:i_end[0]]
    si, sn = find_flash_cycle_sections(cycle, verbose=True)
    print("si>> ", si)
    si_end = si[1:]
    si = si[:-1]
    print("si>> ", si)
    print("si_end>>", si_end)
    print("sample[0:35]>>", sample[0:35])
    li = cycle[si[0]:si_end[1]]
    o2 = cycle[si[1]:si_end[1]]
    rh = cycle[si[2]:si_end[2]]
    rht = cycle[si[3]:si_end[3]]
    print("li>>", li)
    print("o2>>", o2)
    print("rh>>", rh)
    print("rht>>", rht)
    
#    return h, g, e, zpon, zpof, zpcl, spon, spof, spcl, epon, epof, apon, apof


def build_frames(data, start, end, verbose=False, data_type="iridium"):
    if (data_type == "iridium") or (data_type == "terminal"):
        (h, g, e,
         zpon, zpof, zpcl,
         spon, spof, spcl,
         epon, epof,
         apon, apof) = parse_iridium_frame(data=data,
                                           start=start, end=end,
                                           verbose=verbose,
                                           data_type=data_type)

    if data_type == "flash":
        parse_flash_frame(data=data, start=start, end=end, verbose=verbose)
#        (h, g, e,
#         zpon, zpof, zpcl,
#         spon, spof, spcl,
#         epon, epof,
#         apon, apof) = parse_flash_frame(data=data,
#                                         start=start, end=end,
#                                         verbose=verbose)
#
#    print(e.data)
#    h_series = pd.Series(data=h.data(), index=h.data_names)
#    g_series = pd.Series(data=g.data(), index=g.data_names)
#    e_series = pd.Series(data=e.data(), index=e.data_names)
#
#    df = pd.DataFrame(data=[pd.Series(data=zpon.data(), index=zpon.data_names),
#                            pd.Series(data=zpof.data(), index=zpof.data_names),
#                            pd.Series(data=zpcl.data(), index=zpcl.data_names),
#                            pd.Series(data=spon.data(), index=spon.data_names),
#                            pd.Series(data=spof.data(), index=spof.data_names),
#                            pd.Series(data=spcl.data(), index=spcl.data_names),
#                            pd.Series(data=epon.data(), index=epon.data_names),
#                            pd.Series(data=epof.data(), index=epof.data_names),
#                            pd.Series(data=apon.data(), index=apon.data_names),
#                            pd.Series(data=apof.data(), index=apof.data_names),
#                            ],
#                      index=["zpon", "zpof", "zpcl",
#                             "spon", "spof", "spcl",
#                             "epon", "epof",
#                             "apon", "apof"])
#
#    return h_series, g_series, e_series, df


def parse_header(data, verbose=False):
    if verbose:
        print("parse_header >>  ", data)

    h = MAPCO2Header()

    # extract header information
    header = data.split()

    h.mode = header[0]
    h.checksum = header[1]
    h.size = header[2]
    h.date_time = header[3] + "_" + header[4]
    #    unit_unix_time = time.mktime(time.strptime(unit_time, "%Y/%m/%d_%H:%M:%S"))
    h.location = header[5]
    h.system = header[6]

    # older versions of the firmware don't include the version number
    try:
        h.firmware = header[7] + "_" + header[8]
    except:
        h.firmware = False

    return h


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


def parse_gps(data, verbose=False):
    if verbose:
        print("parse_gps    >>  ", data)

    g = MAPCO2GPS()

    # extract location information
    gps = data.split()
    _t = gps[0] + "_" + gps[1]

    # if no fix, fill with zero
    if _t in config.time_ignore:
        g.date_time = "NaT"
    else:
        try:
            g.date_time = _t
        except:
            parse_log.events.append("%s, %s, %s, Unable to parse %s"
                                    % (g.time, g.location,
                                       g.system, g))
            print("parse_gps>> Error parsing: ", gps)

    lat = gps[2].split(".")

    g.lat_deg = lat[0][:-2]
    g.lat_min = lat[0][-2:] + "." + lat[1]
    g.lat_direction = gps[3]

    lon = gps[4].split(".")

    g.lon_deg = lon[0][:-2]
    g.lon_min = lon[0][-2:] + "." + lon[1]
    g.lon_direction = gps[5]

    g.fix_time = gps[6]
    g.quality = gps[7]
    g.time_before_check = gps[8] + "_" + gps[9]
    g.time_after_check = gps[10] + "_" + gps[11]

    try:
        if len(gps) > 12:
            g.valve_time = gps[13]
    except:
        g.valve_time = []
        if verbose:
            print("parse_gps>> Error in valve current: ", gps)
    return g


def parse_engr(data, verbose=False, data_type="iridium"):
    if verbose:
        print("parse_engr   >>  ", data)

    e = MAPCO2Engr(data_type=data_type)

    engr = data.split()

    e.v_logic = float(engr[0])
    e.v_trans = float(engr[1])
    e.zero_coeff = float(engr[2])
    e.span_coeff = float(engr[3])
    e.flag = engr[4]  # needs to remain string for flag bit access

    try:
        e.sst = float(engr[5])
        e.sst_std = float(engr[6])
        e.ssc = float(engr[7])
        e.ssc_std = float(engr[8])
        e.sss = float(engr[9])
        e.sss_std = float(engr[10])
        e.u = float(engr[11])
        e.u_std = float(engr[12])
        e.v = float(engr[13])
        e.v_std = float(engr[14])
        e.raw_compass = float(engr[15])
        e.raw_vane = float(engr[16])
        e.raw_windspeed = float(engr[17])
    except:
        if verbose:
            print("parse_engr>> ENGR line met data parsing error")

    e.update_names()

    return e


def parse_co2_line(data, verbose=False):
    if verbose:
        print("parse_co2    >>  ", data)

    c = MAPCO2Data()

    co2 = data.split()

    #    co2 = [float(n) for n in co2]
    print(co2)
    co2 = float_converter(co2)
    print(co2)

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


def parse_co2_series(data, verbose):
    c = parse_co2_line(data=data, verbose=verbose)
    c_series = pd.Series(data=c.data(), index=c.data_names)
    return c_series
