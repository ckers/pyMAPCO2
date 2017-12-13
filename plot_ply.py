# -*- coding: utf-8 -*-
"""
Plot CO2 data using Plot.ly
Created on 2017-04-25
@author: Colin Dietrich
"""

from pandas import notnull, DataFrame

import plotly.offline as ply
import plotly.graph_objs as go

from . import plot
from . import config
from . import stats

xco2_air_color = 'cyan'
xco2_sw_color = 'blue'
sst_color = 'orange'
sst_mapco2_color = 'orange'
sst_sso2_color = 'orange'
sst_ph_color = 'orange'
sst_partner_color = 'orange'
sss_color = 'purple'
ntu_color = 'grey'
sso2_color = 'red'
ph_color = 'green'
ph_ta_color = '#53f442'
ph_int_color = '#9ff22b'
ph_ext_color = '#2bf2bd'
mbl_color = 'black'
epon_press_color = '#f442f4'  # purple-ish
apon_press_color = '#f47141'  # salmon/orange-ish
precip_color = '#ede21e'  # yellowish
general_color = '#7f808c'  # steel blue/grey


def default_layout(df=None,
                   xco2_sw_range=None,
                   xco2_air_range=None,
                   sst_range=None,
                   sss_range=None,
                   ph_range=None,
                   sso2_range=None,
                   atm_press_range=None,
                   general_range=[0,100],
                   autoscale=False,
                   title=None,
                   ):
    """Plot.ly default layout for xCO2, SST, SSS, pH

    Parameters
    ----------
    df : Pandas DataFrame, data to plot
    xco2_sw_range : array-like, two values - kmin & kmax
    xco2_air_range : array-like, two values - kmin & kmax
    sst_range : array-like, two values - kmin & kmax
    sss_range : array-like, two values - kmin & kmax
    ph_range : array-like, two values - kmin & kmax
    sso2_range : array-like, two values - kmin & kmax
    atm_press_range : array-like, two values - kmin & kmax
    general_range : array-like, two values - kmin & kmax
    autoscale : bool, calculate autoscaled
    title : str, name of plot

    Returns
    -------
    Plot.ly layout
    """

    # TODO: add second left axis for Air xCO2 level
    if xco2_sw_range is None:
        xco2_sw_range = config.k_limits['xco2_sw']
    if xco2_air_range is None:
        xco2_air_range = config.k_limits['xco2_air']
    if sst_range is None:
        sst_range = config.k_limits['sst']
        if autoscale & (df is not None):
            lcf_sst = stats.Linear2dCurveFit()
            lcf_sst.x = df.xCO2_SW_dry
            lcf_sst.y = df.SST
            lcf_sst.fit()
            sst_min = lcf_sst.apply(min(df.xCO2_SW_dry))
            sst_max = lcf_sst.apply(max(df.xCO2_SW_dry))
            sst_range = [sst_min - sst_min * 0.05,
                         sst_max + sst_max * 0.05]
    if ph_range is None:
        ph_range = config.k_limits['ph']
        if autoscale & (df is not None):
            lcf_ph = stats.Linear2dCurveFit()
            lcf_ph.x = df.xCO2_SW_dry
            lcf_ph.y = df.pH
            lcf_ph.fit()
            ph_min = lcf_ph.apply(min(df.xCO2_SW_dry))
            ph_max = lcf_ph.apply(max(df.xCO2_SW_dry))
            ph_range = [ph_min - ph_min * 0.05,
                        ph_min + ph_max * 0.05]
    if sso2_range is None:
        sso2_range = config.k_limits['sso2']
    if sss_range is None:
        sss_range = config.k_limits['sss']
    if atm_press_range is None:
        atm_press_range = config.k_limits['atm_press']

    _title = 'MAPCO2 pCO2 pH SSTC'
    if title is None:
        title = _title
    else:
        title = _title + ': ' + title

    layout = go.Layout(
        title='MAPCO2 SSTC pH Data for ' + title,
        xaxis=dict(title='Date Time', domain=[0.0, 0.86]),
        yaxis=dict(title='MAPCO2 xCO2 (umol/mol)', range=xco2_sw_range),
        legend=dict(orientation="h"),

        yaxis2=dict(
            title='SST (C)',
            titlefont=dict(color=sst_color),
            tickfont=dict(color=sst_color),
            overlaying='y',
            side='right',
            range=sst_range
        ),
        yaxis3=dict(
            title='SSS',
            titlefont=dict(color=sss_color),
            tickfont=dict(color=sss_color),
            overlaying='y',
            side='right',
            range=sss_range,
            position=0.89
        ),

        yaxis4=dict(
            title='Pressure (kPa)',
            titlefont=dict(color=ntu_color),
            tickfont=dict(color=ntu_color),
            overlaying='y',
            side='right',
            range=atm_press_range,
            position=0.91
        ),
        yaxis5=dict(
            title='NTU (NTU) | CHL (μM) | SSO2 (μM)',
            titlefont=dict(color=sso2_color),
            tickfont=dict(color=sso2_color),
            overlaying='y',
            side='right',
            position=0.94,
            range=sso2_range
        ),
        yaxis6=dict(
            title='pH',
            titlefont=dict(color=ph_color),
            tickfont=dict(color=ph_color),
            overlaying='y',
            side='right',
            position=0.97,
            range=ph_range
        ),
        yaxis7=dict(
            title='General',
            titlefont=dict(color=general_color),
            tickfont=dict(color=general_color),
            overlaying='y',
            side='right',
            position=1.0,
            range=general_range

        )
    )

    return layout


