# -*- coding: utf-8 -*-
"""
Parse SSTC Data

@author: Colin Dietrich
"""


def clean_flash(data_list):
    """Clean a list of MAPCO2 flash SSTC data

    Parameters
    ----------
    data_list : list of string lines

    Returns
    -------
    """

    # truncate lines to just met/sstc data
    # (pH data is next thing
    if 'Sami Data' in data_list:
        _line = 'Sami Data'
    elif 'Seafet Data' in data_list:
         _line = 'Seafet Data'
    data_list = data_list[:data_list.index(_line)]

    # remove blank lines
    data_list = [x for x in data_list if x != '']


    return data_list



