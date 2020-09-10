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

##~~~~~~~~~~BITARE HARM~~~~~~~~~~~~~~~

def load_bitrate_solo_summary(filename):
    solo_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename,sep=',', names=["bitrate", "ccalg", "desc", "metric"])
    solo_bitrate_df['network'] = solo_bitrate_df['desc'].apply(util.include_network_solo)
    return solo_bitrate_df

def load_bitrate_combi_summary(filename):
    combi_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename,sep=',', names=["Port", "bitrate", "desc", "metric"])
    combi_bitrate_df['network'] = combi_bitrate_df['desc'].apply(util.include_network_combi)
    combi_bitrate_df['cca'] = combi_bitrate_df['desc'].apply(util.include_cca_combi)

    #Only when the second service is local
    combi_bitrate_df['2_cca'] = combi_bitrate_df['desc'].apply(util.include_cca_second)

    return combi_bitrate_df

def pick_solo_bitrate(solo_bitrate_df, cca, network): 
    victim_solo = solo_bitrate_df.loc[solo_bitrate_df['ccalg'].eq(cca) & solo_bitrate_df['network'].eq(network)]
    return victim_solo['bitrate']

def pick_combi_bitrate(combi_bitrate_df, cca, network): 
    victim_combi = combi_bitrate_df.loc[combi_bitrate_df['cca'].eq(cca) & combi_bitrate_df['network'].eq(network)]
    return victim_combi['bitrate']

def pick_combi_2_bitrate(combi_bitrate_df, cca, cca_2, network, port): 
    # print(cca_2)
    victim_combi = combi_bitrate_df.loc[combi_bitrate_df['cca'].eq(cca) & combi_bitrate_df['2_cca'].eq(cca_2) 
                & combi_bitrate_df['network'].eq(network) & combi_bitrate_df['Port'].eq(port)]
    return victim_combi['bitrate']

def getBitrateHarm(solo_bitrate_df, combi_bitrate_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]

    for cca in ccas: 
        for network in networks:
            solo_bitrate = pick_solo_bitrate(solo_bitrate_df, cca, network)
            combi_bitrate = pick_combi_bitrate(combi_bitrate_df, cca, network)
            harm, percentage = util.calculateHarm_more(solo_bitrate.iloc[0], combi_bitrate.iloc[0])
            print(harm, percentage)
            data = [[harm, percentage, cca, network]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/bitrate_harm_localvideo.csv', header=False, index=False, mode = 'a')

#eg: iperf-localVideo
def getBitrateHarm2(solo_bitrate_df, combi_bitrate_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]
    ccas_2 = ["reno", "cubic", "bbr"]

    for cca in ccas: 
        for cca_2 in ccas_2:
            for network in networks:
                # print(cca, cca_2, network)
                solo_bitrate = pick_solo_bitrate(solo_bitrate_df, cca, network)
                combi_bitrate = pick_combi_2_bitrate(combi_bitrate_df, cca, cca_2, network, 5203)
                if not combi_bitrate.empty:
                    harm, percentage = util.calculateHarm_more(solo_bitrate.iloc[0], combi_bitrate.iloc[0])
                    print(harm, percentage)
                    combi_cca = cca + "-" + cca_2
                    data = [[combi_cca, harm, percentage, cca, cca_2, network]]
                    new_df = pd.DataFrame(data)
                    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/bitrate_harm_localvideo.csv', header=False, index=False, mode = 'a')
##~~~~~~~~~~MAIN~~~~~~~~~~~~~~~
solo_bitrate_df = load_bitrate_solo_summary('/harm/solo-results/solo_localVideo_bitrate.csv')
combi_bitrate_df = load_bitrate_combi_summary('/harm/combi-results/bitrate-iperf-localvideo.csv')
getBitrateHarm2(solo_bitrate_df, combi_bitrate_df)