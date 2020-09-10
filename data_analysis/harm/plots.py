import pandas as pd
import plotly.express as px
import plotly 
import plotly.graph_objects as go


def load_goodput_harm_data():
    goodput_harm_by_localVideo = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-localVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    goodput_harm_by_youtube = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-webVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    iperf_local_youtube_combi = [goodput_harm_by_localVideo, goodput_harm_by_youtube]
    new_df = pd.concat(iperf_local_youtube_combi)
    new_df = new_df.reset_index()
    return new_df
    # return goodput_harm_by_youtube

def plot_combine():
    goodput_harm_by_localVideo = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-localVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    goodput_harm_by_youtube = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-webVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    iperf_local_youtube_combi = [goodput_harm_by_localVideo, goodput_harm_by_youtube]
    new_df = pd.concat(iperf_local_youtube_combi)
    new_df = new_df.reset_index()

    three_g = new_df.query("network == '3G'")
    homelink = new_df.query("network == 'Homelink'")


    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r = three_g['harm'],
        theta = three_g['cca_combo'],
        mode = 'lines',
        connectgaps=True,
        name = '3G',
        fill='toself'
    ))

    fig.add_trace(go.Scatterpolar(
        r = homelink['harm'],
        theta = homelink['cca_combo'],
        mode = 'lines',
        connectgaps=True,
        name = 'Homelink',
        fill='toself'
    ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True
        ),
    ),
    showlegend=True,
    font=dict(
        # family="Courier New, monospace",
        # size=11,
        color="black"
    )
    )

    

    fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    # y=1.07,
    xanchor="right",
    x=0.1,
    font_color="black"
))
    fig.show()
    # plotly.offline.plot(fig, filename='radar3.png')

def plot_bar_combine():
    df_local_video = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-localVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    lv_homelink = df_local_video.query("network == 'Homelink'")
    lv_3G = df_local_video.query("network == '3G'")

    df_youtube = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-webVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    u_homelink = df_youtube.query("network == 'Homelink'")
    u_3G = df_youtube.query("network == '3G'")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=lv_homelink['cca_combo'],
        y=lv_homelink['harm'],
        name='Homelink',
        marker_color='indianred'
    ))
    fig.add_trace(go.Bar(
        x=lv_3G['cca_combo'],
        y=lv_3G['harm'],
        name='3G',
        marker_color='lightsalmon'
    ))

    # Here we modify the tickangle of the xaxis, resulting in rotated labels.
    fig.update_layout(xaxis_tickangle=-45)
    # fig.show()
    plotly.offline.plot(fig, filename='bar_u.html')

def plot_radar():
    df_local_video = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-localVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    lv_homelink = df_local_video.query("network == 'Homelink'")
    lv_3G = df_local_video.query("network == '3G'")

    df_youtube = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/goodput-harm-iperf-webVideo.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    u_homelink = df_youtube.query("network == 'Homelink'")
    u_3G = df_youtube.query("network == '3G'")
    # lv_3G.append(lv_3G.loc[1:2])
    # lv_homelink.append(lv_homelink.loc[1:2])
    # print(lv_homelink['harm'])
    # fig = go.Figure(data=go.Scatterpolar(
    # # r=[1, 5, 2, 2, 3],
    # # theta=['processing cost','mechanical properties','chemical stability', 'thermal stability',
    # #         'device integration'],
    
    # r=[lv_homelink['harm']],
    # theta=[dict(lv_homelink['cca_combo'])],
    # # lv_homelink,
    # fill='toself'
    # ))
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r = lv_homelink['harm'],
        theta = lv_homelink['cca_combo'],
        mode = 'lines',
        connectgaps=True,
        # line_close=True,
        name = 'iperf-localVideo(Homelink)',
        # line_color = 'peru',
        fill='toself'
    ))

    fig.add_trace(go.Scatterpolar(
        r = lv_3G['harm'],
        theta = lv_3G['cca_combo'],
        mode = 'lines',
        name = 'iperf-localVideo(3G)',
        # line_color = 'peru',
        fill='toself'
    ))

    fig1 = go.Figure()
    fig1.add_trace(go.Scatterpolar(
        r = u_homelink['harm'],
        theta = u_homelink['cca_combo'],
        mode = 'lines',
        name = 'iperf-Youtube(Homelink)',
        # line_color = 'peru',
        fill='toself'
    ))

    fig1.add_trace(go.Scatterpolar(
        r = u_3G['harm'],
        theta = u_3G['cca_combo'],
        mode = 'lines',
        name = 'iperf-Youtube(3G)',
        # line_color = 'peru',
        fill='toself'
    ))

    # fig = px.line_polar(lv_homelink, r='harm', theta='cca_combo', line_close=True)
    # fig.update_traces(fill='toself')

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True
        ),
    ),
    showlegend=True
    # line_close=True
    )
    plotly.offline.plot(fig, filename='radar.html')

    fig1.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True
        ),
    ),
    showlegend=True
    # line_close=True
    )
    plotly.offline.plot(fig1, filename='radar_u.html')
    # fig.show()

