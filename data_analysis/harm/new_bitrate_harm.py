# Bring your packages onto the path
import sys, os
sys.path.append('data_analysis')

# Now do your import
# from config.config import *

import pandas as pd 
from pandas import DataFrame
import experiment as ex 
import os 
import subprocess
import json 
import util

def load_local_bitrate_solo_summary(filename):
    solo_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "bitrate"])
    solo_bitrate_df['network'] = solo_bitrate_df['filename'].apply(util.include_network_solo)
    solo_bitrate_df['cca'] = solo_bitrate_df['filename'].apply(util.include_cca_solo)
    return solo_bitrate_df

def load_web_bitrate_solo_summary(filename):
    solo_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "bitrate"])
    solo_bitrate_df['network'] = solo_bitrate_df['filename'].apply(util.include_web_network_solo)
    solo_bitrate_df['cca'] = solo_bitrate_df['filename'].apply(util.include_web_solo)
    return solo_bitrate_df

def load_bitrate_combi_summary(filename):
    combi_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "bitrate"])
    combi_bitrate_df['network'] = combi_bitrate_df['filename'].apply(util.include_network_combi)
    #Only when the second service is local
    combi_bitrate_df['video_cca'] = combi_bitrate_df['filename'].apply(util.include_cca_second)
    combi_bitrate_df['iperf_cca'] = combi_bitrate_df['filename'].apply(util.include_cca_combi)
    return combi_bitrate_df

def pick_solo_bitrate(solo_bitrate_df, cca, network): 
    victim_solo = solo_bitrate_df.loc[solo_bitrate_df['cca'].eq(cca) & solo_bitrate_df['network'].eq(network)]
    return victim_solo['bitrate']

def pick_combi_bitrate(combi_bitrate_df, cca_video, cca_iperf, network): 
    # print(cca_2)
    victim_combi = combi_bitrate_df.loc[combi_bitrate_df['video_cca'].eq(cca_video) & combi_bitrate_df['iperf_cca'].eq(cca_iperf) 
                & combi_bitrate_df['network'].eq(network)]
    return victim_combi['bitrate']

def getBitrateHarm(solo_bitrate_df, combi_bitrate_df):
    networks = ["Homelink", "3G"]
    ccas_video = ["reno", "cubic", "bbr", "none"]
    ccas_iperf = ["reno", "cubic", "bbr", "none"]

    for cca_video in ccas_video: 
        for cca_iperf in ccas_iperf:
            for network in networks:
                # print(cca, cca_2, network)
                solo_bitrate = pick_solo_bitrate(solo_bitrate_df, cca_video, network)
                combi_bitrate = pick_combi_bitrate(combi_bitrate_df, cca_video, cca_iperf, network)
                if not combi_bitrate.empty:
                    harm, percentage = util.calculateHarm_more(solo_bitrate.iloc[0], combi_bitrate.iloc[0])
                    # print(harm, percentage)
                    combi_cca = cca_iperf + "-" + cca_video
                    data = [[combi_cca, harm, percentage, cca_iperf, cca_video, network]]
                    new_df = pd.DataFrame(data)
                    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/bitrate_harm_video.csv', header=False, index=False, mode = 'a')

##~~~~~~~~~~MAIN~~~~~~~~~~~~~~~
solo_bitrate_local_df = load_local_bitrate_solo_summary('/harm/solo-results/avg-solo-bitrate-localVideo.csv')
solo_bitrate_web_df = load_web_bitrate_solo_summary('/harm/solo-results/avg-solo-bitrate-webVideo.csv')
# print(solo_bitrate_local_df)
# print(solo_bitrate_web_df)

all_solo_df = [solo_bitrate_local_df, solo_bitrate_web_df]
solo_df = pd.concat(all_solo_df)
solo_df = solo_df.reset_index()
# print(solo_df)

combi_bitrate_df_local = load_bitrate_combi_summary('/harm/combi-results/avg-bitrate-localVideo.csv')
combi_bitrate_df_web = load_bitrate_combi_summary('/harm/combi-results/avg-bitrate-webVideo.csv')
# print(combi_bitrate_df_local)
# print(combi_bitrate_df_web)

all_combi_df = [combi_bitrate_df_local, combi_bitrate_df_web]
combi_df = pd.concat(all_combi_df)
combi_df = combi_df.reset_index()
# print(combi_df)

getBitrateHarm(solo_df, combi_df)