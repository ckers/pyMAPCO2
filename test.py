import pandas as pd

import parse
from load import Cleaner, Indexer

# Iridium file
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\C0004_2012_07_19.txt"
# f = "C:\\Users\\dietrich\\data\\rudics\\0008\\C0008_2015_10_01.txt"

# Flash file
# f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\0004 2016_07_23 optode test - cleaned.txt"

f = 'C:\\Users\\dietrich\\data\\01 QC\\TAO_170W0N\\TAO_170W0N_dp07_2012\\source\\mapco2_0170w_0032_dp07_20120516_2c.txt'
#f = 'flash_bad_data_test.txt'

# Terminal log
# f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\mapCO2-7-22-16-final - 2016_07_25.txt"

# get indices of data frame separators
indexer = Indexer(file=f, terminal=False)
indexer.df.reset_index(inplace=True)

# clean the data
# z : list, cleaned data
# y : list, unicode error indexes
# x : list, blank lines
cleaner = Cleaner()
z, y, x = cleaner.run(indexer.file_to_list(f))

# identify what kind of data was passed to the process
cleaner.detect(verbose=False)
print("Data Type Detected:", cleaner.data_type)

# header descriptions
print("Header>> ", parse.MAPCO2Header().data_names)
print("GPS>>    ", parse.MAPCO2GPS().data_names)
print("ENGR>>   ", parse.MAPCO2Engr(data_type=cleaner.data_type).data_names)

# testing flash cycle parsing
h, g, e, co2, aux = parse.chooser(data=z,
                                  start=indexer.df.start,
                                  end=indexer.df.end,
                                  verbose=True,
                                  data_type=cleaner.data_type)

# one cycle summary for now...
# print(df.mean())

# experiment with json output
formats = ['split', 'records', 'index', 'columns', 'values']

# for f in formats:
#     print(f, len(df.to_json(orient=f)))
