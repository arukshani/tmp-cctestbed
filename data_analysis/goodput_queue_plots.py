import common as cmn
import experiment as ex

import plotly.express as px
import pandas as pd
import urllib.parse as urlparse
from urllib.parse import parse_qs
from urllib.parse import unquote
import datetime
import numpy as np

import plotly.graph_objs as go
import plotly 

def toMb(x):
   return (x * cmn.BYTES_TO_BITS) * cmn.BITS_TO_MEGABITS

def bitrate(x, window_size):
   return x / (window_size * cmn.MILLISECONDS_TO_SECONDS)

def plot(plot_type, df):
    # colors = ['blue', 'green', 'red', 'goldenrod']
    for trace in list(df.columns):
            fig = go.Figure()
            # i = 0
            for trace in list(df.columns):

                # trace1 = ''
                # if trace == 5203 or trace == 5202:
                #     trace1 = "<b>iperf(Cubic)</b>"
                # else:
                #     trace1 = "<b>YouTube</b>"
                # fig.add_trace(
                #     go.Scatter(x=df.index, y=df[trace], name=trace1, mode=plot_type, line = dict(
                #     color = colors[i]))
                # )
                # i = i + 1
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[trace], name=trace, mode=plot_type)
                )
                # i = i + 1
            return fig

def plot_queue_occupancy(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[df_queue['src'].unique()]
        queue_occupancy.index = (queue_occupancy.index - queue_occupancy.index[0]).total_seconds()
        # plt = queue_occupancy.plot(kind='line', figsize=(25,10))
        # plt.set_xlabel('time (seconds)')
        # plt.set_ylabel('num packets in queue')
        # fig = plt.get_figure()
        # fig.savefig(ex.DATAPATH_PROCESSED + "/queue_occupancy_" + file_name + ".png")
        #plotly graph
        save_plot = plot('lines', queue_occupancy)
        # save_plot.update_xaxes(rangeslider_visible=True)
        save_plot.update_layout(
            # title="Goodput Over Time (100ms interval)",
            xaxis_title="<b>Time (s)</b>",
            yaxis_title="<b>Number of packets in the queue</b>",
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                # family="Courier New, monospace",
                size=16
                # color="RebeccaPurple"
            )
        )
        # save_plot
        filename_plot = ex.DATAPATH_PROCESSED + "/queue_plot_"+ file_name+ ".html"
        plotly.offline.plot(save_plot, filename=filename_plot)

def plot_goodput(experiment_analyzer, window_size, file_name):
    print("print plotly goodput")
    if window_size is None:
        window_size = experiment_analyzer.experiment.flows[0].rtt
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        goodput = (dequeued
                        .groupby('src')
                        .datalen
                        .resample('{}ms'.format(window_size))
                        .sum().apply(toMb).apply(bitrate, args = ([window_size]))
                        .unstack(level='src')
                        .fillna(0))
        goodput.index = (goodput.index - goodput.index[0]).total_seconds()
        
        #plotly graph
        save_plot = plot('lines', goodput)
        # save_plot.update_xaxes(rangeslider_visible=True)
        save_plot.update_layout(
            # title="Goodput Over Time (100ms interval)",
            xaxis_title="<b>Time (s)</b>",
            yaxis_title="<b>Goodput (Mbps)</b>",
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                # family="Courier New, monospace",
                size=16
                # color="RebeccaPurple"
            )
        )
        # save_plot
        filename_plot = ex.DATAPATH_PROCESSED + "/goodput_"+ file_name+ ".html"
        plotly.offline.plot(save_plot, filename=filename_plot)

all_analysers = cmn.get_all_experiment_analysers()
# all_analysers = cmn.get_experiment_analysers("2bw-20rtt-16q-iperf-localVideotest-1-1-cubic-cubic--240s-20200830T161718")
for analyser in all_analysers:
    print("~~~~~~~~",analyser, "~~~~~~")
    plot_queue_occupancy(all_analysers[analyser], analyser)
    plot_goodput(all_analysers[analyser], 100, analyser)