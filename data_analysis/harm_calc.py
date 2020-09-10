import common as cmn
import pandas as pd 
from pandas import DataFrame
import experiment as ex
import os 
import subprocess
import json 

#More is better
def calculateHarm_more(victimSolo, victimWithTestedService):
    # print(victimSolo, victimWithTestedService)
    percentage = ((victimSolo - victimWithTestedService)/victimSolo)*100
    harm = ((victimSolo - victimWithTestedService)/victimSolo)
    return harm, percentage

#Less is better
def calculateHarm_less(victimSolo, victimWithTestedService):
    print(victimSolo, victimWithTestedService)
    percentage = ((victimWithTestedService - victimSolo)/victimWithTestedService)*100
    harm = ((victimWithTestedService - victimSolo)/victimWithTestedService)
    return harm, percentage

def include_network_solo(desc):
    # print(desc)
    network_id = desc.split('-', 4)
    network = network_id[1] + "-" + network_id[2] + "-" + network_id[3]
    if network == "50bw-20rtt-256q":
        return "Homelink"
    elif network == "2bw-20rtt-16q":
        return "3G"

def include_network_combi(desc):
    # print(desc)
    network_id = desc.split('-', 4)
    network = network_id[0] + "-" + network_id[1] + "-" + network_id[2]
    if network == "50bw-20rtt-256q":
        return "Homelink"
    elif network == "2bw-20rtt-16q":
        return "3G"

def include_cca_combi(desc):
    # print(desc)
    jumble = desc.split('-', 8)
    cca = jumble[7]
    return cca

##~~~~~~~~~~GOODPUT HARM~~~~~~~~~~~~~~~

def load_goodput_solo_summary():
    solo_iperf_goodput_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/solo-results/summary_iperf_goodput.csv',sep=',', names=["Port", "Goodput", "ccalg", "desc", "metric"])
    solo_iperf_goodput_df['network'] = solo_iperf_goodput_df['desc'].apply(include_network_solo)
    return solo_iperf_goodput_df

def load_goodput_combi_summary():
    combi_iperf_goodput_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/combi-results/goodput-iperf-youtube.csv',sep=',', names=["Port", "Goodput", "desc", "metric"])
    combi_iperf_goodput_df['network'] = combi_iperf_goodput_df['desc'].apply(include_network_combi)
    combi_iperf_goodput_df['cca'] = combi_iperf_goodput_df['desc'].apply(include_cca_combi)
    return combi_iperf_goodput_df

def get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network): 
    victim_solo = solo_iperf_goodput_df.loc[solo_iperf_goodput_df['ccalg'].eq(cca) & solo_iperf_goodput_df['network'].eq(network)]
    # print(victim_solo['Goodput'])
    return victim_solo['Goodput']

def get_iperf_combi_goodput(combi_iperf_goodput_df, cca, network, port): 
    victim_combi = combi_iperf_goodput_df.loc[combi_iperf_goodput_df['cca'].eq(cca) & combi_iperf_goodput_df['network'].eq(network) & combi_iperf_goodput_df['Port'].eq(port)]
    # print(victim_solo['Goodput'])
    return victim_combi['Goodput']

