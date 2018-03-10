# MAPCO2 Data Processing in Python  

Package for processing MAPCO2 CO2 data

### Legal Disclaimer
This repository is a software product and is not official communication of the National Oceanic and Atmospheric Administration (NOAA), or the United States Department of Commerce (DOC). All NOAA GitHub project code is provided on an 'as is' basis and the user assumes responsibility for its use. Any claims against the DOC or DOC bureaus stemming from the use of this GitHub project will be governed by all applicable Federal law. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the DOC. The DOC seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by the DOC or the United States Government.

## Data Descriptions  
Time format in string format is ISO 8601
in strftime format that is: `'%Y-%m-%dT%H:%M:%S%Z'`
see config.py for definition.
Reference:
    https://en.wikipedia.org/wiki/ISO_8601


## Folder Descriptions
`\docs` : support documents  
`\gserial` : generic serial package, a separate submodule  
`\test_data` : data for testing code outputs  
`\test_out` : output target for testing code  
`\utils` : utility functions, a separate submodule

## File Descriptions  
Basic contents of modules  
`\__init\__.py` : empty, required for package  
`algebra.py` : algebra for calculations  
`co2sys.py` : import .csv data calculated from co2sys.xls  
`config.py` : local configurations, static variables  
`dashboard.py` : dashboard for frontend qc work #TODO  
`datatypes.py` : definitions of date formats used in parsing and processing  
`fasteners.md` : list of fasteners used on parts of the MAPCO2  
`flash.py` : load and parse recovered flash data  
`iridium.py` : load and parse iridium transmitted data  
`lab_tests.py` : multi system data, messy and used in separate Jupyter notebooks #TODO  
`LICENSE` : GNU v3  
`load.py` : open, index and clean raw text data  
`oxygen.py` : convert and compensate oxygen data  
`parse.py` : convert loaded data into data structures  
`plot.py` : core co2 plotting  
`plot_bokeh.py` : Bokeh plots, less used  
`plot_plt.py` : Matplotlib plots  
`plot_ply.py` : Plot.ly plots  
`qc.py` : data quality control  #TODO along with co2sys  
`README.md` : this file  
`scrape.py`: scrapes the PMEL Rudics directory for Iridium data  
`sstc.py` : sea surface salinity and temperature  
`stats.py` : statistical methods  
`terminal.py` : serial terminal parser #TODO  
`xls.py` : Microsoft Excel importer for .xls and .xlsx data  
