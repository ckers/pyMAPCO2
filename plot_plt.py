# -*- coding: utf-8 -*-
"""
Plot CO2 data using Matplotlib
Created on Thu Sep 22 13:58:48 2016
@author: Colin Dietrich
"""

import numpy as np

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as mtick

from . import config, plot
from .utils import utils


def timeseries_multiyear(df, df_mbl=None):
    """Plot data in multiyear and timeseries plots

    Parameters
    ----------
    df : Pandas DataFrame containing xco2, sstc, ph data
    mbl : Pandas DataFrame containing mbl air xco2 values

    Returns
    -------
    matplotlib plots to current artist
    """

    if df_mbl is not None:
        df_mbl = df_mbl[(df_mbl.datetime64_ns >= df.datetime64_ns.min()) &
              (df_mbl.datetime64_ns <= df.datetime64_ns.max())]

    plt.plot(df.day)
    plt.ylabel('Day of Year')
    plt.xlabel('DataFrame Index')
    plt.title('DataFrame Day of Year Check', loc='right')
    plt.show()

    day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my = plot.pivot_year(df)

    # pivoted years, for data checking
    a = []
    for x in [day_my, xco2_air_my, xco2_sw_my, sst_my, sss_my, ph_my]:
        for y in x:
            a.append(y)

    plt.plot(a)
    plt.ylabel('Year')
    plt.xlabel('Pivoted Columns')
    plt.title('Pivot Year Check', loc='right')
    plt.show()

    for y in xco2_air_my:
        plt.plot(xco2_air_my[y],
                 label='Air ' + str(y))  #,
                 #color=plot.xco2_air_pdict[y])

    if df_mbl is not None:
        plt.plot(df_mbl.datetime64_ns, df_mbl.xCO2, color='black', label='MBL')

    plt.legend()
    plt.title('xCO2 Air Multiyear', loc='right')
    plt.show()

    for y in xco2_air_my:
        _x = day_my[y]
        _y = xco2_air_my[y]
        notnull = _y.notnull()
        plt.plot(_x[notnull],
                 _y[notnull],
                 label='Air ' + str(y))  #,
                 #color=plot.xco2_air_pdict[y])
    plt.legend()
    plt.ylabel('CO2 ppm')
    plt.xlabel('Day of Year')
    plt.title('xCO2 Air Multiyear', loc='right')
    plt.show()

    for y in xco2_sw_my:
        plt.plot(xco2_sw_my[y],
                 label='SW ' + str(y),
                 color=plot.xco2_sw_pdict[y])
    plt.legend()
    plt.title('xCO2 Seawater Multiyear', loc='right')
    plt.show()

    for y in xco2_sw_my:
        _x = day_my[y]
        _y = xco2_sw_my[y]
        notnull = _y.notnull()
        plt.plot(_x[notnull],
                 _y[notnull],
                 label='Air ' + str(y),
                 color=plot.xco2_sw_pdict[y])
    plt.legend()
    plt.ylabel('CO2 ppm')
    plt.xlabel('Day of Year')
    plt.title('xCO2 Air Multiyear', loc='right')
    plt.show()

    if ph_my.notnull().sum().sum() > 0:
        for y in ph_my:
            plt.plot(ph_my[y],
                     label='pH ' + str(y),
                     color=plot.ph_pdict[y])
        plt.legend()
        plt.ylabel('pH')
        plt.xlabel('Day of Year')
        plt.title('pH Multiyear', loc='right')
        plt.show()
    else:
        print('No pH timeseries data to plot')

    if ph_my.notnull().sum().sum() > 0:

        for y in ph_my:
            _x = day_my[y]
            _y = ph_my[y]
            notnull = _y.notnull()
            plt.plot(_x[notnull],
                     _y[notnull],
                     label='pH ' + str(y),
                     color=plot.ph_pdict[y])
        plt.legend()
        plt.ylabel('pH')
        plt.xlabel('Day of Year')
        plt.title('pH Multiyear', loc='right')
        plt.show()
    else:
        print('No pH multiyear data to plot')


