import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go
import experiment as ex

def plot_loss_per_port():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/combi-loss-perc.csv', sep=',', names=["filename", "port", "enq", "drop", "loss"])
    iper_df = df.query("port == 5202")
    fig = px.bar(iper_df, x='filename', y='loss', labels={'loss':'<b>Loss %</b>'}, color='loss')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>experiment</b>",
        yaxis_title="<b>Loss %</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="3G - iperf-localVideo [iperf loss%]",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/loss_per_iperf_port.html')

def plot_solo_loss():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/solo-loss-perc.csv', sep=',', names=["filename", "enq", "drop", "loss"])
    # iper_df = df.query("port == 5202")
    fig = px.bar(df, x='filename', y='loss', labels={'loss':'<b>Loss %</b>'}, color='loss')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>experiment</b>",
        yaxis_title="<b>Loss</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="3G - iperf SOLO",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/loss_solo_iperf.html')

def plot_total_loss():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/total-loss-perc.csv', sep=',', names=["filename", "enq", "drop", "loss"])
    # iper_df = df.query("port == 5202")
    fig = px.bar(df, x='filename', y='loss', labels={'loss':'<b>Loss %</b>'}, color='loss')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>experiment</b>",
        yaxis_title="<b>Loss</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="3G - iperf-localVideo [Total Loss %]",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/COMBI/tot_loss.html')

def plot_mean_solo_loss():
    df = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/mean-solo-loss-perc.csv', sep=',', names=["filename", "loss"])
    # iper_df = df.query("port == 5202")
    fig = px.bar(df, x='filename', y='loss', labels={'loss':'<b>Loss %</b>'}, color='loss')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>CCA</b>",
        yaxis_title="<b>Avg Loss % </b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="3G - iperf SOLO",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='/Users/rukshani/Documents/DATASET/WEEK_22/loss/FULL/SOLO/mean_solo_loss.html')

# plot_solo_loss()
# plot_loss_per_port()
plot_total_loss()
# plot_mean_solo_loss()