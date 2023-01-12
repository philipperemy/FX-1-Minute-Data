import numpy as np


def append_to_monthly_pairs(pairs: dict, file_name: str, file_input: str):
    pair_copy = pairs.copy()

    year = get_year(file_name)
    pair = get_currency_pair(file_name)

    if not pair in pair_copy:
        pair_copy[pair] = {}

    if not year in pair_copy[pair]:
        pair_copy[pair][year] = np.array([])

    pair_copy[pair][year] = np.append(pair_copy[pair][year], file_input)
    return pair_copy


def is_monthly_csv(file_name: str):
    return is_monthly(get_date(file_name))


def get_date(file_name: str):
    return file_name.split("_")[-1]


def get_currency_pair(file_name: str):
    return file_name.split("_")[2]


def is_monthly(text: str):
    if len(text) == 6:
        return True
    return False


def get_year(file_name: str):
    year_month = get_date(file_name)
    if is_monthly(year_month):
        return year_month[0:4]
    return year_month
