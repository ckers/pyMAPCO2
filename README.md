# MAPCO2 Data Processing in Python  

Package for processing MAPCO2 CO2 data

## Data Descriptions  
Time format in string format is ISO 8601
in strftime format that is: `'%Y-%m-%dT%H:%M:%S%Z'`
see config.py for definition.
Reference:
    https://en.wikipedia.org/wiki/ISO_8601


## Folder Descriptions
`\docs` :
`\gserial` : generic serial package
`\test_data` : data for testing code outputs
`\test_out` : output target for testing code
`\utils` : utility functions, a separate repo

## File Descriptions  
`\__init\__.py` : empty, required for package  
`cdiac.py` : parse the format the VBA QC process creates and we upload to CDIAC/NESDIS  
`co2plot.py`  
`co2sys.py` : import .csv data calculated from co2sys.xls  
`config.py` : local configurations, static variables  
`dashboard.py`  
`datatypes.py` : definitions of date formats used in parsing and processing  
`fasteners.md` : list of fasteners used on parts of the MAPCO2  
`flash.py` : load and parse recovered flash data  
`iridium.py` : load and parse iridium transmitted data  
 <!---`Lab Testing 02 - 4_8_2017 A.ipynb`  
`Lab Testing 02 - 4_8_2017 B.ipynb`  
`Lab Testing Status.ipynb`  
`lab_tests.py`  -->
`LICENSE`  
`load.py` : opens, indexes and cleans raw text data  
`oxygen.py` : methods to convert, pressure and temperature compensate 02 data
`parse.py`  
`README.md` : this file
`scrape.py`: scrapes the PMEL Rudics directory for Iridium data  
<!--`Scratch.ipynb`  
`snippets.py`  -->
`terminal.py` : serial terminal parser #TODO  