def plot_bar_all():
    # homelink = new_df.query("network == 'Homelink'")
    new_df = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/data-processed/harm/new.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    new_df['display'] = new_df['cca_combo'].str.cat(new_df['network'],sep="-")


    fig = px.bar(new_df, x='percent', y='display', labels={'percent':'<b>Goodput Harm %</b>'}, color='percent', orientation='h')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        yaxis_title="<b>Victim(CCA)-Subject(CCA)-Network</b>",
        xaxis_title="<b>Goodput Harm %</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis =  {                                     
                                    'showgrid': True,
                                    'gridcolor':'LightGrey'
                                         },
                                yaxis = {                              
                                   'showgrid': True,
                                   'gridcolor':'LightGrey'
                                        },
                                    
        font=dict(
                # family="Courier New, monospace",
                size=14
                # color="RebeccaPurple"
            )
    )
    # fig.show()
    plotly.offline.plot(fig, filename='goodput_harm_iperf_locavideo_youtube_homelink_summary.html')

def plot_homelink_goodput_harm(new_df):
    homelink = new_df.query("network == 'Homelink'")
    fig = px.bar(homelink, x='cca_combo', y='percent', labels={'percent':'<b>Goodput Harm %</b>'}, color='percent')
    fig.update_layout(
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>Victim-Competing traffic</b>",
        yaxis_title="<b>Goodput Harm %</b>",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    # fig.show()
    plotly.offline.plot(fig, filename='goodput_harm_iperf_locavideo_youtube_homelink_summary.html')

def plot_3G_goodput_harm(new_df):
    _3G = new_df.query("network == '3G'")
    fig = px.bar(_3G, x='cca_combo', y='percent', labels={'percent':'<b>Goodput Harm %</b>'}, color='percent')
    fig.update_layout(
        # title="Goodput harm done to iperf under 3G (iperf-localVideo | iperf-youtube)",
        xaxis_title="<b>Victim-Competing traffic</b>",
        yaxis_title="<b>Goodput Harm %</b>",
        plot_bgcolor='rgba(0,0,0,0)'
    )
    # fig.show()
    plotly.offline.plot(fig, filename='goodput_harm_iperf_locavideo_youtube_3G_summary.html')

def plot_homelink_bitrate_harm():
    bitrate_homelink = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_14/harm/bitrate_harm_localvideo_iperf.csv',sep=',', 
                  names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])

    bitrate_homelink
    bitrate_homelink = bitrate_homelink.query("network == 'Homelink'")

    options = ['cubic-reno', 'bbr-reno', 'bbr-cubic']
    bitrate_homelink = bitrate_homelink.loc[~bitrate_homelink['cca_combo'].isin(options)] 

    bit = px.bar(bitrate_homelink, x='cca_combo', y='percent', labels={'percent':'Harm %'}, color='percent')
    bit.update_layout(
        title="Bitrate harm done to localVideo under homelink (localVideo-iperf)",
        xaxis_title="victimCCA-CompetingCCA",
        yaxis_title="Harm %"
    )
    # bit.show()
    plotly.offline.plot(bit, filename='bitrate_harm_localVideo_iperf_homelink_summary.html')

