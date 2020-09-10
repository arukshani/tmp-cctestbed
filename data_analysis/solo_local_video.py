import common as cmn
import pandas as pd 
from pandas import DataFrame
import experiment as ex
import os 
import subprocess
import json 

import plotly
import plotly.express as px
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import datetime
import plotly.graph_objects as go

def extract_http_pcap(experiment_analyzer, app_type):
    experiment_analyzer.http_pcap

################~~~~~~~~~~OLD~~~~~~~#####################

# def get_local_video_bitrate(experiment_analyzer, app_type):
#     extract_http_pcap(all_analysers[analyser], analyser)
#     filepath = ex.DATAPATH_PROCESSED + "/http-" + app_type + ".csv"
#     df = pd.read_csv(filepath ,sep='\t', 
#                   names=["Time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport"]).assign(bitrate=lambda df: (df['request_uri']
#                                           .str
#                                           .extract('/bunny_(\d+)bps/.*')
#                                           .astype('float'))).dropna()
#     mean = df['bitrate'].mean()/1000000
#     metric = 'bitrate_Mbps'
#     ccas = experiment_analyzer.get_ccalgs
#     data = [[mean, ccas['cca'], app_type, metric]]
#     new_df = pd.DataFrame(data)
#     new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_localVideo_bitrate.csv', header=False, index=False, mode = 'a')

# def get_local_video_avg_bitrate():
#     all_bitrate_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/solo-results/solo_localVideo_bitrate.csv',sep=',', 
#                   names=["bitrate", "cca", "filename", "metric"])
#     all_bitrate_data['group'] = all_bitrate_data['filename'].apply(cmn.include_group_solo)
#     avg_output = all_bitrate_data.groupby('group')['bitrate'].mean()
#     avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_localVideo_bitrate_avg.csv', header=False, index=True)
    
################~~~~~~~~~~~NEW~~~~~~~~~~~~~#####################

def process_http_pcap(experiment_analyzer, app_type):
    experiment_analyzer.http_pcap
    filepath = ex.DATAPATH_PROCESSED + "/http-" + app_type + ".csv"
    df = pd.read_csv(filepath ,sep='\t', 
                  names=["time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport", "range_header"])
    df['path'] = df.request_uri.apply(extract_path)
    df['mime'] = df.path.apply(extract_mime)
    df['itag'] = df.path.apply(extract_itag)
    df['resolution'], df['bitrate_k'] = zip(*df.path.apply(extract_resolution_and_bitrate_k))
    return df 

def extract_path(request_uri):
    path = urlparse.urlparse(request_uri).path
    return path

def extract_mime(path):
    mime = path[1:6]
    return mime

def extract_itag(path):
    itag = path[6:9]
    return "itag-" + itag

# def map_format(itag):
#     return "itag-" + itag

def extract_resolution_and_bitrate_k(path):
    resolution = path.split('_', 3)
    if len(resolution) == 1 :
        return '', ''
    if len(resolution) == 2 :
        return '', resolution[1][:-6] 
    if len(resolution) == 3 :
        return resolution[1], resolution[2][:-6]

def get_itag_description():
    text = ("* 249-webm-audio-only-tiny-57k, 3.74MiB<br>"
            "* 250-webm-audio-only-tiny-75k, 4.93MiB<br>"
            "* 140-m4a-audio-only-tiny-130k, 9.80MiB<br>"
            "* 251-webm-audio-only-tiny-143k, 9.68MiB<br>"
            "* 256-m4a-audio-only-tiny-196k, 14.76MiB<br>"
            "* 258-m4a-audio-only-tiny-389k, 29.34MiB"
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            ""
            )
    return text

def plot_combine_video_itag(all_dfs):

    fig = go.Figure()
    for key in all_dfs:
        df = all_dfs[key]
        df = df.reindex()
        filtered_video_data = df[(df.mime.str.contains('video'))]
        # print(filtered_video_data)
        fig.add_trace(
        go.Scatter(
            x=filtered_video_data["time"],
            y=filtered_video_data["itag"],
            mode='lines+markers',
            name=key
        ))
    fig.update_layout(
            title="Video quality level over time",
            xaxis_title="time(s)",
            yaxis_title="itag value",
            annotations=[
            go.layout.Annotation(
                text=get_itag_description(),
                align='left',
                showarrow=False,
                xref='paper',
                yref='paper',
                x=1.4,
                y=0.8,
                bordercolor='black',
                borderwidth=1
            )
        ]
    )

    filename_plot = ex.DATAPATH_PROCESSED + "/local_video_itag_over_time_"+ "file_name"+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

all_analysers = cmn.get_experiment_analysers("*video-120s*")
# all_analysers = cmn.get_all_experiment_analysers()
all_dfs = {}
for analyser in all_analysers:
    print("~~~~~~~~",analyser, "~~~~~~")
    df = process_http_pcap(all_analysers[analyser], analyser)
    # print(df)
    all_dfs[analyser] = df
# print(all_dfs)
plot_combine_video_itag(all_dfs)