def default_data(df, suffix='', df_mbl=None, connectgaps=True, **kwargs):
    """Define data dictionary to plot

    Note: hardcoded trace name srings must match dataframe column
        names to be included in data output

    Parameters
    ----------
    df : Pandas DataFrame with columns of mapco2 data
    suffix : str, value to name this series if multiple sites/units are plotted
    df_mbl : Pandas DataFrame containing mbl air xco2 values
    connectgaps : bool, Plot.ly line parameter

    Returns
    -------
    Plot.ly data dictionary
    """

    df_columns = list(df.columns)

    data = []
    x = df.datetime64_ns

    connect_gaps = connectgaps

    def gen_plot(_x, _y, _name, _visible):

        data.append(go.Scatter(
            x=_x, y=_y,
            name=_name,
            yaxis='y7',
            visible=_visible,
            mode='lines',
            line=dict(width=2, color=general_color),
            connectgaps=connect_gaps)
            )

    for key, value in kwargs.items():
        # General Plotting Axis
        if key in df_columns:
            # if value:
            #     visible = True
            # else:
            #     visible = 'legendonly'
            gen_x = x
            gen_y = df[key]
            gen_vis = True
            gen_plot(gen_x, gen_y, key, gen_vis)

        if isinstance(value, list):
            gen_x = value[0]
            gen_y = value[1]
            gen_vis = value[2]
            gen_plot(gen_x, gen_y, key, gen_vis)

    # xCO2 Seawater WET
    if 'xCO2_SW_wet' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_wet,
            name='xCO2_SW_wet' + suffix,
            opacity=0.5,
            visible='legendonly',
            mode='lines',
            line=dict(width=2, color=xco2_sw_color, dash='dash'))
        )

    # xCO2 Seawater DRY
    if 'xCO2_SW_dry' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry,
            name='xCO2_SW_dry' + suffix,
            mode='lines',
            line=dict(width=2, color=xco2_sw_color),
            connectgaps=connect_gaps)
        )

    # xCO2 Seawater DRY flagged 3
    if 'xCO2_SW_dry_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry_flagged_3,
            name='xCO2 SW Dry Flag 3' + suffix,
            mode='markers',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # xCO2 Seawater DRY flagged 4
    if 'xCO2_SW_dry_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry_flagged_4,
            name='xCO2 SW Dry Flag 4' + suffix,
            mode='markers',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    # MBL Air data if available
    if isinstance(df_mbl, DataFrame):
        data.append(go.Scatter(
            x=df_mbl.datetime64_ns, y=df_mbl.mbl_xCO2,
            name='MBL xCO2',
            opacity=0.75,
            visible='legendonly',
            mode='lines',
            line=dict(width=2, color=mbl_color),
            connectgaps=connect_gaps)
        )

    # xCO2 Air WET
    if 'xCO2_Air_wet' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_wet,
            name='xCO2_Air_wet' + suffix,
            opacity=0.5,
            visible='legendonly',
            mode='lines',
            line=dict(width=2, color=xco2_air_color, dash='dash'),
            connectgaps=connect_gaps)
        )

    # xCO2 Air DRY
    if 'xCO2_Air_dry' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry,
            name='xCO2_Air_dry' + suffix,
            mode='lines',
            line=dict(width=2, color=xco2_air_color),
            connectgaps=connect_gaps)
        )

    # xCO2 Air DRY flagged 3
    if 'xCO2_Air_dry_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry_flagged_3,
            name='xCO2 Air Dry Flag 3' + suffix,
            mode='markers',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # xCO2 Air DRY flagged 4
    if 'xCO2_Air_dry_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry_flagged_4,
            name='xCO2 Air Dry Flag 4' + suffix,
            mode='markers',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    # MAPCO2 sea surface temperature (from final data)
    if 'SST' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST,
            name='SST' + suffix,
            yaxis='y2',
            mode='lines',
            line=dict(width=2, color=sst_color),
            connectgaps=connect_gaps)
        )

    # Oxygen Optode internal temperature (from sbe16)
    if 'SST_sso2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_sso2,
            name='SST SSO2' + suffix,
            yaxis='y2',
            mode='lines',
            line=dict(width=2, color=sst_sso2_color),
            connectgaps=connect_gaps)
        )

    # MAPCO2 sea surface temperature (from sbe16)
    if 'SST_mapco2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_mapco2,
            name='SST MAPCO2' + suffix,
            yaxis='y2',
            mode='lines',
            line=dict(width=2, color=sst_mapco2_color),
            connectgaps=connect_gaps)
        )

    # pH sea surface temperature
    if 'SST_ph' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_ph,
            name='SST pH' + suffix,
            yaxis='y2',
            mode='lines',
            line=dict(width=2, color=sst_ph_color),
            connectgaps=connect_gaps)
        )

    # MAPCO2 and partner sea surface temperature
    if 'SST_merged' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_merged,
            name='SST MAPCO2 & Partner' + suffix,
            yaxis='y2',
            mode='lines',
            line=dict(width=2, color=sst_partner_color),
            connectgaps=connect_gaps)
        )

    # sea surface pH INITIAL
    if 'pH' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH,
            name='pH' + suffix,
            yaxis='y6',
            mode='lines',
            line=dict(width=2, color=ph_color),
            connectgaps=connect_gaps)
        )

    # sea surface pH FINAL
    if 'pH_final' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_final,
            name='pH Final' + suffix,
            yaxis='y6',
            mode='lines',
            line=dict(width=2, color=ph_color),
            connectgaps=connect_gaps)
        )

    # sea surface Total Alkalininty pH
    if 'TApH' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.TApH,
            name='TApH' + suffix,
            yaxis='y6',
            mode='lines',
            line=dict(width=2, color=ph_ta_color),
            connectgaps=connect_gaps)
        )

    # sea surface pH flagged 3
    if 'pH_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_flagged_3,
            name='pH Flag 3' + suffix,
            yaxis='y6',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # sea surface pH flagged 4
    if 'pH_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_flagged_4,
            name='pH Flag 4' + suffix,
            yaxis='y6',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    # sea surface salinity from MAPCO2 SBE16
    if 'SSS' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS,
            name='SSS' + suffix,
            yaxis='y3',
            mode='markers+lines',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    # sea surface salinity from MAPCO2 SBE16
    if 'SSS_mapco2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_mapco2,
            name='SSS MAPCO2 SBE16' + suffix,
            yaxis='y3',
            mode='markers+lines',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    # sea surface salinity from Partner
    if 'SSS_partner' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_partner,
            name='SSS Partner' + suffix,
            yaxis='y3',
            mode='markers+lines',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    # sea surface salinity from MAPCO2 and Partner merged
    if 'SSS_merged' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_merged,
            name='SSS MAPCO2 & Partner Merged' + suffix,
            yaxis='y3',
            mode='markers+lines',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    # sea surface O2 from MAPCO2 SBE16
    if 'SSO2_uM' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSO2_uM,
            name='SSO2 MAPCO2 SBE16' + suffix,
            yaxis='y3',
            mode='markers+lines',
            line=dict(width=2, color=sso2_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    if 'delta_aepon_press' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.delta_aepon_press,
            name='ABS(diff) Air EQ Pump On Pressure (kPa)' + suffix,
            yaxis='y4',
            mode='lines',
            line=dict(width=2, color=apon_press_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    if 'epon_press' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.epon_press,
            name='Equilibrator Pump On Pressure (kPa)' + suffix,
            yaxis='y4',
            mode='lines',
            line=dict(width=2, color=epon_press_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    if 'apon_press' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.apon_press,
            name='Air Pump On Pressure (kPa)' + suffix,
            yaxis='y4',
            mode='markers+lines',
            line=dict(width=2, color=apon_press_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    if 'precip' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.precip,
            name='Precipitation' + suffix,
            yaxis='y7',
            mode='markers+lines',
            line=dict(width=2, color=precip_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    if 'windspeed' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.windspeed,
            name='Wind Speed MAG (m/s)' + suffix,
            yaxis='y7',
            mode='markers+lines',
            line=dict(width=2, color=precip_color),
            marker=dict(size=4),
            connectgaps=connect_gaps)
        )

    return data


def ph_data(df):
    df_columns = list(df.columns)

    data = []
    x = df.datetime64_ns

    # sea surface pH INITIAL
    if 'pH' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH,
            name='pH Initial',
            yaxis='y6',
            line=dict(width=2, color=ph_color))
        )

    # sea surface pH INITIAL
    if 'ph_int' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.ph_int,
            name='pH Internal',
            yaxis='y6',
            line=dict(width=2, color=ph_int_color))
        )

    # sea surface pH INITIAL
    if 'ph_ext' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.ph_ext,
            name='pH External',
            yaxis='y6',
            line=dict(width=2, color=ph_ext_color))
        )

    # sea surface pH FINAL
    if 'pH_final' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_final,
            name='pH Final',
            yaxis='y6',
            line=dict(width=2, color=ph_color))
        )

    # sea surface pH flagged 3
    if 'pH_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_flagged_3,
            name='pH Flag 3',
            yaxis='y6',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # sea surface pH flagged 4
    if 'pH_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH_flagged_4,
            name='pH Flag 4',
            yaxis='y6',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    return data


