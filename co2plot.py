# -*- coding: utf-8 -*-
"""
Created on Thu Sep 22 13:58:48 2016

@author: dietrich
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
    

mpl_markers_obvious = ["o",    # circle marker
             "v",    # triangle_down marker
             "^",    # triangle_up marker
             "<",    # triangle_left marker
             ">",    # triangle_right marker
             "s",    # square marker
             "p",    # pentagon marker
             "*",    # star marker
             "h",    # hexagon1 marker
             "H",    # hexagon2 marker
             "D",    # diamond marker
             "d"]#,    # thin_diamond marker
#             "|",    # vline marker
#             "_"]    # hline marker

def day_of_year(date_time):
    """Calculate the decimal days since the begining of the year"""

    day = date_time.dayofyear
    hour = date_time.hour / 24.0
    minute = date_time.minute / 1440.0
    second = date_time.second / 86400.0
    microsecond = date_time.microsecond / 8.64e+10
    nanosecond = date_time.nanosecond / 8.64e+13
    
    day = day + hour + minute + second + microsecond + nanosecond
    return day
    
def year(date_time):
    return date_time.year 
    
def ylim_finder(data, margin=0.1, data_type=None):
    """Set y axis limits to something based on reality
    
    Parameters
    ----------
    data : array-like, values to look for min/max in
    margin : float, factor (1 = 100% etc) to set limit relative to max/min
    data_type : str, identifying code for data to set limits
    
    Returns
    -------
    ymin : float, min value to set axis
    ymax : float, max value to set axis
    """
    
    d = np.array(data)
    
    # put into config
    d_limits = {'xco2_sw': [300, 1200],
                'xco2_air': [380, 500],
                'o2_percent': [85, 100],
                'temp': [-5, 70],
                'sss': [30, 40],
                'atm_press': [45, 130]}
    
    
    d_min = np.min(d)
    d_max = np.max(d)
    d_min = d_min - d_min * margin
    d_max = d_max + d_max * margin    
    
    try:
        limits = d_limits[data_type]
        print(limits)
        print(limits[0])
        print(limits[1])
        print(d_min, d_max)
        return np.max([limits[0], d_min]), np.min([limits[1], d_max])
    except KeyError:
        return d_min, d_max
        
        
def plot_annual(co2, mbl, gtd=[]):
    
#        fig_title = ('Combined MAPCO2 Data')
        
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
                                            offset=(offset*2, 0))
        par3.axis['right'].toggle(all=True)

        par4.axis['right'] = new_fixed_axis(loc='right',
                                            axes=par4,
                                            offset=(offset*3, 0))
        par4.axis['right'].toggle(all=True)

        par5.axis['right'] = new_fixed_axis(loc='right',
                                            axes=par5,
                                            offset=(offset*4, 0))
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
        
        c = 'black'  # Licor Pressure
        lp = co2p['Licor_Atm_Pressure']
        g = 0
        for n in lp.columns:
            
            p7, = par5.plot(lp.index, lp[n],
                            color=c,
                            marker=mpl_markers_obvious[g], markersize=ms,
                            markerfacecolor='None', markeredgecolor=c,
                            alpha=0.4,
                            label='Licor Pressure ' + str(n))
            g += 1
            
        c = 'blue'  # Dry Seawater CO2
        sw = co2p['xCO2_SW_dry']
        g = 0
        for n in sw.columns:
            
            p1, = host.plot(sw.index, sw[n],
                            color=c,
                            linestyle='-',
                            marker=mpl_markers_obvious[g], markersize=co2ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='Seawater dry xCO2 ' + str(n))
            g += 1
            
        c = 'cyan'  # DRY air CO2
        air = co2p['xCO2_Air_dry']
        g = 0
        for n in air.columns:
            p2, = par1.plot(air.index, air[n],
                            color=c,
                            linestyle='-',
                            marker=mpl_markers_obvious[g], markersize=co2ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='Air dry xCO2 ' + str(n))
            g += 1
        

        
        
        c = 'green'  # O2 percentage
        o2 = co2p['Percent_O2']
        g = 0
        for n in o2.columns:
            p3, = par2.plot(o2.index, o2[n],
                            color=c,                        
                            marker=mpl_markers_obvious[g], markersize=ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='Oxygen Percent ' + str(n))
            g += 1

        c = 'red'  # SSS
        sss = co2p['SSS']
        g = 0
        for n in sss.columns:
            p4, = par3.plot(sss.index, sss[n],
                            color=c,                        
                            marker=mpl_markers_obvious[g], markersize=ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='SSS ' + str(n))
            g += 1

        c = 'orange'  # SST
        sst = co2p['SST']
        g = 0
        for n in sst.columns:
            p5, = par4.plot(sst.index, sst[n],
                            color=c,                        
                            marker=mpl_markers_obvious[g], markersize=ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='SST ' + str(n))
            g += 1
        
        c = 'purple'  # Licor Temp
        litemp = co2p['Licor_Atm_Pressure']
        g = 0
        for n in litemp.columns:
            p6, = par4.plot(litemp.index, litemp[n],
                            color=c,                        
                            marker=mpl_markers_obvious[g], markersize=ms,
                            markerfacecolor='None', markeredgecolor=c,
                            label='Licor Temp ' + str(n))
            g += 1

        # CO2 seawater
        y1,y2 = host.get_ylim()
        host.set_ylim((ylim_finder(co2.xCO2_SW_dry, data_type="xco2_sw")[0],1000))

        # CO2 air
        y1,y2 = par1.get_ylim()
        limits = ylim_finder(co2.xCO2_Air_dry, data_type="xco2_air")
        par1.set_ylim(limits[0], 500)

        # O2 limit
        y1,y2 = par2.get_ylim()
        par2.set_ylim((ylim_finder(co2.Percent_O2, data_type="o2_percent")[0],y2))

        # SSS
        y1,y2 = par3.get_ylim()
        limits = (ylim_finder(co2.SSS, data_type="sss"))
        par3.set_ylim(limits[0], limits[1])
        
        # SST / Licor Temperature
        y1,y2 = par4.get_ylim()
        y_data = np.concatenate([co2.SST, co2.Licor_Temp])
        limits = (ylim_finder(y_data, data_type="temp"))
        par4.set_ylim(limits[0], limits[1])

        # Licor Pressure / GTD Pressure
        y1,y2 = par5.get_ylim()
        y_data = np.concatenate([co2.Licor_Atm_Pressure, gtd])
        limits = (ylim_finder(y_data, data_type="atm_press"))
        par5.set_ylim(limits[0], limits[1])
        
        if mbl is not None:
            c = 'black'  # MBL Air CO2
            mblplot = mblp['xCO2']
            g = 0
            for n in mblplot.columns:
                p8, = par1.plot(mblplot.index, mblplot[n],
                         color=c,
                         linestyle='-',
                         marker=mpl_markers_obvious[g], markersize=5,
                         markerfacecolor='None', markeredgecolor=c,
                         label='MBL CO2 ' + str(n))
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
    

    
        
        
    
    
    
def plot_combined(date_time,
                  xCO2_air_dry, xCO2_sw_dry,
                  o2_percent,
                  sss, sst,
                  licor_temp, licor_press,
                  gtd=[],
                  mbl=None,
                  overlay=False):
        
#        fig_title = ('Combined MAPCO2 Data')
        
        mbl = mbl[(mbl.datetime <= date_time.max()) & (mbl.datetime >= date_time.min())]
        
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
                                            offset=(offset*2, 0))
        par3.axis['right'].toggle(all=True)

        par4.axis['right'] = new_fixed_axis(loc='right',
                                            axes=par4,
                                            offset=(offset*3, 0))
        par4.axis['right'].toggle(all=True)

        par5.axis['right'] = new_fixed_axis(loc='right',
                                            axes=par5,
                                            offset=(offset*4, 0))
        par5.axis['right'].toggle(all=True)
    
    
  
    
    #    host.set_xlim(0, 2)
    #    host.set_ylim(0, 2)
    
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
        
        ms = 10

        c = 'black'  # Licor Pressure
        p7, = par5.plot(date_time, licor_press,
                        color=c,                        
                        marker='None', markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        alpha=0.4,
                        label='Licor Pressure')
        
        c = 'blue'  # Dry Seawater CO2
        p1, = host.plot(date_time, xCO2_sw_dry,
                 color=c,
                 linestyle='-',
                 marker='.', markersize=5,
                 markerfacecolor='None', markeredgecolor=c,
                 label='Seawater dry xCO2',)
    
        c = 'cyan'  # DRY air CO2
        p2, = par1.plot(date_time, xCO2_air_dry,
                 color=c,
                 linestyle='-',
                 marker='.', markersize=5,
                 markerfacecolor='None', markeredgecolor=c,
                 label='Air dry xCO2')
        
        if mbl is not None:
            c = 'black'  # MBL Air CO2
            p8, = par1.plot(mbl.datetime, mbl.xCO2,
                     color=c,
                     linestyle='-',
                     marker='.', markersize=5,
                     markerfacecolor='None', markeredgecolor=c,
                     label='MBL CO2')
        
        
        c = 'green'  # O2 percentage
        p3, = par2.plot(date_time, o2_percent,
                        color=c,                        
                        marker='None', markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='Oxygen Percent')

        c = 'red'  # SSS
        p4, = par3.plot(date_time, sss,
                        color=c,                        
                        marker='None', markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='SSS')

        c = 'orange'  # SST
        p5, = par4.plot(date_time, sst,
                        color=c,                        
                        marker='None', markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='SST')
        
        c = 'purple'  # Licor Temp
        p6, = par4.plot(date_time, licor_temp,
                        color=c,                        
                        marker='None', markersize=ms,
                        markerfacecolor='None', markeredgecolor=c,
                        label='Licor Temp')

        # CO2 seawater
        y1,y2 = host.get_ylim()
        host.set_ylim((ylim_finder(xCO2_sw_dry, data_type="xco2_sw")[0],y2))

        # CO2 air
        y1,y2 = par1.get_ylim()
        par1.set_ylim((ylim_finder(xCO2_air_dry, data_type="xco2_air")[0],y2))

        # O2 limit
        y1,y2 = par2.get_ylim()
        par2.set_ylim((ylim_finder(o2_percent, data_type="o2_percent")[0],y2))

        # SSS
        y1,y2 = par3.get_ylim()
        limits = (ylim_finder(sss, data_type="sss"))
        par3.set_ylim(limits[0],limits[1])
        
        # SST / Licor Temperature
        y1,y2 = par4.get_ylim()
        y_data = np.concatenate([sst, licor_temp])
        limits = (ylim_finder(y_data, data_type="temp"))
        par4.set_ylim(limits[0], limits[1])

        # Licor Pressure / GTD Pressure
        y1,y2 = par5.get_ylim()
        y_data = np.concatenate([licor_press, gtd])
        limits = (ylim_finder(y_data, data_type="atm_press"))
        par5.set_ylim(limits[0], limits[1])
        
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
    
        host.legend(loc=2)
        
        plt.show()
    

    
        