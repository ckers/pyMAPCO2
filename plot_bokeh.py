# -*- coding: utf-8 -*-
"""
Plot CO2 data using Bokeh
Created on 2017-04-25
@author: Colin Dietrich
"""

from bokeh.charts import Horizon, output_file, show

def plot_bokeh_horizon():

    p_co2['plot_date'] = p_co2.index.values

    hp = Horizon(p_co2, x='plot_date',
                 plot_width=1800, plot_height=900,
                 title="MAPCO2 call success history",
                 tools="pan,lasso_select,box_select",
                 legend=None)

    output_file("horizon.html")

    show(hp)