# -*- coding: utf-8 -*-
"""
Parse MAPCO2 Iridium data

Created on Thu Jul 28 14:45:54 2016
@author: Colin Dietrich
"""

import pandas as pd

from . import config
from . import datatypes
from . import parse
from .algebra import common_key


def concat(data, start, end, verbose=False):
    """Break the data file into sections

    Parameters
    ----------
    data :
    start :
    end :
    verbose : bool, print debug statements

    """

    (h, g, e, co2, aux, sbe16, ph) = frame(data[start[0]:end[0]],
                                           verbose=verbose)

    '''
    for n in range(1, len(start)):
        # break the data file into samples
        sample = data[start[n]:end[n]]
        frame(sample=sample, verbose=True)
    '''

    for n in range(1, len(start)):

        (h_n, g_n, e_n,
         co2_n, aux_n, sbe16_n, ph_n) = frame(data[start[n]:end[n]],
                                              verbose=verbose)

        print('aux_n>>', aux_n)
        print('sbe16_n', sbe16_n)
        print('yay!')

        h = pd.concat([h, h_n])
        g = pd.concat([g, g_n])
        e = pd.concat([e, e_n])
        co2 = pd.concat([co2, co2_n])
        ph = pd.concat([ph, ph_n])
#        aux = pd.concat([aux, aux_n])
#        sbe16 = pd.concat([sbe16, sbe16_n])

    aux = None
    sbe16 = None

    return h, g, e, co2, aux, sbe16, ph


def frame_co2(sample, system, verbose=False):
    """Parse CO2 data into DataFrames.  Does not handle auxilary data.
    Allowed datatypes are:
        'm' : mapco2
        'w' : waveglider
        'a' : asv

    Parameters
    ----------
    sample : list of string data containg frame of co2 data
    system : str, type of data source and serial number for data identification
    verbose : bool, print debug statements

    Returns
    -------
    h : Pandas DataFrame, header data
    g : Pandas DataFrame, GPS data
    e : Pandas DataFrame, engineering data
    _co2 : Pandas DataFrame, co2 data
    """
    if verbose:
        print('iridium.frame>>')
        print(sample)
        print("="*10)

    for line in sample:
        if line == config.repeat_flag:
            h = pd.DataFrame(data=None)
            g = pd.DataFrame(data=None)
            e = pd.DataFrame(data=None)
            _co2 = pd.DataFrame(data=None)
            if verbose:
                print('iridium.frame_co2>> Repeat line found, skipping data =====')
            return h, g, e, _co2

    h = parse.header(sample[0], verbose=verbose)
    g = parse.gps(sample[1], verbose=verbose)
    e = parse.engr(sample[2], verbose=verbose,
                   data_type='iridium', firmware=h.firmware)

    h = pd.DataFrame(data=[h.data], columns=h.data_names)
    g = pd.DataFrame(data=[g.data], columns=g.data_names)
    e = pd.DataFrame(data=[e.data], columns=e.data_names)

    if verbose:
        print('g.datetime_gps, h.system, h.date_time')
        print(g)
        print('  >>', g.datetime_gps, h.system, h.datetime_mapco2)
        print('h>>', h, type(h), type(h.datetime_mapco2), type(h.system))



    h['datetime64_ns_mapco2'] = pd.to_datetime(h.datetime_mapco2,
                                               format=config.header_datetime_format)

    data_common_key = common_key(system, h.datetime64_ns_mapco2[0])

    if verbose:
        print('h common_key>>', data_common_key, type(data_common_key))

    h['common_key'] = data_common_key
    g['common_key'] = data_common_key
    e['common_key'] = data_common_key

    def gps_time_fix(x):
        if x[0:4] == '0000':
            return h.datetime_mapco2
        else:
            return x

    g.datetime_gps = g.datetime_gps.apply(gps_time_fix)

    g['datetime64_ns_gps'] = pd.to_datetime(g.datetime_gps,
                                            format=config.gps_datetime_format)
    e['datetime64_ns_engr'] = pd.to_datetime(h.datetime64_ns_mapco2)

    if verbose:
        print('h.head()>>', h.head())
        print('g.head()>>', g.head())
        print('e.head()>>', e.head())

    if len(sample) < 12:
        _co2 = pd.DataFrame(data=None)
    else:
        zpon = parse.co2_line(sample[3], verbose=verbose)
        zpof = parse.co2_line(sample[4], verbose=verbose)
        zpcl = parse.co2_line(sample[5], verbose=verbose)
        spon = parse.co2_line(sample[6], verbose=verbose)
        spof = parse.co2_line(sample[7], verbose=verbose)
        spcl = parse.co2_line(sample[8], verbose=verbose)
        epon = parse.co2_line(sample[9], verbose=verbose)
        epof = parse.co2_line(sample[10], verbose=verbose)
        apon = parse.co2_line(sample[11], verbose=verbose)
        apof = parse.co2_line(sample[12], verbose=verbose)

        zpon = ['zpon'] + zpon.data
        zpof = ['zpof'] + zpof.data
        zpcl = ['zpcl'] + zpcl.data
        spon = ['spon'] + spon.data
        spof = ['spof'] + spof.data
        spcl = ['spcl'] + spcl.data
        epon = ['epon'] + epon.data
        epof = ['epof'] + epof.data
        apon = ['apon'] + apon.data
        apof = ['apof'] + apof.data

        data_template = datatypes.MAPCO2Data()

        _co2 = pd.DataFrame(data=[zpon, zpof, zpcl, spon, spof, spcl, epon, epof,
                                  apon, apof], columns=['cycle']+data_template.data_names)

        _co2['common_key'] = data_common_key
        _co2['system'] = system
        _co2['datetime_str'] = h.datetime_mapco2[0]
        _co2['datetime64_ns'] = h.datetime64_ns_mapco2[0]

    if verbose:
        print(_co2.head())
    return h, g, e, _co2


