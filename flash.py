# -*- coding: utf-8 -*-
"""
Parse MAPCO2 flash data

@author: Colin Dietrich
"""
import pandas as pd

import datatypes
import parse


def concat(data, start, end, verbose=False):
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

    # break the data file into samples
    frame = data[start[0]:end[0]]

    # first frame of data to initialize DataFrames and Panel
    h_0, g_0, e_0, co2_0, aux_0, sbe16_0 = frame(sample=frame, verbose=verbose)

    # print('h>>', g_0.date_time, h_0.system, h_0.date_time)
    # print('h>>', h_0.data)

    if g_0.date_time == 'NaT':
        dt = h_0.date_time
    else:
        dt = g_0.date_time

    common_key = dt + '_' + h_0.system
    # print('h common_key>>', common_key)

    h = pd.DataFrame(data=[h_0.data], columns=h_0.data_names)
    g = pd.DataFrame(data=[g_0.data], columns=g_0.data_names)
    e = pd.DataFrame(data=[e_0.data], columns=e_0.data_names)
    h['common_key'] = common_key
    g['common_key'] = common_key
    e['common_key'] = common_key

    # print(h.head())
    # print(g.head())
    # print(e.head())

    co2 = co2_0
    co2['common_key'] = common_key

    # aux = pd.DataFrame(data=[aux.data], columns=aux.data_names)
    aux = [aux_0]
    sbe16 = [sbe16_0]

    # TODO: break this out to use in IRIDIUM files and terminal dumps too!

    for n in range(1, len(start)):
        # break the data file into samples
        frame = data[start[n]:end[n]]
        h_n, g_n, e_n, co2_n_df, aux_n, sbe16_n = frame(sample=frame, verbose=verbose)
        # print('co2_n df>>', co2_n.head())
        # print('h>>', g_n.date_time, h_n.system, h_n.date_time)
        # print('h>>', h_n.data)

        if g_n.date_time == 'NaT':
            dt = h_n.date_time
        else:
            dt = g_n.date_time

        common_key = dt + '_' + h_n.system
        # print('h common_key>>', common_key)

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
            # global_log.events.append('Error parsing aux data at:', common_key)
            print('Error parsing aux data at:', common_key)
        try:
            # co2[common_key] = co2_n
            co2_n_df['common_key'] = common_key
            co2 = pd.concat([co2, co2_n_df])
        except ValueError:
            # print('parse.flash>> co2', co2.ix[-1])
            # global_log.events.append('Error parsing co2 data at:', common_key)
            print('Error parsing co2 data at:', common_key)
        aux.append(aux_n)
        sbe16.append(sbe16_n)

    return h, g, e, co2, aux, sbe16


def frame(sample, verbose=False):
    h = sample[0]
    g = sample[1]
    e = sample[2]

    if verbose:
        print("frame header>>", h)
        print("frame gps>>", g)
        print("frame engineering>>", e)

    h = parse.header(line=h, verbose=verbose)
    g = parse.gps(line=g, verbose=verbose)
    g.timestamp = h.timestamp
    e = parse.engr(line=e, verbose=verbose, data_type='flash')
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


def clean_flash_line(line):
    """Clean a line of flash data

    Parameters
    ----------
    line : str

    Returns
    -------

    """
    if line == '':
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


def index_frame(data, verbose=False):
    """Find delimiters between cycles

    Parameters
    ----------
    data : list, str of each line from flash file in this frame
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

    met_df = None
    sbe16_df = None

    i, m, c = frame(sample, verbose=False)
    i_end = i[1:] + [len(sample)]

    if verbose:
        print("frame delimiters, i>>", i)
        print("frame min,  m>>", m)
        print("frame cycles, c>>", c)
        print("frame info lengths>> ", len(i), len(m), len(c))

    cycle_0 = sample[i[0]:i_end[0]]
    co2_container_0 = flash_single_cycle(cycle_0)

    co2_container_0.data["cycle"] = c[0]

    co2_df = co2_container_0.data

    for n in range(1, len(c)):

        cycle = sample[i[n]:i_end[n]]

        if c[n].lower() == 'met':
            met_container = frame_met(cycle, header=header,
                                      verbose=verbose)
            met_df = met_container.data
        elif c[n].lower() == 'sbe16':
            sbe16_container = frame_sbe16(cycle, header=header,
                                          verbose=verbose)
            sbe16_df = sbe16_container.data
        else:
            co2_df_n = flash_single_cycle(cycle)
            if co2_df_n is None:
                continue
            co2_df_n.data["cycle"] = c[n]
            co2_df = pd.concat([co2_df, co2_df_n.data])
            co2_df['n'] = co2_df.index

    return co2_df, met_df, sbe16_df


def frame_met(raw_data, header, verbose=False):
    """Parse met data from the flash frame

    Parameters
    ----------
    raw_data :
    header :
    verbose : bool,
    """

    if verbose:
        pass

    md = datatypes.MetData()
    md.raw = raw_data
    md.header = header
    md.extract()
    md.convert()
    return md


def frame_sbe16(raw_data, header, verbose=False):
    """Parse met data from the flash frame

    Parameters
    ----------
    raw_data :
    header :
    verbose : bool,
    """

    if verbose:
        pass

    sbe16 = datatypes.SBE16Data()
    sbe16.raw = raw_data
    sbe16.header = header
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
        if cycle[n][0:2] in ('Li', 'O2', 'RH', 'Rh', 'Met', 'SBE16', 'Seafet Data'):
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

    cycle_out = datatypes.LIData()
    cycle_out.raw = cycle_li
    cycle_out.header()
    cycle_out.extract()
    cycle_out.convert()

    # if cycle_out.number > 1:
    #     cycle_out.extract()
    #     cycle_out.convert()

    o2 = datatypes.AuxData()
    o2.header()
    if o2.number > 1 & len(cycle_out.data) > 0:
        o2.raw = cycle_o2
        o2.extract()
        cycle_out.data["O2_percent"] = o2.data

    rh = datatypes.AuxData()
    rh.header()
    if rh.number > 1 & len(cycle_out.data) > 0:
        rh.raw = cycle_rh
        rh.extract()
        cycle_out.data["RH_percent"] = rh.data

    rht = datatypes.AuxData()
    rht.header()
    if rht.number > 1 & len(cycle_out.data) > 0:
        rht.raw = cycle_rht
        rht.extract()
        cycle_out.data["RH_temp_c"] = rht.data

    return cycle_out
