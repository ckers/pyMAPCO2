# -*- coding: utf-8 -*-
"""
Compenstate oxygen optode measurements with salinity and temperature
Created on Thu Mar 16 15:30:18 2017
@author: Colin Dietrich

Equations from Aanderaa documentation available online:
    http://www.aanderaa.com/productsdetail.php?Oxygen-Optodes-2
Specifically:
    http://www.aanderaa.com/media/pdfs/TD-280-Oxygen-Optode-Calculations.xls

Which contains these notes on the basis of these calculations:

Note 1. Solubility and salinity compensation calculation based on:
Garcia and Gordon. 1992. Oxygen solubility in seawater: Better fitting
equations Limnology and Oceanography: 37(6) :1307-1312.
Note 2. Pressure compensation based on:
Hiroshi Uchida, Takeshi Kawano, Ikuo Kaneko and Masao Fukasawa. In-Situ 
calibration of optode-based oxygen sensors. Journal of Atmospheric and 
Oceanic Technology December 2008
Note 3. For other calcualtions refer to AADI Operating Manual TD218 and TD269
"""

import numpy as np


def temperature_scaled(t_C):
    """Scale temperature in degrees C
    TODO: understand why this scale happens
    """
    c0 = 273.15  # zero degrees Celsius in Kelvin
    c25 = 298.15  # 25 degrees Celsius in Kelvin
    return np.log((c25 - t_C)/(c0 + t_C))
   
def s_c_f(ts, s, s0=0):
    """Salinity compensatation factor for an oxygen measurement
    TODO: cite source of constants
    
    Parameters
    ----------
    ts : float, temperature of measurement (C)
    s : float, salinity (PSU)
    s0 : float, salinity setting of instrument while recording (PSU),
        default in device is 0.
    
    Returns
    -------
    SCf : float, salinity compensation factor for Oxygen measurement
    """
    
    # Coefficients for Salinity Compensation		
    B0 = -6.24097E-03	
    B1 = -6.93498E-03	
    B2 = -6.90358E-03	
    B3 = -4.29155E-03	
    C0 = -3.11680E-07	
    
    scf = np.exp((s - s0) * 
                 (B0 + B1 * ts + B2 * ts**2 + B3 * ts**3) + 
                  C0 * (s**2 - s0**2))
    return scf

def p_c_f(d=0, pc=0.032):
    """Pressure compensate an oxygen measurement
    TODO: cite source of constants
    
    Parameters
    ----------
    d : float, depth in meters (m)
    pc : float, pressure compensation coefficient
    
    Returns
    -------
    float, pressure compensation factor
    """
    
    return ((np.abs(d) / 1000) * pc) + 1
    
def volts_to_temp_C(v):
    """Convert voltage out of Aanderaa 4175 to temperature in C
    
    Refer to pg 2: http://www.aanderaa.com/media/pdfs/Oxygen-Optode-3835-4130-4175.pdf
    measurement range: -5 to 40 C, therefore range = 45
    minus 5 to get below zero
    therefore: ((X VDC / 1) * (45 C / 5 VDC)) - 5 VDC = Y C
    
    Parameters
    ----------
    v : float, voltage value from Aandera output (0-5 VDC)
    
    Returns
    -------
    t : float, temperature in degrees Celcius
    """
    
    return ((v / 1) * (45.0 / 5.0)) - 5.0
    
def volts_to_O2_uM(v):
    """Convert voltage out of Aanderaa 4175 to μM Oxygen concentration
    o2 = (v2 / 5.0) * 500 --> units micromoles --> μM
    measurement range: 0-500 μM
    voltage output range: 0-5 VDC
    therefore: (X VDC / 1) * (500 μM / 5 VDC) = Y μM Oxygen
    
    Parameters
    ----------
    v : float, voltage value from Aandera output (0-5 VDC)
    """
    return (v / 1) * (500.0 / 5.0)

def solubility(p, ts, s):
    """Solubility of oxygen in seawater 
    
    Parameters
    ----------
    p : float, air pressure (hPa)
    ts : float, scaled temperature (C)
    s : float, salinity (PSU)
    
    Returns
    -------
    float, solubility of oxygen in seawater (μM)
    """
    
    sol = ((p / 1013.25) * 44.659 
           * np.exp(2.00856 +
                    3.224 * ts +
                    3.99063 * ts**2 +
                    4.80299 * ts**3 +
                    0.978188 * ts**4 +
                    1.71069 * ts**5 +
                    s * (-0.00624097 - 0.00693498 * ts +
                         -0.00690358 * ts**2 +
                         -0.00429155 * ts**3) +
                         -0.00000031168 * s**2))

    return sol
    
def o2_compensate(o2, scf, pcf, unit='uM'):
    """Compensate for salinity and pressure influences on oxygen measurement
    
    Parameters
    ----------
    o2 : float, o2 concentration measured (μM)
    scf : float, salinity compensation factor
    pcf : float, pressure compensation factor
    unit : str, units to return.  Valid options:
        'uM' = micromoles (μM) (default and if invalid)
        'mg/l' = milligrams per liter (mg/l)
        'ml/l' = milliliters per liter (ml/l)
    
    Returns
    -------
    o2cc : float, oxygen compensated for salinity and pressure (μM)
    """
    
    o2cc = o2 * scf * pcf
    if unit == 'uM':
        return o2cc
    elif unit == 'mg/l':
        return 32 * o2cc / 1000
    elif unit == 'ml/l':
        return o2cc/ 44.615
    else:
        return o2cc
    
def o2_air_saturation(o2cc, sol):
    """Oxygen saturation in air
    
    Parameters
    ----------
    o2cc : float, oxygen concentration compensated (μM)
    sol : float, solubility of oxygen (μM)
    
    Returns
    -------
    float : saturation of oxygen in air (%)
    """
    
    return 100 * o2cc / sol
    