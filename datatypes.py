# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 09:41:25 2016

@author: dietrich
"""

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


class MAPCO2ParseLog(object):
    def __init__(self):
        self.events = []


global_log = MAPCO2ParseLog()
global_key = ''


class MAPCO2Base(object):

    def __init__(self):
        self.data = None
        self.data_names = None
        self.df = None

    def series(self):
        """Single dimension data"""
        return pd.Series(data=self.data(), index=self.data_names)

    def dataframe(self):
        """Multi dimension timeseries data"""
        self.df = pd.DataFrame(data=self.data(), columns=self.data_names)


class MAPCO2Header(MAPCO2Base):

    def __init__(self):
        self.line = None
        self.df = None
        self.mode = None
        self.checksum = None
        self.size = None
        self.date_time = None
        self.location = None
        self.system = None
        self.firmware = None
        self.timestamp = None

        self.date_time_format = "%Y/%m/%d_%H:%M:%S"
        self.firmware_format = "A.B_%m/%d/%Y"

        self.data_names = ["mode",
                           "checksum",
                           "size",
                           "date_time",
                           "location",
                           "system",
                           "firmware",
                           "timestamp"]

    def parse(self, line, verbose=False):
        """Parse one line of MAPCO2 data that contains the header information"""
        if verbose:
            print("MAPCO2Header.parse >>  ", line)

        # extract header information
        header = line.split()

        self.mode = header[0]
        self.checksum = header[1]
        self.size = header[2]
        self.date_time = header[3] + "_" + header[4]
        self.timestamp = pd.Timestamp(header[3] + " " + header[4])
        self.location = header[5]
        self.system = header[6]

        # older versions of the firmware don't include the version number
        try:
            self.firmware = header[7] # + "_" + header[8]
        except:
            self.firmware = '0.0'

    @property
    def data(self):
        _a = [self.mode,
              self.checksum,
              self.size,
              self.date_time,
              self.location,
              self.system,
              self.firmware,
              self.timestamp]
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
        self.timestamp = None

        self.date_time_format = "%m/%d/%Y_%H:%M:%S"

        self.data_names = ["date_time",
                           "lat_deg", "lat_min", "lat_direction",
                           "lon_deg", "lon_min", "lon_direction",
                           "fix_time", "quality",
                           "time_before_check", "time_after_check",
                           "valve_time", "timestamp"]

    def parse(self, line, verbose=False):

        # extract location information
        gps = line.split()
        _date = gps[0]
        
        # convert month/day/year to year/month/day
        _date = _date[6:10] + '/' + _date[:2] + '/' + _date[3:5]
        _t = _date + "_" + gps[1]



        # if no fix, fill with zero
        if _t in config.time_ignore:
            self.date_time = "NaT"
        else:
            try:
                self.date_time = _t
            except:
#                parse_log.events.append("%s, %s, %s, Unable to parse %s"
#                                        % (self.time, self.location,
#                                           self.system, self))
                print("parse_gps>> Error parsing: ", gps)

        lat = gps[2].split(".")

        self.lat_deg = lat[0][:-2]
        self.lat_min = lat[0][-2:] + "." + lat[1]
        self.lat_direction = gps[3]

        lon = gps[4].split(".")

        self.lon_deg = lon[0][:-2]
        self.lon_min = lon[0][-2:] + "." + lon[1]
        self.lon_direction = gps[5]

        self.fix_time = gps[6]
        self.quality = gps[7]
        self.time_before_check = gps[8] + "_" + gps[9]
        self.time_after_check = gps[10] + "_" + gps[11]

        if self.date_time[0:4] == '0000':
            self.date_time = self.time_after_check

        try:
            if len(gps) > 12:
                self.valve_time = gps[13]
        except:
            self.valve_time = []
            if verbose:
                print("parse_gps>> Error in valve current: ", gps)

    @property
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
                self.valve_time,
                self.timestamp]


class MAPCO2Engr(MAPCO2Base):
    def __init__(self, data_type="iridium"):

        self.df = None

        self.data_type = data_type

        self.v_logic = None
        self.v_trans = None
        self.zero_coeff = None
        self.span_coeff = None
        self.span2_coeff = None
        self.flag = None
        self.span_flag = 0
        self.zero_flag = 0

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

        self.timestamp = None

        self.f_span_5 = None
        self.f_span_4 = None
        self.f_span_3 = None
        self.f_span_2 = None
        self.f_span_1 = None
        self.f_zero_5 = None
        self.f_zero_4 = None
        self.f_zero_3 = None
        self.f_zero_2 = None
        self.f_zero_1 = None

        self.data_names = ["v_logic", "v_trans", "zero_coeff", "span_coeff",
                           "flag", "sst", "sst_std", "ssc", "ssc_std",
                           "sss", "sss_std", "u", "u_std", "v", "v_std",
                           "raw_compass", "raw_vane", "raw_windspeed",
                           "timestamp",
                           'f_span_5',
                           'f_span_4',
                           'f_span_3',
                           'f_span_2',
                           'f_span_1',
                           'f_zero_5',
                           'f_zero_4',
                           'f_zero_3',
                           'f_zero_2',
                           'f_zero_1',
                           'span_flag',
                           'zero_flag']

        self.flag_names = ['', '', '',
                           'f_span_5',
                           'f_span_4',
                           'f_span_3',
                           'f_span_2',
                           'f_span_1',
                           '', '', '',
                           'f_zero_5',
                           'f_zero_4',
                           'f_zero_3',
                           'f_zero_2',
                           'f_zero_1']

        self.flag_name_def = ['', '', '',
                              'no span cal coefficient',
                              'no zero cal coefficient',
                              'licor error',
                              'licor nak',
                              'licor timeout',
                              '', '', '',
                              'no span cal coefficient',
                              'no zero cal coefficient',
                              'licor error',
                              'licor nak',
                              'licor timeout']

        self.update_names()

    def update_names(self):
        if self.data_type != "iridium":
            self.data_names = self.data_names[:5] + self.data_names[-12:]

    def decode_flag(self):
        """Convert 4 character flag into 16 item list of binary values
        for all flag states"""
        flag = self.flag
        
        s = flag[0:2]
        z = flag[2:4]

        if s.lower() == 'ff':
            self.span_flag = 1
            flag = '00' + flag[-2:]

        if z.lower() == 'ff':
            self.zero_flag = 1
            flag = flag[:2] + '00'

        fl = [int(n) for n in bin(int(flag, 16))[2:].zfill(16)]

        self.f_span_5 = fl[3]
        self.f_span_4 = fl[4]
        self.f_span_3 = fl[5]
        self.f_span_2 = fl[6]
        self.f_span_1 = fl[7]
        self.f_zero_5 = fl[11]
        self.f_zero_4 = fl[12]
        self.f_zero_3 = fl[13]
        self.f_zero_2 = fl[14]
        self.f_zero_1 = fl[15]

    def parse(self, line, verbose=False):

        if verbose:
            print("parse_engr   >>  ", line)

        engr = line.split()

        self.v_logic = float(engr[0])
        self.v_trans = float(engr[1])
        self.zero_coeff = float(engr[2])
        self.span_coeff = float(engr[3])


        if verbose:
            print('engr:', engr, len(engr))
            
        _x = 0
        # handle 3rd licor coefficient dumbly inserted into middle of line
        if len(engr) == 18:
            # no span flag
            pass
        elif len(engr) == 19:
            # 3rd span coefficient is present
            self.span2_coeff = engr[4]
            _x = 1

        try:
            self.flag = engr[4+_x]  # needs to remain string for flag bit access
            self.sst = float(engr[5+_x])
            self.sst_std = float(engr[6+_x])
            self.ssc = float(engr[7+_x])
            self.ssc_std = float(engr[8+_x])
            self.sss = float(engr[9+_x])
            self.sss_std = float(engr[10+_x])
            self.u = float(engr[11+_x])
            self.u_std = float(engr[12+_x])
            self.v = float(engr[13+_x])
            self.v_std = float(engr[14+_x])
            self.raw_compass = float(engr[15+_x])
            self.raw_vane = float(engr[16+_x])
            self.raw_windspeed = float(engr[17+_x])
        except:
            if verbose:
                print("parse_engr>> ENGR line met data parsing error")

    @property
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
              self.raw_windspeed,
              self.timestamp,
              self.f_span_5,
              self.f_span_4,
              self.f_span_3,
              self.f_span_2,
              self.f_span_1,
              self.f_zero_5,
              self.f_zero_4,
              self.f_zero_3,
              self.f_zero_2,
              self.f_zero_1,
              self.span_flag,
              self.zero_flag]

        if (self.data_type == "flash") or (self.data_type == "terminal"):
            _a = _a[:5] + _a[-12:]
        return _a


class AuxData(object):
    def __init__(self):
        self.raw
        self.h
        self.log
        self.aux_type = ""
        self.number = None
        self.data = pd.DataFrame(data=None)
        self.status = ""

    def extract(self):
        """Extract float data from four char string data, i.e.
        "2345" to 23.45
        Units: O2 = percent, RH = percent, RH Temp = deg C
        """
        self.header()
        self.data = [float(n) / 100.0 for n in " ".join(self.raw[1:]).split(" ")]

    def header(self):
        """Extract header information from aux section,
        sensor data type and number of samples"""
        self.aux_type = ' '.join(self.raw[0].split()[:-2])
        self.number = int(self.raw[0].split()[-1])


class MetData(AuxData):
    """Hold auxilary and meterological data"""

    def extract(self):
        print("MetData.extract>> raw:", self.raw)
        pass

    def convert(self):
        self.data = pd.DataFrame(data=None)


class SBE16Data(AuxData):
    def __init__(self):
        super(AuxData, self).__init__()

    """Hold SBE16 data"""
    def extract(self):
        print("SBE16Data.extract>> raw:", self.raw)
        
    def convert(self):
        self.data = pd.DataFrame(data=None)


class SAMI2Data(AuxData):
    """Hold SAMI2 hex data"""

    def __init__(self):
        super(AuxData, self).__init__()
        self.datetime = None
        self.data = None
        
    def extract(self):
        print("SAMI2.extract>> raw:", self.raw)
        self.datetime = self.raw[1]
        _n = None
        try:
            _n = self.raw.index('^0A')
        except ValueError:
            return
            
#        if _n is not None:
        first = self.raw[:_n]
        second = self.raw[_n+1:]
        print(first)
        print(len(first))
        print(second)
        print(len(second))

        second = ''.join(second)
        
        if len(first) == 3:
            first = first[-1]
            self.data = [first, second]
        else:
            self.data = [second]
        
        print(self.data)
        
        
        
        
    def convert(self):
        self.data = pd.DataFrame(data=None)


class LIData(AuxData):
    def extract(self):
        """Extract string list of """
        self.header()
        self.data = '  '.join(self.raw[1:]).split('  ')

    def convert(self):
        """Convert list of string lines to nested list of strings,
         then to Pandas DataFrame, then convert from str(int (f x 100))
         to float with 2 decimals.
         """
        self.data = [n.split(' ') for n in self.data]
        # print(self.data)

        if self.data[0][0] == '':
            self.data = pd.DataFrame(data=None)
            self.log.append()
        else:
            self.data = pd.DataFrame(self.data,
                                     columns=["co2_ppm", "temp_c",
                                              "press_kpa", "raw1", "raw2"])
            self.data.co2_ppm = self.data.co2_ppm.astype(float) / 100.0
            self.data.temp_c = self.data.temp_c.astype(float) / 100.0
            self.data.press_kpa = self.data.press_kpa.astype(float) / 100.0
            self.data.raw1 = self.data.raw1.astype(int)
            self.data.raw2 = self.data.raw2.astype(int)


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

                           "dfCO2", ]

    @property
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


# def dataframe(self, date_time):
#        self.df = pd.DataFrame(data=self.data(),
#                               index=self.date_time,
#                               columns=self.data_names)


class MAPCO2Data(MAPCO2Base):
    def __init__(self):
        self.df = None

        self.cycle = []
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

    @property
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