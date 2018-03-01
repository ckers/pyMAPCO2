"""Companion module to lab_tests
for plotting multi-system data

Colin Dietrich 2018

Data note: All plots assume a MultiIndex format of:
system, cycle, datetime64_ns
    system : str, 'm_XXXX' i.e. 'm_0168' for MAPCO2 0168, or 'a_0003' for ASV 0003
    cycle : str, 'apon', 'apof', etc
    datetime64_ns : datetime object, created with pd.to_datetime()
"""
import time
import numpy as np

from plotly import tools
import plotly.offline as ply
import plotly.graph_objs as go

from . import config


def one_cycle(df, keepers, cycle='apof', verbose=False):
    """Create a subplot of one cycle and 'keeper' data types"""

    systems = df.index.levels[0].values
    color_mapper = dict(zip(systems, config.lab_test_colors[0:len(systems)]))
    e_values  = enumerate(keepers)

    fig = tools.make_subplots(rows=len(keepers), cols=1,
                              subplot_titles     = keepers,
                              shared_xaxes       = True,
                              horizontal_spacing = 0.001,
                              vertical_spacing   = 0.01,
                              print_grid         = False)

    for vn, v in e_values:
        if verbose:
            print('  ', vn, v)
        for s in systems:
            if verbose:
                print('      ', s)

            _df = df.loc[(s, cycle), v]

            trace = go.Scatter(x=_df.index, y=_df.values,
                               name=s, mode='lines+markers',
                               marker = dict(size = 3,
                                             color=color_mapper[s],
                                             )
                              )
            fig.append_trace(trace, vn+1, 1)

    fig['layout'].update(height=2000,
                         width=650,
                         title='Lab 1030 Testing',
                         showlegend=False,
                         margin=go.Margin(l=30, r=10, b=60, t=60, pad=10)
                         )
    ply.iplot(fig, show_link=False)


def xCO2_sw_air(df, publish=False, verbose=False):

    systems = df.index.levels[0].values
    color_mapper = dict(zip(systems, config.lab_test_colors[0:len(systems)]))
    e_cycles = enumerate(['apof', 'epof'])

    fig = tools.make_subplots(rows=2, cols=1,
                              subplot_titles = ['Air xCO2 Dry', 'Seawater xCO2 Dry'],
                              shared_xaxes       = True,
                              horizontal_spacing = 0.001,
                              vertical_spacing   = 0.01,
                              print_grid         = False)

    for cn, c in e_cycles:
        if verbose:
            print(c.upper())
        for s in systems:
            if verbose:
                print('      ', s)

            _df = df.loc[(s, c), 'xCO2_dry']

            trace = go.Scatter(x=_df.index, y=_df.values,
                               name=s, mode='lines+markers',
                               marker = dict(size = 3,
                                             color=color_mapper[s],
                                             )
                              )
            fig.append_trace(trace, cn+1, 1)

    fig['layout'].update(height=1000,
                         width=650,
                         title='APOF and EPOF xCO2 Dry',
                         showlegend=False,
                         margin=go.Margin(l=30, r=10, b=30, t=60, pad=10)
                         )

    _f = 'lab1030_co2_data.html'
    ply.plot(fig, output_type='file',
             auto_open=True, filename=_f,  show_link=False)
    if publish:
        #TODO: add target to config.py and remove here
        network_dir = 'Z:\\dietrich\\lab1030_status\\'
        _f_dated = (network_dir +
                    time.strftime('%Y_%m_%d_%H_%M_%S') +
                    '_lab1030 - [' +
                    ' '.join(list(df.index.levels[0])) +
                    '].html')
        ply.plot(fig, output_type='file',
                 auto_open=False, filename=_f_dated, show_link=False)
    ply.iplot(fig, show_link=False)


