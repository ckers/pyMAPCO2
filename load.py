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
        self.data_type = None
        self.line_starts = []
        self.line_len = 10
        self.limit = 700

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
        
        
        for n in range(0, a):
    
            line = data_list[n]
            
            if n < self.limit:
                # collate data lines for identification
                self.line_starts.append(line[0:self.line_len])        
            
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

    def detect(self, verbose=False):
        """Detect the kind of data source: flash, iridium or terminal"""
        
        # flash data is the only one with "*****" delimiters
        if "*" * self.line_len in self.line_starts:
            self.data_type = "flash"
        # it's not flash so find difference in terminal and iridium
        # based on the terminal outputting the system number, specifically
        # look for the space (" ") after the 4 character system number
        # and use the fact that in terminal, lines are formatted like that
        # more than half the time
        else:
            _c = 0
            for n in range(0, len(self.line_starts)):
                _d = self.line_starts[n]
                if verbose:
                    print("MAPCO2Engr.detect>> ", _d, "| length:", len(_d))
                
                # skip lines shorter than system number + " "
                if len(_d) >= 5:
                    # look for the delimiting space
                    if (_d[4] == " "):
                        _c += 1
            # calculate the ratio of spaces to total lines checked
            ratio = float(_c)/float(len(self.line_starts))
            if verbose:
                print("Cleaner.detect>> stats: detections=%s lines=%s ratio=%s"
                      % (_c, len(self.line_starts), ratio))
            if ratio > 0.5:
                self.data_type = "terminal"
            else:
                self.data_type = "iridium"
        if verbose:
            print("Cleaner.detect>> result:", self.data_type)

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
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\0004 2016_07_23 optode test - cleaned.txt"
    
    # Terminal log
#    f = "C:\\Users\\dietrich\\data\\misc\\pco2_optode\\mapCO2-7-22-16-final - 2016_07_25.txt"
    
    indexer = Indexer(file=f, terminal=False)
    index_df = indexer.df
    index_df.reset_index(inplace=True)
    
    d = indexer.file_to_list(f)
    cleaner = Cleaner()
    d, w, x = cleaner.run(d)
    
    cleaner.detect(verbose=False)
    print("Data Type Detected:", cleaner.data_type)
    
    _ = parse.MAPCO2Header()
    print("Header>> ", _.data_names)
    _ = parse.MAPCO2GPS()
    print("GPS>>    ", _.data_names)
    _ = parse.MAPCO2Engr(data_type=cleaner.data_type)
    print("ENGR>>   ", _.data_names)
    
    panel_dict = {}
    
    for n in range(0, len(index_df.start)):
        s = index_df.start[n]
        e = index_df.end[n]
#        a, b, c, zpon, zpof, zpcl, spon, spof, spcl, epon, epof, apon, apof = parse.parse_frame(d, s, e, verbose=True, data_type=cleaner.data_type)
#        print("Parse Frame | header >>  ", a.data())
#        print("Parse Frame | gps    >>  ", b.data())
#        print("Parse Frame | engr   >>  ", c.data())
#        print("Parse Frame | zpon   >>  ", zpon.data())
#        print("Parse Frame | zpof   >>  ", zpof.data())
#        print("Parse Frame | zpcl   >>  ", zpcl.data())
#        print("Parse Frame | spon   >>  ", spon.data())
#        print("Parse Frame | spof   >>  ", spof.data())
#        print("Parse Frame | spcl   >>  ", spcl.data())
#        print("Parse Frame | epon   >>  ", epon.data())
#        print("Parse Frame | epof   >>  ", epof.data())
#        print("Parse Frame | apon   >>  ", apon.data())
#        print("Parse Frame | apof   >>  ", apof.data())
        
        h, g, e, df = parse.build_frames(d,s,e,verbose=True, data_type=cleaner.data_type)
        print("="*50)
        print(h.date_time)
        panel_dict[h.date_time] = df
        print("header>>")
        print("------")
        print(h)
        print("gps>>")
        print("------")
        print(g)
        print("engineering>>")
        print("------")
        print(e)
        print("data frame>>")
        print("------")
        print(df)
        
    panel = pd.Panel(data=panel_dict)