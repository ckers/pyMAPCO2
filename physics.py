# -*- coding: utf-8 -*-
"""Meteorology calculations for CO2 data processing

Colin Dietrich 2017
colin.dietrich@noaa.gov
"""

import numpy as np


def relative_humidity(vapor_pressure, temperature, saturation_vapor_pressure):
    pass


def calc_sat_vapor_press(t_rh, f=1.004):
    """Form of Teten's Equation
    Cited in Sutton et al. 2014, equation 2
    Values from Licor 610 manual 2nd Edition, November 2004, page 3-7
    Which are from Buck 1981, equation 8

    General form: e_w = f * a * exp((b * T)/(T + C))
    See pg 1528, equation 3a and add enhancement factor f

    Values are from suggested ew1, fw3
    Therefore 1.004 = (1.0007 + (3.46e-6 * P)) where P = 1000 mbar

    Parameters
    ----------
    t_rh : float, temperature in degrees C
    f : float, enhancement factor.  Adjustment between pure vapor and
        water vapor in air

    Returns
    -------
    float, saturation vapor pressure in kPa
    """

    return f * 0.61365 * np.exp((17.502 * t_rh) / (240.97 + t_rh))


def tetens(t_rh):
    """Form of Teten's Equation
    Tetens, O. 1930. Über einige meteorologische Begriffe. Z.
    Geophys 6: 207-309.

    Constants are copied from Buck 1981

    Parameters
    ----------
    t_rh : float, temperature in degrees C

    Returns
    -------
    float, saturation vapor pressure in kPa
    """

    return 0.61365 * np.exp((17.502 * t_rh) / (t_rh + 240.97))


def buck_equation(T):
    """Buck Equation for approximation of saturated vapour pressure
    over water

    Sourced from some company hardware manual:
    http://www.hygrometers.com/wp-content/uploads/CR-1A-users-manual-2009-12.pdf

    Parameters
    ----------
    T : float, temperature in degrees C

    Returns
    -------
    float, saturation vapor pressure in kPa
    """
    return 0.61121 * np.exp((18.678 - (T / 234.5)) * (T / (257.14 + T)))


def calc_vapor_pressure(rh_sample, rh_span, vp_sat):
    """Caclulate the vapor pressure of a sample,
    from Stacy's notes, requires citation

    Parameters
    ----------
    rh_sample : relative humidity of the sample cycle pump off
    rh_span : relative humidity of the span cycle post-cal
    vp_sat : saturation vapor pressure at the temperature of the rh measurements

    Returns
    -------
    vp : float, vapor pressure in XXX units
    """
    return (rh_sample - rh_span) * (vp_sat / 100)


def calc_co2_dry(xco2, press, vapor_press):
    """Calculate CO2 dry from xCO2

    Parameters
    ----------
    xco2 : float, xCO2
    press : float, pressure in licor (kPa)
    vapor_press : float, vapor pressure in licor (kPa)

    Returns
    -------
    xco2_dry : float
    """

    return xco2 / ((press - vapor_press) / press)
