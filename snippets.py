# -*- coding: utf-8 -*-
"""
Snippets useful for analyzing MAPCO2 flash data
@author: Colin Dietrich
"""


def chooser(data, start, end, verbose=False, data_type="iridium"):
    if (data_type == "iridium") or (data_type == "terminal"):
        h, g, e, co2, aux, sbe16 = parse_iridium(data=data,
                                   start=start, end=end,
                                   verbose=verbose,
                                   data_type=data_type)

    # df, df, df, dict of dfs
    if data_type == "flash":
        h, g, e, co2, aux, sbe16 = flash(data=data, start=start, end=end, verbose=verbose)
        return h, g, e, co2, aux, sbe16