def batch_co2(df, verbose=False):
    """Batch process and concatenate data from a DataFrame that contains list
    data and datatype strings.

    Parameters
    ----------
    df : Pandas DataFrame, with list data and datatype columns
        list_data : list of str, co2 data lines
        datatype : str, datatype of co2 imported see irdium.frame_co2 for details
    verbose : bool, print debug statements

    Returns
    -------
    h, g, e, co2 : Pandas DataFrames
    """

    data_list = df.co2_list
    system = df.system
    if verbose:
        print(len(data_list[0]))

    h, g, e, co2 = frame_co2(data_list[0], system[0], verbose=verbose)

    for n in range(1, len(data_list)):
        if verbose:
            print(len(n))
        h_n, g_n, e_n, co2_n = frame_co2(data_list[n], system[n], verbose=verbose)
        h = pd.concat([h, h_n])
        g = pd.concat([g, g_n])
        e = pd.concat([e, e_n])
        co2 = pd.concat([co2, co2_n])

    return h, g, e, co2


def frame(sample, verbose=False, ph=False):
    """Handle one frame of data

    Parameters
    ----------
    sample : list of str, cleaned data from MAPCO2
    verbose : bool, print debug statements
    pH : bool, whether to process pH data found in Iridium data

    Returns
    -------

    """

    if verbose:
        print('iridium.frame>>')
        print(sample)
        print("="*10)

    h = parse.header(sample[0], verbose=verbose)
    g = parse.gps(sample[1], verbose=verbose)
    e = parse.engr(sample[2], verbose=verbose,
                   data_type='iridium', firmware=h.firmware)

    h = pd.DataFrame(data=[h.data], columns=h.data_names)
    g = pd.DataFrame(data=[g.data], columns=g.data_names)
    e = pd.DataFrame(data=[e.data], columns=e.data_names)

    if verbose:
        print('g.datetime_gps, h.system, h.date_time')
        print(g)
        print('  >>', g.datetime_gps, h.system, h.datetime_mapco2)
        print('h>>', h, type(h), type(h.datetime_mapco2), type(h.system))

    common_key = h.datetime_mapco2[0] + '_' + h.system[0]

    if verbose:
        print('h common_key>>', common_key, type(common_key))

    h['common_key'] = common_key
    g['common_key'] = common_key
    e['common_key'] = common_key

    if verbose:
        print('h.head()>>', h.head())
        print('g.head()>>', g.head())
        print('e.head()>>', e.head())

    zpon = parse.co2_line(sample[3], verbose=verbose)
    zpof = parse.co2_line(sample[4], verbose=verbose)
    zpcl = parse.co2_line(sample[5], verbose=verbose)
    spon = parse.co2_line(sample[6], verbose=verbose)
    spof = parse.co2_line(sample[7], verbose=verbose)
    spcl = parse.co2_line(sample[8], verbose=verbose)
    epon = parse.co2_line(sample[9], verbose=verbose)
    epof = parse.co2_line(sample[10], verbose=verbose)
    apon = parse.co2_line(sample[11], verbose=verbose)
    apof = parse.co2_line(sample[12], verbose=verbose)

    zpon = ['zpon'] + zpon.data
    zpof = ['zpof'] + zpof.data
    zpcl = ['zpcl'] + zpcl.data
    spon = ['spon'] + spon.data
    spof = ['spof'] + spof.data
    spcl = ['spcl'] + spcl.data
    epon = ['epon'] + epon.data
    epof = ['epof'] + epof.data
    apon = ['apon'] + apon.data
    apof = ['apof'] + apof.data

    data_template = datatypes.MAPCO2Data()

    _co2 = pd.DataFrame(data=[zpon, zpof, zpcl, spon, spof, spcl, epon, epof,
                              apon, apof], columns=['cycle']+data_template.data_names)

    _co2['common_key'] = common_key
    _co2['system'] = h.system[0]
    _co2['datetime_str'] = h.datetime_mapco2[0]

    _co2['datetime'] = pd.to_datetime(_co2.datetime_str,
                                      format='%Y/%m/%d_%H:%M:%S')

    if verbose:
        print(_co2.head())

    # handle sstc and ph data
    sbe16_i, ph_i = index_frame(sample)

    if verbose:
        print('sbe16_i>>', sbe16_i)
        print('ph_i>>', ph_i)

    if len(sbe16_i) == 2:
        sbe16 = datatypes.SBE16Data()
        sbe16.raw = sample[sbe16_i[0]:sbe16_i[1]]
        
    if len(ph_i) == 2:
        # TODO: Seafet data handler
        ph = datatypes.SAMI2Data()
        ph.raw = sample[ph_i[0]:ph_i[1]]
        ph.extract()
        if ph.data is not None:
            phdf = pd.DataFrame({'hex': ph.data, 'index': list(range(0, len(ph.data)))})
        else:
            phdf = pd.DataFrame({})
    else:
        phdf = pd.DataFrame({})
        
    sbe16 = pd.DataFrame({})
    aux = pd.DataFrame({})

    return h, g, e, _co2, aux, sbe16, phdf


