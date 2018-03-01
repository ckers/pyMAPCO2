# -*- coding: utf-8 -*-
"""
Configuration values
@author: Colin Dietrich
"""

import os
from pandas import to_datetime


dial_rudics = 'http://eclipse.pmel.noaa.gov/rudics/ALL_RUDICS/PLATFORM_CALL_SUMMARIES/'
local_rudics_dial_data = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\dial\\')

url_mapco2 = 'http://eclipse.pmel.noaa.gov/rudics/pco2/'
url_waveglider = 'http://eclipse.pmel.noaa.gov/rudics/PCWG/'
url_asv = 'http://eclipse.pmel.noaa.gov/rudics/PCAV/'

local_mapco2_data_directory = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\mapco2\\')
local_waveglider_data_directory = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\waveglider\\')
local_asv_data_directory = os.path.normpath('C:\\Users\\dietrich\\data\\rudics\\asv\\')

cm = {'red':            'ff0000',
      'blue':           '0000ff',
      'green':          '00c800',
      'brown':          '8B4513',
      'purple':         'A01FF0',
      'dk blue gray':   '314F4F',
      'Magenta':        'ff00ff',
      'dk green':       '006400',
      'dk yellow':      'FFD700',
      'dk red':         'B22222',
      'black':          '000000'}

# final data .csv column names as published
column_names = ['Mooring', 'Latitude', 'Longitude',
                'Date', 'Time', 'xCO2_SW_wet', 'xCO2_SW_QF',
                'H2O_SW', 'xCO2_Air_wet', 'xCO2_Air_QF', 'H2O_AIR',
                'Licor_Atm_Pressure', 'Licor_Temp', 'Percent_O2',
                'SST', 'SSS', 'xCO2_SW_dry', 'xCO2_Air_dry',
                'fCO2_SW_sat', 'fCO2_Air_sat', 'dfCO2',
                'pCO2_SW_sat', 'pCO2_Air_sat', 'dpCO2', 'pH', 'pH_QF']

column_names_colors = ['black', 'black', 'black',
                       'black', 'black', '314F4F', 'orange',
                       cm['purple'], cm['blue'], 'orange', 'pink',
                       'grey', 'red', 'green',
                       'orange', 'purple', 'blue', 'cyan',
                       'blue', 'cyan', 'grey',
                       'blue', 'cyan', 'grey', 'red', 'orange']
data_colors = dict(zip(column_names, column_names_colors))

lab_test_colors = ['green', 'orange', 'blue', 'cyan',
                   'red', 'magenta', 'grey', 'yellow']

# data not included in published data
data_colors['NTU'] = 'grey'
data_colors['O2'] = 'magenta'
data_colors['TA'] = '#53f442'
data_colors['pH_int'] = '#9ff22b'
data_colors['pH_ext'] = '#2bf2bd'
data_colors['MBL'] = 'black'
data_colors['epon_press'] = '#f442f4'  # purple-ish
data_colors['apon_press'] = '#f47141'  # salmon/orange-ish
data_colors['precipt'] = '#ede21e'  # yellowish
data_colors['general'] = '#7f808c'  # steel blue/grey

data_colors['xCO2_Air_dry_flagged_3'] = 'orange'
data_colors['xCO2_Air_dry_flagged_4'] = 'red'
data_colors['xCO2_SW_dry_flagged_3'] = 'orange'
data_colors['xCO2_SW_dry_flagged_4'] = 'red'
data_colors['pH_flagged_3'] = 'orange'
data_colors['pH_flagged_4'] = 'red'

