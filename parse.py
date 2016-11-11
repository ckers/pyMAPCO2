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
            self.firmware = header[7] + "_" + header[8]
        except:
            self.firmware = False

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
        _t = gps[0] + "_" + gps[1]

        # if no fix, fill with zero
        if _t in config.time_ignore:
            self.date_time = "NaT"
        else:
            try:
                self.date_time = _t
            except:
                parse_log.events.append("%s, %s, %s, Unable to parse %s"
                                        % (self.time, self.location,
                                           self.system, self))
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
                           "span_flag", "zero_flag", "timestamp",
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

        # handle 3rd licor coefficient dumbly inserted into middle of line
        if len(engr) == 5:
            self.flag = engr[4]  # needs to remain string for flag bit access
        else:
            self.span2_coeff = engr[4]
            self.flag = engr[5]

        try:
            self.sst = float(engr[5])
            self.sst_std = float(engr[6])
            self.ssc = float(engr[7])
            self.ssc_std = float(engr[8])
            self.sss = float(engr[9])
            self.sss_std = float(engr[10])
            self.u = float(engr[11])
            self.u_std = float(engr[12])
            self.v = float(engr[13])
            self.v_std = float(engr[14])
            self.raw_compass = float(engr[15])
            self.raw_vane = float(engr[16])
            self.raw_windspeed = float(engr[17])
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
              self.span_flag,
              self.zero_flag,
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
    def __init__(self, raw_data, header, log):
        self.raw = raw_data
        self.h = header
        self.log = log
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
    """Hold SBE16 data"""
    def extract(self):
        print("SBE16Data.extract>> raw:", self.raw)
        
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

# ================================================================


def chooser(data, start, end, verbose=False, data_type="iridium"):
    if (data_type == "iridium") or (data_type == "terminal"):
        (h, g, e,
         zpon, zpof, zpcl,
         spon, spof, spcl,
         epon, epof,
         apon, apof) = parse_iridium(data=data,
                                     start=start, end=end,
                                     verbose=verbose,
                                     data_type=data_type)

    # df, df, df, dict of dfs
    if data_type == "flash":
        h, g, e, co2, aux, sbe16 = flash(data=data, start=start, end=end, verbose=verbose)
        return h, g, e, co2, aux, sbe16


def flash(data, start, end, verbose=False):
    """Parse a list of lines from a flash MAPCO2 data file which contains
    frames of data
        cycle measurements within the frame
            sections/samples of different data within the cycle
        auxiliary data

    Parameters
    ----------
    data : list,
    start : list,
    end : list,
    verbose : bool
    """

    global global_key
    global global_log

    # start = start[0]
    # end = end[0]

    # break the data file into samples
    frame = data[start[0]:end[0]]

    # first frame of data to initialize DataFrames and Panel
    h_0, g_0, e_0, co2_0, aux_0, sbe16_0 = flash_compile(sample=frame, verbose=verbose)

    print('h>>', g_0.date_time, h_0.system, h_0.date_time)
    print('h>>', h_0.data)

    if g_0.date_time == 'NaT':
        dt = h_0.date_time
    else:
        dt = g_0.date_time

    common_key = dt + '_' + h_0.system
    print('h common_key>>', common_key)

    # for error logging
    global_key = common_key

    h = pd.DataFrame(data=[h_0.data], columns=h_0.data_names)
    g = pd.DataFrame(data=[g_0.data], columns=g_0.data_names)
    e = pd.DataFrame(data=[e_0.data], columns=e_0.data_names)
    h['common_key'] = common_key
    g['common_key'] = common_key
    e['common_key'] = common_key

    print(h.head())
    print(g.head())
    print(e.head())

    # co2 = pd.Panel({common_key: co2_0})

    co2 = co2_0
    co2['common_key'] = common_key

    # aux = pd.DataFrame(data=[aux.data], columns=aux.data_names)
    aux = [aux_0]
    sbe16 = [sbe16_0]

    for n in range(1, len(start)):
        # break the data file into samples
        frame = data[start[n]:end[n]]
        h_n, g_n, e_n, co2_n_df, aux_n, sbe16_n = flash_compile(sample=frame, verbose=verbose)
        # print('co2_n df>>', co2_n.head())
        print('h>>', g_n.date_time, h_n.system, h_n.date_time)
        # print('h>>', h_n.data)

        if g_n.date_time == 'NaT':
            dt = h_n.date_time
        else:
            dt = g_n.date_time

        common_key = dt + '_' + h_n.system
        print('h common_key>>', common_key)

        # for error logging
        global_key = common_key

        try:
            h_n_df = pd.DataFrame(data=[h_n.data], columns=h_n.data_names)
            g_n_df = pd.DataFrame(data=[g_n.data], columns=g_n.data_names)
            e_n_df = pd.DataFrame(data=[e_n.data], columns=e_n.data_names)
            h_n_df['common_key'] = common_key
            g_n_df['common_key'] = common_key
            e_n_df['common_key'] = common_key

            h = pd.concat([h, h_n_df])
            g = pd.concat([g, g_n_df])
            e = pd.concat([e, e_n_df])
        except:
            global_log.events.append('Error parsing aux data at:', common_key)
            print('Error parsing aux data at:', common_key)
        try:
            # co2[common_key] = co2_n
            co2_n_df['common_key'] = common_key
            co2 = pd.concat([co2, co2_n_df])
        except ValueError:
            # print('parse.flash>> co2', co2.ix[-1])
            global_log.events.append('Error parsing co2 data at:', common_key)
            print('Error parsing co2 data at:', common_key)
        aux.append(aux_n)
        sbe16.append(sbe16_n)

    return h, g, e, co2, aux, sbe16


