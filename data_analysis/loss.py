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
                print(trace)
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

def plot_loss(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        dequeued = hdf_queue.select('df_queue')
        # dropped = dequeued[dequeued.dropped==1]
        
        # if dropped.empty:
        #     dropped = 0
        #     print("No packet drops")
        # else:
        #     # dropped = dropped[dropped['src'].unique()]
        #     dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        #     print(dropped)
        #     save_plot = plot('markers', dropped)
        #     # save_plot.update_xaxes(rangeslider_visible=True)
        #     save_plot.update_layout(
        #         # title="Goodput Over Time (100ms interval)",
        #         xaxis_title="<b>Time (s)</b>",
        #         yaxis_title="<b>Dropped packets in the queue</b>",
        #         plot_bgcolor='rgba(0,0,0,0)',
        #         font=dict(
        #             # family="Courier New, monospace",
        #             size=16
        #             # color="RebeccaPurple"
        #         )
        #     )
        #     # save_plot
        #     filename_plot = ex.DATAPATH_PROCESSED + "/DOT_LOSS_"+ file_name+ ".html"
        #     plotly.offline.plot(save_plot, filename=filename_plot)

def loss_rate(experiment_analyzer, file_name):
    print(file_name)
    with all_analysers[analyser].hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'dequeued', 'dropped']]
        # print(queue_occupancy)
        queue_occupancy.index = (queue_occupancy.index - queue_occupancy.index[0]).total_seconds()
        quiet = queue_occupancy.loc[1:60]
        # print(quiet)

        print("~~~~~enqueued~~~~")
        quiet_enq = quiet[quiet.dequeued==0]
        number_enq = quiet_enq.sort_index().groupby('src')['dequeued'].count()
        print(number_enq)

        print("~~~~~Dropped~~~~")
        quiet_drop = quiet[quiet.dropped==1]
        number_drop = quiet_drop.sort_index().groupby('src')['dropped'].count()
        print(number_drop)

def solo_lossrate(experiment_analyzer, file_name):
    with all_analysers[analyser].hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'dequeued', 'dropped']]
        queue_occupancy.index = (queue_occupancy.index - queue_occupancy.index[0]).total_seconds()

        print("~~~~~enqueued~~~~")
        enq = queue_occupancy[queue_occupancy.dequeued==0] #dequeued ==0 means its enqueued
        number_enq = enq.sort_index().groupby('src', as_index=False)['dequeued'].count()
        # print(number_enq["dequeued"].iloc[0])
        enq_packets = number_enq["dequeued"].iloc[0]

        print("~~~~~Dropped~~~~")
        drop = queue_occupancy[queue_occupancy.dropped==1]
        number_drop = drop.sort_index().groupby('src', as_index=False)['dropped'].count()
        # print(number_drop["dropped"].iloc[0])
        
        dropped_packets = 0
        if number_drop["dropped"].empty != True:
            dropped_packets = number_drop["dropped"].iloc[0]
            # print("No loss")
            # number_drop["dropped"] = 0

        loss_perc = (dropped_packets/enq_packets) * 100
        # print("Loss Percent>>", file_name, "-", loss_perc)

        data = [[file_name, enq_packets, dropped_packets, loss_perc]]
        new_df = pd.DataFrame(data)
        new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/solo-loss-perc.csv', header=False, index=False, mode = 'a')

def combi_lossrate(experiment_analyzer, file_name):
     with all_analysers[analyser].hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'dequeued', 'dropped']]
        queue_occupancy.index = (queue_occupancy.index - queue_occupancy.index[0]).total_seconds()

        ports = queue_occupancy['src'].unique()

        # print("~~~~~enqueued~~~~")
        enq = queue_occupancy[queue_occupancy.dequeued==0] #dequeued ==0 means its enqueued
        number_enq = enq.sort_index().groupby('src', as_index=False)['dequeued'].count()
        # print(number_enq)
        # print(number_enq["dequeued"].iloc[0])
        # enq_packets = number_enq["dequeued"].iloc[0]

        # print("~~~~~Dropped~~~~")
        drop = queue_occupancy[queue_occupancy.dropped==1]
        number_drop = drop.sort_index().groupby('src', as_index=False)['dropped'].count()
        # print(number_drop)
        # print(number_drop["dropped"].iloc[0])

        for port in ports:
            enq_pk = number_enq.loc[number_enq['src'].eq(port)]
            drop_pk = number_drop.loc[number_drop['src'].eq(port)]
            if not enq_pk.empty and not drop_pk.empty:
                # print(drop_pk.iloc[0][1], enq_pk.iloc[0][1])
                loss_rate = (drop_pk.iloc[0][1] / enq_pk.iloc[0][1]) * 100
                data = [[file_name, port, enq_pk.iloc[0][1], drop_pk.iloc[0][1], loss_rate]]
                new_df = pd.DataFrame(data)
                new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/combi-loss-perc.csv', header=False, index=False, mode = 'a')

