# General Oceanics pCO2 data  



## Data Types and Descriptions
| Name          | Type          | Units      | Source Name  | Description |
| ----          | ----          | -----      | -----------  | ----------- |
|type           | object        |            | Type         | Type of sample for this row, i.e. equilibrator (EQU)
|error          | int64         |            | error        | Error flag
|pc_date        | object        | date       | PC Date      | Date in day/month/year formatted as dd/mm/yy
|pc_time        | object        | time       | PC Time      | Time in hour:minute:second formatted as HH:MM:SS
|equ_temp       | float64       | C          | equ temp     | Equilibrator temperature
|std_val        | float64       | um/m       | std val      | Value of standard if run
|co2a_w         | float64       | counts     | CO2a W       | Raw CO2 detector counts of detector a, wet
|co2b_w         | float64       | counts     | CO2b W       | Raw CO2 detector counts of detector b, wet
|co2_um/m       | float64       | μM/M       | CO2 um/m     | Concentration of CO2 calculated by Licor firmware
|h2oa_w         | float64       | counts     | H2Oa W       | Raw H2O detector counts of detector a, wet
|h2ob_w         | float64       | counts     | H2Ob W       | Raw H2O detector counts of detector a, wet
|h2o_mm/m       | float64       | μM/M       | H2O mm/m     | Concentration of H2O calculated by Licor firmware
|licor_temp     | float64       | C          | licor temp   | Temperature of Licor detector
|licor_press    | float64       | hPa        | licor press  | Pressure of Licor detector
|equ_press      | float64       | hPa        | equ press    | Equilibrator pressure
|h2o_flow       | float64       | L/min      | H2O flow     | Flow of water into wetbox
|licor_flow     | float64       | L/min      | licor flow   | Flow of air into Licor
|equ_pump       | float64       | ADC steps  | equ pump     | Equilibrator pump speed
|vent_flow      | float64       | ADC steps  | vent flow    | Vent flow rate
|atm_cond       | float64       | ADC steps  | atm cond     | Atmospheric air conductivity detector in condenser
|equ_cond       | float64       | ADC steps  | equ cond     | Equilibrator air conductivity detector in condenser
|drip_1         | float64       | ADC steps  | drip 1       | Drip sensor at bottom of wet box
|na             | float64       |            | na           |
|cond_temp      | float64       | C          | cond temp    | Condenser temperature
|dry_box_temp   | float64       | C          | dry box temp | Dry box temperature
|deck_press     | float64       | kPa        | Deck_Press   | Deck pressure
|druck_press    | float64       | kPa        | druck        | External Druck pressure in Licor detector cell
|SST            | float64       | C          | SST          | Temperature of inlet seawater (or test tank)
|datetime64_str | object        |            |              | Combination of pc_date and pc_time
|datetime64_ns  | datetime64[ns]|            |              | Datetime object created from datetime64_str
|co2_cal        | float64       | μM/M       | CO2 um/m     | Concentration of CO2 after 4 standard calibation


## Extended Descriptions  
* accepted cycle names include 'ATM', 'EQU', 'STD5z', 'STD1', 'STD2', 'STD3', 'STD4'  
* ppm is approximately equal to mole fraction in micro-moles per mole (μM/M)
* Hectopascal (hPa) is equal to millibar (mb)

## VBA Processing Code Breakdown  
Code imbedded in 'ApplyStandardsCalculatefCO2_wDilutionCorrectionJuly12.xlsm'

| Lines   | Descriptions |
| -----   | ------------ |
| 1-42    | setup variables and data selection
| 43-119  | check for column headers and select them
| 120-145 | select type of Licor data was collected with
| 146-170 | select type of SST data was collected
| 171-190 | select type of SSS data was collected
| 191-205 | select use of Druck or internal Licor Pressure  
| 206-210 | decide if there is atmospheric pressue to calculate fCO2a
| 211-216 | add manual offest and flagging columns
| 217-261 | add and calculate date in mm/dd/yyyy
| 262-562 | calculate standards
| 563-703 | calculate fCO2
| 705-735 | least squares fitting submodule
| 738     | end of file

### Calculate and Apply Standards Code Analysis  
This code finds and interpolates standards, fits a linear fit to the standard response and applies that equation to ATM and EQ samples  

| Lines   | Descriptions |
| -----   | ------------ |
| 264-282 | find concentrations standard values of variables std1Conc, std2Conc, std3Conc, std4Conc
| 283-313 | exclude a standard based on values (std1Conc, etc) found in lines 264-282  
| 318-336 | create columns for calculations of 'std CO2 - dry', 'XCo2sw - dry@eqT', xCO2sw -dry@SST', 'XCO2air -dry'
| 339-    | beginning of calc loop
| 341-344 | `----` make sure there are at least 2 good standard measurements to fit an equation to
| 345-353 | `----` find the pre-sample standard measurements (preStds)
| 355     | `----` check there are at least two good standard measurements to work with
| 356-359 | `----` look for the next set of standard measurements to use as post-sample standards
| 360-373 | `----` found post-sample set of standards measurements (postStds)
| 374-378 | `----` calculate time between pre-sample and post-sample std1 and std4 (assuming 4 standards)
| 379-388 | `--------` check that for each standard there is a good pre and post-sample value
| 389-436 | `--------` check the time between standards is below preset maxiums MaxStdSetInterval = 4 ( was previously 24)</div>
| 389-404 | `--------` set good standard values to pre-known calibration values (from ESRL)
| 405-422 | `--------` if no flags, interpolate a standard measurements based on y = pre and post-sample and x = time diff at current time T
| 423-    | `--------` least squares fit to interpolated standard measurements and standard values, return m and b of y = mx+b
|    -434 | `--------` apply T of current row to interpolation, fit and apply, return to ATM, SW or STD column
| 437-482 | `-----` If interval is too long between standards, use the pre-sample standards and apply least squares as above
| 483-544 | no post-sample standard, use pre-sample standard values and apply least squares as above
| 544-558 | close if statements

### Calculate fCO2 and pCO2 Analysis  
| Lines   | Descriptions |
| -----   | ------------ |
| 566-585 | variable setup
| 586-602 | average equilibrator and atmospheric pressure readings  
| 603-    | beginning of calc loop
| 605-610 | `-----` setup SST values
| 612-616 | `-----` if equilibrator pressure is below 100, set it to eq + atm pressure
| 618-674 | `-----` calculate EQ pH2O, pco2wet, fco2_wet, xco2_dry, and drying corrections
| 676-702 | `-----` calculate ATM pco2, fco2
