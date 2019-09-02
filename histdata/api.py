import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


class TimeFrame:
    ONE_MINUTE = 'M1'
    TICK_DATA = 'T'
    TICK_DATA_LAST = 'T_LAST'
    TICK_DATA_BID = 'T_BID'
    TICK_DATA_ASK = 'T_ASK'


class Platform:
    META_TRADER = 'MT'
    GENERIC_ASCII = 'ASCII'
    EXCEL = 'XLSX'
    NINJA_TRADER = 'NT'
    META_STOCK = 'MS'


class URL:
    META_TRADER = 'https://www.histdata.com/download-free-forex-historical-data/?/metatrader/1-minute-bar-quotes/'
    ASCII_1M = 'https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/'
    ASCII_TICK_DATA = 'https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/'
    EXCEL = 'https://www.histdata.com/download-free-forex-historical-data/?/excel/1-minute-bar-quotes/'
    NINJA_TRADER = 'https://www.histdata.com/download-free-forex-historical-data/?/ninjatrader/1-minute-bar-quotes/'
    NINJA_TRADER_LAST_QUOTES = 'https://www.histdata.com/download-free-forex-historical-data/?/ninjatrader/tick-last-quotes/'
    NINJA_TRADER_BID_QUOTES = 'https://www.histdata.com/download-free-forex-historical-data/?/ninjatrader/tick-bid-quotes/'
    NINJA_TRADER_ASK_QUOTES = 'https://www.histdata.com/download-free-forex-historical-data/?/ninjatrader/tick-ask-quotes/'
    META_STOCK = 'https://www.histdata.com/download-free-forex-historical-data/?/metastock/1-minute-bar-quotes/'


def get_prefix_referer(time_frame, platform):
    if time_frame == TimeFrame.TICK_DATA and platform == Platform.GENERIC_ASCII:
        return URL.ASCII_TICK_DATA
    elif time_frame == TimeFrame.TICK_DATA_LAST and platform == Platform.NINJA_TRADER:
        return URL.NINJA_TRADER_LAST_QUOTES
    elif time_frame == TimeFrame.TICK_DATA_BID and platform == Platform.NINJA_TRADER:
        return URL.NINJA_TRADER_BID_QUOTES
    elif time_frame == TimeFrame.TICK_DATA_ASK and platform == Platform.NINJA_TRADER:
        return URL.NINJA_TRADER_ASK_QUOTES
    elif time_frame == TimeFrame.ONE_MINUTE and platform == Platform.GENERIC_ASCII:
        return URL.ASCII_1M
    elif time_frame == TimeFrame.ONE_MINUTE and platform == Platform.META_TRADER:
        return URL.META_TRADER
    elif time_frame == TimeFrame.ONE_MINUTE and platform == Platform.EXCEL:
        return URL.EXCEL
    elif time_frame == TimeFrame.ONE_MINUTE and platform == Platform.NINJA_TRADER:
        return URL.NINJA_TRADER
    elif time_frame == TimeFrame.ONE_MINUTE and platform == Platform.META_STOCK:
        return URL.META_STOCK
    else:
        raise Exception('Invalid combination of time_frame and platform.')


def get_referer(referer_prefix, pair, year, month):
    if month is not None:
        return referer_prefix + '{}/{}/{}'.format(pair.lower(), year, month)
    return referer_prefix + '{}/{}'.format(pair.lower(), year)