def total_loss():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/combi-loss-perc.csv', sep=',', names=["filename", "port", "enq", "drop", "loss"])
    tot_enq = df.groupby('filename', as_index=False)['enq'].sum()
    tot_drp = df.groupby('filename', as_index=False)['drop'].sum()

    unq_filenames = df['filename'].unique()
    # print(unq_filenames)
    # print(tot_drp)

    for expname in unq_filenames:
        enq_row = tot_enq.loc[tot_enq['filename'].eq(expname)]
        drp_row = tot_drp.loc[tot_drp['filename'].eq(expname)]
        # print(enq_row.iloc[0][1])
        if not enq_row.empty and not drp_row.empty:
            tot_loss_perc = (drp_row.iloc[0][1] /enq_row.iloc[0][1]) * 100
            data = [[expname, enq_row.iloc[0][1], drp_row.iloc[0][1], tot_loss_perc]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/total-loss-perc.csv', header=False, index=False, mode = 'a')

def solo_mean_loss():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/solo-loss-perc.csv', sep=',', names=["filename", "enq", "drop", "loss"])
    df['group'] = df['filename'].apply(cmn.include_group_solo)
    mean = df.groupby('group', as_index=False)['loss'].mean()
    # print(mean)
    # data = [[mean]]
    new_df = pd.DataFrame(mean)
    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/mean-solo-loss-perc.csv', header=False, index=False, mode = 'a')

def map_format(seq):
    return "seq-" + str(seq)

def plot_loss_seq(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'seq', 'dropped']]
        dropped = queue_occupancy[queue_occupancy.dropped==1]
        # dropped = queue_occupancy[queue_occupancy.port!=5202]
        dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_loss_seq/' + file_name + '.csv'
        dropped.to_csv(tmp_file, header=False, index=True, mode = 'a')
        df = pd.read_csv(tmp_file, sep=',', names=["time", "src", "seq", "drp"])
        df['seq_str'] = df['seq'].apply(map_format)

        fig = go.Figure()
        ports = df_queue['src'].unique()
        for port in ports:
            dropped_port = df[df.src==port]
            fig.add_trace(go.Scatter(
                x=dropped_port["time"],
                y=dropped_port["seq_str"],
                mode='markers',
                name=str(port)
            ))
        # fig.update_traces(marker=dict(size=2,
        #                       line=dict(width=2,
        #                                 color='DarkSlateGrey')),
        #           selector=dict(mode='markers'))
        fig.update_layout(
            title="Sequence Numbers of Dropped Packets",
            xaxis_title="<b>Time(s)</b>",
            yaxis_title="<b>TCP Sequence Number</b>",
        )
        filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_loss_seq/DROPPED_SEQ_" +file_name +  ".html"
        plotly.offline.plot(fig, filename=filename_plot)

def plot_deq_seq(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'seq', 'dequeued']]
        dropped = queue_occupancy[queue_occupancy.dequeued==1]
        # dropped = queue_occupancy[queue_occupancy.port!=5202]
        dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_deq_seq/' + file_name + '.csv'
        dropped.to_csv(tmp_file, header=False, index=True, mode = 'a')
        df = pd.read_csv(tmp_file, sep=',', names=["time", "src", "seq", "deq"])
        df['seq_str'] = df['seq'].apply(map_format)

        fig = go.Figure()
        ports = df_queue['src'].unique()
        for port in ports:
            dropped_port = df[df.src==port]
            fig.add_trace(go.Scatter(
                x=dropped_port["time"],
                y=dropped_port["seq_str"],
                mode='markers',
                name=str(port)
            ))
        fig.update_layout(
            title="Sequence Numbers of Dequeued Packets",
            xaxis_title="<b>Time(s)</b>",
            yaxis_title="<b>TCP Sequence Number</b>",
        )
        filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_deq_seq/DEQ_SEQ_" +file_name +  ".html"
        plotly.offline.plot(fig, filename=filename_plot)    

