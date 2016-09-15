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

    @staticmethod
    def unicode_check(line):
        """Try to decode each line to Unicode
        :param line:
        """
        try:
            line.decode("utf-8")
            return True
        except UnicodeDecodeError:
            return False

    @staticmethod
    def whitespace(line):
        """Try to remove whitespace from line"""
        try:
            return line.rstrip()
        except:
            return False

    @staticmethod
    def remove_control_characters(s):
        """Use category identification to remove control characters
        :param s:
        """
        try:
            return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")
        except:
            return False

    def run(self, data_list):  # , inplace=False):
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
        """Detect the kind of data source: flash, iridium or terminal
        Parameters
        ----------
        verbose : bool,

        Returns
        -------
        None : sets self.datatype
        """

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
                    if _d[4] == " ":
                        _c += 1
            # calculate the ratio of spaces to total lines checked
            ratio = float(_c) / float(len(self.line_starts))
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
        """Find index locations in a text file that delimit data samples"""

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

    @staticmethod
    def file_to_list(file):
        """Convert string/file data to list, no cleaning
        Parameters
        ----------
        file : str, filepath to file to open
    
        Returns
        -------
        data : list, lines of data from file
        """
        data = []
        f = open(file, mode="r", errors="ignore", encoding="utf-8")
        for _line in f:
            data.append(_line)
        return data

    @staticmethod
    def index_data(data):
        """Find indexes of interest in a list of data
        Parameters
        ----------
        data : list,
        """

        # get line number of data frame start
        c = 0
        i = []
        for _line in data:
            if _line[:4] in config.pco2_start_delimiters:
                i.append(c)
            c += 1
        return i

    @staticmethod
    def get_times(data, indexes):
        """Find times in list of data
        Parameters
        ----------
        data : list,
        indexes : array-like,

        Returns
        -------
        t : list,
        """
        t = []
        for _i in indexes:
            header = data[_i].strip().split()
            _t = header[3] + "_" + header[4]
            t.append(_t)
        return t

    def run(self, file):
        """
        Parameters
        ----------
        file : str,

        Returns
        -------

        """
        # load text to list
        d = self.file_to_list(file)

        # index list values to frames of data
        i = self.index_data(d)
        i_end = i[1:] + [len(d)]

        # times for each frame of data
        t = self.get_times(d, i)

        # convert to pandas
        self.df = pd.DataFrame({"time_str": t, "start": i, "end": i_end})

        # make DateTime values
        self.df["time"] = pd.to_datetime(self.df.time_str, format="%Y/%m/%d_%H:%M:%S")

        # drop dups and sort chronologically
        self.df.drop_duplicates(subset="time_str", inplace=True)
        self.df.sort_values(by="time")  # inplace
        self.df = self.df[["time", "time_str", "start", "end"]]

        # add enough lines to capture entire printed dataframe
        if self.terminal:
            self.df["end"] = self.df["start"] + self.terminal_lines
