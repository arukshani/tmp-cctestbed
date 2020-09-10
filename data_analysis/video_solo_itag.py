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

def map_bitrate(itag_str):
    return cmn.bitrate_itag_map.get(itag_str)

def convert_bitrate_mbps(bitrate):
    mbps = (bitrate * cmn.BITS_TO_MEGABITS)
    answer = round(mbps, 2)
    # print(answer)
    return float(answer)
    
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
    df['bitrate'] = df['itag_str'].apply(map_bitrate)
    df['bitrate_mbps'] = df['bitrate'].apply(convert_bitrate_mbps)
    
    # print(df)
    return df

##########LOCAL DASH########################

mp4_itag_map = {'media-video-avc1-1.mp4':133,
                'media-video-avc1-2.mp4':134,
                'media-video-avc1-3.mp4':135,
                'media-video-avc1-4.mp4':136,
                'media-video-avc1-5.mp4':137,
                'media-video-avc1-6.mp4':160,
                'media-video-avc1-7.mp4':298,
                'media-video-avc1-8.mp4':299,
                'media-audio-und-mp4a-1.mp4':140,
                'media-audio-und-mp4a-2.mp4':256,
                'media-audio-und-mp4a-3.mp4':258,
                }

def extract_local_video_http(experiment_analyzer):
    experiment_analyzer.http_pcap

def process_http_pcap(experiment_analyzer, app_type):
    filepath = ex.DATAPATH_PROCESSED + "/http-" + app_type + ".csv"
    # df = pd.read_csv(filepath ,sep='\t', 
    #               names=["time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport", "range_header"])
    df = pd.read_csv(filepath ,sep='\t', 
                  names=["time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport"])
    df['path'] = df.request_uri.apply(extract_path)
    df['mime'] = df.path.apply(extract_mime_DASH)
    df['itag_str'] = df.path.apply(extract_itag_DASH)
    df['bitrate'] = df['itag_str'].apply(map_bitrate)
    df['bitrate_mbps'] = df['bitrate'].apply(convert_bitrate_mbps)
    return df 

def extract_path(request_uri):
    path = urlparse.urlparse(request_uri).path
    return path

def extract_mime_DASH(path):
    mime = ''
    if path.startswith('/video') or path.startswith('/audio'):
        mime = path[1:6]
    elif path.startswith('/media'):
        mime  = path[7:12]
    return mime

def extract_itag_DASH(path):
    itag = ''
    if path.startswith('/video') or path.startswith('/audio'):
        itag = path[6:9]
        return "itag-" + itag
    elif path.startswith('/media'):
        itag = mp4_itag_map[path[1:]]
        return "itag-" + str(itag)
    return itag 

################BITRATE CALCULATION#############
def avg_bitrate_youtube_per_experiment(all_dataframes):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('video'))]
        all_columns =  list(filtered_video_data.columns)
        # print(all_columns)
        bitrates = filtered_video_data[all_columns[14]]
        # print(bitrates)
        if not bitrates.empty:
            mean = (bitrates.mean())/1000000
            metric = 'bitrate_Mbps'
            data = [[mean, key, metric]]
            # print(mean, key)
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_webVideo_bitrate.csv', header=False, index=False, mode = 'a')


def avg_bitrate_video_per_experiment(all_dataframes):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('video'))]
        all_columns =  list(filtered_video_data.columns)
        bitrates = filtered_video_data[all_columns[10]]
    
        mean = bitrates.mean()/1000000
        metric = 'bitrate_Mbps'
        data = [[mean, key, metric]]
        new_df = pd.DataFrame(data)
        new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/solo_localVideo_bitrate.csv', header=False, index=False, mode = 'a')


def final_avg_localVideo():
    all_bitrate_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/solo-results/solo_localVideo_bitrate.csv' ,sep=',', 
                  names=["bitrate", "filename", "metric"])
    all_bitrate_data.dropna()
    # filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    all_bitrate_data['group'] = all_bitrate_data['filename'].apply(cmn.include_group_solo)
    # print(all_bitrate_data)
    # print(filtered_iperf_data)
    avg_output = all_bitrate_data.groupby('group')['bitrate'].mean()
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/avg-solo-bitrate-' + 'localVideo' + '.csv', header=False, index=True)

def final_avg_youtube():
    all_bitrate_data = pd.read_csv(ex.DATAPATH_PROCESSED + '/harm/solo-results/solo_webVideo_bitrate.csv' ,sep=',', 
                  names=["bitrate", "filename", "metric"])
    all_bitrate_data = all_bitrate_data.dropna()
    # filtered_iperf_data = all_goodput_data[(all_goodput_data.port == 5202)]
    all_bitrate_data['group'] = all_bitrate_data['filename'].apply(cmn.include_group_solo)
    # print(all_bitrate_data)
    # print(filtered_iperf_data)
    avg_output = all_bitrate_data.groupby('group')['bitrate'].mean()
    # print(avg_output)
    avg_output.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-results/avg-solo-bitrate-' + 'webVideo' + '.csv', header=False, index=True)


