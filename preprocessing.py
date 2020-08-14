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


def symmetric_normalize(current, previous):
    if current > previous:
        return current / previous - 1
    return - previous / current + 1


def prepare_data(symbol_folder, name, overwrite):
    path = os.path.join(symbol_folder, name.replace('.zip', '.csv'))
    numpy_path = path.replace('.csv', '.npy')
    if not path.endswith('.csv') or (not overwrite and os.path.exists(numpy_path)):
        return
    df0 = pd.read_csv(path, sep=';', header=None)
    datetime_objects = [datetime.datetime.strptime(timestamp, "%Y%m%d %H%M%S") for timestamp in df0[0]]
    price = df0[4]
    df0[0] = [obj.timestamp() for obj in datetime_objects]
    df0[1] = [obj.year for obj in datetime_objects]
    df0[2] = [obj.month for obj in datetime_objects]
    df0[3] = [obj.day for obj in datetime_objects]
    df0[4] = [obj.hour for obj in datetime_objects]
    df0[5] = [obj.minute for obj in datetime_objects]
    df0[6] = [0] + [current / previous - 1 for current, previous in zip(price[1:], price)]
    df0[7] = [0] + [symmetric_normalize(current, previous) for current, previous in zip(price[1:], price)]
    df0[8] = price
    df1 = df0.copy(deep=True)
    df1[6] = 1 / (1 + df1[6]) - 1
    df1[7] = -df1[7]
    df1[8] = 1 / df1[8]
    f64df0 = df0.to_numpy(dtype='float64')
    f64df1 = df1.to_numpy(dtype='float64')
    np.save(numpy_path, f64df0)
    np.save(numpy_path + 'i', f64df1)  # npyi -> npy inverted


def concatenate(folder, ending):
    files = sorted([name for name in os.listdir(folder) if name.endswith(ending)])
    if not files:
        return
    files = [os.path.join(folder, name) for name in files]
    numpy = [np.load(name) for name in files]
    numpy = np.concatenate(numpy, axis=0)
    np.save(f'{folder}{ending}', numpy)


def sub_iterator(overwrite, output_folder, symbol, functions):
    symbol_folder = os.path.join(output_folder, symbol)
    if not os.path.isdir(symbol_folder):
        return
    for name in os.listdir(symbol_folder):
        for fn in functions:
            fn(symbol_folder, name, overwrite)
    concatenate(symbol_folder, '.npy')
    concatenate(symbol_folder, '.npyi.npy')
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
