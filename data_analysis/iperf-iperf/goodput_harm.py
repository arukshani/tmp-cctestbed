# Bring your packages onto the path
import sys, os
sys.path.append('data_analysis')
# sys.path.append('data_analysis/harm')
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
    # print(solo_iperf_goodput_df)
    solo_iperf_goodput_df['network'] = solo_iperf_goodput_df['filename'].apply(util.include_network_solo)
    solo_iperf_goodput_df['cca'] = solo_iperf_goodput_df['filename'].apply(util.include_cca_solo)
    # print(solo_iperf_goodput_df)
    return solo_iperf_goodput_df

def load_goodput_combi_summary(filename):
    combi_iperf_goodput_df = pd.read_csv(ex.DATAPATH_PROCESSED + filename, sep=',', names=["filename", "port", "goodput"])
    # print(combi_iperf_goodput_df)
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

def get_iperf_combi_goodput(combi_iperf_goodput_df, cca, cca_2, network, port): 
    # print(cca_2)
    victim_combi = combi_iperf_goodput_df.loc[combi_iperf_goodput_df['cca'].eq(cca) & combi_iperf_goodput_df['cca_2'].eq(cca_2) 
                & combi_iperf_goodput_df['network'].eq(network) & combi_iperf_goodput_df['port'].eq(port)]
    return victim_combi['goodput']

def calculate_jfi(value1, value2):
    numerator = (value1 + value2) * (value1 + value2)
    denominator = 2 * ((value1 * value1) + (value2 * value2))
    jfi = numerator / denominator
    return jfi 

#eg: iperf-iperf
def iperf_iperf_harm(solo_iperf_goodput_df, combi_iperf_goodput_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]
    ccas_2 = ["reno", "cubic", "bbr"]
    for cca in ccas: 
        for cca_2 in ccas_2:
            for network in networks:
                solo_iperf_goodput = get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network)
                combi_iperf1_gp = get_iperf_combi_goodput(combi_iperf_goodput_df, cca, cca_2, network, 5202)
                combi_iperf2_gp = get_iperf_combi_goodput(combi_iperf_goodput_df, cca, cca_2, network, 5203)
                if not combi_iperf1_gp.empty and not combi_iperf2_gp.empty:
                    logval = cca + "-" + cca_2+ "-" + network+ "-" + str(solo_iperf_goodput.iloc[0])+ "-" +str(combi_iperf1_gp.iloc[0]) + "-" + str(combi_iperf2_gp.iloc[0])
                    print(logval)
                    iperf1_harm, iperf1_perc = util.calculateHarm_more(solo_iperf_goodput.iloc[0], combi_iperf1_gp.iloc[0])
                    iperf2_harm, iperf2_perc = util.calculateHarm_more(solo_iperf_goodput.iloc[0], combi_iperf2_gp.iloc[0])
                    gp_jfi = calculate_jfi(combi_iperf1_gp.iloc[0], combi_iperf2_gp.iloc[0])
                    harm_jfi = calculate_jfi(iperf1_harm, iperf2_harm)
                    gp_1_jfi = 1 - gp_jfi
                    harm_1_jfi = 1 - harm_jfi
                    combi_cca = cca + "-" + cca_2
                    data = [[combi_cca, iperf1_harm, iperf1_perc, iperf2_harm, iperf2_perc, cca, cca_2, network, gp_jfi, harm_jfi, gp_1_jfi, harm_1_jfi]]
                    new_df = pd.DataFrame(data)
                    new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/goodput-harm-iperf-iperf.csv', header=False, index=False, mode = 'a')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN GOODPUT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
solo_iperf_goodput_df = load_goodput_solo_summary('/harm/solo-results/solo_iperf_goodput_avg.csv')
combi_iperf_goodput_df = load_goodput_combi_summary('/harm/combi-results/avg-goodput-iperf-iperf.csv')
print(solo_iperf_goodput_df)
print(combi_iperf_goodput_df)
iperf_iperf_harm(solo_iperf_goodput_df, combi_iperf_goodput_df)

    









