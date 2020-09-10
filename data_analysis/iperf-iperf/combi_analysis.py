# Bring your packages onto the path
import sys, os
sys.path.append('data_analysis')

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

def get_goodput(experiment_analyzer, app_type, combination): #Goodput of each flow in a single experiment
    goodput = 0
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        # print("Duration>>", (dequeued.index.max() - dequeued.index.min()).total_seconds())
        goodput = (dequeued.groupby('src')['datalen'].sum() * cmn.BYTES_TO_BITS * cmn.BITS_TO_MEGABITS) / (dequeued.index.max() - dequeued.index.min()).total_seconds()
        goodput.to_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv', header=False, index=True)
        new_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv',sep=',', names=["Port", "Performance"])
        new_df['app_type'] = app_type
        new_df['Metric'] = 'goodput_Mbps'
        os.remove(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv')
        new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-results/goodput-' + combination + '.csv', header=False, index=False, mode = 'a')
    return goodput

def get_iperf_avg_goodput(combination):
    all_goodput_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/combi-results/goodput-' + combination + '.csv',sep=',', 
                  names=["port", "goodput", "filename", "metric"])
    all_goodput_data['group'] = all_goodput_data['filename'].apply(cmn.include_group_combi)
    avg_output = all_goodput_data.groupby(['group','port'])['goodput'].mean()
    write_to_file(avg_output, combination)

def write_to_file(avg_output, combination):
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-results/avg-goodput-' + combination + '.csv', header=False, index=True, mode = 'a')


# all_analysers = cmn.get_experiment_analysers("*iperf-iperftest*")
# # all_analysers = cmn.get_all_experiment_analysers()
# for analyser in all_analysers:
#     print("~~~~~~~~",analyser, "~~~~~~")
#     get_goodput(all_analysers[analyser], analyser, "iperf-iperf")

get_iperf_avg_goodput("iperf-iperf")