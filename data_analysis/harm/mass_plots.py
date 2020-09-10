import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go

def load_goodput_harm_data():
    goodput_harm_by_localVideo = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_19/OLDDATASET_RESULTS.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    # goodput_harm_by_youtube = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-webVideo.csv',sep=',', 
    #                 names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    # iperf_local_youtube_combi = [goodput_harm_by_localVideo, goodput_harm_by_youtube]
    # new_df = pd.concat(iperf_local_youtube_combi)
    # new_df = new_df.reset_index()
    # return new_df
    return goodput_harm_by_localVideo

def plot_goodput_harm_homelink(new_df):
    # three_g = new_df.query("network == '3G'")
    homelink = new_df.query("network == 'Homelink'")
    fig = px.bar(homelink, x='cca_combo', y='percent', labels={'percent':'<b>Goodput Harm %</b>'}, color='percent')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>Victim(iperf)-Subject(youtube)</b>",
        yaxis_title="<b>Goodput Harm %</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="iperf-youtube (Homelink)",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='goodput_harm_iperf_youtube_homelink_summary.html')

def plot_goodput_harm_3G(new_df):
    three_g = new_df.query("network == '3G'")
    # homelink = new_df.query("network == 'Homelink'")
    fig = px.bar(three_g, x='cca_combo', y='percent', labels={'percent':'<b>Goodput Harm %</b>'}, color='percent')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>Victim(iperf)-Subject(youtube)</b>",
        yaxis_title="<b>Goodput Harm %</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        title="iperf-youtube (3G)",
    )
    # fig.show()
    plotly.offline.plot(fig, filename='goodput_harm_iperf_youtube_3G_summary.html')

def all_bars(new_df):
    fig = px.bar(new_df, x="cca_combo", y="percent", barmode="group",
    #  color="subject",
        # color_discrete_sequence=["blue", "green", "goldenrod", "red"],
             facet_col="network",
             
             category_orders={"network": ["3G", "Homelink"]
                            #   "time": ["Lunch", "Dinner"]
                            }
                            # ,
                            # labels={'subject':'<b>Subject(CCA)<b>',
                            #         'network':'<b>Network<b>',
                            #         # 'victim':'<b>Victim(CCA)<b>'
                            #         }
                                    )
    fig.update_layout(
        # secondary_x=False,
        title="Goodput harm done to iperf (iperf-localVideo | iperf-youtube)"
    )
    plotly.offline.plot(fig, filename='old_dataset_summary.html')

new_df = load_goodput_harm_data()
all_bars(new_df)
# plot_goodput_harm_homelink(new_df)
# plot_goodput_harm_3G(new_df)
# ["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"]