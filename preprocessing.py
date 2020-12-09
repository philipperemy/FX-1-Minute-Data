import datetime
import multiprocessing
import os
import zipfile

import numpy as np
import pandas as pd


def unzip(symbol_folder, name, overwrite):
    if (not name.endswith('.zip') or
            (not overwrite and os.path.exists(os.path.join(symbol_folder, name.replace('.zip', '.csv'))))):
        return
    with zipfile.ZipFile(os.path.join(symbol_folder, name), 'r') as f:
        f.extractall(symbol_folder)


def norm(current_list, previous_list):
    return zip(*((current / previous - 1, (current / previous - 1) if current > previous else (- previous / current + 1)) for current, previous in zip(current_list, previous_list)))


def save(path, high, low, close):
    np.save(path, 
            np.array([*norm(high[1:], close),
                      *norm(low[1:], close),
                      *norm(close[1:], close)], 
                     dtype=np.float64))


def prepare_data(symbol_folder, name, overwrite):
    path = os.path.join(symbol_folder, name.replace('.zip', '.csv'))
    numpy_path = path.replace('.csv', '')
    if not path.endswith('.csv') or (not overwrite and os.path.exists(numpy_path)):
        return
    dataframe = pd.read_csv(path, sep=';', header=None)
    high, low, close = dataframe[2], dataframe[3], dataframe[4]
    save(numpy_path, high, low, close)
    save(numpy_path + 'i', 1 / low, 1 / high, 1 / close)


def concatenate(folder, ending):
    files = sorted([name for name in os.listdir(folder) if name.endswith(ending)])
    if not files:
        return
    files = [os.path.join(folder, name) for name in files]
    numpy = [np.load(name) for name in files]
    numpy = np.concatenate(numpy, axis=1)
    np.save(f'{folder}{ending}', numpy)


def sub_iterator(overwrite, output_folder, symbol, functions):
    symbol_folder = os.path.join(output_folder, symbol)
    if not os.path.isdir(symbol_folder):
        return
    for name in os.listdir(symbol_folder):
        for fn in functions:
            fn(symbol_folder, name, overwrite)
    concatenate(symbol_folder, '.npy')
    concatenate(symbol_folder, 'i.npy')
    print(f"FINISHED {symbol}")


def iterate(overwrite, *functions):
    output_folder = os.path.join(os.getcwd(), "output")
    args = tuple((overwrite, output_folder, symbol, functions) for symbol in os.listdir(output_folder))
    pool = multiprocessing.Pool(6)
    pool.starmap(sub_iterator, args)
    pool.close()
    pool.join()
    pool.terminate()


if __name__ == '__main__':
    iterate(True, unzip, prepare_data)