column_names_original = ['Mooring Name', 'Latitude', 'Longitude', 'Date', 'Time',
                         'xCO2 SW (wet) (umol/mol)', 'CO2 SW QF', 'H2O SW (mmol/mol)',
                         'xCO2 Air (wet) (umol/mol)', 'CO2 Air QF', 'H2O Air (mmol/mol)',
                         'Licor Atm Pressure (hPa)', 'Licor Temp (C)', 'MAPCO2 %O2', 'SST (C)',
                         'Salinity', 'xCO2 SW (dry) (umol/mol)', 'xCO2 Air (dry) (umol/mol)',
                         'fCO2 SW (sat) uatm', 'fCO2 Air (sat) uatm', 'dfCO2',
                         'pCO2 SW (sat) uatm', 'pCO2 Air (sat) uatm', 'dpCO2',
                         'pH (total scale)', 'pH QF']

column_mapper = dict(zip(column_names_original, column_names))
column_mapper['dp_n'] = 'dp_n'

# merged data in .xlsx workbooks, before being output to .csv
xlsx_merged_header = column_names[3:-2]  # just pCO2 data
xlsx_merged_header_ph = column_names[3:]  # pCo2 and pH data

# year range for generated time deltas and multiyear plots
y0 = 2000
y1 = 2020

# Time formatting specifications
iso_strftime_utc = '%Y-%m-%dT%H:%M:%SZ'  # assumes time is UTC/Z
iso_strftime_timezone = '%Y-%m-%dT%H:%M:%S%Z'  # returns timezone or blank if naive
header_datetime_format = '%Y/%m/%d_%H:%M:%S'
header_firmware_datetime_format = 'A.B_%m/%d/%Y'
gps_datetime_format = '%Y/%m/%d_%H:%M:%S'  # converted from '%m/%d/%Y_%H:%M:%S' in datatypes.py

# repeat flag inserted where '000000' etc is found in data
repeat_flag = '<repeat flag>'