def my_data(df):
    """Define data dictionary to plot multiyear data

    Note: hardcoded trace name srings must match dataframe column
        names to be included in data output

    Parameters
    ----------
    df : Pandas DataFrame with columns:
        xx

    Returns
    -------
    Plot.ly data dictionary
    """

    day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my = plot.pivot_year(df)

    data_multi = []

    # Seawater xCO2 Dry
    for y in xco2_sw_my:
        _x = day_my[y].values
        _y = xco2_sw_my[y].values
        keep = notnull(_y)
        data_multi.append(go.Scatter(
            x=_x[keep], y=_y[keep],
            name=str(y) + ' xCO2_SW_dry',
            yaxis='y',
            mode='line',
            line=dict(width=2, color=xco2_sw_color))
        )

    # Air xCO2 Dry
    for y in xco2_air_my:
        _x = day_my[y].values
        _y = xco2_air_my[y].values
        keep = notnull(_y)
        data_multi.append(go.Scatter(
            x=_x[keep], y=_y[keep],
            name=str(y) + ' xCO2_Air_dry',
            yaxis='y',
            mode='line',
            line=dict(width=2, color=xco2_air_color))
        )

    # Sea Surface pH
    if ph_my is not None:
        for y in ph_my:
            _x = day_my[y].values
            _y = ph_my[y].values
            keep = notnull(_y)
            data_multi.append(go.Scatter(
                x=_x[keep], y=_y[keep],
                name=str(y) + ' pH',
                yaxis='y6',
                mode='line',
                # visible='legendonly',
                line=dict(width=2, color=ph_color))
            )

    # Sea Surface Temperature
    for y in sst_my:
        _x = day_my[y].values
        _y = sst_my[y].values
        keep = notnull(_y)
        data_multi.append(go.Scatter(
            x=_x[keep], y=_y[keep],
            name=str(y) + ' SST',
            yaxis='y2',
            visible='legendonly',
            mode='line',
            line=dict(width=2, color=sst_color))
        )

    # Sea Surface Salinity
    for y in sss_my:
        _x = day_my[y].values
        _y = sss_my[y].values
        keep = notnull(_y)
        data_multi.append(go.Scatter(
            x=_x[keep], y=_y[keep],
            name=str(y) + ' SSS',
            yaxis='y3',
            visible='legendonly',
            mode='line',
            line=dict(width=2, color=sss_color))
        )

    return data_multi