def flash_compile(sample, verbose=False):
    h = sample[0]
    g = sample[1]
    e = sample[2]

    if verbose:
        print("frame header>>", h)
        print("frame gps>>", g)
        print("frame engineering>>", e)

    h = parse_header(h, verbose=verbose)
    g = parse_gps(g, verbose=verbose)
    g.timestamp = h.timestamp
    e = parse_engr(e, verbose=verbose, data_type='flash')
    e.decode_flag()
    e.timestamp = h.timestamp

    if verbose:
        print("frame header>>", h.data)
        print("frame gps>>", g.data)
        print("frame engineering>>", e.data)

    print("parse.parse_flash>>ID INFO:", h.date_time + '_' + h.system)

    co2, aux, sbe16 = flash_co2_aux(sample, header=h, verbose=verbose)
    co2["timestamp"] = h.timestamp

    return h, g, e, co2, aux, sbe16


def parse_iridium(data, start, end, verbose=False, data_type="iridium"):
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


def flash_cycle_id(line):
    """Identify what sort of data is in a flash data cycle header
    row that starts with '*****...'
    Parameters
    ----------
    line : str, delimiter line of flash data
    """
    line = line.split(' ')

    if line[1] in ['Met', 'SBE16']:
        return 0, line[1]
    minute = int(line[-1])
    cycle = line[1] + '_' + line[-2]

    names = {'Zero_on': 'zpon',
             'Zero_off': 'zpof',
             'Zero_cal': 'zcal',
             'Span_on': 'spon',
             'Span_off': 'spof',
             'Span_cal': 'scal',
             'Equil_on': 'epon',
             'Equil_off': 'epof',
             'Air_on': 'apon',
             'Air_off': 'apof'}

    cycle = names[cycle]

    return minute, cycle


def flash_index_frame(data, verbose=False):
    """Find delimiters between cycles
    Parameters
    ----------
    sample : list, str of each line from flash file in this frame
    verbose : bool
    Returns
    -------
    list, index numbers of headers for each data frame
    """

    indexes = []
    minutes = []
    cycles = []

    for n in range(0, len(data)):
        if verbose:
            print(n)
        if data[n][0:5] == "*****":
            m, c = flash_cycle_id(data[n])
            indexes.append(n)
            minutes.append(m)
            cycles.append(c)
    return indexes, minutes, cycles


def flash_co2_aux(sample, header, verbose=False):
    """Parse a complete frame of MAPCO2 cyles and auxiliary data for one
    location/datetime

    Parameters
    ----------
    sample : list, lines of data
    header : object, header data class of data for sample
    verbose : bool

    Returns
    -------
    co2_container.data : pd.DataFrame, all licor, o2 and rh data
    met_container.data : pd.DataFrame, all aux sensor data, sbe16 etc
    """

    i, m, c = flash_index_frame(sample, verbose=False)
    i_end = i[1:] + [len(sample)]

    if verbose:
        print("frame delimiters, i>>", i)
        print("frame min,  m>>", m)
        print("frame cycles, c>>", c)
        print("frame info lengths>> ", len(i), len(m), len(c))

    # def co2_cycle(data, cycle_name):
    #     container = flash_single_cycle(data)
    #     container.data["cycle"] = cycle_name
    #     return container

    cycle_0 = sample[i[0]:i_end[0]]
    # co2_container_0 = co2_cycle(data=cycle_0, cycle_name=c[0])
    co2_container_0 = flash_single_cycle(cycle_0)

    co2_container_0.data["cycle"] = c[0]

    co2_df = co2_container_0.data

    for n in range(1, len(c)):

        cycle = sample[i[n]:i_end[n]]

#        if c[n].lower() in ['met', 'sbe16']:
        if c[n].lower() == 'met':
            met_container = flash_single_met(cycle, header=header,
                                             verbose=verbose)
        elif c[n].lower() == 'sbe16':
            sbe16_container = flash_single_sbe16(cycle, header=header,
                                                 verbose=verbose)
        else:
            # co2_df_n = co2_cycle(data=cycle, cycle_name=c[n])
            co2_df_n = flash_single_cycle(cycle)
            if co2_df_n is None:
                continue
            co2_df_n.data["cycle"] = c[n]
            co2_df = pd.concat([co2_df, co2_df_n.data])

    co2_df['n'] = co2_df.index
    met_df = met_container.data
    sbe16_df = sbe16_container.data

    return co2_df, met_df, sbe16_df


