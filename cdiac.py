# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 17:17:47 2016

@author: dietrich
"""

import numpy as np
import pandas as pd
from os import walk

class CDIACCSV(object):
    
    def __init__(self):
#        self.fp = fp
        self.target = None
        
    def load_df(self, fp):
        """Load MAPCO2 data from final .csv to Pandas DataFrame
        
        Parameters
        ----------
        fp : str, filepath to .csv file of final MAPCO2 data 
        
        Returns
        -------
        _df : DataFrame, final MAPCO2 data formatted as
            Date                          object
            H2O_AIR                      float64
            H2O_SW                       float64
            Latitude                     float64
            Licor_Atm_Pressure           float64
            Licor_Temp                   float64
            Longitude                    float64
            Mooring                       object
            Percent_O2                   float64
            SSS                          float64
            SST                          float64
            Time                          object
            datetime              datetime64[ns]
            dfCO2                        float64
            dpCO2                        float64
            fCO2_Air_sat                 float64
            fCO2_SW_sat                  float64
            pCO2_Air_sat                 float64
            pCO2_SW_sat                  float64
            xCO2_Air_QF                    int64
            xCO2_Air_dry                 float64
            xCO2_Air_wet                 float64
            xCO2_SW_QF                     int64
            xCO2_SW_dry                  float64
            xCO2_SW_wet                  float64
            dtype: object
        """

        _df = pd.read_csv(fp, sep=',',
                             header=0,
                             skiprows=[1])
        _df['datetime'] = _df.Date + ' ' + _df.Time
        _df['datetime'] = pd.DatetimeIndex(_df.datetime)
#        _df['datetime'] = pd.DatetimeIndex(_df.loc[:,'datetime'],
#                                         format='%m/%d/%Y_%H:%M')
        return _df
        
    def get_files(self, fp):
        """Get all files in a directory.  Uses 3.5 os.walk
        Only include files in fp directory that should be loaded.
        
        Parameters
        ----------
        fp : str, directory to walk into
        Returns
        -------
        files_out : list, of str abs filepath locations of all files
        """
        files_out = []        
        for root, dirs, files in walk(fp):
            for name in files:
                files_out.append(root + name)
        return files_out        
        
    def load_batch(self, fp_list):       
        """Load all files in a directory that are CDIAC VBA MAPCO2 format

        Parameters
        ----------
        fp_list : list, str filepath to .csv files to load
        
        Returns
        -------
        _df : DataFrame, final MAPCO2 data.  See load_df for dtypes
        _dfmbl : DataFrame, mbl data.  See load_mbl for dtypes        
        """
        mapco2_fp_list = []
        mbl_fp = None
        
        for fp in fp_list:
            if "mbl" in fp:
                mbl_fp = fp
            else:
                mapco2_fp_list.append(fp)
        
        _df = self.load_df(mapco2_fp_list[0])
        for _fp in mapco2_fp_list[1:]:
            _df2 = self.load_df(_fp)
            _df = pd.concat([_df, _df2])
            
        _df = _df.sort_values(by=["datetime"], axis=0)
        _df.reset_index(inplace=True)
        
        
        _dfmbl = self.load_mbl(mbl_fp)
        print(_dfmbl.head())
        
        return _df, _dfmbl

    def load_mbl(self, fp):
        """Load a .csv file of location specific MBL data generated from
        Pandas via import_mbl.py
        Parameters
        ----------
        fp : str, file path to .csv file containing precompiled mbl
            data for the location being batched
        
        Returns
        -------
        _df : DataFrame, containing mbl umol/mol CO2 formatted as
            Unnamed: 0              int64
            t              datetime64[ns]
            xCO2                  float64
            xCO2_uncert           float64
            dtype: object
            
        """

        _df = pd.read_csv(fp, sep=',',
                          header=0)
#        _df['t'] = pd.to_datetime(_df['t'])
        _df['datetime'] = pd.DatetimeIndex(_df['t'])

        return _df
    

class CDIACDL(object):
    
    def __init__(self, target=None):
        """Download data from CDIAC and store locally"""
        pass
    
class CDIACPlot(object): 
    
    def __init__(self):
        pass
    
if __name__ == "__main__":
#    import parse
    import co2plot
    
    fp = 'C:\\Users\\dietrich\\data\\01 QC\\TAO_110W0N\\TAO_110W0N_all\\cdiac\\TAO110W_0N_Jul2010_Oct2010.csv'
    fp_all = 'C:\\Users\\dietrich\\data\\01 QC\\TAO_110W0N\\TAO_110W0N_all\\cdiac\\'
    c = CDIACCSV()
    
    fp_list = c.get_files(fp_all)
    print(fp_list)

    df3, mbl = c.load_batch(fp_list=fp_list)
    
    df3["day"] = df3.datetime.map(co2plot.day_of_year)
    df3["year"] = df3.datetime.map(co2plot.year)
    
    mbl["day"] = mbl.datetime.map(co2plot.day_of_year)
    mbl["year"] = mbl.datetime.map(co2plot.year)
    
#    co2plot.plot_combined(date_time=df3.datetime,
#                          xCO2_air_dry=df3.xCO2_Air_dry,
#                          xCO2_sw_dry=df3.xCO2_SW_dry,
#                          o2_percent=df3.Percent_O2,
#                          sss=df3.SSS,
#                          sst=df3.SST,
#                          licor_temp=df3.Licor_Temp,
#                          licor_press=df3.Licor_Atm_Pressure,
#                          mbl=mbl)
    
    
    co2plot.plot_annual(co2=df3,
                        mbl=mbl)    
    
#    final = parse.MAPCO2DataFinal()
#    final.xCO2_air_dry = df3.xCO2_Air_dry
#    final.date_time = df3.datetime
    