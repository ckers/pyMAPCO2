# -*- coding: utf-8 -*-
"""
Scrape PMEL html server data and save locally

Created on Mon Apr 20 11:43:28 2015
@author: Colin Dietrich
"""

import os
import time
import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
        
from . import config


def apache_table_scraper(html_file):
    """Scrape HTML table from an Apache Server index into a
    Pandas DataFrame.  Note: assumes the table is the only
    one on the page, this is a pretty good assumption on
    Apache servers producing generic 'index.html' like files.

    Parameters
    ----------
    html_file : str, url path to HTML file to parse

    Returns
    -------
    Pandas DataFrame, containing parsed HTML table

    """

    html = requests.get(html_file)
    soup = BeautifulSoup(html.text, "html.parser")
    table = soup.find_all('table')[0]  # first table is only one
    df_list = pd.read_html(io=str(table))
    return df_list[0]


def apache_concat(url_sources):
    """Concatenate Pandas DataFrames scraped from a list of
    Apache Server urls.

    Parameters
    ----------
    url_sources : list,

    Returns
    -------
    Pandas DataFrame, all Apache server files found
    """

    df_list = []
    for _u in url_sources:
        df_n = apache_table_scraper(_u)
        df_n['url_source'] = _u
        df_list.append(df_n)
    return pd.concat(df_list)


def rudics_file_timestamp(filename):
    """Get the timestamp of a Rudics Iridium data file
    
    Parameters
    ----------
    filename : str, filename
    
    Returns
    -------
    datetime object : datetime of file timestamp
    """
    pass


def rudics_file_time_modified(server_timestamp):
    """Get the timestamp of a Apache modified timestamp
    
    Parameters
    ----------
    server_timestamp : str, file timestamp
    
    Returns
    -------
    datetime object : datetime of file timestamp
    """
    return time.mktime(time.strptime(server_timestamp, "%d-%b-%Y %H:%M"))
    
    
def rudics_file_time(filename):
    """Get the timestamp of a Apache Rudics data file.
    """
    
    if "." in filename:
        filename = filename.split(".")[0]
    return filename[6:]

    
def local_file_time(filepath):
    """Get the date from a Python formatted local file where:
    C0AAA_YYYY_MM_DD.txt

    Parameters
    ----------
    filepath : str, absolute path (C:// etc) to file being dated

    Returns
    -------
    tfile : int, unix time of file date
    """
    
    tstr = "_".join(filepath.split(".")[0].split("\\")[-1].split("_")[1:4])
    tfile = int(time.mktime(time.strptime(tstr, "%Y_%m_%d")))
    return tfile
    

def rename_file(filename):
    """Rename a rudics file to sort chronologically in a file browswer
    
    Parameters
    ----------
    filename : str, file name as found on the Rudics server
    
    Returns
    -------
    destination_file : str, new file name to save locally, formatted 
        CNNNN_YYYY_mm_dd_version.txt
    """

    if "." in filename:
        filename, version = filename.split(".")
        version = '_' + version
    else:
        version = ""

    sn_m_d_y = filename.split("_")
        
    # reorder files so they sort by time
    new_filename = (sn_m_d_y[0] + '_' + sn_m_d_y[3] + '_' +
                    sn_m_d_y[1] + '_' + sn_m_d_y[2] + version +
                    '.txt')
    return new_filename


def rudics_files(url_sources, local_target):
    """Get inventory of all files that should be downloaded
    """
    
    _df = apache_concat(url_sources)
    _df.columns = ['img',
                   'filename', 'modified', 'size',
                   'description', 'url_source']
    _df.drop(['img', 'description'], axis=1, inplace=True)
    
    for _value in ['Name', 'Parent Directory']:
        _df = _df[_df.filename != _value]
    
    _df['datetime_file'] = pd.to_datetime(_df.modified)
    _df['filename_new'] = _df.filename.apply(rename_file)
    _df['datetime64_ns'] = _df.filename.apply(rudics_file_time)
    _df['datetime64_ns'] = pd.to_datetime(_df.datetime64_ns,
                                          format='%m_%d_%Y')
    _df.sort_values(by='datetime64_ns', inplace=True, axis=0)
    _df['url_file'] = (_df.url_source.astype(str) + 
                       '/' + 
                       _df.filename.astype(str))
    _df['unit'] = _df.filename.str[1:5]
    _df['local_dir'] = local_target + '\\' + _df.unit
    _df['local_filepath'] = local_target + '\\' + _df.unit + '\\' + _df.filename_new
    return _df


