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
        self.location = None
        self.system = None
        self.time = None
        self.gps = None
        self.lat = None
        self.lon = None
        self.firmware = None
        self.mode = None

    def data(self):
        _a = [self.location,
                self.system,
                self.time,
                self.gps,
                self.lat,
                self.lon,
                self.firmware,
                self.mode]
        return _a

class MAPCO2GPS(object):
    def __init__(self):
        self.date = None
        self.time = None
        self.lat = None
        self.ns = None
        self.lon = None
        self.ew = None
        self.flags = None
        

class MAPCO2HeaderLog(object):
    def __init__(self):
        self.events = []

header_log = MAPCO2HeaderLog()

def parse_frame(data, start, end):

    # break the data file into samples
    sample = data[start:end]

    h = parse_header(sample[0])
    
    return h


def parse_header(data):
    
    h = MAPCO2Header()

    # extract header information
    header = data[0].split()
    print(header)
    h.mode = header[0]
    h.time = header[3] + "_" + header[4]
#    unit_unix_time = time.mktime(time.strptime(unit_time, "%Y/%m/%d_%H:%M:%S"))
    h.location = header[5]
    h.system = header[6]
    
    # older versions of the firmware don't include the version number
    try:
        h.firmware = header[7]
    except:
        h.firmware = False
        
    return h

def parse_gps(data):

    # extract location information
    g = data.split()
    _t = g[0] + "_" + g[1]
    
    # if no fix, fill with zero
    if _t in config.time_ignore:
        g.gps = "NaT"
    else:
        try:
            g.gps = time.mktime(time.strptime(_t, "%m/%d/%Y_%H:%M:%S"))
        except:
            header_log.events.append("%s, %s, %s, Unable to parse %s" 
                                     % (g.time, g.location, 
                                        g.system, g))
            print("Error parsing: ", g)

    
def convert_gps(gps):
    # convert NSEW to +/- (but keep in string format)
    signs = {"N": "", "S": "-", "E": "", "W": "-"}
    lat = signs[gps[3]] + gps[2]
    lon = signs[gps[5]] + gps[4]
    return lat, lon
    
    
        