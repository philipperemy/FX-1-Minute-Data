import csv
import os
import shutil

from api import download_fx_m1_data, download_fx_m1_data_year


def mkdir_p(path):
    import errno
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


if __name__ == '__main__':

    with open('pairs.csv', 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader, None)  # skip the headers
        for row in reader:
            currency_pair_name, currency_pair_code, history_first_trading_month = row
            year = int(history_first_trading_month[0:4])
            print(currency_pair_name)
            output_folder = os.path.join('output', currency_pair_code)
            mkdir_p(output_folder)
            try:
                while True:
                    could_download_full_year = False
                    try:
                        output_filename = download_fx_m1_data_year(year, currency_pair_code)
                        shutil.move(output_filename, os.path.join(output_folder, output_filename))
                        could_download_full_year = True
                    except:
                        pass  # lets download it month by month.
                    month = 1
                    while not could_download_full_year and month <= 12:
                        output_filename = download_fx_m1_data(str(year), str(month), currency_pair_code)
                        shutil.move(output_filename, os.path.join(output_folder, output_filename))
                        month += 1
                    year += 1
            except Exception as e:
                print('[DONE] for currency', currency_pair_name)