def download_files(x):
    """Download files from Rudics to a local directory for processing

    If x.skip_download is set, skip downloading new data for that file

    Parameters
    ----------
    x : str, absolute filepath to file to download

    Returns
    -------
    None, writes to disk
    """
    if x.skip_download:
        return False

    url = x.url_file

    # if the local folder does not exist, make it
    if not os.path.exists(x.local_dir):
        os.mkdir(x.local_dir)

    # note: no modified time checks!
    # get the text, convert to unicode and save using byte write
    _text = requests.get(url)             # request the data
    _text = _text.text                    # get the text body
    _text = _text.encode('utf-8')         # convert to unicode
    _file = open(x.local_filepath, 'wb')  # open as bytes
    _file.write(_text)                    # write the data
    _file.close()

    return True


def get_timespan(t_start='01/01/2010', t_end='01/01/2020', days_in_past=None):
    """Get the start and end dates for further calculations.
    d supercedes t0, t1 range.
    format = 'mm/dd/yyyy hh:mm'
    
    Parameters
    ----------
    t_start : str, start of time range
    t_end : str, end of time range
    days_in_past : int, number of days from present to create time range
    
    Returns
    -------
    t_start : Pandas datetime64
    t_end : Pandas datetime64
    """

    # if True, override to start of the day specified by 'days_in_past'
    if days_in_past is not None:
        t_end = pd.to_datetime('now')
        t_start = pd.to_datetime('today') - pd.Timedelta('%s days' % days_in_past)
    else:
        t_start = pd.to_datetime(t_start)
        t_end = pd.to_datetime(t_end)

    return t_start, t_end

     
def run(units, t_start, t_end,
        url_source=False,
        local_target=False,
        skip=[],
        verbose=False,
        plot=False):
    """Download files from the rudics server
    
    Parameters
    ----------
    units : str or list, one or more unit serial numbers to scrape data for
    t_start : str, start of time range
    t_end : str, end of time range
    days_in_past : int, number of days from present to create time range
    url_source : str, eclipse location to download files from
    local_target : str, location to save files downloaded
    skip : list, str file name to skip (if perhaps manually edited locally)
    verbose : bool, enable verbose printout
    plot : bool, show plots of indexes and datetime values
    
    Returns
    -------
    Pandas Dataframe, containing file attributes and download status
    """
    
    if isinstance(units, str):
        units = [units]
    if not url_source:
        url_source = config.mapco2_rudics
    url_sources = [url_source + _u for _u in units]
    if verbose:
        print('scrape.download>> URL sources:\n', url_sources)
    if not local_target:
        local_target = config.local_mapco2_data_directory
    if verbose:
        print('scrape.download>> Local Target:', local_target)
    
    df = rudics_files(url_sources, local_target)
    if plot:
        plt.plot(df.datetime64_ns)
        plt.title('Data Indexes and Dates')
        plt.show()
    
    df = df[(df.datetime64_ns >= t_start) & (df.datetime64_ns <= t_end)]
    df.reset_index(inplace=True)
    if plot:
        plt.plot(df.datetime64_ns)
        plt.title('Data Indexes and Dates - filtered to date range')
        plt.show()

    df['skip_download'] = ''

    # TODO: capture skip parameter and insert to df.skip_download

    df['download_success'] = df.apply(download_files, axis=1)
    return df

    
