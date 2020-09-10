import sys, os
sys.path.append('data_analysis')

import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go
# import experiment as ex

plot_save_path = '/Users/rukshani/Documents/DATASET/WEEK_21/NEW_RESULTS/all-3G/'

def load_goodput_harm_data():
    goodput_harm = pd.read_csv(plot_save_path + '/harm/goodput-harm-iperf-all-video.csv',sep=',', 
                    names=["cca_combo", "harm", "harm_perc", "iperf_cca", "video_cca", "network"])
    goodput_harm["harm_type"] = "goodput"
    return goodput_harm

def load_bitrate_harm_data():
    bitrate_harm = pd.read_csv(plot_save_path + '/harm/bitrate_harm_video.csv',sep=',', 
                    names=["cca_combo", "harm", "harm_perc", "iperf_cca", "video_cca", "network"])
    bitrate_harm["harm_type"] = "bitrate"
    return bitrate_harm

def plot_harm_percent(harm_df):
    fig = px.bar(harm_df, x='cca_combo', y='harm_perc', labels={'percent':'<b>Harm(%)</b>'}, color='harm_type', barmode="group", category_orders={"harm_type": ["goodput", "bitrate"]})
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>CCA-CCA</b>",
        yaxis_title="<b>Harm(%)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="IPERF-VIDEO(Local or YouTube) - Goodput harm (cca<--cca) | Bitrate harm (cca-->cca) - 3G",
    )
    # fig.show()
    filename = plot_save_path + "all_harm_3G.html"
    plotly.offline.plot(fig, filename=filename)


goodput_harm = load_goodput_harm_data()
bitrate_harm = load_bitrate_harm_data()

all_harm_df = [goodput_harm, bitrate_harm]
harm_df = pd.concat(all_harm_df)
harm_df = harm_df.reset_index()
# print(harm_df)

plot_harm_percent(harm_df)

