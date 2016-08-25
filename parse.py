# -*- coding: utf-8 -*-
"""
Parse MAPCO2 data
Created on Thu Jul 28 14:45:54 2016
@author: Colin Dietrich
"""
import time

import config

# we're shooting for all this data:
pco2_header =  ("location_code", "system_code",
                "unit_time","unit_unix_time",
                "gps_time","lat","lon","firmware","mode",
                "cycle",
                "licor_temp","licor_temp_std",
                "licor_pres","licor_pres_std",
                "pco2","pco2_std",
                "o2_percent","o2_std",
                "rh","rh_std","rh_temp","rh_temp_std",
                "raw1","raw1_std","raw2","raw2_std")


class MAPCO2Header(object):
    def __init__(self):
        self.mode = None
        self.checksum = None
        self.size = None
        self.date_time = None
        self.location = None
        self.system = None
        self.firmware = None

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

class MAPCO2GPS(object):
    def __init__(self):
        self.date_time = None
        self.lat_deg = None
        self.lat_min = None
        self.lat_direction = None
        self.lat = None
        self.lon_deg = None
        self.lon_min = None
        self.lon_direction = None
        self.lon = None
        self.fix_time = None  # seconds to find a fix
        self.quality = None  # quality factor, lower is better
        self.time_before_check = None
        self.time_after_check = None
        self.valve_time = None
        
        self.date_time_format = "%m/%d/%Y_%H:%M:%S"
        
        self.data_names = ["date_time", "lat_deg", "lat_min", "lat_direction",
                           "lon_deg", "lon_min", "lon_direction", 
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
        
class MAPCO2Engr(object):
    def __init__(self):
        self.v_logic = None
        self.v_trans = None
        self.zero_coeff = None
        self.span_coeff = None
        self.flag = None
        
        self.sst = None
        self.sst_std = None
        self.ssc = None
        self.ssc_std = None
        self.sss = None
        self.sss_std = None
        self.u = None
        self.u_std = None
        self.v = None
        self.v_std = None
        self.raw_compass = None
        self.raw_vane = None
        self.raw_windspeed = None
        
        self.data_names = ["v_logic", "v_trans", "zero_coeff", "span_coeff",
                           "flag", "sst", "sst_std", "ssc", "ssc_std",
                           "sss", "sss_std", "u", "u_std", "v", "v_std",
                           "raw_compass", "raw_vane", "raw_windspeed"]
    def data(self):
        return [self.v_logic,
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
        
class MAPCO2HeaderLog(object):
    def __init__(self):
        self.events = []

header_log = MAPCO2HeaderLog()

def parse_frame(data, start, end, verbose=False):

    # break the data file into samples
    sample = data[start:end]

    h = parse_header(sample[0], verbose=verbose)
    g = parse_gps(sample[1], verbose=verbose)
    e = parse_engr(sample[2], verbose=verbose)
    return h, g, e


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
#            header_log.events.append("%s, %s, %s, Unable to parse %s"
#                                     % (g.time, g.location,
#                                        g.system, g))
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
        g.valve_time = None
        if verbose:
            print("parse_gps>> Error in valve current: ", gps)
    return g
    
def parse_engr(data, verbose=False):
    
    if verbose:
        print("parse_engr   >>  ", data)
        
    e = MAPCO2Engr()
    
    engr = data.split()
    
    e.v_logic = engr[0]
    e.v_trans = engr[1]
    e.zero_coeff = engr[2]
    e.span_coeff = engr[3]
    e.flag = engr[4]
    
    try:
        e.sst = engr[5]
        e.sst_std = engr[6]
        e.ssc = engr[7]
        e.ssc_std = engr[8]
        e.sss = engr[9]
        e.sss_std = engr[10]
        e.u = engr[11]
        e.u_std = engr[12]
        e.v = engr[13]
        e.v_std = engr[14]
        e.raw_compass = engr[15]
        e.raw_vane = engr[16]
        e.raw_windspeed = engr[17]
    except:
        if verbose:
            print("parse_engr>> ENGR line met data parsing error")
    
    return e
    
        