def ms_data(df_co2):
    """Define data dictionary to plot multi-system data

    Note: hardcoded trace name srings must match dataframe column
        names to be included in data output

    Note2: this is a copy of my_data(), one method might be good to unify

    Parameters
    ----------
    df_co2 : list of Pandas DataFrame with columns:
        0 : str, system number
        1 : str, co2 test cycle
        2 : Pandas DataFrame of data for system and cycle

    Returns
    -------
    Plot.ly data list
    """

    data = []
    for system in df_co2.system.unique():
        for cycle in df_co2.cycle.unique():
            key = system + '_' + cycle
            _df = df_co2[(df_co2.system == system) & (df_co2.cycle == cycle)].copy()
            _df.sort_values(by='datetime64_ns', inplace=True)
            _df.reset_index(inplace=True, drop=True)
            data.append((system, cycle, _df))

    # create a dict system: number for color maps
    systems = list(set([d[0] for d in data]))
    systems.sort()
    sysc = {v: k for k, v in dict(enumerate(systems)).items()}

    data_multi = []

    for d in data:

        # EPON
        if d[1] == 'epon':
            _d = d[2]
            _x = _d.datetime64_ns
            _y = _d.xCO2.values
            data_multi.append(go.Scatter(
                x=_x, y=_y,
                name=d[0] + ' ' + d[1] + ' ' + 'xCO2',
                yaxis='y',
                visible='legendonly',
                mode='line',
                line=dict(width=2, color=xco2_sw_color))
            )

        # EPOF
        if d[1] == 'epof':
            _d = d[2]
            _x = _d.datetime64_ns
            _y = _d.xCO2.values
            data_multi.append(go.Scatter(
                x=_x, y=_y,
                name=d[0] + ' ' + d[1] + ' ' + 'xCO2_wet',
                yaxis='y',
                visible='legendonly',
                mode='lines+markers',
                line=dict(width=2, color=xco2_sw_color))
            )

        # EPOF
        if d[1] == 'epof':
            try:
                _d = d[2]
                _x = _d.datetime64_ns
                _y = _d.xCO2_dry.values
                data_multi.append(go.Scatter(
                    x=_x, y=_y,
                    name=d[0] + ' ' + d[1] + ' ' + 'xCO2_dry',
                    yaxis='y',
                    # visible='legendonly',
                    mode='lines+markers',
                    line=dict(width=2, color=xco2_sw_color))
                )
            except AttributeError:
                # no dry data in this DataFrame
                pass

        # APON
        if d[1] == 'apon':
            _d = d[2]
            _x = _d.datetime64_ns
            _y = _d.xCO2.values
            data_multi.append(go.Scatter(
                x=_x, y=_y,
                name=d[0] + ' ' + d[1] + ' ' + 'xCO2',
                yaxis='y',
                visible='legendonly',
                mode='line',
                line=dict(width=2, color=xco2_air_color))
            )

        # APOF
        if d[1] == 'apof':
            _d = d[2]
            _x = _d.datetime64_ns
            _y = _d.xCO2.values
            #keep = notnull(_y)
            data_multi.append(go.Scatter(
                #x=_x[keep], y=_y[keep],
                x=_x, y=_y,
                name=d[0] + ' ' + d[1] + ' ' + 'xCO2_wet',
                yaxis='y',
                visible='legendonly',
                mode='lines+markers',
                line=dict(width=2, color=xco2_air_color))
            )

        # APOF
        if d[1] == 'apof':
            try:
                _d = d[2]
                _x = _d.datetime64_ns
                _y = _d.xCO2_dry.values
                #keep = notnull(_y)
                data_multi.append(go.Scatter(
                    #x=_x[keep], y=_y[keep],
                    x=_x, y=_y,
                    name=d[0] + ' ' + d[1] + ' ' + 'xCO2_dry',
                    yaxis='y',
                    # visible='legendonly',
                    mode='lines+markers',
                    line=dict(width=2, color=xco2_air_color))
                )
            except AttributeError:
                # no dry data in this DataFrame
                pass

        """
        # Air xCO2 Dry
        for y in xco2_air_my:
            _x = day_my[y].values
            _y = xco2_air_my[y].values
            keep = notnull(_y)
            data_multi.append(go.Scatter(
                x=_x[keep], y=_y[keep],
                name=str(y) + ' xCO2_Air_dry',
                yaxis='y',
                mode='line',
                line=dict(width=2, color=xco2_air_color))
            )

        # Sea Surface pH
        for y in ph_my:
            _x = day_my[y].values
            _y = ph_my[y].values
            keep = notnull(_y)
            data_multi.append(go.Scatter(
                x=_x[keep], y=_y[keep],
                name=str(y) + ' pH',
                yaxis='y6',
                mode='line',
                # visible='legendonly',
                line=dict(width=2, color=ph_color))
            )

        # Sea Surface Temperature
        for y in sst_my:
            _x = day_my[y].values
            _y = sst_my[y].values
            keep = notnull(_y)
            data_multi.append(go.Scatter(
                x=_x[keep], y=_y[keep],
                name=str(y) + ' SST',
                yaxis='y2',
                visible='legendonly',
                mode='line',
                line=dict(width=2, color=sst_color))
            )

        # Sea Surface Salinity
        for y in sss_my:
            _x = day_my[y].values
            _y = sss_my[y].values
            keep = notnull(_y)
            data_multi.append(go.Scatter(
                x=_x[keep], y=_y[keep],
                name=str(y) + ' SSS',
                yaxis='y3',
                visible='legendonly',
                mode='line',
                line=dict(width=2, color=sss_color))
            )
        """
    return data_multi

