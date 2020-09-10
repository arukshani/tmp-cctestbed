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
 

def include_ccalg(port, ports):
    return ports[port]

#Works for iperf solo 
def get_goodput_of_solo_exp(experiment_analyzer, app_type): #Goodput of each flow in a single experiment
    goodput = 0
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        # print("Duration>>", (dequeued.index.max() - dequeued.index.min()).total_seconds())
        goodput = (dequeued.groupby('src')['datalen'].sum() * cmn.BYTES_TO_BITS * cmn.BITS_TO_MEGABITS) / (dequeued.index.max() - dequeued.index.min()).total_seconds()
        goodput.to_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv', header=False, index=True)
        new_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv',sep=',', names=["Port", "Performance"])
        ports = experiment_analyzer.flow_receiver_ports
        new_df['ccalg'] = new_df.apply(lambda row: include_ccalg(row.Port.astype(int), ports), axis=1)
        new_df['app_type'] = app_type
        new_df['Metric'] = 'goodput_Mbps'
        os.remove(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv')
        new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_iperf_goodput.csv', header=False, index=False, mode = 'a')
    return goodput

def get_iperf_avg_goodput():
    all_goodput_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/solo-results/solo_iperf_goodput.csv',sep=',', 
                  names=["port", "goodput", "cca", "filename", "metric"])
    all_goodput_data['group'] = all_goodput_data['filename'].apply(cmn.include_group_solo)
    avg_output = all_goodput_data.groupby('group')['goodput'].mean()
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_iperf_goodput_avg.csv', header=False, index=True)
    # avg_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_avg.csv',sep=',', names=["group", "goodput"])

#Solo
def get_webpage_load_time(experiment_analyzer, app_type):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        port = dequeued.src.unique().item(0)
        webpage_port_row = dequeued.loc[dequeued['src'] == port]
        page_load_time = (webpage_port_row.index.max() - webpage_port_row.index.min()).total_seconds()
        # page_load_time = (dequeued.index.max() - dequeued.index.min()).total_seconds()
        ccas = experiment_analyzer.get_ccalgs
        #app_type
        metric = 'time_s'
        data = [[port, page_load_time, ccas['cca'], app_type, metric]] 
        # Create the pandas DataFrame 
        df = pd.DataFrame(data)
        # print(df)
        df.to_csv(ex.DATAPATH_PROCESSED +'/solo-results/summary_webpage_loadtime.csv', header=False, index=False, mode = 'a')

def extract_http_pcap(experiment_analyzer, app_type):
    experiment_analyzer.http_pcap
    # list_files = subprocess.run(["ls", "-l"])

def get_local_video_bitrate(experiment_analyzer, app_type):
    extract_http_pcap(all_analysers[analyser], analyser)
    filepath = ex.DATAPATH_PROCESSED + "/http-" + app_type + ".csv"
    df = pd.read_csv(filepath ,sep='\t', 
                  names=["Time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport"]).assign(bitrate=lambda df: (df['request_uri']
                                          .str
                                          .extract('/bunny_(\d+)bps/.*')
                                          .astype('float'))).dropna()
    # print(df)
    # per_flow_median = (df.groupby(['srcip','scrport','dstip','dstport'])['bitrate'].mean().median())
    # per_flow_mean = (df.groupby(['srcip','scrport','dstip','dstport'])['bitrate'].mean()/1000000)
    # median = df['bitrate'].median()/1000000
    mean = df['bitrate'].mean()/1000000
    metric = 'bitrate_Mbps'
    ccas = experiment_analyzer.get_ccalgs
    data = [[mean, ccas['cca'], app_type, metric]]
    new_df = pd.DataFrame(data)
    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_localVideo_bitrate.csv', header=False, index=False, mode = 'a')

def get_local_video_avg_bitrate():
    all_bitrate_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/solo-results/solo_localVideo_bitrate.csv',sep=',', 
                  names=["bitrate", "cca", "filename", "metric"])
    all_bitrate_data['group'] = all_bitrate_data['filename'].apply(cmn.include_group_solo)
    avg_output = all_bitrate_data.groupby('group')['bitrate'].mean()
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_localVideo_bitrate_avg.csv', header=False, index=True)
    # avg_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_avg.csv',sep=',', names=["group", "goodput"])

###YOUTUBE ANALYSIS###################

def extract_youtube_requests(experiment_analyzer, app_type):
    experiment_analyzer.server_tcpdump_youtube

def request_parse(Request):
    request = unquote(Request)
    return request

def extract_mime(Request):
    parsed = urlparse.urlparse(Request)
    params = urlparse.parse_qsl(parsed.query)
    for x,y in params:
        if(x == 'mime'):
            return y
        else:
            continue

def extract_itag(Request):
    parsed = urlparse.urlparse(Request)
    params = urlparse.parse_qsl(parsed.query)
    for x,y in params:
        if(x == 'itag'):
            return y
        else:
            continue

def map_format(itag):
    return "itag-" + itag

def extract_range(Request):
    parsed = urlparse.urlparse(Request)
    params = urlparse.parse_qsl(parsed.query)
    for x,y in params:
        if(x == 'range'):
            return y
        else:
            continue