def plot_annual(co2, mbl, markers='.', lines='-', gtd=[]):
    #        fig_title = ('Combined MAPCO2 Data')

    if not markers:
        markers = 'None'

    if not lines:
        lines = 'None'

    mbl = mbl[(mbl.datetime <= co2.datetime.max()) & (mbl.datetime >= co2.datetime.min())]

    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(right=0.75)
    plt.subplots_adjust(bottom=0.2)

    par1 = host.twinx()
    par2 = host.twinx()
    par3 = host.twinx()
    par4 = host.twinx()
    par5 = host.twinx()

    offset = 80

    new_fixed_axis = host.get_grid_helper().new_fixed_axis

    par2.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par2,
                                        offset=(offset, 0))

    par2.axis['right'].toggle(all=True)

    par3.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par3,
                                        offset=(offset * 2, 0))
    par3.axis['right'].toggle(all=True)

    par4.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par4,
                                        offset=(offset * 3, 0))
    par4.axis['right'].toggle(all=True)

    par5.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par5,
                                        offset=(offset * 4, 0))
    par5.axis['right'].toggle(all=True)

    host.set_xlabel('DateTime')
    host.set_ylabel('Seawater xCO2 (ppm)')
    par1.set_ylabel('Air xCO2 (ppm)')
    par2.set_ylabel('O2_percent')
    par3.set_ylabel('SSS')
    par4.set_ylabel('SST & Licor T (C)')
    par5.set_ylabel('Licor ATM Pressure (mbar)')

    host.set_navigate(True)

    par1.set_navigate(True)
    par2.set_navigate(True)
    par3.set_navigate(True)
    par4.set_navigate(True)
    par5.set_navigate(True)

    #        par1.set_ylabel('Pressure (kPa)')  # GTD data
    #        par4.set_ylabel('Pressure Diff (kPa)')
    #        par3.set_ylabel('SBE16 battery voltage (VDC)')
    #        par5.set_ylabel('SBE16 battery current (mA)')

    # order puts one object on top the next


    co2ms = 7
    ms = 7

    columns = ['Licor_Atm_Pressure',
               'xCO2_SW_dry',
               'xCO2_Air_dry',
               'mbl',
               'Percent_O2',
               'SSS',
               'SST',
               'Licor_Temp',
               'Licor_Atm_Pressure']

    co2p = co2.pivot("day", "year")
    mblp = mbl.pivot('day', 'year')

    c = 'blue'  # Dry Seawater CO2
    sw = co2p['xCO2_SW_dry']
    g = 0
    for n in sw.columns:
        p1, = host.plot(sw.index, sw[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=co2ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')
        g += 1

    p1, = host.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=co2ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='Seawater dry xCO2')

    c = 'cyan'  # DRY air CO2
    air = co2p['xCO2_Air_dry']
    g = 0
    for n in air.columns:
        #            print(n)
        #            print('_a' in str(n))
        if '_a' in str(n):
            c = '#00CCCC'
        p2, = par1.plot(air.index, air[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=co2ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')

        g += 1
    p2, = par1.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=co2ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='Air dry xCO2')

    c = 'black'  # Licor Pressure
    lp = co2p['Licor_Atm_Pressure']
    g = 0
    for n in lp.columns:
        p7, = par5.plot(lp.index, lp[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        alpha=0.4, label='_nolegend_')  # ,
        #                            label='Licor Pressure ' + str(n))
        g += 1
    p7, = par5.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=ms,
                    markerfacecolor=c, markeredgecolor=c,
                    alpha=0.4, label='Licor Pressure')

    c = 'green'  # O2 percentage
    o2 = co2p['Percent_O2']
    g = 0
    for n in o2.columns:
        p3, = par2.plot(o2.index, o2[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')

        g += 1

    p3, = par2.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='Oxygen Percent')

    c = 'red'  # SSS
    sss = co2p['SSS']
    g = 0
    for n in sss.columns:
        p4, = par3.plot(sss.index, sss[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')
        g += 1

    p4, = par3.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='SSS')

    c = 'orange'  # SST
    sst = co2p['SST']
    g = 0
    for n in sst.columns:
        p5, = par4.plot(sst.index, sst[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')
        g += 1

    p5, = par4.plot(sst.index, sst[n],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='SST')

    c = 'purple'  # Licor Temp
    litemp = co2p['Licor_Temp']
    g = 0
    for n in litemp.columns:
        p6, = par4.plot(litemp.index, litemp[n],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='_nolegend_')  # ,
        g += 1

    p6, = par4.plot([], [],
                    color=c,
                    linestyle=lines,
                    marker='s', markersize=ms,
                    markerfacecolor=c, markeredgecolor=c,
                    label='Licor Temp')

    # labels
    c = "black"
    g = 0
    for n in lp.columns:
        p8, = par5.plot([], [],
                        color=c,
                        linestyle=lines,
                        marker=config.mpl_obvious_markers[g], markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        alpha=1.0,
                        label=str(n))
        g += 1

    # CO2 seawater
    y1, y2 = host.get_ylim()
    host.set_ylim((plot.lim_finder(co2.xCO2_SW_dry, data_type="xco2_sw")[0], 1000))

    # CO2 air
    y1, y2 = par1.get_ylim()
    limits = plot.lim_finder(co2.xCO2_Air_dry, data_type="xco2_air")
    par1.set_ylim(limits[0], 500)

    # O2 limit
    y1, y2 = par2.get_ylim()
    par2.set_ylim((plot.lim_finder(co2.Percent_O2, data_type="o2_percent")[0], y2))

    # SSS
    y1, y2 = par3.get_ylim()
    limits = (plot.lim_finder(co2.SSS, data_type="sss"))
    par3.set_ylim(limits[0], limits[1])

    # SST / Licor Temperature
    y1, y2 = par4.get_ylim()
    y_data = np.concatenate([co2.SST, co2.Licor_Temp])
    limits = (plot.lim_finder(y_data, data_type="sst"))
    par4.set_ylim(limits[0], limits[1])

    # Licor Pressure / GTD Pressure
    y1, y2 = par5.get_ylim()
    y_data = np.concatenate([co2.Licor_Atm_Pressure, gtd])
    limits = (plot.lim_finder(y_data, data_type="atm_press"))
    #        par5.set_ylim(limits[0], limits[1])

    if mbl is not None:
        c = 'black'  # MBL Air CO2
        mblplot = mblp['xCO2']
        g = 0
        for n in mblplot.columns:
            p8, = par1.plot(mblplot.index, mblplot[n],
                            color=c,
                            linestyle='-',
                            marker=config.mpl_obvious_markers[g], markersize=5,
                            markerfacecolor='None', markeredgecolor=c, label='_nolegend_')
            g += 1

    host.axis["left"].label.set_color(p1.get_color())
    par1.axis["right"].label.set_color(p2.get_color())
    par2.axis["right"].label.set_color(p3.get_color())
    par3.axis["right"].label.set_color(p4.get_color())
    par4.axis["right"].label.set_color(p5.get_color())
    par5.axis["right"].label.set_color(p7.get_color())

    #        par1 = host.twiny()
    #        par2 = host.twiny()
    #        par3 = host.twiny()
    #        par4 = host.twiny()
    #        par5 = host.twiny()

    #        host.legend(loc=2)
    plt.legend(bbox_to_anchor=(0.5, -0.1), loc=9, ncol=4)
    plt.show()


def plot_combined(co2, mbl, markers='.', lines='-'):
    """Plot multiple timeseries on stacked twinx axis
    data columns must be present

    Parameters
    ----------
    co2 :
    mbl :
    markers :
    lines :

    Returns
    -------

    """

    if markers == False:
        markers = 'None'

    if lines == False:
        lines = 'None'

    mbl = mbl[(mbl.datetime <= co2.datetime.max()) & (mbl.datetime >= co2.datetime.min())]

    host = host_subplot(111, axes_class=AA.Axes)
    plt.subplots_adjust(right=0.75)

    par1 = host.twinx()
    par2 = host.twinx()
    par3 = host.twinx()
    par4 = host.twinx()
    par5 = host.twinx()

    offset = 80

    new_fixed_axis = host.get_grid_helper().new_fixed_axis

    par2.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par2,
                                        offset=(offset, 0))

    par2.axis['right'].toggle(all=True)

    par3.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par3,
                                        offset=(offset * 2, 0))
    par3.axis['right'].toggle(all=True)

    par4.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par4,
                                        offset=(offset * 3, 0))
    par4.axis['right'].toggle(all=True)

    par5.axis['right'] = new_fixed_axis(loc='right',
                                        axes=par5,
                                        offset=(offset * 4, 0))
    par5.axis['right'].toggle(all=True)

    host.set_xlabel('DateTime')
    host.set_ylabel('Seawater xCO2 (ppm)')
    par1.set_ylabel('Air xCO2 (ppm)')
    par2.set_ylabel('O2_percent')
    par3.set_ylabel('SSS')
    par4.set_ylabel('SST & Licor T (C)')
    par5.set_ylabel('Licor ATM Pressure (mbar)')

    host.set_navigate(True)

    #        par1.set_ylabel('Pressure (kPa)')  # GTD data
    #        par4.set_ylabel('Pressure Diff (kPa)')
    #        par3.set_ylabel('SBE16 battery voltage (VDC)')
    #        par5.set_ylabel('SBE16 battery current (mA)')

    # order puts one object on top the next

    ms = 10

    c = 'black'  # Licor Pressure
    p7, = par5.plot(co2.datetime, co2.Licor_Atm_Pressure,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=ms,
                    markerfacecolor='None', markeredgecolor=c,
                    alpha=0.4,
                    label='Licor Pressure')

    c = 'blue'  # Dry Seawater CO2
    co2_sw = co2[co2.xCO2_SW_QF != 4]
    p1, = host.plot(co2_sw.datetime, co2_sw.xCO2_SW_dry,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=5,
                    markerfacecolor='None', markeredgecolor=c,
                    label='Seawater dry xCO2', )

    c = 'cyan'  # DRY air CO2
    co2_air = co2[co2.xCO2_Air_QF != 4]
    p2, = par1.plot(co2_air.datetime, co2_air.xCO2_Air_dry,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=5,
                    markerfacecolor='None', markeredgecolor=c,
                    label='Air dry xCO2')

    if mbl is not None:
        c = 'black'  # MBL Air CO2
        p8, = par1.plot(mbl.datetime, mbl.xCO2,
                        color=c,
                        linestyle=lines,
                        marker=markers, markersize=5,
                        markerfacecolor='None', markeredgecolor=c,
                        label='MBL CO2')

    c = 'green'  # O2 percentage
    p3, = par2.plot(co2.datetime, co2.Percent_O2,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=ms,
                    markerfacecolor='None', markeredgecolor=c,
                    label='Oxygen Percent')

    c = 'red'  # SSS
    p4, = par3.plot(co2.datetime, co2.SSS,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=ms,
                    markerfacecolor='None', markeredgecolor=c,
                    label='SSS')

    c = 'orange'  # SST
    p5, = par4.plot(co2.datetime, co2.SST,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=ms,
                    markerfacecolor='None', markeredgecolor=c,
                    label='SST')

    c = 'purple'  # Licor Temp
    p6, = par4.plot(co2.datetime, co2.Licor_Temp,
                    color=c,
                    linestyle=lines,
                    marker=markers, markersize=ms,
                    markerfacecolor='None', markeredgecolor=c,
                    label='Licor Temp')
    """
    # CO2 seawater
    y1,y2 = host.get_ylim()
    host.set_ylim((plot.lim_finder(co2.xCO2_SW_dry, data_type="xco2_sw")[0],y2))

    # CO2 air
    y1,y2 = par1.get_ylim()
    limits = plot.lim_finder(co2.xCO2_Air_dry, data_type="xco2_air")

    par1.set_ylim((limits[0],limits[1]))

    # O2 limit
    y1,y2 = par2.get_ylim()
    par2.set_ylim((plot.lim_finder(co2.Percent_O2, data_type="o2_percent")[0],y2))

    # SSS
    y1,y2 = par3.get_ylim()
    limits = (plot.lim_finder(co2.SSS, data_type="sss"))
    par3.set_ylim(limits[0],limits[1])

    # SST / Licor Temperature
    y1,y2 = par4.get_ylim()
    y_data = np.concatenate([co2.SST, co2.Licor_Temp])
    limits = (plot.lim_finder(y_data, data_type="temp"))
    par4.set_ylim(limits[0], limits[1])

    # Licor Pressure / GTD Pressure
    y1,y2 = par5.get_ylim()
    y_data = np.concatenate([co2.Licor_Atm_Pressure, gtd])
    limits = (plot.lim_finder(y_data, data_type="atm_press"))
    par5.set_ylim(limits[0], limits[1])
    """

    host.axis["left"].label.set_color(p1.get_color())
    par1.axis["right"].label.set_color(p2.get_color())
    par2.axis["right"].label.set_color(p3.get_color())
    par3.axis["right"].label.set_color(p4.get_color())
    par4.axis["right"].label.set_color(p5.get_color())
    par5.axis["right"].label.set_color(p7.get_color())

    par1.set_navigate(True)
    par2.set_navigate(True)
    par3.set_navigate(True)
    par4.set_navigate(True)
    par5.set_navigate(True)

    host.legend(loc=2)

    plt.show()


def show(title=None, legend=True, xformat=False, yformat=False):
    """Format timeseries plots nicely for Jupyter

    Parameters
    ----------
    #array : array-like, each item containing parameters to pass to
    #    matplotlib.pyplot.plot method
    title : str, optional title text
    xformat : str, formatter string for number display
    yformat : str, formatter string for number display

    Returns
    -------
    None, directly displays
    """

    ax = plt.gca()

    if legend:

        # Shrink current axis by 20%
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        # add legend
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    if title is not None:
        plt.title(title, loc='right')

    if xformat:
        ax.xaxis.set_major_formatter(FormatStrFormatter(xformat))

    if yformat:
        ax.yaxis.set_major_formatter(FormatStrFormatter(xformat))


    plt.margins(0.05, 0.1)
    plt.xticks(rotation='vertical')
    plt.show()


def scatter_cm(x, y, c, cmap='hot'):
    """Scatter colormap template
    Call with plot_plt.show for extra formatting
    """

    fig, ax = plt.subplots(1,1)
    sc = ax.scatter(x=x, y=y, c=c, cmap=cmap,
                    edgecolor='face', alpha=0.5)
    plt.colorbar(sc)


def plot_dtstd(df, dt_data, cols=None):
    """Plot the std deviation of differentiated data

    Parameters
    ----------
    df : Pandas DataFrame, with columns:
        datetime64_ns
        (timeseries name)
    dt_data : str, name of column with differentiated timeseries data
    cols : list of str, columns of data to plot

    Returns
    -------
    None, plots to notebook or popout
    """

    plt.plot(df.datetime64_ns, df[dt_data], zorder=1)
    if cols is None:
        cols = [n for n in df.columns if dt_data in n]
    colors = utils.color_generator(len(cols))
    markers = [n for n in utils.flatten([utils.mpl_markers_obvious] * 5)][0:len(cols)]
    c = 0
    for n in cols:
        if 'dtf' in n:
            print(n)
            _df_plot = df[df[n] == True]
            plt.scatter(_df_plot.datetime64_ns.values, _df_plot[dt_data],
                        color=colors[c], marker=markers[c], s=20, label=n, zorder=c+2)
            c += 1


def plot_gps(df, gps_fit=None, center=None, title_str='', xlim=None, ylim=None):
    """Plot GPS data
    Note: Seaborn with reformat and break this plot

    Parameters
    ----------
    df : Pandas Dataframe, with 'lon', 'lat' and 'flag' columns
    gps_fit : tuple of array-like, x and y values of fit circle
    center : 2 length array of float, x and y values of center
    """

    plt.scatter(df.lon, df.lat,
                color='black', marker='x', label='GPS Data')

    if 'flag' in df:
        gps4 = df[(df.flag >= 4.0) & (df.flag < 5.0)]

        plt.plot(gps4.lon, gps4.lat,
                 color='red', marker='s', alpha=0.3, linestyle='', label='GPS Data 4')

    if gps_fit is not None:
        x_fit, y_fit = gps_fit
        plt.plot(x_fit, y_fit,
                 color='orange', marker='None', label='LSQ Fit Circle', lw=2)

    if center is not None:
        xc, yc = center
        plt.plot(xc, yc,
                 color='green', marker='o', label='LSQ Fit Center')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.axis('equal')

    ax = plt.gca()
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))
    ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    if xlim is not None:
        plt.xlim(xlim)
    if ylim is not None:
        plt.ylim(ylim)

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title_str, loc='right')
    plt.margins(0.05, 0.1)

    plt.show()


