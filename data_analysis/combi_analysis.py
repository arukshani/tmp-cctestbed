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

def include_ccalg(port, ports):
    return ports[port]

def extract_tcpdump(experiment_analyzer, app_type):
    experiment_analyzer.server_tcpdump_tcp

def extract_tcpdump_http(experiment_analyzer, app_type):
    experiment_analyzer.server_tcpdump_http

def extract_http_pcap(experiment_analyzer, app_type):
    experiment_analyzer.http_pcap

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
    filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    filtered_iperf_data['group'] = filtered_iperf_data['filename'].apply(cmn.include_group_combi)
    # print(filtered_iperf_data)
    avg_output = filtered_iperf_data.groupby('group')['goodput'].mean()
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-results/avg-goodput-' + combination + '.csv', header=False, index=True)

def get_webpage_load_time(experiment_analyzer, app_type, combination, port): #Goodput of each flow in a single experiment
    filepath = ex.DATAPATH_PROCESSED + "/server-tcpdump-" + app_type + ".csv"
    df = pd.read_csv(filepath, sep='\t', 
                  names=["Date", "Host", "Src", "Dst", "Request", "SrcPort", "DstPort"])
    new_data_frame=df.drop_duplicates(["SrcPort", "DstPort"])[["SrcPort", "DstPort"]]
    new_data_frame = new_data_frame.dropna().astype(int)
    rows_for_port = new_data_frame.loc[new_data_frame['DstPort'] == port]
    srcport_webpage = rows_for_port['SrcPort'].iloc[0]
    # print(srcport_webpage)
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        webpage_port_row = dequeued.loc[dequeued['src'] == srcport_webpage]
        page_load_time = (webpage_port_row.index.max() - webpage_port_row.index.min()).total_seconds()
        metric = "page_load_time_s"
        data = [[srcport_webpage, page_load_time, app_type, metric]]
        web_df = pd.DataFrame(data)
        web_df.to_csv(ex.DATAPATH_PROCESSED +'/combi-results/webpageload-' + combination + '.csv', header=False, index=False, mode = 'a')

def get_local_video_bitrate(experiment_analyzer, app_type, combination, port):
    filepath = ex.DATAPATH_PROCESSED + "/server-tcpdump-" + app_type + ".csv"
    df = pd.read_csv(filepath ,sep='\t', 
                  names=["Time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport"]).assign(bitrate=lambda df: (df['request_uri']
                                          .str
                                          .extract('/bunny_(\d+)bps/.*')
                                          .astype('float'))).dropna()
    rows_for_port = df.loc[df['dstport'] == port]
    mean = rows_for_port['bitrate'].mean()/1000000
    metric = 'bitrate_Mbps'
    # dummy_port = 1111
    data = [[port, mean, app_type, metric]]
    bitrate_df = pd.DataFrame(data)
    bitrate_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-results/bitrate-' + combination + '.csv', header=False, index=False, mode = 'a')

def get_local_video_avg_bitrate(combination):
    all_bitrate_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/combi-results/bitrate-' + combination + '.csv',sep=',', 
                  names=["port", "bitrate", "filename", "metric"])
    # filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    all_bitrate_data['group'] = all_bitrate_data['filename'].apply(cmn.include_group_combi)
    # print(filtered_iperf_data)
    avg_output = all_bitrate_data.groupby('group')['bitrate'].mean()
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-results/avg-bitrate-' + combination + '.csv', header=False, index=True)

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

def process_youtube_pcap(experiment_analyzer, app_type, filter_port):
    filepath = ex.DATAPATH_PROCESSED + "/server-tcpdump-" + app_type + ".csv"
    df = pd.read_csv(filepath, sep='\t', 
                  names=["Date", "Host", "Src", "Dst", "Request", "SrcPort", "DstPort"])
    #Filter out iperf or competing traffic since we only need youtube traffic
    df = df[df['DstPort'] != filter_port]
    df['decoded_req']= df.Request.apply(request_parse)
    df['itag'] = df.decoded_req.apply(extract_itag)
    df['mime'] = df.Request.apply(extract_mime)
    df['itag_str'] = df['itag'].apply(map_format)
    # print(df)
    return df

def plot_video_quality_level_change(df, file_name):
    filtered_video_data = df[(df.mime.str.contains('video'))]
    # print(filtered_video_data)
    fig = px.line(filtered_video_data, x="Date", y="itag_str", title='Video Quality Level Change')
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
    # print(filtered_audio_data)
    fig = px.line(filtered_audio_data, x="Date", y="itag_str", title='Audio Quality Level Change')
    fig.update_layout(
            title="Audio Quality Level Change",
            xaxis_title="Time(s)",
            yaxis_title="itag"
        )
    # save_plot
    filename_plot = ex.DATAPATH_PROCESSED + "/audio_"+ file_name+ ".html"
    plotly.offline.plot(fig, filename=filename_plot)

###END OF YOUTUBE ANALYSIS###################

# all_analysers = cmn.get_experiment_analysers("*iperf-localVideo*")
# all_analysers = cmn.get_all_experiment_analysers()
# for analyser in all_analysers:
#     print("~~~~~~~~",analyser, "~~~~~~")
#     get_goodput(all_analysers[analyser], analyser, "iperf-all-video")
    # ~~~~~~~~~~~~~~~YOUTUBE_ANALYSIS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # extract_youtube_requests(all_analysers[analyser], analyser)
    # df = process_youtube_pcap(all_analysers[analyser], analyser, 5202)
    # plot_video_quality_level_change(df, analyser)
    # plot_audio_quality_level_change(df, analyser)
    #~~~~~~~~~~~~~~~WEBPAGE_LOAD_TIME~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # extract_tcpdump(all_analysers[analyser], analyser)
    # get_webpage_load_time(all_analysers[analyser], analyser, "localwebpage-youtube", 5202)
    #~~~~~~~~~~~~~~~LOCAL_VIDEO_BITRATE~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # extract_tcpdump_http(all_analysers[analyser], analyser)
    # get_local_video_bitrate(all_analysers[analyser], analyser, "localVideo-iperf", 5202)
    # get_local_video_avg_bitrate("localVideo-iperf")

get_iperf_avg_goodput("iperf-all-video")