def download_hist_data(year='2016',
                       month=None,
                       pair='eurusd',
                       time_frame=TimeFrame.ONE_MINUTE,
                       platform=Platform.GENERIC_ASCII,
                       output_directory='.',
                       verbose=True):
    """
    Download 1-Minute FX data per month.
    :param year: Trading year. Format is 2016.
    :param month: Trading month. Format is 7 or 12.
    :param pair: Currency pair. Example: eurgbp.
    :param time_frame: M1 (one minute) or T (tick data)
    :param platform: MT, ASCII, XLSX, NT, MS
    :param output_directory: Where to dump the data.
    :return: ZIP Filename.
    """

    tick_data = time_frame.startswith('T')
    if (not tick_data) and ((int(year) >= datetime.now().year and month is None) or
                            (int(year) <= datetime.now().year - 1 and month is not None)):
        msg = 'For the current year, please specify month=7 for example.\n'
        msg += 'For the past years, please query per year with month=None.'
        raise AssertionError(msg)

    prefix_referer = get_prefix_referer(time_frame, platform)
    referer = get_referer(prefix_referer, pair.lower(), year, month)

    # Referer is the most important thing here.
    headers = {'Host': 'www.histdata.com',
               'Connection': 'keep-alive',
               'Content-Length': '104',
               'Cache-Control': 'max-age=0',
               'Origin': 'https://www.histdata.com',
               'Upgrade-Insecure-Requests': '1',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Referer': referer}

    if verbose:
        print(referer)
    r1 = requests.get(referer, allow_redirects=True)
    assert r1.status_code == 200, 'Make sure the website www.histdata.com is up.'

    soup = BeautifulSoup(r1.content, 'html.parser')
    try:
        token = soup.find('input', {'id': 'tk'}).attrs['value']
        assert len(token) > 0
    except:
        raise AssertionError('There is no token. Please make sure your year/month/pair is correct.'
                             'Example is year=2016, month=7, pair=eurgbp')

    data = {'tk': token,
            'date': str(year),
            'datemonth': '{}{}'.format(year, str(month).zfill(2)) if month is not None else str(year),
            'platform': platform,
            'timeframe': time_frame,
            'fxpair': pair.upper()}
    r = requests.post(url='https://www.histdata.com/get.php',
                      data=data,
                      headers=headers)

    assert len(r.content) > 0, 'No data could be found here.'
    if verbose:
        print(data)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    if month is None:
        output_filename = 'DAT_{}_{}_{}_{}.zip'.format(platform, pair.upper(), time_frame, str(year))
    else:
        output_filename = 'DAT_{}_{}_{}_{}.zip'.format(platform, pair.upper(), time_frame,
                                                       '{}{}'.format(year, str(month).zfill(2)))
    output_filename = os.path.join(output_directory, output_filename)
    with open(output_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    if verbose:
        print('Wrote to {}'.format(output_filename))
    return output_filename


if __name__ == '__main__':
    # print(download_hist_data(year='2019', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_LAST))
    # print(download_hist_data(year='2019', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_ASK))
    # print(download_hist_data(year='2019', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_BID))
    # print(download_hist_data(year='2019', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2019', month='6', platform=Platform.GENERIC_ASCII, time_frame=TimeFrame.TICK_DATA))
    # print(download_hist_data(year='2019', month='6', platform=Platform.EXCEL, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2019', month='6', platform=Platform.META_TRADER, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2019', month='6', platform=Platform.META_STOCK, time_frame=TimeFrame.ONE_MINUTE))

    # print(
    #     download_hist_data(year='2018', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_LAST))
    # print(
    #     download_hist_data(year='2018', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_ASK))
    # print(
    #     download_hist_data(year='2018', month='6', platform=Platform.NINJA_TRADER, time_frame=TimeFrame.TICK_DATA_BID))
    # print(download_hist_data(year='2018', month=None, platform=Platform.NINJA_TRADER, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2018', month='2', platform=Platform.GENERIC_ASCII, time_frame=TimeFrame.TICK_DATA))
    # print(download_hist_data(year='2018', month=None, platform=Platform.EXCEL, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2018', month=None, platform=Platform.META_TRADER, time_frame=TimeFrame.ONE_MINUTE))
    # print(download_hist_data(year='2018', month=None, platform=Platform.META_STOCK, time_frame=TimeFrame.ONE_MINUTE))
    pass
