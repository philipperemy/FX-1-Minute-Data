# FX 1-Minute Dataset

Retrieval made easy.

## Data specification

This repository contains:
- A dataset of all the FX prices (1-minute data) from 2000 to late June 2019, in Generic ASCII.
- Contains some commodities:
   - WTI/USD = WEST TEXAS INTERMEDIATE in USD
   - BCO/USD = BRENT CRUDE OIL in USD
- Contains some indexes:
   - SPX/USD = S&P 500 in USD
   - JPX/JPY = NIKKEI 225 in JPY
   - NSX/USD = NASDAQ 100 in USD
   - FRX/EUR = FRENCH CAC 40 in EUR
   - UDX/USD = US DOLLAR INDEX in USD
   - UKX/GBP = FTSE 100 in GBP
   - GRX/EUR = DAX 30 in EUR
   - AUX/AUD = ASX 200 in AUD
   - HKX/HKD = HAN SENG in HKD
E   - TX/EUR = EUROSTOXX 50 in EUR
- A set of functions to download the historical prices yourself.

All the data is retrieved from: http://www.histdata.com/

Any file in a dataset is zipped and contains: 
- a CSV (semicolon separated file).
- a status report (containing some meta data such as gaps).

Any CSV file looks like this:

```bash
20120201 000000;1.306600;1.306600;1.306560;1.306560;0
20120201 000100;1.306570;1.306570;1.306470;1.306560;0
20120201 000200;1.306520;1.306560;1.306520;1.306560;0
20120201 000300;1.306610;1.306610;1.306450;1.306450;0
20120201 000400;1.306470;1.306540;1.306470;1.306520;0
[...]
```

Headers are not included in the CSV files. They are:

```bash
DateTime Stamp;Bar OPEN Bid Quote;Bar HIGH Bid Quote;Bar LOW Bid Quote;Bar CLOSE Bid Quote;Volume
```

### DateTime Stamp

Format:
`YYYYMMDD HHMMSS`

Legend:
- YYYY – Year
- MM – Month (01 to 12)
- DD – Day of the Month
- HH – Hour of the day (in 24h format)
- MM – Minute
- SS – Second, in this case it will be always 00

TimeZone: Eastern Standard Time (EST) time-zone *WITHOUT* Day Light Savings adjustments

### OPEN Bid Quote

The open (first) bid quote of the 1M bin.

### HIGH Bid Quote

The highest bid quote of the 1M bin.


### LOW Bid Quote

The lowest bid quote of the 1M bin.

### CLOSE Bid Quote

The close (last) bid quote of the 1M bin.

### Volume

Number of lots. From what I saw it's always 0 here.

## Data files provided: Early 2000 to nowadays

Available here: [2000-Jun2019](2000-Jun2019)

## How to download your own dataset?

This command will re-download all the FULL FX dataset up to today (expect the runtime to be ~4 hours).

```bash
pip install -r requirements.txt
python download_all_fx_data.py
```

## API

Then, of course, you can use directly the API in `api.py`. There are two endpoints depending on what you query:

- If you want data for the current year, then you have to query it per month.

```python
def download_fx_m1_data(year='2016', month='7', pair='eurgbp'):
    """
    Download 1-Minute FX data per month.
    :param year: Trading year. Format is 2016.
    :param month: Trading month. Format is 7 or 12.
    :param pair: Currency pair. Example: eurgbp.
    :return: ZIP Filename.
    """
```

- If you are interested in data for the past years, then you can query per year.

```python
def download_fx_m1_data_year(year='2016', pair='eurgbp'):
    """
    Download 1-Minute FX data per year.
    :param year: Trading year. Format is 2016.
    :param month: Trading month. Format is 7 or 12.
    :param pair: Currency pair. Example: eurgbp.
    :return: ZIP Filename.
    """
```