def flash_single_met(data, header, verbose=False):
    """Parse met data from the flash frame"""
    if verbose:
        pass
    md = MetData(data, header=header, log=global_log)
    
    md.extract()
    md.convert()
    return md


def flash_single_sbe16(data, header, verbose=False):
    """Parse met data from the flash frame"""
    if verbose:
        pass
    sbe16 = SBE16Data(data, header=header, log=global_log)
    
    sbe16.extract()
    sbe16.convert()
    return sbe16


def flash_find_sections(cycle, verbose=False):
    """Find index and name of a section within one cycle of a frame of data
    Parameters
    ----------
    cycle : list, lines of data for one data frame, i.e. spon, spoff, spcal, etc.
    verbose : bool
    """
    indexes = []
    names = []
    for n in range(0, len(cycle)):
        if verbose:
            print(n, cycle[n][0:2])
        if cycle[n][0:2] in ("Li", "O2", "RH", "Rh", "Met", "SBE16"):
            indexes.append(n)
            names.append(cycle[n])
    indexes.append(len(cycle))
    return indexes, names


def flash_single_cycle(cycle, verbose=False):
    """Find specific types of data within one cycle of data
    Parameters
    ----------
    cycle :
    verbose : bool

    """
    global parse_log

    indexes, names = flash_find_sections(cycle, verbose=False)

    if verbose:
        print("indexes>> ", indexes)

    indexes_end = indexes[1:]
    indexes = indexes[:-1]

    if len(indexes_end) == 0:
            return None

    if verbose:
        print("indexes (new)>> ", indexes)
        print("indexes_end>>", indexes_end)
        print("cycle[0:2]>>", cycle[0:2])

    cycle_li = cycle[indexes[0]:indexes_end[0]]
    cycle_o2 = cycle[indexes[1]:indexes_end[1]]
    cycle_rh = cycle[indexes[2]:indexes_end[2]]
    cycle_rht = cycle[indexes[3]:indexes_end[3]]

    cycle_out = LIData(raw_data=cycle_li, header=None, log=global_log)
    cycle_out.header()
    if cycle_out.number > 1:
        # return pd.DataFrame(data=None)
        cycle_out.extract()
        cycle_out.convert()

    o2 = AuxData(raw_data=cycle_o2, header=None, log=global_log)
    o2.header()
    if o2.number > 1 & len(cycle_out.data) > 0:
        o2.extract()
        cycle_out.data["O2_percent"] = o2.data

    rh = AuxData(raw_data=cycle_rh, header=None, log=global_log)
    rh.header()
    if rh.number > 1 & len(cycle_out.data) > 0:
        rh.extract()
        cycle_out.data["RH_percent"] = rh.data

    rht = AuxData(raw_data=cycle_rht, header=None, log=global_log)
    rht.header()
    if rht.number > 1 & len(cycle_out.data) > 0:
        rht.extract()
        cycle_out.data["RH_temp_c"] = rht.data

    return cycle_out


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


def parse_header(line, verbose=False):
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
        print("parse_header >>  ", line)

    h = MAPCO2Header()
    h.parse(line=line)

    return h


def parse_gps(line, verbose=False):
    """Parse the gps header line of the mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    Returns
    -------
    g : class, instance of data class MAPCO2GPS with data set

    """
    g = MAPCO2GPS()
    g.parse(line=line, verbose=verbose)

    return g


def parse_engr(line, verbose=False, data_type="iridium"):
    """Parse the engineering header line of a mapco2 data frame
    Parameters
    ----------
    line : str, line of space delimited values
    verbose : bool, output print information
    data_type : str, 'iridium', 'flash' or 'terminal'
    Returns
    -------
    e : class, instance of data class MAPCO2Engr with data set
    """

    e = MAPCO2Engr(data_type=data_type)
    e.parse(line=line, verbose=verbose)
    e.update_names()
    e.decode_flag()

    return e


def parse_co2_line(line, verbose=False):
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

    c = MAPCO2Data()

    co2 = line.split()

    #    co2 = [float(n) for n in co2]
    # print(co2)
    co2 = float_converter(co2)
    # print(co2)

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
    """Convert line of co2 data into a pandas series
    Parameters
    ----------
    data : str, one line of licor data
    verbose : bool, output print information
    Returns
    -------
    c_series : Series, pandas series object
    """
    c = parse_co2_line(data=data, verbose=verbose)
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
        parse_log.events.append("parse.float_validator>> error converting to float: "
                                + current_frame)
        line.append(y)
    return line
