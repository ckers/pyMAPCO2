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

import config


class Iridium(object):
    
    def __init__(self, form):
        
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
        
    @staticmethod
    def time_file(filepath):
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
                
                try:
                    ft = time.mktime(time.strptime(fts, "%d-%b-%Y %H:%M"))
                    self.data_urls_modtime_str.append(fts)
                except ValueError:
                    # these are the non-timestamp rows in the page                    
                    pass
                
                try:
                    if fa not in self.apache_links:
                        self.data_urls.append(self.url_source + 
                            _u + "/" + fa)
                        self.data_urls_modtime.append(ft)
                except ValueError:
                    pass
        
    def rename_file(self, filename):
        """Rename a rudics file to sort chronologically in a file browswer
        
        Parameters
        ----------
        name : str, file name as found on the Rudics server
        
        Returns
        -------
        destination_file : str, new file name to save locally, formatted 
            CNNNN_YYYY_mm_dd_version.txt
        """
#        print(name)
        
#        sn_sn_date = url.split("/")[-2:]
        
        
        
#        if "." in name[1]: 
        if "." in filename:
            filename, version = filename.split(".")
            version = '_' + version
#            name = name.split("_")
            
        else:
                        
#            name = name[1].split("_")
            version = ""

        sn_m_d_y = filename.split("_")
            
        # reorder files so they sort by time
#        name = name[0] + "_" + name[3] + "_" + name[1] + "_" + name[2]
            
        new_filename = (sn_m_d_y[0] + '_' + sn_m_d_y[3] + '_' + 
                        sn_m_d_y[1] + '_' + sn_m_d_y[2] + version +
                        '.txt')
        
#        destination_file = name + version + ".txt"
#        return destination_file
        return new_filename
    
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
        

#        print('#######>', self.data_urls)
#        self.data_names = [_.split("/")[-2:] for _ in self.data_urls]
#        print("0>>", self.data_names)
                
        
        """
        names_urls = zip(self.data_names, self.data_urls)
        urls_times = dict(zip(self.data_urls, self.data_urls_modtime))
        
        # for name, url in names_urls:
        name ===== filename now!
        """
        
        urls_times = dict(zip(self.data_urls, self.data_urls_modtime))
                
        
        for url in self.data_urls:
            url_parts = url.split('/')
            filename = url_parts[-1]
            
            new_filename = self.rename_file(filename)
            sn = new_filename[1:5]  # based on Iridium server files
#            print(filename, sn, new_filename)

            self.data_sn.append(sn)
            self.data_filename.append(filename)
            
            _dir = self.local_data_directory + os.path.sep + sn + os.path.sep

            # if the local folder does not exist, make it
            if os.path.exists(_dir):
                pass
            else:
                os.mkdir(_dir)

            t_server = urls_times[url]
            

            """
            self.data_names = [_.split("/")[-2:] for _ in self.data_urls]
            
            
            
            _dir = self.local_data_directory + os.path.sep + name[0] + os.path.sep
            t_server = urls_times[url]
            
            # if the local folder does not exist, make it
            if os.path.exists(_dir):
                pass
            else:
                os.mkdir(_dir)
            """
        
            # create the local data file and keep a record of it's 
            # absolute path.
            # print('download_files>>', name)
        
        
            destination_file = _dir + new_filename
            self.data_new_filename.append(new_filename)
            
            if os.path.exists(destination_file):
                t_local = os.path.getmtime(destination_file)
                self.local_data_files.append(destination_file)
            
                _refresh = (self.time_file(destination_file) >
                            int(time.time() - self.time_span(days=refresh_days)))
                if _refresh:
                    os.remove(destination_file)
                
                # if the server file has newer data, refresh as well
                elif t_local < t_server:
                        os.remove(destination_file)
                
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

    # TODO: scrap Rudics call logs for connection failures

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
    
        