def getHarm(solo_iperf_goodput_df, combi_iperf_goodput_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]

    for cca in ccas: 
        for network in networks:
            solo_iperf_goodput = get_iperf_solo_goodput(solo_iperf_goodput_df, cca, network)
            combi_iperf_goodput = get_iperf_combi_goodput(combi_iperf_goodput_df, cca, network, 5202)
            # print(combi_iperf_goodput)
            # print (solo_iperf_goodput.iloc[0])
            harm, percentage = calculateHarm_more(solo_iperf_goodput.iloc[0], combi_iperf_goodput.iloc[0])
            # print(harm, percentage)
            data = [[harm, percentage, cca, network]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/goodput_harm_iperf-youtube.csv', header=False, index=False, mode = 'a')

##~~~~~~~~~~END OF GOODPUT HARM~~~~~~~~~~~~~~~

##~~~~~~~~~~BITARE HARM~~~~~~~~~~~~~~~

def load_bitrate_solo_summary():
    solo_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/solo-results/summary_local_video_bitrate.csv',sep=',', names=["bitrate", "ccalg", "desc", "metric"])
    solo_bitrate_df['network'] = solo_bitrate_df['desc'].apply(include_network_solo)
    return solo_bitrate_df

def load_bitrate_combi_summary():
    combi_bitrate_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/combi-results/bitrate-localvideo-youtube.csv',sep=',', names=["Port", "bitrate", "desc", "metric"])
    combi_bitrate_df['network'] = combi_bitrate_df['desc'].apply(include_network_combi)
    combi_bitrate_df['cca'] = combi_bitrate_df['desc'].apply(include_cca_combi)
    return combi_bitrate_df

def pick_solo_bitrate(solo_bitrate_df, cca, network): 
    victim_solo = solo_bitrate_df.loc[solo_bitrate_df['ccalg'].eq(cca) & solo_bitrate_df['network'].eq(network)]
    return victim_solo['bitrate']

def pick_combi_bitrate(combi_bitrate_df, cca, network): 
    victim_combi = combi_bitrate_df.loc[combi_bitrate_df['cca'].eq(cca) & combi_bitrate_df['network'].eq(network)]
    return victim_combi['bitrate']

def getBitrateHarm(solo_bitrate_df, combi_bitrate_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]

    for cca in ccas: 
        for network in networks:
            solo_bitrate = pick_solo_bitrate(solo_bitrate_df, cca, network)
            combi_bitrate = pick_combi_bitrate(combi_bitrate_df, cca, network)
            harm, percentage = calculateHarm_more(solo_bitrate.iloc[0], combi_bitrate.iloc[0])
            print(harm, percentage)
            data = [[harm, percentage, cca, network]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/bitrate_harm_localvideo.csv', header=False, index=False, mode = 'a')


##~~~~~~~~~~END OF BITRATE HARM~~~~~~~~~~~~~~~

##~~~~~~~~~~WEB PAGE LOAD~~~~~~~~~~~~~~~
def load_webpage_solo_summary():
    solo_webpage_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/solo-results/summary_webpage_loadtime.csv',sep=',', names=["Port", "page_load_time", "ccalg", "desc", "metric"])
    solo_webpage_df['network'] = solo_webpage_df['desc'].apply(include_network_solo)
    print(solo_webpage_df)
    return solo_webpage_df

def load_webpage_combi_summary():
    combi_webpage_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/combi-results/webpageload-localwebpage-youtube.csv',sep=',', names=["Port", "page_load_time", "desc", "metric"])
    combi_webpage_df['network'] = combi_webpage_df['desc'].apply(include_network_combi)
    combi_webpage_df['cca'] = combi_webpage_df['desc'].apply(include_cca_combi)
    print(combi_webpage_df)
    return combi_webpage_df

def pick_solo_row_webpage(solo_webpage_df, cca, network): 
    victim_solo = solo_webpage_df.loc[solo_webpage_df['ccalg'].eq(cca) & solo_webpage_df['network'].eq(network)]
    # print(victim_solo)
    return victim_solo['page_load_time']

def pick_combi_row_webpage(combi_webpage_df, cca, network): 
    victim_combi = combi_webpage_df.loc[combi_webpage_df['cca'].eq(cca) & combi_webpage_df['network'].eq(network)]
    # print(victim_combi)
    return victim_combi['page_load_time']

def getPageLoadHarm(solo_pageload_df, combi_pageload_df):
    networks = ["Homelink", "3G"]
    ccas = ["reno", "cubic", "bbr"]
    for cca in ccas: 
        for network in networks:
            solo_webpage_load = pick_solo_row_webpage(solo_pageload_df, cca, network)
            combi_webpage_load = pick_combi_row_webpage(combi_pageload_df, cca, network)
            harm, percentage = calculateHarm_less(solo_webpage_load.iloc[0], combi_webpage_load.iloc[0])
            print(harm, percentage)
            data = [[harm, percentage, cca, network]]
            new_df = pd.DataFrame(data)
            new_df.to_csv(ex.DATAPATH_PROCESSED +'/harm/pageload_harm_website.csv', header=False, index=False, mode = 'a')

##~~~~~~~~~~END OF WEB PAGE LOAD~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN GOODPUT~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
solo_iperf_goodput_df = load_goodput_solo_summary()
combi_iperf_goodput_df = load_goodput_combi_summary()
getHarm(solo_iperf_goodput_df, combi_iperf_goodput_df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~MAIN BITRATE~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# solo_bitrate_df = load_bitrate_solo_summary()
# combi_bitrate_df = load_bitrate_combi_summary()
# getBitrateHarm(solo_bitrate_df, combi_bitrate_df)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~WEB PAGE LOAD TIME~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# solo_pageload_df = load_webpage_solo_summary()
# combi_pageload_df = load_webpage_combi_summary()
# getPageLoadHarm(solo_pageload_df, combi_pageload_df)


    