################PLOTS############################

def plot_youtube_quality_all_in_one(all_dataframes, fig):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('video'))]
        all_columns =  list(filtered_video_data.columns)
        print(all_columns)
        # ['Date', 'Host', 'Src', 'Dst', 'Request', 'SrcPort', 'DstPort', 'decoded_req', 'itag', 'mime', 'range_str', 'clen', 'itag_str', 'range', 'bitrate', 'bitrate_mbps']
        y_data= filtered_video_data[all_columns[15]]
        x_data = filtered_video_data[all_columns[0]]
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name=key, mode='lines+markers', text=y_data)
        )
    return fig

def plot_youtube_audio_quality_all_in_one(all_dataframes, fig):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('audio'))]
        all_columns =  list(filtered_video_data.columns)
        print(all_columns)
        # ['Date', 'Host', 'Src', 'Dst', 'Request', 'SrcPort', 'DstPort', 'decoded_req', 'itag', 'mime', 'range_str', 'clen', 'itag_str', 'range', 'bitrate', 'bitrate_mbps']
        y_data= filtered_video_data[all_columns[12]]
        x_data = filtered_video_data[all_columns[0]]
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name=key, mode='lines+markers', text=y_data)
        )
    return fig

def plot_dash_audio_quality_all_in_one(all_dataframes, fig):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('audio'))]
        all_columns =  list(filtered_video_data.columns)
        print(all_columns)
        #['time', 'dstip_dstport', 'srcip', 'dstip', 'request_uri', 'scrport', 'dstport', 'path', 'mime', 'itag_str', 'bitrate', 'bitrate_mbps']
        y_data= filtered_video_data[all_columns[9]]
        x_data = filtered_video_data[all_columns[0]]
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name=key, mode='lines+markers', text=y_data)
        )
    return fig

def plot_dash_quality_all_in_one(all_dataframes, fig):
    for key, value in all_dataframes.items():
        filtered_video_data = value[(value.mime.str.contains('video'))]
        all_columns =  list(filtered_video_data.columns)
        print(all_columns)
        #['time', 'dstip_dstport', 'srcip', 'dstip', 'request_uri', 'scrport', 'dstport', 'path', 'mime', 'itag_str', 'bitrate', 'bitrate_mbps']
        y_data= filtered_video_data[all_columns[11]]
        x_data = filtered_video_data[all_columns[0]]
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name=key, mode='lines+markers', text=y_data)
        )
    return fig

####################################MAIN###################

# all_youtube_dataframes = {}
# all_dash_dataframes = {}
# # all_analysers = cmn.get_experiment_analysers("50bw-20rtt-256q-www.youtube.com-240s-20200826T005005")
# all_analysers = cmn.get_all_experiment_analysers()
# for analyser in all_analysers:
#     print("~~~~~~~~",analyser, "~~~~~~")
#     if "video" in analyser:
#         # extract_local_video_http(all_analysers[analyser])
#         dash_df = process_http_pcap(all_analysers[analyser], analyser)
#         all_dash_dataframes[analyser] = dash_df
#     elif "youtube" in  analyser:
#         #~~~~~~~~~~~~~~~YOUTUBE_ANALYSIS~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#         # extract_youtube_requests(all_analysers[analyser], analyser)
#         df = process_youtube_pcap(all_analysers[analyser], analyser)
#         all_youtube_dataframes[analyser] = df

#####################PLOT ITAG GRAPHS##############
# fig = go.Figure()
# fig = plot_youtube_quality_all_in_one(all_youtube_dataframes, fig)
# fig = plot_dash_quality_all_in_one(all_dash_dataframes, fig)
# fig.update_layout(
#             title="Solo [YouTube & Local DASH] - Video bitrate change over time",
#             xaxis_title="<b>Time (s)</b>",
#             yaxis_title="<b>bitrate (Mbps)</b>"
#             # yaxis={'tickformat': ',d'}
#         )
# filename_plot = ex.DATAPATH_PROCESSED + "/harm/solo_"+ "video_itags_3G"+ ".html"
# plotly.offline.plot(fig, filename=filename_plot)

# ###Audio
# fig1 = go.Figure()
# fig1 = plot_youtube_audio_quality_all_in_one(all_youtube_dataframes, fig1)
# fig1 = plot_dash_audio_quality_all_in_one(all_dash_dataframes, fig1)
# fig1.update_layout(
#             title="Solo [YouTube & Local DASH] - Audio bitrate change over time",
#             xaxis_title="<b>Time (s)</b>",
#             yaxis_title="<b>bitrate (Mbps)</b>"
#             # yaxis={'tickformat': ',d'}
#         )
# filename_plot1 = ex.DATAPATH_PROCESSED + "/harm/solo_"+ "audio_itags_3G"+ ".html"
# plotly.offline.plot(fig1, filename=filename_plot1)

# avg_bitrate_youtube_per_experiment(all_youtube_dataframes)
# avg_bitrate_video_per_experiment(all_dash_dataframes)
final_avg_localVideo()
final_avg_youtube()