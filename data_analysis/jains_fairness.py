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

def calculate_jfi(combination):
    all_goodput_data = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_20/JFI/goodput-' + combination + '.csv',sep=',', 
                  names=["port", "goodput", "filename", "metric"])
    filtered_video_data = all_goodput_data[(all_goodput_data.port != 5202)]
    filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    video_goodput_sum = filtered_video_data.groupby('filename').agg({'goodput': ['sum']}).reset_index()
    # print(video_goodput_sum)
    # print(filtered_iperf_data)

    new_df = filtered_iperf_data['port'], filtered_iperf_data['filename'], filtered_iperf_data['goodput']
    headers = ["port", "filename", "goodput"]
    df3 = pd.concat(new_df, axis=1, keys=headers)
    # result = pd.concat(new_df)
    print(df3)

    video_goodput_sum["port"] = 1111
    video_df = video_goodput_sum["port"], video_goodput_sum['filename'], video_goodput_sum['goodput']
    headers1 = ["port", "filename", "goodput"]
    test = pd.concat(video_df, axis=1, keys=headers1)
    print(test)

    #Write to file and read to remove headers

    # all_df = [df3, test]
    # result = pd.concat(all_df)
    # print(result)

calculate_jfi("iperf-localVideo")