def relative_press(df, verbose=False):
    """Calculate and plot relative pressure
    TODO: break the calculations out into lab_tests
    ...this might be confusing broken out of Jupyter, the df
    assignment is no longer inline other calculations!
    """

    systems = df.index.levels[0].values
    color_mapper = dict(zip(systems, config.lab_test_colors[0:len(systems)]))
    e_cycles  = enumerate(['zpon', 'spon', 'epon', 'apon'])

    df['relative_press'] = np.nan

    cycle_pump_deltas = [['zpon', 'zpof'], ['spon', 'spof'],
                         ['epon', 'epof'], ['apon', 'apof']]

    for sn in systems:
        for cycles in cycle_pump_deltas:
            _rel_press = (df.loc[(sn, cycles[1]), 'licor_press'] -
                          df.loc[(sn, cycles[0]), 'licor_press'])
            df.loc[(sn, cycles[0]), 'relative_press'] = _rel_press.values

    fig = tools.make_subplots(rows=4, cols=1,
                              subplot_titles = ['ZPON', 'SPON', 'EPON', 'APON'],
                              shared_xaxes       = True,
                              horizontal_spacing = 0.001,
                              vertical_spacing   = 0.05,
                              print_grid         = False)

    for cn, c in e_cycles:
        if verbose: print(c.upper())
        for s in systems:
            if verbose: print('      ', s)

            _df = df.loc[(s, c), 'relative_press']

            trace = go.Scatter(x=_df.index, y=_df.values,
                               name=s, mode='lines+markers',
                               marker = dict(size = 3,
                                             color=color_mapper[s],
                                             ),
                               yaxis='y1'
                              )
            fig.append_trace(trace, cn+1, 1)

    fig['layout'].update(height=1000,
                         width=650,
                         title='Lab 1030 Testing - On/OFF Pressure Difference',
                         showlegend=False,
                         margin=go.Margin(l=30, r=10, b=100, t=60, pad=50),
                         )
    ply.iplot(fig, show_link=False)


def delta_press_filled(df, verbose=False):
    """Plot the absolute pressure of ON/OFF cycles and fill between them
    TODO: create standard y axis range
        """
    systems = df.index.levels[0].values

    fig = tools.make_subplots(rows=len(systems), cols=1,
                              subplot_titles = systems,
                              shared_xaxes   = True,
                              horizontal_spacing=0.001, vertical_spacing=0.01,
                              print_grid     = False)

    for sn, s in enumerate(systems):

        _df = df.loc[(s, 'apon'), 'licor_press']

        trace = go.Scatter(x=_df.index, y=_df.values,
                           name=s + ' apon', mode='lines+markers',
                           marker = dict(size = 3,
                                         color='cyan',
                                         ),
                           yaxis='y1'
                           )
        fig.append_trace(trace, sn + 1, 1)

        _df = df.loc[(s, 'epon'), 'licor_press']

        trace = go.Scatter(x=_df.index, y=_df.values,
                           fill='tonexty',
                           name=s + ' epon', mode='lines+markers',
                           marker = dict(size = 3,
                                         color='blue',
                                         ),
                           yaxis='y1'
                           )
        fig.append_trace(trace, sn + 1, 1)

    fig['layout'].update(height=1000,
                         width=600,
                         title='APON and EPON ABS Pressure (kPa)',
                         showlegend=False,
                         margin=go.Margin(l=60, r=10, b=30, t=60, pad=10),
                         #yaxis={'range':[80, 120],
                         #       'title':'Time',
                         #       'autorange':False}
                         )
    ply.iplot(fig, show_link=False)


def gps(df, verbose=False):

    systems = df.index.levels[0].values
    for sn in systems:
        gps = df.loc[(sn, 'apof'), ('lat', 'lon', 'datetime_mapco2')]
        gps[gps.lat != 0.0].iplot(kind='scatter', mode='markers+lines',
                                  x='lon', y='lat',
                                  text='datetime_mapco2',
                                  title='GPS for ' + sn)


