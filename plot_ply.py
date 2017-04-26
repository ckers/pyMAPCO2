# -*- coding: utf-8 -*-
"""
Plot CO2 data using Plot.ly
Created on 2017-04-25
@author: Colin Dietrich
"""

from pandas import notnull

import plotly.offline as ply
import plotly.graph_objs as go

from . import plot

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
mbl_color = 'black'


def default_layout(xco2_range,
                   sst_range,
                   ph_range,
                   sso2_range,
                   title=None,
                   ):
    """Plot.ly default layout for xCO2, SST, SSS, pH

    Parameters
    ----------
    xco2_range : array-like, two values - kmin & kmax
    sst_range : array-like, two values - kmin & kmax
    sso2_range : array-like, two values - kmin & kmax
    ph_range : array-like, two values - kmin & kmax
    title : str, name of plot

    Returns
    -------
    Plot.ly layout
    """

    _title = 'MAPCO2 pCO2 pH SSTC'
    if title is None:
        title = _title
    else:
        title = _title + ': ' + title

    layout = go.Layout(
        title='MAPCO2 SSTC pH Data for ' + title,
        xaxis=dict(title='Date Time', domain=[0.0, 0.86]),
        yaxis=dict(title='MAPCO2 xCO2 (umol/mol)', range=xco2_range),
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
            position=0.89
        ),

        yaxis4=dict(
            title='Pressure (kPa)',
            titlefont=dict(color=ntu_color),
            tickfont=dict(color=ntu_color),
            overlaying='y',
            side='right',
            position=0.91
        ),
        yaxis5=dict(
            title='SSO2 (μM)',
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
            title='NTU (NTU) & CHL (μM)',
            titlefont=dict(color=ph_color),
            tickfont=dict(color=ph_color),
            overlaying='y',
            side='right',
            position=1.0

        )
    )

    return layout


def default_data(df, df_mbl=None):
    """Define data dictionary to plot

    Note: hardcoded trace name srings must match dataframe column
        names to be included in data output

    Parameters
    ----------
    df : Pandas DataFrame with columns of mapco2 data
    mbl : Pandas DataFrame containing mbl air xco2 values

    Returns
    -------
    Plot.ly data dictionary
    """

    df_columns = list(df.columns)

    data = []
    x = df.datetime64_ns

    # xCO2 Seawater WET
    if 'xCO2_SW_wet' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_wet,
            name='xCO2_SW_wet',
            opacity=0.5,
            line=dict(width=2, color=xco2_sw_color, dash='dash'))
        )

    # xCO2 Seawater DRY
    if 'xCO2_SW_dry' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry,
            name='xCO2_SW_dry',
            line=dict(width=2, color=xco2_sw_color))
        )

    # xCO2 Seawater DRY flagged 3
    if 'xCO2_SW_dry_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry_flagged_3,
            name='xCO2 SW Dry Flag 3',
            yaxis='y6',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # xCO2 Seawater DRY flagged 4
    if 'xCO2_SW_dry_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_SW_dry_flagged_4,
            name='xCO2 SW Dry Flag 4',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    # MBL Air data if available
    if df_mbl is not None:
        data.append(go.Scatter(
            x=df_mbl.datetime64_ns, y=df_mbl.xCO2,
            name='MBL xCO2',
            opacity=0.75,
            line=dict(width=2, color=mbl_color))
        )

    # xCO2 Air WET
    if 'xCO2_Air_wet' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_wet,
            name='xCO2_Air_wet',
            opacity=0.5,
            line=dict(width=2, color=xco2_air_color, dash='dash'))
        )

    # xCO2 Air DRY
    if 'xCO2_Air_dry' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry,
            name='xCO2_Air_dry',
            line=dict(width=2, color=xco2_air_color))
        )

    # xCO2 Air DRY flagged 3
    if 'xCO2_Air_dry_flagged_3' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry_flagged_3,
            name='xCO2 Air Dry Flag 3',
            marker=dict(size=10, symbol='square-open', color='orange'))
        )

    # xCO2 Air DRY flagged 4
    if 'xCO2_Air_dry_flagged_4' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.xCO2_Air_dry_flagged_4,
            name='xCO2 Air Dry Flag 4',
            marker=dict(size=10, symbol='circle-open', color='red'))
        )

    # MAPCO2 sea surface temperature (from final data)
    if 'SST' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST,
            name='SST Final',
            yaxis='y2',
            line=dict(width=2, color=sst_color))
        )

    # Oxygen Optode internal temperature (from sbe16)
    if 'SST_sso2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_sso2,
            name='SST SSO2',
            yaxis='y2',
            line=dict(width=2, color=sst_sso2_color))
        )

    # MAPCO2 sea surface temperature (from sbe16)
    if 'SST_mapco2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_mapco2,
            name='SST MAPCO2',
            yaxis='y2',
            line=dict(width=2, color=sst_mapco2_color))
        )

    # pH sea surface temperature
    if 'SST_ph' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_ph,
            name="SST pH",
            yaxis='y2',
            line=dict(width=2, color=sst_ph_color))
        )

    # MAPCO2 and partner sea surface temperature
    if 'SST_merged' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SST_merged,
            name='SST MAPCO2 & Partner',
            yaxis='y2',
            line=dict(width=2, color=sst_partner_color))
        )

    # sea surface pH INITIAL
    if 'pH' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.pH,
            name='pH Initial',
            yaxis='y6',
            line=dict(width=2, color=ph_color, dash='dash'))
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

    # sea surface salinity from MAPCO2 SBE16
    if 'SSS' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS,
            name='SSS Final',
            yaxis='y3',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4))
        )

    # sea surface salinity from MAPCO2 SBE16
    if 'SSS_mapco2' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_mapco2,
            name='SSS MAPCO2 SBE16',
            yaxis='y3',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4))
        )

    # sea surface salinity from Partner
    if 'SSS_partner' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_partner,
            name='SSS Partner',
            yaxis='y3',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4))
        )

    # sea surface salinity from MAPCO2 and Partner merged
    if 'SSS_merged' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSS_merged,
            name='SSS MAPCO2 & Partner Merged',
            yaxis='y3',
            line=dict(width=2, color=sss_color),
            marker=dict(size=4))
        )

    # sea surface O2 from MAPCO2 SBE16
    if 'SSO2_uM' in df_columns:
        data.append(go.Scatter(
            x=x, y=df.SSO2_uM,
            name='SSO2 MAPCO2 SBE16',
            yaxis='y3',
            line=dict(width=2, color=sso2_color),
            marker=dict(size=4))
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

    day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my = plot.pivot(df)

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
    for y in ph_my:
        _x = day_my[y].values
        _y = ph_my[y].values
        keep = notnull(_y)
        data_multi.append(go.Scatter(
            x=_x[keep], y=_y[keep],
            name=str(y) + ' pH',
            yaxis='y6',
            mode='line',
            #visible='legendonly',
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
