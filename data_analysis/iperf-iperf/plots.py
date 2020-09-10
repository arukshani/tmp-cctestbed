import sys, os
sys.path.append('data_analysis')

import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go
import experiment as ex

def load_goodput_harm_data():
    goodput_harm = pd.read_csv('/tmp/data-processed/harm/goodput-harm-iperf-iperf.csv',sep=',', 
                    names=["cca_combo", "iperf1_harm", "iperf1_perc", "iperf2_harm", "iperf2_perc", "cca_1", "cca_2", "network", "gp_jfi", "harm_jfi", "gp_1_jfi", "harm_1_jfi"])
    return goodput_harm

def all_bars(new_df, fig):
    # fig = px.bar(new_df, x="cca_combo", y="iperf1_perc", barmode="group",
    #          facet_col="network",
             
    #          category_orders={"network": ["3G", "Homelink"]
    #                         }
    #             )
    new_df_3g = new_df[(new_df.network.str.contains('3G'))]
    all_columns_3g =  list(new_df_3g.columns)
    iperf1_harm_3g= new_df_3g[all_columns_3g[1]]
    iperf2_harm_3g= new_df_3g[all_columns_3g[3]]
    gp_jfi_3g= new_df_3g[all_columns_3g[8]]
    harm_jfi_3g= new_df_3g[all_columns_3g[9]]
    gp_1_jfi_3g= new_df_3g[all_columns_3g[10]]
    harm_1_jfi_3g= new_df_3g[all_columns_3g[11]]
    x_data_3g = new_df_3g[all_columns_3g[0]]
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=iperf1_harm_3g, name="iperf1harm-3G", mode="lines+markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=iperf2_harm_3g, name="iperf2harm-3G", mode="lines+markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=gp_jfi_3g, name="JFI-Goodput-3G", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=harm_jfi_3g, name="JFI-Harm-3G", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=gp_1_jfi_3g, name="Unfairness-Goodput-3G", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_3g, y=harm_1_jfi_3g, name="Unfairness-Harm-3G", mode="markers")
    )

    new_df_homelink = new_df[(new_df.network.str.contains('Homelink'))]
    all_columns_homelink =  list(new_df_homelink.columns)
    iperf1_harm_homelink= new_df_homelink[all_columns_homelink[1]]
    iperf2_harm_homelink= new_df_homelink[all_columns_homelink[3]]
    gp_jfi_homelink= new_df_homelink[all_columns_3g[8]]
    harm_jfi_homelink= new_df_homelink[all_columns_3g[9]]
    gp_1_jfi_homelink= new_df_homelink[all_columns_3g[10]]
    harm_1_jfi_homelink= new_df_homelink[all_columns_3g[11]]
    x_data_homelink = new_df_homelink[all_columns_homelink[0]]
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=iperf1_harm_homelink, name="iperf1harm-Homelink", mode="lines+markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=iperf2_harm_homelink, name="iperf2harm-Homelink", mode="lines+markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=gp_jfi_homelink, name="JFI-Goodput--Homelink", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=harm_jfi_homelink, name="JFI-Harm-Homelink", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=gp_1_jfi_homelink, name="Unfairness-Goodput--Homelink", mode="markers")
    )
    fig.add_trace(
        go.Scatter(x=x_data_homelink, y=harm_1_jfi_homelink, name="Unfairness-Harm-Homelink", mode="markers")
    )
    return fig



new_df = load_goodput_harm_data()
fig1 = go.Figure()
fig1 = all_bars(new_df, fig1)
fig1.update_layout(
            title="iperf-iperf [harm = 0-1; 0 good 1 bad] [JFI = 0-1; 0 bad 1 good;] [Discrimination index = 1 - JFI; (0-1; 0 good 1 bad)]",
            xaxis_title="<b>CCA-CCA (s)</b>",
            yaxis_title="<b>Index (Harm | JFI)</b>",
        )
fig1.update_traces(marker=dict(size=12,
                              line=dict(width=2,
                                        color='DarkSlateGrey')),
                  selector=dict(mode='markers'))
filename_plot = ex.DATAPATH_PROCESSED + "/harm/iperf-iperf-harm-plot.html"
plotly.offline.plot(fig1, filename=filename_plot)

# fig2 = go.Figure()
# fig2 = all_bars(new_df, fig2, 'Homelink')
# fig2.update_layout(
#             title="iperf-iperf-Homelink",
#             xaxis_title="<b>CCA-CCA (s)</b>",
#             yaxis_title="<b>Harm(%)</b>",
#         )

# filename_plot = ex.DATAPATH_PROCESSED + "/homelink-iperf-iperf-harm-plot.html"
# plotly.offline.plot(fig2, filename=filename_plot)