# -*- coding: utf-8 -*-
"""
Configuration values
@author: Colin Dietrich
"""

import os

mapco2_rudics = "http://eclipse.pmel.noaa.gov/rudics/pco2/"
waveglider_rudics = "http://eclipse.pmel.noaa.gov/rudics/PCWG/"
dial_rudics = "http://eclipse.pmel.noaa.gov/rudics/ALL_RUDICS/PLATFORM_CALL_SUMMARIES/"

local_mapco2_data_directory = os.path.normpath("C:\\Users\\dietrich\\data\\rudics\\mapco2\\")
local_waveglider_data_directory = os.path.normpath("C:\\Users\\dietrich\\data\\rudics\\waveglider\\")
local_rudics_dial_data = os.path.normpath("C:\\Users\\dietrich\\data\\rudics\\dial\\")

# Iridium Data Format
cycles = ["zero_pump_on", "zero_pump_off", "zero_post_cal", "span_pump_on",
          "span_pump_off", "span_post_cal", "equil_pump_on", "equil_pump_off",
          "air_pump_on", "air_pump_off"]

# times to ignore, these are default fillers
time_ignore = ('0000/00/00 00:00:00', '00/00/0000_00:00:00')

engr_header = {27:["location_code", "system_code",
                "unit_time","unit_unix_time",
                "gps_time","lat","lon","firmware","mode",
                "logic_batt","trans_batt","zero_coeff","span_coeff","flag",
                "SST","SST_std",
                "conductivity","conductivity_st",
                "salinity","salinity_std",
                "EW_vector","EW_vector_std","NS_vector","NS_vector_std",
                "compass","vane","windspeed"],
                28:["location_code", "system_code",
                "unit_time","unit_unix_time",
                "gps_time","lat","lon","firmware","mode",
                "logic_batt","trans_batt",
                "zero_coeff","span_coeff","one_coeff",
                "flag","SST","SST_std",
                "conductivity","conductivity_st",
                "salinity","salinity_std",
                "EW_vector","EW_vector_std","NS_vector","NS_vector_std",
                "compass","vane","windspeed"]}

pco2_start_delimiters = ("NORM", "FAST", "DEPL", "POSO", "RECV", "STSF")
pco2_end_delimiters = ("SW_xCO2", "Ocean co2")

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
                
pco2_summary_header = ("location_code","system_code",
               "unit_time","unit_unix_time","gps_time",
               "lat","lon","firmware","mode",
               "sw_xco2","atm_xco2")
               
samiph_header = ("location_code","system_code",
               "unit_time","unit_unix_time","gps_time",
               "lat","lon","firmware","mode","hex1","hex2")

# different length data need different headers.  keys == list length/columns
sbe16_header = {43: ["location_code","system_code",     # deployment did not startnow
                "unit_time","unit_unix_time","gps_time",
                "lat","lon","firmware","mode",
                "temp","temp_std",
                "cond","cond_std",
                "press","press_std",
                "v1","v1_std","v2","v2_std","v3","v3_std",
                "v4","v4_std","v5","v5_std","v6","v6_std",
                "temp1_serial","temp1_serial_std", 
                "press1_serial","press1_serial_std",
                "temp2_serial","temp2_serial_std",
                "press2_serial","press2_serial_std", 
                "o2_serial","o2_serial_std",
                "salinity","salinity_std",
                "soundv","soundv_std",
                "density","density_std"],
                45: ["location_code","system_code", 
                "unit_time","unit_unix_time","gps_time",
                "lat","lon","firmware","mode",
                "temp","temp_std",
                "cond","cond_std",
                "press","press_std",
                "v1","v1_std","v2","v2_std","v3","v3_std",
                "v4","v4_std","v5","v5_std","v6","v6_std",
                "temp1_serial","temp1_serial_std", 
                "press1_serial","press1_serial_std",
                "temp2_serial","temp2_serial_std",
                "press2_serial","press2_serial_std", 
                "o2_serial","o2_serial_std",
                "salinity","salinity_std",
                "soundv","soundv_std",
                "density","density_std",
                "battery_voltage","current"],
                53: ["location_code","system_code", # deployment did not startnow
                "unit_time","unit_unix_time","gps_time",
                "lat","lon","firmware","mode",
                "temp","temp_std",
                "cond","cond_std",
                "press","press_std",
                "v1","v1_std","v2","v2_std","v3","v3_std",
                "v4","v4_std","v5","v5_std","v6","v6_std",
                "temp1_serial","temp1_serial_std", 
                "press1_serial","press1_serial_std",
                "temp2_serial","temp2_serial_std",
                "press2_serial","press2_serial_std", 
                "o2_serial","o2_serial_std",
                "v7", "v8", "v9", "v10", "v11",
                "v12", "v13", "v14", "v15", "v16",
                "salinity","salinity_std",
                "soundv","soundv_std",
                "density","density_std"],
                55: ["location_code","system_code", 
                "unit_time","unit_unix_time","gps_time",
                "lat","lon","firmware","mode",
                "temp","temp_std",
                "cond","cond_std",
                "press","press_std",
                "v1","v1_std","v2","v2_std","v3","v3_std",
                "v4","v4_std","v5","v5_std","v6","v6_std",
                "temp1_serial","temp1_serial_std", 
                "press1_serial","press1_serial_std",
                "temp2_serial","temp2_serial_std",
                "press2_serial","press2_serial_std", 
                "o2_serial","o2_serial_std",
                "v7", "v8", "v9", "v10", "v11",
                "v12", "v13", "v14", "v15", "v16",
                "salinity","salinity_std",
                "soundv","soundv_std",
                "density","density_std", 
                "battery_voltage","current"]}
                