# -*- coding: utf-8 -*-
"""
Configuration values
@author: Colin Dietrich
"""

import os
from pandas import to_datetime

mapco2_rudics = 'http://eclipse.pmel.noaa.gov/rudics/pco2/'
waveglider_rudics = 'http://eclipse.pmel.noaa.gov/rudics/PCWG/'
dial_rudics = 'http://eclipse.pmel.noaa.gov/rudics/ALL_RUDICS/PLATFORM_CALL_SUMMARIES/'

local_mapco2_data_directory = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\mapco2\\')
local_waveglider_data_directory = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\waveglider\\')
local_rudics_dial_data = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\dial\\')

# final data .csv column names as published
column_names = ['Mooring', 'Latitude', 'Longitude',
                'Date', 'Time', 'xCO2_SW_wet', 'xCO2_SW_QF',
                'H2O_SW', 'xCO2_Air_wet', 'xCO2_Air_QF', 'H2O_AIR',
                'Licor_Atm_Pressure', 'Licor_Temp', 'Percent_O2',
                'SST', 'SSS', 'xCO2_SW_dry', 'xCO2_Air_dry',
                'fCO2_SW_sat', 'fCO2_Air_sat', 'dfCO2',
                'pCO2_SW_sat', 'pCO2_Air_sat', 'dpCO2', 'pH', 'pH_QF']

# year range for generated time deltas and multiyear plots
y0 = 2000
y1 = 2020

# ranges of data considered possible/reality
k_limits = {'datetime64_ns': [to_datetime('1980-01-01'), to_datetime('2020-01-01')],
            'xco2_sw': [300, 1200],
            'xco2_air': [380, 500],
            'xco2': [0, 20000],
            'o2_percent': [85, 100],
            'sst': [-5, 40],
            'sss': [30, 40],
            'atm_press': [45, 130],
            'ph': [6, 9]}

# Iridium Data Format
cycles = ['zero_pump_on', 'zero_pump_off', 'zero_post_cal', 'span_pump_on',
          'span_pump_off', 'span_post_cal', 'equil_pump_on', 'equil_pump_off',
          'air_pump_on', 'air_pump_off']

# times to ignore, these are default fillers
time_ignore = ('0000/00/00 00:00:00', '00/00/0000_00:00:00')

engr_header = {27: ['location_code', 'system_code',
                    'unit_time', 'unit_unix_time',
                    'gps_time', 'lat', 'lon', 'firmware', 'mode',
                    'logic_batt', 'trans_batt', 'zero_coeff', 'span_coeff', 'flag',
                    'SST', 'SST_std',
                    'conductivity', 'conductivity_st',
                    'salinity', 'salinity_std',
                    'EW_vector', 'EW_vector_std', 'NS_vector', 'NS_vector_std',
                    'compass', 'vane', 'windspeed'],
               28: ['location_code', 'system_code',
                    'unit_time', 'unit_unix_time',
                    'gps_time', 'lat', 'lon', 'firmware', 'mode',
                    'logic_batt', 'trans_batt',
                    'zero_coeff', 'span_coeff', 'one_coeff',
                    'flag', 'SST', 'SST_std',
                    'conductivity', 'conductivity_st',
                    'salinity', 'salinity_std',
                    'EW_vector', 'EW_vector_std', 'NS_vector', 'NS_vector_std',
                    'compass', 'vane', 'windspeed']}

pco2_start_delimiters = ('NORM', 'FAST', 'DEPL', 'POSO', 'RECV', 'STSF')
pco2_end_delimiters = ('SW_xCO2', 'Ocean co2')

pco2_header = ('location_code', 'system_code',
               'unit_time', 'unit_unix_time',
               'gps_time', 'lat', 'lon', 'firmware', 'mode',
               'cycle',
               'licor_temp', 'licor_temp_std',
               'licor_pres', 'licor_pres_std',
               'pco2', 'pco2_std',
               'o2_percent', 'o2_std',
               'rh', 'rh_std', 'rh_temp', 'rh_temp_std',
               'raw1', 'raw1_std', 'raw2', 'raw2_std')

pco2_summary_header = ('location_code', 'system_code',
                       'unit_time', 'unit_unix_time', 'gps_time',
                       'lat', 'lon', 'firmware', 'mode',
                       'sw_xco2', 'atm_xco2')