class Iridium(object):
    
    def __init__(self, form):
        """OBSOLETE, see static methods above!"""

        # location of pCO2 Rudics data
        if form == 'ma':
            self.url_source = config.mapco2_rudics
            self.local_data_directory = config.local_mapco2_data_directory
        if form == 'wg':
            self.url_source = config.waveglider_rudics
            self.local_data_directory = config.local_waveglider_data_directory
        
        # local data files
        self.local_data_files = []
        
        # ignore these links
        self.apache_links = ("Name", "Last modified", "Size",
                             "Description", "Parent Directory")
                             
        # list of unit numbers as "XXXX\" directory folders
        self.units = []

        self.data_names = None

        self.data_sn = []
        self.data_filename = []
        self.data_new_filename = []

        # list of data files for all units searched for
        self.data_urls = []
        self.data_urls_modtime = []
        self.data_urls_modtime_str = []
        
        # network access apache file index
        html = requests.get(self.url_source)

        # get all the numbered unit folders (not wave glider, etc.)
        soup = BeautifulSoup(html.text, "html.parser")
        for _a in [_.text for _ in soup.find_all("a")]:
            try:
                if _a not in self.apache_links:
                    self.units.append(_a)
            except ValueError:
                pass

    @staticmethod
    def time_span(days=5, hours=0):
        """Calculate the number of seconds in a set number of hours or days

        Parameters
        ----------
        days : int, number of days. Default is 5.
        hours : int, number of hours. Default is 0.

        Returns
        -------
        seconds : in, number of seconds in input combination of days and hours
        """
        
        return 60 * 60 * (hours + (24 * days))

    def unit_num_filter(self):
        
        units_temp = []
        for unit in self.units:
            try:
                int(unit[:-1])
                units_temp.append(unit)
            except ValueError:
                pass
        self.units = units_temp


    def unit_files(self, units=None):
        """Compile all files of the requested unit numbers
        
        Parameters
        ----------
        units : list, string folder names off root apache directory of units
            to compile file list
        
        Returns
        -------
        None, sets self.download_files to a list of string path names
        """
        
        
        
        # filter out links that aren't unit numbers i.e. "0123/"
        self.unit_num_filter()        
        
        for _u in units:
            html = requests.get(self.url_source + _u)
            soup = BeautifulSoup(html.text, "html.parser")
            a_soup = soup.find_all("a")

            for a in a_soup:
                fa = a.text.strip()
                fts = a.next_element.next_element.text.strip()
                
                # timestamp in 3rd column of rows are file listings
                try:
                    ft = time.mktime(time.strptime(fts, "%d-%b-%Y %H:%M"))
                    self.data_urls_modtime_str.append(fts)

                    # skip links that are standard apache server links
                    try:
                        if fa not in self.apache_links:
                            self.data_urls.append(self.url_source +
                                                  _u + "/" + fa)
                            self.data_urls_modtime.append(ft)
                    except ValueError:
                        pass
                except ValueError:
                    # non-timestamp rows in the page                    
                    pass

    def download_files(self, oldest=None, refresh_days=False, download_delay=False):
        """Download files from Rudics to a local directory for processing
        
        Parameters
        ----------
        oldest : str, oldest file to download, in YYYY_MM_DD date format
        refresh_days : int, number of days in the past to purge and redownload
        download_delay : int, number of seconds to pause between files

        Returns
        -------
        None, writes to disk
        """
        
        files_downloaded = []
        urls_times = dict(zip(self.data_urls, self.data_urls_modtime))
        
        for url in self.data_urls:
            url_parts = url.split('/')
            filename = url_parts[-1]
            
            new_filename = self.rename_file(filename=filename)
            sn = new_filename[1:5]  # based on Iridium server files
            
            self.data_sn.append(sn)
            self.data_filename.append(filename)
            
            _dir = self.local_data_directory + os.path.sep + sn + os.path.sep

            # if the local folder does not exist, make it
            if os.path.exists(_dir):
                pass
            else:
                os.mkdir(_dir)

            t_server = urls_times[url]

            destination_file = _dir + new_filename
            self.data_new_filename.append(new_filename)
            
            if os.path.exists(destination_file):
                t_local = os.path.getmtime(destination_file)
                self.local_data_files.append(destination_file)
            
                _refresh = (time_file(destination_file) >
                            int(time.time() - self.time_span(days=refresh_days)))
                if _refresh:
                    os.remove(destination_file)
                
                # if the server file has newer data, refresh as well
                elif t_local < t_server:
                        os.remove(destination_file)

            # download and rename data files
            # if the local file does not exist, make it
            if not os.path.exists(destination_file):
                # get the text, convert to unicode and save using byte write
                _text = requests.get(url)             # request the data
                _text = _text.text                    # get the text body
                _text = _text.encode('utf-8')         # convert to unicode
                _file = open(destination_file, 'wb')  # open as bytes
                _file.write(_text)                    # write the data
                _file.close()
                files_downloaded.append(filename)
            
            if download_delay:
                if download_delay == "random":
                    t = random.random()*5
                else:
                    t = float(download_delay)
                print("scrape.download_files>> Done with %s" % str(filename))
                print("...pausing for %s seconds." % "{:10.2f}".format(t))
                time.sleep(t)

        self.local_data_files.sort()
        
        if len(files_downloaded) == 0:
            files_downloaded = None
        
        return files_downloaded
         

class CallLog(object):

    """scrap Rudics call logs for connection failures
    """

    def __init__(self, url_source="http://eclipse.pmel.noaa.gov/rudics/ALL_RUDICS/",
                 local_data_directory=None):

        self.data = []
        
        # network access file index
        html = requests.get(url_source)

        # get all the dial logs for the last 2 months
        soup = BeautifulSoup(html.text, "html.parser")
        soup_a = soup.find_all("a")
        for _ in soup_a:
            
            text = _.text
            href = _["href"]
            if "outlogs" in href:
                print("|", text, "|", href)
