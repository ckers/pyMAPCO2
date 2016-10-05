import pandas as pd

import parse
from load import Cleaner, Indexer

# Iridium file
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\C0004_2012_07_19.txt"
# f = "C:\\Users\\dietrich\\data\\rudics\\0008\\C0008_2015_10_01.txt"

# Flash file
f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\0004 2016_07_23 optode test - cleaned.txt"

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

# start a dictionary to put dataframes into for panel conversion
# panel_dict = {}

# testing flash cycle parsing
h, g, e, co2, aux = parse.chooser(z,
                                  indexer.df.start,
                                  indexer.df.end,
                                  verbose=True,
                                  data_type=cleaner.data_type)

# one cycle summary for now...
#print(df.mean())


formats = ['split', 'records', 'index', 'columns', 'values']

# for f in formats:
#     print(f, len(df.to_json(orient=f)))
    
#for n in range(0, len(index_df.start)):
#    s = index_df.start[n]
#    e = index_df.end[n]
#    #        (a, b, c, zpon, zpof, zpcl, spon, spof, spcl, epon, epof, apon, apof) = parse.parse_frame(d, s, e,
#    #            verbose=True, data_type=cleaner.data_type)
#    #        print("Parse Frame | header >>  ", a.data())
#    #        print("Parse Frame | gps    >>  ", b.data())
#    #        print("Parse Frame | engr   >>  ", c.data())
#    #        print("Parse Frame | zpon   >>  ", zpon.data())
#    #        print("Parse Frame | zpof   >>  ", zpof.data())
#    #        print("Parse Frame | zpcl   >>  ", zpcl.data())
#    #        print("Parse Frame | spon   >>  ", spon.data())
#    #        print("Parse Frame | spof   >>  ", spof.data())
#    #        print("Parse Frame | spcl   >>  ", spcl.data())
#    #        print("Parse Frame | epon   >>  ", epon.data())
#    #        print("Parse Frame | epof   >>  ", epof.data())
#    #        print("Parse Frame | apon   >>  ", apon.data())
#    #        print("Parse Frame | apof   >>  ", apof.data())
#    parse.build_frames(d, s, e, verbose=True, data_type=cleaner.data_type)
#    h, g, e, df = parse.build_frames(d, s, e, verbose=True, data_type=cleaner.data_type)
#    print("=" * 50)
#    print(h.date_time)
#    panel_dict[h.date_time] = df
#    print("header>>")
#    print("------")
#    print(h)
#    print("gps>>")
#    print("------")
#    print(g)
#    print("engineering>>")
#    print("------")
#    print(e)
#    print("data frame>>")
#    print("------")
#    print(df)
#
#panel = pd.Panel(data=panel_dict)
