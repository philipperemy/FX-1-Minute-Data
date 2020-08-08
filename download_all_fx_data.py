import csv
import datetime
import multiprocessing
import os
import sys
import time

from histdata.api import download_hist_data


def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class RateTracker:
    def __init__(self):
        self.start_time = time.time()
        self.instances = 0

    def __call__(self):
        self.instances += 1
        return (time.time() - self.start_time) / self.instances


def process_currency(row, start_year):
    currency_pair_name, pair, history_first_trading_month = row
    year = int(history_first_trading_month[0:4])
    sys.__stdout__.write(f'Started {currency_pair_name}')
    output_folder = os.path.join('output', pair)
    mkdir_p(output_folder)
    local_rate = RateTracker()
    total_years = start_year - year
    try:
        while True:
            try:
                download_hist_data(year=year, pair=pair,
                                   output_directory=output_folder)
            except AssertionError:
                month = 1
                while month <= 12:
                    download_hist_data(year=str(year), month=str(month),
                                       pair=pair,
                                       output_directory=output_folder)
                    month += 1
            year += 1
            sys.__stdout__.write(f'[{currency_pair_name}]'
                                 f'[{local_rate.instances}/{total_years}] '
                                 f'Current: {local_rate():.2f}s/Year')
    except Exception:
        pass
    sys.__stdout__.write(f"FINISHED {currency_pair_name} - {year} years downloaded")


def download_all():
    sys.stdout = open("/dev/null", 'w')
    start_year = datetime.datetime.now().year
    with open('pairs.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # skip the headers
        pool = [multiprocessing.Process(target=process_currency, args=(row, start_year)) for row in reader]
    for p in pool:
        p.start()
    for p in pool:
        p.join()
    sys.stdout = sys.__stdout__


if __name__ == '__main__':
    download_all()
