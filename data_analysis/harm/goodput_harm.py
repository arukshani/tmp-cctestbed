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

##~~~~~~~~~~GOODPUT HARM~~~~~~~~~~~~~~~

def load_goodput_solo_summary(filename):
    solo_iperf_goodput_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "goodput"])
    solo_iperf_goodput_df['network'] = solo_iperf_goodput_df['filename'].apply(util.include_network_solo)
    solo_iperf_goodput_df['cca'] = solo_iperf_goodput_df['filename'].apply(util.include_cca_solo)
    # print(solo_iperf_goodput_df)
    return solo_iperf_goodput_df

def load_goodput_combi_summary(filename):
    combi_iperf_goodput_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "goodput"])
    combi_iperf_goodput_df['network'] = combi_iperf_goodput_df['filename'].apply(util.include_network_combi)
    combi_iperf_goodput_df['cca'] = combi_iperf_goodput_df['filename'].apply(util.include_cca_combi)
    #Only when the second service is local
    combi_iperf_goodput_df['cca_2'] = combi_iperf_goodput_df['filename'].apply(util.include_cca_second)
    # print(combi_iperf_goodput_df)
    return combi_iperf_goodput_df

def get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network): 
    victim_solo = solo_iperf_goodput_df.loc[solo_iperf_goodput_df['cca'].eq(cca) & solo_iperf_goodput_df['network'].eq(network)]
    # print(victim_solo['Goodput'])
    return victim_solo['goodput']

def get_iperf_combi_goodput(combi_iperf_goodput_df, cca, network, port): 
    victim_combi = combi_iperf_goodput_df.loc[combi_iperf_goodput_df['cca'].eq(cca) & combi_iperf_goodput_df['network'].eq(network) & combi_iperf_goodput_df['Port'].eq(port)]
    # print(victim_solo['Goodput'])
    return victim_combi['goodput']

def get_iperf_combi_2_goodput(combi_iperf_goodput_df, cca, cca_2, network): 
    # print(cca_2)
    victim_combi = combi_iperf_goodput_df.loc[combi_iperf_goodput_df['cca'].eq(cca) & combi_iperf_goodput_df['cca_2'].eq(cca_2) 
                & combi_iperf_goodput_df['network'].eq(network)]
    return victim_combi['goodput']

#eg: iperf-youtube
def getHarm(solo_iperf_goodput_df, combi_iperf_goodput_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]

    for cca in ccas: 
        for network in networks:
            solo_iperf_goodput = get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network)
            combi_iperf_goodput = get_iperf_combi_goodput(combi_iperf_goodput_df, cca, network, 5202)
            # print(combi_iperf_goodput)
            # print (solo_iperf_goodput.iloc[0])
            harm, percentage = util.calculateHarm_more(solo_iperf_goodput.iloc[0], combi_iperf_goodput.iloc[0])
            # print(harm, percentage)
            data = [[harm, percentage, cca, network]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/goodput_harm_iperf_localvideo.csv', header=False, index=False, mode = 'a')

#eg: iperf-localVideo
def getHarm2(solo_iperf_goodput_df, combi_iperf_goodput_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]
    ccas_2 = ["reno", "cubic", "bbr", "none"]

    for cca in ccas: 
        for cca_2 in ccas_2:
            for network in networks:
                # print(cca, cca_2, network)
                solo_iperf_goodput = get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network)
                # print(network)
                combi_iperf_goodput = get_iperf_combi_2_goodput(combi_iperf_goodput_df, cca, cca_2, network)
                # print(combi_iperf_goodput)
                if not combi_iperf_goodput.empty:
                    logval = cca + "-" + cca_2+ "-" + network+ "-" + str(solo_iperf_goodput.iloc[0])+ "-" +str(combi_iperf_goodput.iloc[0])
                    print(logval)
                    harm, percentage = util.calculateHarm_more(solo_iperf_goodput.iloc[0], combi_iperf_goodput.iloc[0])
                    combi_cca = cca + "-" + cca_2
                    data = [[combi_cca, harm, percentage, cca, cca_2, network]]
                    new_df = pd.DataFrame(data)
                    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/goodput-harm-iperf-all-video.csv', header=False, index=False, mode = 'a')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN GOODPUT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
solo_iperf_goodput_df = load_goodput_solo_summary('/harm/solo-results/solo_iperf_goodput_avg.csv')
combi_iperf_goodput_df = load_goodput_combi_summary('/harm/combi-results/avg-goodput-iperf-all-video.csv')
# print(solo_iperf_goodput_df)
# print(combi_iperf_goodput_df)
getHarm2(solo_iperf_goodput_df, combi_iperf_goodput_df)








