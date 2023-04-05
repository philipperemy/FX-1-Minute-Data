import argparse
import os
import datetime
import re
import numpy as np
import pandas as pd
import histdata.monthly_merger_api as monthly

TIMEFRAME_CONST = 60 * 1000  # 1 minute
OUTPUT_PATH = "fixoutput"
COLNAMES = ['datetime_str', 'open', 'high', 'low', 'close', 'volume']


def fix_data(dirpath: str, output_format: str, monthly_to_yearly: bool):
    walk_through_data(dirpath, output_format, monthly_to_yearly)


def walk_through_data(dirpath: str, output_format: str, monthly_to_yearly: bool):
    for root, _, files in os.walk(dirpath):
        output_dir = root.replace(dirpath, OUTPUT_PATH, 1)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(root)

        monthly_pairs = {}

        for file in sorted(files):
            file_input = os.path.join(root, file)

            splitted_file_name = os.path.splitext(file_input)

            if splitted_file_name[1] != ".csv":
                continue

            if monthly_to_yearly & monthly.is_monthly_csv(splitted_file_name[0]):
                monthly_pairs = monthly.append_to_monthly_pairs(
                    monthly_pairs, splitted_file_name[0], file_input)
                continue

            print(f"---Parsing file {file_input}---")

            csv_df = pd.read_csv(file_input, names=COLNAMES,
                                 header=None, delimiter=";")

            gap_info_df = get_gap_info(file_input)

            fix(csv_df, gap_info_df, file_input, dirpath, output_format)

        if monthly_to_yearly:
            fix_monthly(monthly_pairs, dirpath, output_format)


def fix(data_df: pd.DataFrame, gap_info_df: pd.DataFrame,
        file_input: str, dirpath: str, output_format: str):

    fixed_df = fix_csv(data_df, gap_info_df)

    file_output = file_input.replace(
        dirpath, OUTPUT_PATH, 1).replace(".csv", "", 1)

    write_output(fixed_df, file_output, output_format)


def fix_monthly(pairs: dict, dirpath: str, output_format: str):
    for pair in pairs.values():
        for year in pair.values():
            df_list = []
            gap_df_list = []

            for file in year:
                print(f"-----Parsing monthly file {file}-----")
                df_monthly = pd.read_csv(file, names=COLNAMES,
                                         header=None, delimiter=";")
                gap_df_monthly = get_gap_info(file)

                df_list.append(df_monthly)
                gap_df_list.append(gap_df_monthly)

            if len(df_list) == 0:
                continue

            yearly_input_file = get_yearly_input_file(year[0])
            print(
                f"---Converting monthly to yearly file {yearly_input_file}---")

            yearly_df = pd.concat(df_list).reset_index(drop=True)
            yearly_gap_df = pd.concat(gap_df_list)

            fix(yearly_df, yearly_gap_df, yearly_input_file, dirpath, output_format)


def get_yearly_input_file(input_file: str):
    split_file = os.path.splitext(input_file)
    return split_file[0][:-2] + split_file[1]


def write_output(fixed_df: pd.DataFrame, file_output: str, output_format: str = "csv"):
    full_output_file = f"{file_output}.{output_format}"

    match output_format:
        case "csv":
            fixed_df.to_csv(full_output_file, sep=";")
        case "h5" | "hdf5":
            fixed_df.to_hdf(full_output_file, key='df', mode='w')
        case _:
            raise Exception(f"Not supported output format: {output_format}")


def fix_csv(data_df: pd.DataFrame, gap_info_df: pd.DataFrame):

    gap_info_df = modify_gap_info(gap_info_df)

    data_df["datetime"] = pd.to_datetime(
        data_df["datetime_str"]).dt.tz_localize('-0500')

    csv_df = data_df.drop("datetime_str", axis=1)

    if not gap_info_df.empty:
        csv_df = pd.merge(csv_df, gap_info_df, on='datetime', how='outer')

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


def get_gap_info(csv_full_file: str):
    file_gap = f"{os.path.splitext(csv_full_file)[0]}.txt"

    with open(file_gap, newline='', encoding="utf-8") as file:
        gap_info_list = []
        for line in file:
            if line.startswith("Gap of"):
                gap_info_list.append(parse_gap_line(line))

        gap_info_df = pd.DataFrame(np.array(gap_info_list), columns=[
            "gap", "datetime_str1", "datetime_str2"])

    return gap_info_df


def parse_gap_line(line: str):
    return re.findall(r'\d+', line)


def datetime_to_unix(_datetime: datetime.datetime):
    return int(datetime.datetime.timestamp(_datetime) * 1000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fix histdata forex 1 minute data')
    parser.add_argument('--dir', metavar='path', required=True,
                        help='directory for the data')
    parser.add_argument('--output_format', metavar='path', default="csv",
                        help='output data format')
    parser.add_argument('--monthly_to_yearly', metavar='path', default=False,
                        action=argparse.BooleanOptionalAction,
                        help='Converts monthly datasets to yearly by concatenating')
    args = parser.parse_args()

    fix_data(dirpath=args.dir, output_format=args.output_format,
             monthly_to_yearly=args.monthly_to_yearly)
