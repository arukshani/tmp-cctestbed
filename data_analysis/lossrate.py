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
import os 

def toMb(x):
   return (x * cmn.BYTES_TO_BITS) * cmn.BITS_TO_MEGABITS

def rate(x, window_size):
   return x / (window_size * cmn.MILLISECONDS_TO_SECONDS)

def plot(plot_type, df):
    # colors = ['blue', 'green', 'red', 'goldenrod']
    for trace in list(df.columns):
            fig = go.Figure()
            # i = 0
            for trace in list(df.columns):
                # print(trace)
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[trace], name=trace, mode=plot_type)
                )
            return fig

def plot_loss_rate(experiment_analyzer, window_size, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dropped_df = df_queue[df_queue.dropped==1]
        # print(dropped_df)
        loss_rate = (dropped_df
                        .groupby('src')
                        .dropped
                        .resample('{}ms'.format(window_size))
                        .count().apply(rate, args = ([window_size]))
                        .unstack(level='src')
                        .fillna(0))
        loss_rate.index = (loss_rate.index - loss_rate.index[0]).total_seconds()
        # print(loss_rate)
        #plotly graph
        save_plot = plot('lines', loss_rate)
        save_plot.update_layout(
            title="Loss Rate; iperf-localVideo (100ms interval)",
            xaxis_title="<b>Time (s)</b>",
            yaxis_title="<b>Loss rate (Number of dropped packets per second)</b>",
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(
                # family="Courier New, monospace",
                size=16
                # color="RebeccaPurple"
            )
        )
        # save_plot
        filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_loss_rate/LOSSRATE_" +file_name +  ".html"
        plotly.offline.plot(save_plot, filename=filename_plot)

def get_iperf_loss_per_exp(experiment_analyzer, window_size, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dropped_df = df_queue[df_queue.dropped==1]
        if dropped_df.empty == True:
            return dropped_df
        else:
            dropped_df = dropped_df[dropped_df.src==5202]
            # print(dropped_df)
            loss_rate = (dropped_df
                            .groupby('src')
                            .dropped
                            .resample('{}ms'.format(window_size))
                            .count().apply(rate, args = ([window_size]))
                            .unstack(level='src')
                            .fillna(0))
            loss_rate.index = (loss_rate.index - loss_rate.index[0]).total_seconds()

            tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/plots_loss_rate/' + file_name + '.csv'
            loss_rate.to_csv(tmp_file, header=False, index=True, mode = 'a')
            df = pd.read_csv(tmp_file, sep=',', names=["time", "drprate"])
            return df 

def plot_all_in_one(all_dataframes, fig):
    for key, value in all_dataframes.items():
        all_columns =  list(value.columns)
        # print(all_columns)
        # ['Date', 'Host', 'Src', 'Dst', 'Request', 'SrcPort', 'DstPort', 'decoded_req', 'itag', 'mime', 'range_str', 'clen', 'itag_str', 'range', 'bitrate', 'bitrate_mbps']
        y_data= value[all_columns[1]]
        x_data = value[all_columns[0]]
        fig.add_trace(
            go.Scatter(x=x_data, y=y_data, name=key, mode='lines+markers', text=y_data)
        )
    return fig

def avg_combi_loss_rate_per_exp(experiment_analyzer, file_name, window_size):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dropped_df = df_queue[df_queue.dropped==1]

        loss = (dropped_df.groupby('src')['dropped'].count()) / (dropped_df.index.max() - dropped_df.index.min()).total_seconds()
        tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/' + 'tmp_rate_per_exp' + '.csv'
        loss.to_csv(tmp_file, header=False, index=True, mode = 'a')

        new_df = pd.read_csv(tmp_file ,sep=',', names=["Port", "LossRate"])
        new_df['app_type'] = file_name
        # new_df['Metric'] = 'goodput_Mbps'
        os.remove(tmp_file)
        save_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/' + 'lossrate_per_exp' + '.csv'
        new_df.to_csv(save_file, header=False, index=False, mode = 'a')

        # print(dropped_df)
        # loss_rate = (dropped_df
        #                 .groupby('src')
        #                 .dropped
        #                 .resample('{}ms'.format(window_size))
        #                 .count().apply(rate, args = ([window_size]))
        #                 .unstack(level='src')
        #                 .fillna(0))
        # loss_rate.index = (loss_rate.index - loss_rate.index[0]).total_seconds()
        # tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/' + file_name + '.csv'
        # loss_rate.to_csv(tmp_file, header=False, index=True, mode = 'a')
        # df = pd.read_csv(tmp_file, sep=',', names=["time", "drprate"])
        # df['group'] = df['filename'].apply(cmn.include_group_combi)
        # avg_output = df.groupby(['group','port'])['drprate'].mean()
        # write_to_file(avg_output, combination)

def avg_combi_loss_rate():
    save_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/' + 'lossrate_per_exp' + '.csv'
    loss_data = pd.read_csv(save_file,sep=',', 
                  names=["port", "lossrate", "filename"])
    loss_data = loss_data[loss_data.port==5202]
    loss_data['group'] = loss_data['filename'].apply(cmn.include_group_combi)
    avg_output = loss_data.groupby(['group','port'])['lossrate'].mean()

    save2_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/' + 'avg_loss_rate' + '.csv'
    avg_output.to_csv(save2_file, header=False, index=True, mode = 'a')


# all_dataframes = {}
# all_analysers = cmn.get_all_experiment_analysers()
# # all_analysers = cmn.get_experiment_analysers("2bw-20rtt-16q-iperf-localVideotest-1-1-cubic-cubic--240s-20200830T163527")
# for analyser in all_analysers:
#     print("~~~~~~~~",analyser, "~~~~~~")
#     # df = get_iperf_loss_per_exp(all_analysers[analyser], 100, analyser)
#     # if not df.empty == True:
#     #     all_dataframes[analyser] = df
#     avg_combi_loss_rate_per_exp(all_analysers[analyser], analyser, 100)

avg_combi_loss_rate()

# fig = go.Figure()
# fig = plot_all_in_one(all_dataframes, fig)
# # fig = plot_dash_quality_all_in_one(all_dash_dataframes, fig)

# fig.update_layout(
#             title="SOLO iperf loss rates",
#             xaxis_title="<b>Time (s)</b>",
#             yaxis_title="<b>Number of dropped packets per second</b>",
#         )

# filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/plots_loss_rate/ALL_IN_ONE_IPERF.html"
# plotly.offline.plot(fig, filename=filename_plot)