# ranges of data considered possible/reality
k_limits = {'datetime64_ns': [to_datetime('1980-01-01'), to_datetime('2020-01-01')],
            'xco2_sw': [300, 1200],
            'xco2_air': [380, 500],
            'xco2': [0, 20000],
            'o2_percent': [85, 100],
            'sso2': [85, 100],
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

# the set of all 999 fill values observed from the MAPCO2 firmware
nan_9s = ['99.999', '99.9999', '99.999999', '9999.999', '9999.99999', '99999.']

# more -9x nan fill from NDBC data
nan_9s.append(-9.999)
nan_9s.append(-99.9)

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

pco2_start_delimiters = ('NORM', 'FAST', 'DEPL', 'POSO', 'STSF')  #, 'RECV')
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

# This works with iridium data... imagine a place where there was ONE data spec...
sbe16_columns_short = ['sst', 'sst_std',
                       'ssc', 'ssc_std',
                       'press', 'press_std',
                       'v0', 'v0_std', 'v1', 'v1_std', 'v2', 'v2_std',
                       'v3', 'v3_std', 'v4', 'v4_std', 'v5', 'v5_std',
                       'gtd_temp', 'gtd_temp_std', 'gtd_press', 'gtd_press_std',
                       'temp1_serial', 'temp1_serial_std',
                       'press1_serial', 'press1_serial_std',
                       'o2_serial', 'o2_serial_std',
                       'a', 'b', 'c', 'd', 'e', 'f',
                       'sbe63_phase', 'sbe63_phase_std', 'sbe63_temp', 'sbe63_temp_std',
                       'salinity', 'salinity_std',
                       'soundv', 'soundv_std',
                       'density', 'density_std',
                       'battery_v', 'current_i']

# different length data need different headers.  keys == list length/columns
# V0 is start value of voltage channels!
# TODO: fix
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

co2sys_column_names_in = ['datetime64_ns',
                          'SSS',
                          'SST',
                          'p_dbar_in',
                          'total_P',
                          'total_Si',
                          'SST_out',
                          'p_dbar_out',
                          'TA',
                          'tco2',
                          'pH',
                          'fco2',
                          'pCO2_SW_sat']

co2sys_column_units_in = ['datetime64_ns',
                          '',
                          'C',
                          'dbars',
                          'mmol/kgSW',
                          'mmol/kgSW',
                          'C',
                          'dbars',
                          'mmol/kgSW',
                          'mmol/kgSW',
                          '',
                          'matm',
                          'matm']

co2sysxls_column_names = co2sys_column_names_in[1:] + ['clear_data',
                                                       'none_1',
                                                       'none_2',
                                                       'none_3',
                                                       'SSS_in',
                                                       'SST_in',
                                                       'p_dbar_in',
                                                       'total_P_in',
                                                       'total_Si_in',
                                                       'TA_in',
                                                       'tco2_in',
                                                       'pH_in',
                                                       'fco2_in',
                                                       'pco2_SW_sat_in',
                                                       'HCO3_in',
                                                       'CO3_in',
                                                       'CO2_in',
                                                       'B_Alk_in',
                                                       'OH_in',
                                                       'P_Alk_in',
                                                       'Si_Alk_in',
                                                       'Revelle_in',
                                                       'WCa_in',
                                                       'WAr_in',
                                                       'xCO2_dry_in',
                                                       'none_4',
                                                       'SST_out',
                                                       'p_dbar_out',
                                                       'ph_out',
                                                       'fco2_out',
                                                       'pco2_out',
                                                       'HCO3_out',
                                                       'CO3_out',
                                                       'CO2_out',
                                                       'B_Alk_out',
                                                       'OH_out',
                                                       'P_Alk_out',
                                                       'Si_Alk_out',
                                                       'Revelle_out',
                                                       'WCa_out',
                                                       'WAr_out',
                                                       'xCO2_dry_out',
                                                       'none_5',
                                                       'subflag']

co2sysxls_column_units = co2sys_column_units_in[1:] + ['',
                                                       '',
                                                       '',
                                                       '',
                                                       'C',
                                                       'dbars',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       '',
                                                       'matm',
                                                       'matm',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'Revelle',
                                                       'WCa',
                                                       'WAr',
                                                       'ppm',
                                                       '',
                                                       'C',
                                                       'dbars',
                                                       '',
                                                       'matm',
                                                       'matm',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'mmol/kgSW',
                                                       'Revelle',
                                                       'WCa',
                                                       'WAr',
                                                       'ppm',
                                                       '',
                                                       '']

xlsx_cycle_headers = ['mode',
                      'cycle',
                      'Time',
                      'Temp oC',
                      'T Std Dev',
                      'Licor Pressure',
                      'Licor Pressure (atm)',
                      'P Std Dev',
                      'xCO2',
                      'xCO2 Std Dev',
                      'pCO2 umol/mol atm',
                      '%O2',
                      'Std Dev %O2',
                      'Rel Humidity',
                      'Std Dev Rel Humidity',
                      'RH Temp',
                      'Std Dev RH Temp',
                      'Raw1',
                      'StdDev Raw1',
                      'Raw2',
                      'StdDev Raw2',
                      'Licor Zero Coeff',
                      'Licor Span Coeff',
                      'Calculated xCO2 from Averaged Data',
                      'none_Y',
                      'xCO2 (Dry)',
                      'none_AA',
                      'SST',
                      'none_AC',
                      'Cond',
                      'none_AE',
                      'SSS',
                      'none_AG',
                      'Calc_Sal_average',
                      'SSS_from_ave',
                      'none_AJ',
                      'none_AK',
                      'none_AL',
                      'none_AM',
                      'none_AN',
                      'none_AO',
                      'none_AP',
                      'none_AQ',
                      'SBE16 SST',
                      'SBE16 SST SD',
                      'SBE16 Cond',
                      'SBE16 Cond SD',
                      'SBE16 Press',
                      'SBE16 Press SD',
                      'SBE16 V0',
                      'SBE16 V0 SD',
                      'SBE16 V1',
                      'SBE16 V1 SD',
                      'SBE16 V2',
                      'SBE16 V2 SD',
                      'SBE16 V3',
                      'SBE16 V3 SD',
                      'SBE16 V4',
                      'SBE16 V4 SD',
                      'SBE16 V5',
                      'SBE16 V5 SD',
                      'SBE16 Serial Channel Temp',
                      'SBE16 Serial Channel Temp SD',
                      'SBE16 Serial Channel Press',
                      'SBE16 Serial Channel Press SD',
                      'SBE16 Serial Channel Temp2',
                      'SBE16 Serial Channel Temp2 SD',
                      'SBE16 Serial Channel Press2',
                      'SBE16 Serial Channel Press2 SD',
                      'SBE16 Serial Channel O2',
                      'SBE16 Serial Channel O2 SD',
                      'SBE16 SSS',
                      'SBE16 SSS SD',
                      'SBE16 SV',
                      'SBE16 SV SD',
                      'SBE16 density',
                      'SBE16 density SD',
                      'SBE16 batt voltage',
                      'SBE16 i current drain',
                      '# of SBE16 samples',
                      'none_CC',
                      'none_CD',
                      'none_CE',
                      'serial_SBE38_ave',
                      'serial_SBE38_std',
                      'serial_SBE50_ave',
                      'serial_SBE50_std',
                      'serial_GTD_ave',
                      'serial_GTD_std',
                      'serial_dual_GTD_ave',
                      'serial_dual_GTD_std',
                      'Voltage_samples_std',
                      'Current_samples_std',
                      'none_CP',
                      'Calc_Sal_average',
                      'SSS_from_ave',
                      'none_CS',
                      'V0 - Chl (ug/l)',
                      'V1 - NTU',
                      'V2 - O2',
                      'V3 - O2 Temp (C)']

# cycle names for xlsx worksheets created using VBA
cycle_names = {'Zero Pump On': 'zpon', 'Zero Pump Off': 'zpof', 'Zero Post Cal': 'zpcal',
               'Span Pump On': 'zpon', 'Span Pump Off': 'spof', 'Span Post Cal': 'spcal',
               'Equil Pump On': 'epon', 'Equil Pump Off': 'epof',
               'Air Pump On': 'apon', 'Air Pump Off': 'apof'}

sbe16_columns = ['datetime_v',
                 'SBE16_SST', 'SBE16_SST_SD',
                 'SBE16_Cond', 'SBE16_Cond_SD',
                 'SBE16_Press', 'SBE16_Press_SD',
                 'SBE16_V0', 'SBE16_V0_SD',
                 'SBE16_V1', 'SBE16_V1_SD',
                 'SBE16_V2', 'SBE16_V2_SD',
                 'SBE16_V3', 'SBE16_V3_SD',
                 'SBE16_V4', 'SBE16_V4_SD',
                 'SBE16_V5', 'SBE16_V5_SD',
                 'SBE16_Serial_Temp', 'SBE16_Serial_Temp_SD',
                 'SBE16_Serial_Press', 'SBE16_Serial_Press_SD',
                 'SBE16_Serial_Temp2', 'SBE16_Serial_Temp2_SD',
                 'SBE16_Serial_Press2', 'SBE16_Serial_Press2_SD',
                 'SBE16_Serial_O2', 'SBE16_Serial_O2_SD',
                 'SBE16_SSS', 'SBE16_SSS_SD',
                 'SBE16_SV', 'SBE16_SV_SD',
                 'SBE16_density', 'SBE16_density_SD',
                 'SBE16_V_bat', 'SBE16_A_current',
                 'SBE16_n_samples']

# sheet names of MS Excel VBA sourced workbooks
xls_sheet_names = ['Zero Pump On', 'Zero Pump Off', 'Zero Post Cal',
                   'Span Pump On', 'Span Pump Off', 'Span Post Cal',
                   'Equil Pump On', 'Equil Pump Off',
                   'Air Pump On', 'Air Pump Off']

xls_merged_sheet = 'Merged'

# Data type header IDs in Flash Data
frame_data_types = ['mapco2', 'ph_sami', 'ph_seafet', 'sbe16', 'met']

# Number of lines to save if no end of frame line is found
frame_default_number_of_list_lines = 30
