import common as cmn
import pandas as pd 
from pandas import DataFrame
import experiment as ex
import os 
import subprocess
import json

import plotly.express as px
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import datetime
import plotly


def get_combi_iperf_avg_and_std(combination):
    all_goodput_data = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_20/std_dev/goodput-' + combination + '.csv',sep=',', 
                  names=["port", "goodput", "filename", "metric"])
    filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    filtered_iperf_data['group'] = filtered_iperf_data['filename'].apply(cmn.include_group_combi)
    # print(filtered_iperf_data)
    # avg_output = filtered_iperf_data.groupby('group')['goodput'].mean()
    # stddev_output = filtered_iperf_data.groupby('group')['goodput'].std()
    grouped_single = filtered_iperf_data.groupby('group').agg({'goodput': ['mean', 'std']})
    print(grouped_single)
    # print(stddev_output.iloc[0])
    grouped_single.to_csv('/Users/rukshani/Documents/DATASET/WEEK_20/std_dev/stddev-goodput-' + combination + '.csv', header=False, index=True)
    # stddev_output.to_csv('/Users/rukshani/Documents/DATASET/WEEK_20/std_dev/stddev-goodput-' + combination + '.csv', header=False, index=True)


def get_solo_iperf_avg_and_std():
    all_goodput_data = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_20/std_dev/solo_iperf_goodput.csv',sep=',', 
                  names=["port", "goodput", "cca", "filename", "metric"])
    all_goodput_data['group'] = all_goodput_data['filename'].apply(cmn.include_group_solo)
    # avg_output = all_goodput_data.groupby('group')['goodput'].mean()
    grouped_single = all_goodput_data.groupby('group').agg({'goodput': ['mean', 'std']})
    grouped_single.to_csv('/Users/rukshani/Documents/DATASET/WEEK_20/std_dev/stddev_solo_iperf.csv', header=False, index=True)

# get_combi_iperf_avg_and_std("iperf-webVideo")
# get_solo_iperf_avg_and_std()