def plot_co2(df, width=12, height=6, style=None, **kwargs):
    """Plot co2 data using the .plot method

    Call with: plot_co2[['x', 'y']] to only plot x and y columns

    Parameters
    ----------
    df : Pandas Dataframe, all columns will be plotted
    width : float, width in inches of plot
    height : float, height in inches of plot
    style : array-like, plot styles for each column
    """

    ax = df.plot(**kwargs, figsize=(width, height), style=style)

    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.title('CO2 Response', loc='right')
    plt.margins(0.05, 0.1)
    plt.show()
    return ax


def plot_pressures(df, width=12, height=6, title=None, style=None):
    # df.plot(figsize=(width, height), style=style)
    # ax = plt.gca()
    # ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    #
    # # Put a legend to the right of the current axis
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # if title=None:
    # plt.title('Pressures (kPa)', loc='right')
    # plt.margins(0.05, 0.1)
    # plt.show()
    ax = df_plot(df, width=width, height=height, title='Pressures (kPa)', style=style)
    return ax


def df_plot(df, width=12, height=6, title=None, style=None, **kwargs):
    df.plot(figsize=(width, height), style=style, **kwargs)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(title, loc='right')
    plt.margins(0.05, 0.1)
    plt.show()
    return ax


def reformat(title=None, width=12, height=6, ):
    fig = plt.gcf()
    fig.set_size_inches(width, height)

    lines_all = []
    for ax in fig.get_axes():
        ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%3.2f'))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        lines = ax.lines
        for line in lines:
            lines_all.append(line)
    labels_all = [l.get_label() for l in lines_all]
    # Put a legend to the right of the current axis
    plt.legend(lines_all, labels_all, loc='center left', bbox_to_anchor=(1.1, 0.5))
    if title:
        plt.title(title, loc='right')
    plt.margins(0.05, 0.1)