def extract_clen(Request):
    parsed = urlparse.urlparse(Request)
    params = urlparse.parse_qsl(parsed.query)
    for x,y in params:
        if(x == 'clen'):
            return int(y) * cmn.BYTES_TO_MEGABYTES
        else:
            continue

def get_range(Request):
    parsed = urlparse.urlparse(Request)
    params = urlparse.parse_qsl(parsed.query)
    for x,y in params:
        if(x == 'range'):
            vals = y.split('-', 2)
            val0 = int(vals[0])
            val1 = int(vals[1])
            return (val1 - val0) * cmn.BYTES_TO_MEGABYTES
        else:
            continue

def process_youtube_pcap(experiment_analyzer, app_type):
    filepath = ex.DATAPATH_PROCESSED + "/server-tcpdump-" + app_type + ".csv"
    df = pd.read_csv(filepath, sep='\t', 
                  names=["Date", "Host", "Src", "Dst", "Request", "SrcPort", "DstPort"])
    df['decoded_req']= df.Request.apply(request_parse)
    df['itag'] = df.decoded_req.apply(extract_itag)
    df['mime'] = df.Request.apply(extract_mime)
    df['range_str'] = df.Request.apply(extract_range)
    df['clen'] = df.Request.apply(extract_clen)
    df['mime'] = df.Request.apply(extract_mime)
    df['itag_str'] = df['itag'].apply(map_format)
    df['range'] = df.Request.apply(get_range)
    # print(df)
    return df

def plot_clen(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.scatter(filtered_video_data, x="clen", y="itag_str", title='clen and itag')
    fig.update_layout(
            title="Clen(MB)",
            xaxis_title="clen(MB)",
            yaxis_title="itag"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_clen_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_range(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.scatter(filtered_video_data, x="range", y="itag_str", title='range and itag')
    fig.update_layout(
            title="Range(MB)",
            xaxis_title="range(MB)",
            yaxis_title="range str"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_range"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_clen_time(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.scatter(filtered_video_data, x="Date", y="clen", title='Chunk size')
    fig.update_layout(
            title="clen(MB)",
            xaxis_title="Date",
            yaxis_title="clen(MB)"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_range"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_range_time(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.scatter(filtered_video_data, x="Date", y="range", title='Range over time')
    fig.update_layout(
            title="Range(MB)",
            xaxis_title="Date",
            yaxis_title="range(MB)"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_range_over_time_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def combine_range_clen(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=filtered_video_data["Date"],
            y=filtered_video_data["range"],
            mode='markers',
            name='range'
        ))

    fig.add_trace(
        go.Scatter(
            x=filtered_video_data["Date"],
            y=filtered_video_data["clen"],
            mode='markers',
            name='clen'
        ))

    fig.update_layout(
            title="clen and range",
            xaxis_title="Date",
            yaxis_title="MB"
        )

    # fig.show()
    filename_plot = ex.DATAPATH_PROCESSED + "/video_range_clen_over_time_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_clen_histogram(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.histogram(filtered_video_data, x="clen", title='Video Quality Level Change')
    fig.update_layout(
            title="clen histogram",
            xaxis_title="clen",
            yaxis_title="count"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_clen_histo_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_video_quality_level_change(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    fig = px.scatter(filtered_video_data, x="Date", y="itag_str", title='Video Quality Level Change')
    fig.update_layout(
            title="Video Quality Level Change",
            xaxis_title="Time(s)",
            yaxis_title="itag"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/video_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

def plot_audio_quality_level_change(df, file_name):
    filtered_audio_data = df[(df.mime.str.contains('audio'))]
    fig = px.scatter(filtered_audio_data, x="Date", y="itag_str", title='Audio Quality Level Change')
    fig.update_layout(
            title="Audio Quality Level Change",
            xaxis_title="Time(s)",
            yaxis_title="itag"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/audio_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

###END OF YOUTUBE ANALYSIS###################

# all_analysers = cmn.get_experiment_analysers("1iperf-240s")
# # all_analysers = cmn.get_all_experiment_analysers()
# for analyser in all_analysers:
#     print("~~~~~~~~",analyser, "~~~~~~")
#     #~~~~~~~~~~~~~~~IPERF GOODPUT AVG~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#     get_goodput_of_solo_exp(all_analysers[analyser], analyser)
    #~~~~~~~~~~~~~~~LOCAL VIDEO~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # get_local_video_bitrate(all_analysers[analyser], analyser)
    # get_local_video_avg_bitrate()
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # get_webpage_load_time(all_analysers[analyser], analyser)
    #~~~~~~~~~~~~~~~YOUTUBE_ANALYSIS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # extract_youtube_requests(all_analysers[analyser], analyser)
    # df = process_youtube_pcap(all_analysers[analyser], analyser)
    # plot_video_quality_level_change(df, analyser)
    # plot_audio_quality_level_change(df, analyser)
    # plot_clen(df, analyser)
    # plot_range(df, analyser)
    # plot_range_time(df, analyser)
    # plot_clen_time(df, analyser)
    # combine_range_clen(df, analyser)
    # plot_clen_histogram(df, analyser)
    #~~~~~~~~~~~~~~~END OF YOUTUBE_ANALYSIS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
get_iperf_avg_goodput()