def plot_3G_bitrate_harm():
    bitrate_3G = pd.read_csv('/Users/rukshani/Documents/DATASET/WEEK_14/harm/bitrate_harm_localvideo_iperf.csv',sep=',', 
                  names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    bitrate_3G = bitrate_3G.query("network == '3G'")

    options = ['cubic-reno', 'bbr-reno', 'bbr-cubic']
    bitrate_3G = bitrate_3G.loc[~bitrate_3G['cca_combo'].isin(options)] 

    bit = px.bar(bitrate_3G, x='cca_combo', y='percent', labels={'percent':'Harm %'}, color='percent')
    bit.update_layout(
        title="Bitrate harm done to localVideo under 3G (localVideo-iperf)",
        xaxis_title="victimCCA-CompetingCCA",
        yaxis_title="Harm %"
    )
    bit.show()
    plotly.offline.plot(bit, filename='bitrate_harm_localVideo_iperf_3G_summary.html')

def include_victim(desc):
    # print(desc)
    jumble = desc.split('-', 2)
    victim = jumble[0]
    return victim

def include_subject(desc):
    # print(desc)
    jumble = desc.split('-', 2)
    subject = jumble[1]
    return subject

def plot_bar_3G():
    # homelink = new_df.query("network == 'Homelink'")
    new_df = pd.read_csv('/Users/rukshani/Documents/DATASET/draft/NEW/data-processed/harm/order_final.csv',sep=',', 
                    names=["cca_combo", "harm", "percent", "cca_1", "cca_2", "network"])
    
    new_df['victim'] = new_df['cca_combo'].apply(include_victim)
    new_df['subject'] = new_df['cca_combo'].apply(include_subject)

    fig = px.bar(new_df, x="victim", y="percent", barmode="group", color="subject",
        color_discrete_sequence=["blue", "green", "goldenrod", "red"],
             facet_col="network",
             
             category_orders={"network": ["3G", "Homelink"]
                            #   "time": ["Lunch", "Dinner"]
                            },
                            labels={'subject':'<b>Subject(CCA)<b>',
                                    'network':'<b>Network<b>',
                                    # 'victim':'<b>Victim(CCA)<b>'
                                    })
    # fig.update_xaxes(title_text="<b>Victim(CCA)<b>")
    fig['layout']['xaxis']['title']['text']=''
    fig['layout']['xaxis2']['title']['text']=''
    fig.update_layout(
        # secondary_x=False,
        # title="Goodput harm done to iperf under homelink (iperf-localVideo | iperf-youtube)",
        yaxis_title="<b>Goodput Harm %</b>",
        # xaxis_title="<b>Victim(CCA)</b>",
        # xaxis_title2="<b>Victim(CCA)</b>",
        plot_bgcolor='rgba(0,0,0,0)',
        # xaxis = dict(title = 'Epoch'),
        xaxis1 =  {                                     
                                    'showgrid': False,
                                    'gridcolor':'LightGrey'
                                    # 'title':'<b>Victim(CCA)</b>'
                                         },
                                yaxis1 = {                              
                                   'showgrid': True,
                                   'gridcolor':'LightGrey'
                                        },
        xaxis2 =  {                                     
                                    'showgrid': False,
                                    'gridcolor':'LightGrey'
                                    # 'title':'<b>Victim(CCA)</b>'
                                         },
                                yaxis2 = {                              
                                   'showgrid': True,
                                   'gridcolor':'LightGrey'
                                        },
                                    
        font=dict(
                # family="Courier New, monospace",
                size=16
                # color="RebeccaPurple"
            )
    )

    fig.update_layout(
    # keep the original annotations and add a list of new annotations:
    annotations = list(fig.layout.annotations) + 
    [go.layout.Annotation(
            x=0.55,
            y=-0.35,
            font=dict(
                size=16
            ),
            showarrow=False,
            text="<b>Victim(CCA)</b>",
            # textangle=-90,
            xref="paper",
            yref="paper"
        )
    ])
    plotly.offline.plot(fig, filename='goodput_harm_iperf_locavideo_youtube_homelink_summary.html')

# new_df = load_goodput_harm_data()
# plot_bar_combine()
# plot_homelink_goodput_harm(new_df)
# plot_3G_goodput_harm(new_df)
plot_bar_3G()



