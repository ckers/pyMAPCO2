# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 2017
@author: Colin Dietrich

co2sys methods
"""

import pandas as pd


def parse_excel_csv_output(_f):
    """Parse the output columns from co2sys.xls
    Note: these columns AND header rows need to be manually pasted
    into a new .csv using Excel.

    Parameters
    ----------
    _f : str, filepath

    Returns
    -------
    units : tuple of str, units for each column
    Pandas DataFrame : data from .csv
    """

    names_units = [['datetime', 'excel_datetime'],
               ['t_out', 'C'],
               ['p_out', 'dbar'],
               ['pH_out', 'pH units'],
               ['fco2_out', 'matm'],
               ['pco2_out', 'matm'],
               ['hco3_out', 'mmol/kg SW'],
               ['co3_out', 'mmol/kg SW'],
               ['co2_out', 'mmol/kg SW'],
               ['b_alk_out', 'mmol/kg SW'],
               ['oh_out', 'mmol/kg SW'],
               ['p_alk_out', 'mmol/kg SW'],
               ['si_alk_out', 'mmol/kg SW'],
               ['revelle_out', 'Revelle units'],
               ['wca_out', 'WCa units'],
               ['war_out', 'WAr units'],
               ['xco2_out', 'ppm']]

    names, units = zip(*names_units)

    return units, pd.read_csv(_f, names=names, header=0)