def deq_drp_seq(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'seq', 'dequeued', "dropped"]]
        deq = queue_occupancy[queue_occupancy.dequeued==1]
        drp = deq[deq.dropped==1]
        print(drp)

def plot_loss_scatter(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'seq', 'dropped']]
        dropped = queue_occupancy[queue_occupancy.dropped==1]
        dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_scatter_loss/' + file_name + '.csv'
        dropped.to_csv(tmp_file, header=False, index=True, mode = 'a')
        df = pd.read_csv(tmp_file, sep=',', names=["time", "src", "seq", "drp"])

        fig = go.Figure()
        ports = df_queue['src'].unique()
        for port in ports:
            dropped_port = df[df.src==port]
            fig.add_trace(go.Scatter(
                x=dropped_port["time"],
                y=dropped_port["drp"],
                mode='markers',
                name=str(port)
            ))
        # fig.update_traces(marker=dict(size=2,
        #                       line=dict(width=2,
        #                                 color='DarkSlateGrey')),
        #           selector=dict(mode='markers'))
        fig.update_layout(
            title="Sequence Numbers of Dropped Packets",
            xaxis_title="<b>Time(s)</b>",
            yaxis_title="<b>TCP Sequence Number</b>",
        )
        filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_scatter_loss/SCATTER_LOSS_" +file_name +  ".html"
        plotly.offline.plot(fig, filename=filename_plot)
        # if dropped.empty:
        #     dropped = 0
        #     print("No packet drops")
        # else:
        #     dropped = dropped[dropped['src'].unique()]
        #     dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        #     save_plot = plot('lines', dropped)
        #     # save_plot.update_xaxes(rangeslider_visible=True)
        #     save_plot.update_layout(
        #         # title="Goodput Over Time (100ms interval)",
        #         xaxis_title="<b>Time (s)</b>",
        #         yaxis_title="<b>Dropped packets in the queue</b>",
        #         plot_bgcolor='rgba(0,0,0,0)',
        #         font=dict(
        #             # family="Courier New, monospace",
        #             size=16
        #             # color="RebeccaPurple"
        #         )
        #     )
        #     # save_plot
        #     filename_plot = ex.DATAPATH_PROCESSED + "/SCATTER_LOSS_"+ file_name+ ".html"
        #     plotly.offline.plot(save_plot, filename=filename_plot)        

def plot_deq_scatter(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[['src', 'seq', 'dequeued']]
        dropped = queue_occupancy[queue_occupancy.dequeued==1]
        dropped.index = (dropped.index - dropped.index[0]).total_seconds()
        tmp_file = '/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_scatter_deq/' + file_name + '.csv'
        dropped.to_csv(tmp_file, header=False, index=True, mode = 'a')
        df = pd.read_csv(tmp_file, sep=',', names=["time", "src", "seq", "dequeued"])

        fig = go.Figure()
        ports = df_queue['src'].unique()
        for port in ports:
            dropped_port = df[df.src==port]
            fig.add_trace(go.Scatter(
                x=dropped_port["time"],
                y=dropped_port["dequeued"],
                mode='markers',
                name=str(port)
            ))
        # fig.update_traces(marker=dict(size=2,
        #                       line=dict(width=2,
        #                                 color='DarkSlateGrey')),
        #           selector=dict(mode='markers'))
        fig.update_layout(
            title="Sequence Numbers of dequeued",
            xaxis_title="<b>Time(s)</b>",
            yaxis_title="<b>dequeued</b>",
        )
        filename_plot = "/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/plots_scatter_deq/SCATTER_DEQ_" +file_name +  ".html"
        plotly.offline.plot(fig, filename=filename_plot)

all_analysers = cmn.get_all_experiment_analysers()
# all_analysers = cmn.get_experiment_analysers("2bw-20rtt-16q-iperf-localVideotest-1-1-cubic-cubic--240s-20200830T160340")
for analyser in all_analysers:
    print("~~~~~~~~",analyser, "~~~~~~")
    plot_deq_scatter(all_analysers[analyser], analyser)
#     combi_lossrate(all_analysers[analyser], analyser)
    # plot_loss(all_analysers[analyser], analyser)
    # plot_queue_occupancy(all_analysers[analyser], analyser)
    # plot_goodput(all_analysers[analyser], 100, analyser)

# total_loss()
# solo_mean_loss()