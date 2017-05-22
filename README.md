# FX 1-Minute Dataset / Price API

## Data files: Detailed Specification

Here you can find all the details regarding any downloaded file (Generic ASCII in M1 Bars).

As example, in `DAT_ASCII_EURUSD_M1_201202.csv`:

```
20120201 000000;1.306600;1.306600;1.306560;1.306560;0
20120201 000100;1.306570;1.306570;1.306470;1.306560;0
20120201 000200;1.306520;1.306560;1.306520;1.306560;0
20120201 000300;1.306610;1.306610;1.306450;1.306450;0
20120201 000400;1.306470;1.306540;1.306470;1.306520;0
20120201 000500;1.306510;1.306650;1.306510;1.306600;0
20120201 000600;1.306610;1.306760;1.306610;1.306650;0
```

Row Fields:
`DateTime Stamp;Bar OPEN Bid Quote;Bar HIGH Bid Quote;Bar LOW Bid Quote;Bar CLOSE Bid Quote;Volume`

DateTime Stamp Format:
`YYYYMMDD HHMMSS`

Legend:
- YYYY – Year
- MM – Month (01 to 12)
- DD – Day of the Month
- HH – Hour of the day (in 24h format)
- MM – Minute
- SS – Second, in this case it will be allways 00

TimeZone: Eastern Standard Time (EST) time-zone *WITHOUT* Day Light Savings adjustments

## Data files provided: Early 2000 to May 2017
```
git clone https://github.com/philipperemy/FX-1-Minute-Data.git fx
cd fx/data # contains the FULL dataset of all FX pairs.
```

## How to use the API?

`download_all_fx_data.py` re-downloads all the FULL FX dataset (~4 hours to complete). It's a good example on how to use the FX API.

Use this function for downloading data related to the CURRENT year. E.g. if you're interested in data of 2017 and we're in 2017, use this one.
`api.download_fx_m1_data(year='2016', month='7', pair='eurgbp')`

This function is used to download one year of data in one block. Use it for all the years EXCEPT the current one. E.g. if you're interested in data of 2004 and we're in 2017, use this one.
`api.download_fx_m1_data_year(year='2016', pair='eurgbp')`

All the files are retrieved from: http://www.histdata.com/
