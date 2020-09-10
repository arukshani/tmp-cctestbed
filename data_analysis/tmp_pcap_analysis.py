import subprocess
import os 
import pandas as pd 
import plotly
import plotly.express as px
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import datetime
import plotly.graph_objects as go
import experiment as ex
import common as cmn 

DATAPATH_PROCESSED = '/Users/rukshani/Documents/DATASET/WEEK_22/homemachine'
pcap_path = '/Users/rukshani/Documents/DATASET/WEEK_22/homemachine/second_chrome.pcapng'


def map_bitrate(itag_str):
    return cmn.bitrate_itag_map.get(itag_str)

def convert_bitrate_mbps(bitrate):
    mbps = (bitrate * cmn.BITS_TO_MEGABITS)
    answer = round(mbps, 2)
    # print(answer)
    return float(answer)

def get_http_traffic():
    http_tarpath = 'second_chrome.pcapng'
    http_processed_localpath = os.path.join(DATAPATH_PROCESSED, http_tarpath)[:-len('.pcapng')] + '.csv'
    print(http_processed_localpath)
    cmd = "/Applications/Wireshark.app/Contents/MacOS/tshark -r {} -V -Y http.request -T fields -e frame.time_relative -e http.host -e ip.src -e ip.dst -e http.request.full_uri  -e tcp.srcport -e tcp.dstport -e http.header.Range >> {}".format(
                pcap_path , http_processed_localpath)
    proc = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE)

def process_http_pcap():
    
    filepath = DATAPATH_PROCESSED + "/second_chrome" + ".csv"
    df = pd.read_csv(filepath ,sep='\t', 
                  names=["time", "dstip_dstport", "srcip", "dstip", "request_uri", "scrport", "dstport", "range_header"])
    df['bitrate'] = df['itag_str'].apply(map_bitrate)
    df['bitrate_mbps'] = df['bitrate'].apply(convert_bitrate_mbps)
    # df['path'] = df.request_uri.apply(extract_path)
    # df['mime'] = df.path.apply(extract_mime)
    # df['itag'] = df.path.apply(extract_itag)
    # df['resolution'], df['bitrate_k'] = zip(*df.path.apply(extract_resolution_and_bitrate_k))
    return df

def plot_combine_video_requests(all_dfs):

    fig = go.Figure()
    # for key in all_dfs:
        # df = all_dfs[key]
        # df = df.reindex()
        # filtered_video_data = df[(df.mime.str.contains('video'))]
        # print(filtered_video_data)
    fig.add_trace(
    go.Scatter(
        x=df["time"],
        y=df["range_header"],
        mode='markers',
        # color = "range_header"
        # name=key
    ))
    # fig.update_layout(
    #         title="Video Requests",
    #         xaxis_title="time(s)",
    #         yaxis_title="itag value",
    #         annotations=[
    #         go.layout.Annotation(
    #             # text=get_itag_description(),
    #             align='left',
    #             showarrow=False,
    #             xref='paper',
    #             yref='paper',
    #             x=1.4,
    #             y=0.8,
    #             bordercolor='black',
    #             borderwidth=1
    #         )
    #     ]
    # )

    filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/homemachine/second_chrome_range.html"
    plotly.offline.plot(fig, filename=filename_plot)

get_http_traffic()
df = process_http_pcap()
# print(df['request_uri'])
plot_combine_video_requests(df)