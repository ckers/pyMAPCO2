# -*- coding: utf-8 -*-
"""
Parse summary data frames from MAPCO2
Created on Mon Jul 25 14:30:25 2016
@author: Colin Dietrich
"""

import unicodedata
import pandas as pd

import config


class Cleaner(object):
    def __init__(self):
        pass

    def unicode_check(self, line):
        """Try to decode each line to Unicode"""
        try:
            line.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False
            
    def whitespace(self, line):
        """Try to remove whitespace from line"""
        try:
            return line.rstrip()
        except:
            return False
    
    def remove_control_characters(self, s):
        """Use category identification to remove control characters"""
        try:
            return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")
        except:
            return False
    
    def run(self, data_list): #, inplace=False):
        """
        Parameters
        ----------
        data_list : list, subset of data to check for integrity
        
        Returns
        -------
        z : list, cleaned data
        y : list, unicode error indexes
        x : list, blank lines
        """
        
        a = len(data_list)    
        
        z = [""] * a
        y = [False] * a
        x = [False] * a
        
#        if not inplace:
        
        for n in range(0, a):
    
            line = data_list[n]
            
            # strip whitespace from start & end
            _y = self.whitespace(line)
            if _y is False:
                y[n] = True
            else:
                line = _y
            
            # remove control characters
            _x = self.remove_control_characters(line)
            if _x is False:
                x[n] = True
            else:
                line = _x
    
            # option for making changes in place to the source list
#            if inplace:
#                data_list[n] = line
#            else:
            z[n] = line
    
#        if inplace:
#            return w, x
#        else:
        return z, y, x

class Indexer(object):
    def __init__(self, file=None, terminal=False):
        self.terminal = terminal
        self.terminal_lines = 50
        self.status = ""        
        self.errors = []
        self.df = None
        
        if file is not None:
            try:
                self.run(file)
            except:
                self.status = "Auto import failed"

    def file_to_list(self, file):
        """Convert string/file data to list, no cleaning
        Parameters
        ----------
        file : filepath to file to open
    
        Returns
        -------
        data : list, lines of data from file
        """
        data = []
        f = open(file=file, mode="r", errors="ignore", encoding="utf-8")
        for _line in f:
            data.append(_line)
        return data
        
    def index_data(self, data):
        """Find indexes of interest in a list of data"""
        
        # get line number of data frame start
        c = 0
        i = []
        for _line in data:
            if _line[:4] in config.pco2_start_delimiters:
                i.append(c)
            c += 1
        return i
        
    def get_times(self, data, indexes):
        """Find times in list of data"""
        t = []
        for _i in indexes:
            header = data[_i].strip().split()
            _t = header[3] + "_" + header[4]
            t.append(_t)
        return t
        
    def run(self, file):
        # load text to list
        d = self.file_to_list(file)
        # index list values to frames of data
        i = self.index_data(d)
        i_end = i[1:] + [len(d)]
        # times for each frame of data
        t = self.get_times(d, i)
        # convert to pandas
        self.df = pd.DataFrame({"time_str":t, "start":i, "end":i_end})
        # make DateTime values    
        self.df["time"] = pd.to_datetime(self.df.time_str, format="%Y/%m/%d_%H:%M:%S")
        # drop dups and sort chronologically    
        self.df.drop_duplicates(subset="time_str", inplace=True)
        self.df.sort_values(by="time")  # inplace
        self.df = self.df[["time", "time_str", "start", "end"]]
        
        if self.terminal:
            self.df["end"] = self.df["start"] + self.terminal_lines
    
    
if __name__ == "__main__":
    
    import parse
    
    # Iridium file
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\C0004_2012_07_19.txt"
    f = "C:\\Users\\dietrich\\data\\rudics\\0008\\C0008_2015_10_01.txt"
    
    # Flash file
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\0004 2016_07_23 optode test.txt"
    
    # Terminal log
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\mapCO2-7-22-16-final - 2016_07_25.txt"
    
    indexer = Indexer(file=f, terminal=True)
    df = indexer.df
    df.reset_index(inplace=True)
    
    d = indexer.file_to_list(f)
    cleaner = Cleaner()
    d, w, x = cleaner.run(d) #, inplace=True)

#    def cut(row, data):
#        header = parse.parse_index(data, row.start, row.end)
#        print(header)
#        
#    df.apply(cut, args=(d))
    _ = parse.MAPCO2Header()
    print("Header>> ", _.data_names)
    _ = parse.MAPCO2GPS()
    print("GPS>>    ", _.data_names)
    
    for n in range(0, len(df.start)):
        s = df.start[n]
        e = df.end[n]
        a, b = parse.parse_frame(d, s, e, verbose=True)
        print("Parse Frame | header >>  ", a.data())
        print("Parse Frame | gps    >>  ", b.data())
        
        