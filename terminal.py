# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 15:38:18 2016

@author: dietrich
"""

import pandas as pd

import parse
from load import Cleaner, Indexer

# f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\0004 2016_07_23 optode test - cleaned.txt"

# get indices of data frame separators
indexer = Indexer(file=f, terminal=False)
indexer.df.reset_index(inplace=True)
    
    