samiph_header = ('location_code', 'system_code',
                 'unit_time', 'unit_unix_time', 'gps_time',
                 'lat', 'lon', 'firmware', 'mode', 'hex1', 'hex2')

# different length data need different headers.  keys == list length/columns
sbe16_header = {43: ['location_code', 'system_code',  # deployment did not startnow
                     'unit_time', 'unit_unix_time', 'gps_time',
                     'lat', 'lon', 'firmware', 'mode',
                     'temp', 'temp_std',
                     'cond', 'cond_std',
                     'press', 'press_std',
                     'v1', 'v1_std', 'v2', 'v2_std', 'v3', 'v3_std',
                     'v4', 'v4_std', 'v5', 'v5_std', 'v6', 'v6_std',
                     'temp1_serial', 'temp1_serial_std',
                     'press1_serial', 'press1_serial_std',
                     'temp2_serial', 'temp2_serial_std',
                     'press2_serial', 'press2_serial_std',
                     'o2_serial', 'o2_serial_std',
                     'salinity', 'salinity_std',
                     'soundv', 'soundv_std',
                     'density', 'density_std'],
                45: ['location_code', 'system_code',
                     'unit_time', 'unit_unix_time', 'gps_time',
                     'lat', 'lon', 'firmware', 'mode',
                     'temp', 'temp_std',
                     'cond', 'cond_std',
                     'press', 'press_std',
                     'v1', 'v1_std', 'v2', 'v2_std', 'v3', 'v3_std',
                     'v4', 'v4_std', 'v5', 'v5_std', 'v6', 'v6_std',
                     'temp1_serial', 'temp1_serial_std',
                     'press1_serial', 'press1_serial_std',
                     'temp2_serial', 'temp2_serial_std',
                     'press2_serial', 'press2_serial_std',
                     'o2_serial', 'o2_serial_std',
                     'salinity', 'salinity_std',
                     'soundv', 'soundv_std',
                     'density', 'density_std',
                     'battery_voltage', 'current'],
                53: ['location_code', 'system_code',  # deployment did not startnow
                     'unit_time', 'unit_unix_time', 'gps_time',
                     'lat', 'lon', 'firmware', 'mode',
                     'temp', 'temp_std',
                     'cond', 'cond_std',
                     'press', 'press_std',
                     'v1', 'v1_std', 'v2', 'v2_std', 'v3', 'v3_std',
                     'v4', 'v4_std', 'v5', 'v5_std', 'v6', 'v6_std',
                     'temp1_serial', 'temp1_serial_std',
                     'press1_serial', 'press1_serial_std',
                     'temp2_serial', 'temp2_serial_std',
                     'press2_serial', 'press2_serial_std',
                     'o2_serial', 'o2_serial_std',
                     'v7', 'v8', 'v9', 'v10', 'v11',
                     'v12', 'v13', 'v14', 'v15', 'v16',
                     'salinity', 'salinity_std',
                     'soundv', 'soundv_std',
                     'density', 'density_std'],
                55: ['location_code', 'system_code',
                     'unit_time', 'unit_unix_time', 'gps_time',
                     'lat', 'lon', 'firmware', 'mode',
                     'temp', 'temp_std',
                     'cond', 'cond_std',
                     'press', 'press_std',
                     'v1', 'v1_std', 'v2', 'v2_std', 'v3', 'v3_std',
                     'v4', 'v4_std', 'v5', 'v5_std', 'v6', 'v6_std',
                     'temp1_serial', 'temp1_serial_std',
                     'press1_serial', 'press1_serial_std',
                     'temp2_serial', 'temp2_serial_std',
                     'press2_serial', 'press2_serial_std',
                     'o2_serial', 'o2_serial_std',
                     'v7', 'v8', 'v9', 'v10', 'v11',
                     'v12', 'v13', 'v14', 'v15', 'v16',
                     'salinity', 'salinity_std',
                     'soundv', 'soundv_std',
                     'density', 'density_std',
                     'battery_voltage', 'current']}

mpl_obvious_markers = ['o',  # circle marker
                       'v',  # triangle_down marker
                       '^',  # triangle_up marker
                       '<',  # triangle_left marker
                       '>',  # triangle_right marker
                       's',  # square marker
                       'p',  # pentagon marker
                       '*',  # star marker
                       'h',  # hexagon1 marker
                       'H',  # hexagon2 marker
                       'D',  # diamond marker
                       'd']  # thin_diamond marker