def index_frame(data, verbose=False):
    """Find delimiters between cycles

    Parameters
    ----------
    data : list, str of each line from flash file in this frame
    verbose : bool, print debug statements

    Returns
    -------
    sbe16 : list, start index and end index of sbe16 data
    ph : list, start and end index of ph data
    """

    sbe16 = []
    ph = []

    sbe16_temp_start = 0
    ph_temp_start = 0

    for n in range(0, len(data)):
        if verbose:
            print(n)
        if data[n][0:5].lower() == 'sbe16':
            sbe16_temp_start = n
        if data[n][0:9].lower() == 'end sbe16':
            sbe16.append(sbe16_temp_start)
            sbe16.append(n)
        if data[n][0:5].lower() == 'ph':
            ph_temp_start = n
        if data[n][0:9].lower() == 'end ph':
            ph.append(ph_temp_start)
            ph.append(n)

    return sbe16, ph


def batch_list(data_list, verbose=False):
    """Batch process and concatenate data from a DataFrame column
    that contains list data"""

    h, g, e, co2, aux, sbe16, phdf = frame(data_list[0], verbose=verbose)

    for n in data_list[1:]:
        h_n, g_n, e_n, co2_n, aux_n, sbe16_n, phdf_n = frame(n, verbose=verbose)
        h = pd.concat([h, h_n])
        g = pd.concat([g, g_n])
        e = pd.concat([e, e_n])
        co2 = pd.concat([co2, co2_n])
        phdf = pd.concat([phdf, phdf_n])
        if verbose:
            print(type(aux_n))
            print(type(phdf_n))
        aux = pd.concat([aux, aux_n])
        sbe16 = pd.concat([sbe16, sbe16_n])

    return h, g, e, co2, aux, sbe16, phdf
