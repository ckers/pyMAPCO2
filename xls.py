# -*- coding: utf-8 -*-
"""
Methods for loading and working with
MS Excel CO2 Data
Created on Tues May 09 2017
@author: Colin Dietrich
"""

from pandas import read_excel

from . import config


def import_qc_xlsx(filepath):
    """Import worksheets of data from a QC workbook

    Parameters
    ----------
    filepath : str, absolute filepath to file

    Returns
    -------
    dict of Pandas DataFrames
    """

    _df = read_excel(filepath,
                     index=False,
                     sheetname=config.xls_sheet_names)
    return _df
