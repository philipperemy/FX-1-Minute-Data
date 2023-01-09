import argparse
from io import TextIOWrapper
import os
import datetime
import re
import numpy as np
import pandas as pd

TIMEFRAME_CONST = 60 * 1000  # 1 minute
OUTPUT_PATH = "fixoutput"


def fix_data(dirpath: str, output_format: str):
    walk_through_data(dirpath, output_format)


def walk_through_data(dirpath: str, output_format: str):
    for root, _, files in os.walk(dirpath):
        output_dir = root.replace(dirpath, OUTPUT_PATH, 1)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(root)

        for file in files:
            file_input = os.path.join(root, file)

            if os.path.splitext(file_input)[1] != ".csv":
                continue

            fixed_df = fix_csv(file_input)

            file_output = file_input.replace(
                dirpath, OUTPUT_PATH, 1).replace(".csv", "", 1)

            write_output(fixed_df, file_output, output_format)


def write_output(fixed_df: pd.DataFrame, file_output: str, output_format: str = "csv"):
    full_output_file = f"{file_output}.{output_format}"

    match output_format:
        case "csv":
            fixed_df.to_csv(full_output_file, sep=";")
        case "h5" | "hdf5":
            fixed_df.to_hdf(full_output_file, key='df', mode='w')
        case _:
            raise Exception(f"Not supported output format: {output_format}")


def fix_csv(file_input: str):
    splited_file = os.path.splitext(file_input)

    file_gap = f"{splited_file[0]}.txt"

    print(f"---Parsing file {file_input}---")

    colnames = ['datetime_str', 'open', 'close', 'high', 'low', 'volume']
    csv_df = pd.read_csv(file_input, names=colnames,
                         header=None, delimiter=";")

    with open(file_gap, newline='', encoding="utf-8") as gapfile:
        gap_info = pd.DataFrame(get_gap_info(gapfile), columns=[
                                "gap", "datetime_str1", "datetime_str2"])

    gap_info = modify_gap_info(gap_info)

    csv_df["datetime"] = pd.to_datetime(
        csv_df["datetime_str"]).dt.tz_localize('-0500')

    csv_df = csv_df.drop("datetime_str", axis=1)

    if not gap_info.empty:
        csv_df = pd.merge(csv_df, gap_info, on='datetime', how='outer')

    resampled_df = apply_resample(csv_df)

    resampled_df['unix'] = resampled_df.apply(
        lambda x: datetime_to_unix(x['datetime']), axis=1)

    resampled_df["datetime"] = resampled_df["unix"]
    resampled_df = resampled_df.drop("unix", axis=1).set_index("datetime")

    return resampled_df


def apply_resample(df1: pd.DataFrame):
    df2 = df1.drop_duplicates(subset=["datetime"])
    df2 = (df2.assign(date=df1["datetime"].dt.date)
           .set_index('datetime')
           .groupby('date', group_keys=True)
           .apply(lambda x: x.resample('1Min').asfreq())
           )
    df2["isgap"] = df2['open'].isnull()
    df2 = (df2.ffill()
           .reset_index('date', drop=True)
           .drop('date', axis=1)
           .reset_index()
           )
    return df2


def modify_gap_info(gap_info: pd.DataFrame):
    gap_info["datetime1"] = pd.to_datetime(
        gap_info["datetime_str1"]).dt.tz_localize('-0500').dt.floor("T")

    gap_info["datetime2"] = pd.to_datetime(
        gap_info["datetime_str2"]).dt.tz_localize('-0500').dt.floor("T")

    mask1 = (gap_info["datetime2"].dt.date -
             gap_info["datetime1"].dt.date).dt.days > 0
    mask2 = (gap_info["datetime2"] - gap_info["datetime1"]
             ).astype('timedelta64[m]') < 300

    mask = mask1 & mask2

    gap_info = gap_info[mask]

    gap_info = gap_info.drop("gap", axis=1).drop("datetime_str1",
                                                 axis=1).drop("datetime_str2", axis=1)

    gap_info = gap_info.stack().reset_index()
    gap_info = (gap_info.set_index(0)
                .groupby('level_0', group_keys=True)
                .apply(lambda x: x.resample('1Min').ffill())
                .drop("level_0", axis=1)
                .drop("level_1", axis=1)
                .reset_index()
                .drop("level_0", axis=1)
                .reset_index(drop=True)
                .rename(columns={0: "datetime"})
                )
    return gap_info


def get_gap_info(file: TextIOWrapper):
    gap_info_list = []
    for line in file:
        if line.startswith("Gap of"):
            gap_info_list.append(parse_gap_line(line))
    return np.array(gap_info_list)


def parse_gap_line(line: str):
    return re.findall(r'\d+', line)


def datetime_to_unix(_datetime: datetime):
    return int(datetime.datetime.timestamp(_datetime) * 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fix histdata forex 1 minute data')
    parser.add_argument('--dir', metavar='path', required=True,
                        help='directory for the data')
    parser.add_argument('--output_format', metavar='path', default="csv",
                        help='output data format')
    args = parser.parse_args()
    fix_data(dirpath=args.dir, output_format=args.output_format)
