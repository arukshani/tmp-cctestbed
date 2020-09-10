import common as cmn
import pandas as pd 
from pandas import DataFrame
import experiment as ex
import os 

def include_ccalg(port, ports):
    # cca = experiment_analyzer.flow_receiver_ports.get(Port, "empty")
    # if cca!= "empty":
    #     return experiment_analyzer.flow_receiver_ports[Port]
    # else:
    #     return "third party or unknown"
    return ports[port]

def get_total_data_transferred(experiment_analyzer):
    # df_queue[df_queue['dequeued']==1].sort_index().groupby('src')['datalen'].sum()
    tot_data = 0
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        tot_data = df_queue[df_queue['dequeued']==1].sort_index().groupby('src')['datalen'].sum() * cmn.BYTES_TO_MEGABYTES
    return tot_data

def save_transfer_size_by_port(experiment_analyzer, filename):
    # df_queue[df_queue['dequeued']==1].sort_index().groupby('src')['datalen'].sum()
    enqueued = 0
    dequeued = 0
    dropped = 0
    frames = None
    result = None 
    final = None 
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        enqueued = df_queue[df_queue['dequeued']==0].sort_index().groupby('src')['datalen'].sum() * cmn.BYTES_TO_MEGABYTES
        dequeued = df_queue[df_queue['dequeued']==1].sort_index().groupby('src')['datalen'].sum() * cmn.BYTES_TO_MEGABYTES
        dropped = df_queue[df_queue['dropped']==1].sort_index().groupby('src')['datalen'].sum() * cmn.BYTES_TO_MEGABYTES
        frames = [enqueued, dequeued, dropped]
        result = pd.concat([enqueued, dequeued, dropped], axis=1, sort=False)
        # result = result.columns = ['Port', 'Dequeued', 'Enqueued', 'Dropped']
        final = DataFrame (result)
        final = final.fillna(0)
        final.to_csv(ex.DATAPATH_PROCESSED +'/summary_transfersize_AWS_'+ filename + '.csv', header=False, index=True)
    return final

def get_total_data_transferred_for_given_flows(flows):
    print("Total data transferred of given ports>>", flows.sum(axis=0))

#Works for iperf 
def get_goodput_of_solo_exp(experiment_analyzer, app_type): #Goodput of each flow in a single experiment
    goodput = 0
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        # print("Duration>>", (dequeued.index.max() - dequeued.index.min()).total_seconds())
        goodput = (dequeued.groupby('src')['datalen'].sum() * cmn.BYTES_TO_BITS * cmn.BITS_TO_MEGABITS) / (dequeued.index.max() - dequeued.index.min()).total_seconds()
        goodput.to_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv', header=False, index=True)
        new_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv',sep=',', names=["Port", "Performance"])
        ports = experiment_analyzer.flow_receiver_ports
        new_df['ccalg'] = new_df.apply(lambda row: include_ccalg(row.Port.astype(int), ports), axis=1)
        new_df['app_type'] = app_type
        new_df['Metric'] = 'goodput_Mbps'
        os.remove(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv')
        new_df.to_csv(ex.DATAPATH_PROCESSED +'/summary_iperf_goodput.csv', header=False, index=False, mode = 'a')
    return goodput

def get_goodput(experiment_analyzer, app_type): #Goodput of each flow in a single experiment
    goodput = 0
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        # print("Duration>>", (dequeued.index.max() - dequeued.index.min()).total_seconds())
        goodput = (dequeued.groupby('src')['datalen'].sum() * cmn.BYTES_TO_BITS * cmn.BITS_TO_MEGABITS) / (dequeued.index.max() - dequeued.index.min()).total_seconds()
    return goodput

#Solo
def get_webpage_load_time(experiment_analyzer, app_type):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        port = dequeued.src.unique()
        page_load_time = (dequeued.index.max() - dequeued.index.min()).total_seconds()
        ccas = experiment_analyzer.get_ccalgs
        #app_type
        metric = 'time_s'
        data = [[port, page_load_time, ccas['cca'], app_type, metric]] 
        # Create the pandas DataFrame 
        df = pd.DataFrame(data)
        # print(df)
        df.to_csv(ex.DATAPATH_PROCESSED +'/summary_webpage_loadtime.csv', header=False, index=False, mode = 'a')

# def get_webpage_throughput(experiment_analyzer, app_type):
#     with experiment_analyzer.hdf_queue() as hdf_queue:
#         df_queue = hdf_queue.select('df_queue')
#         dequeued = df_queue[df_queue.dequeued==1]
#         goodput = (dequeued.groupby('src')['datalen'].sum() * cmn.BYTES_TO_BITS * cmn.BITS_TO_MEGABITS) / (dequeued.index.max() - dequeued.index.min()).total_seconds()
#         goodput.to_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv', header=False, index=True)
#         new_df = pd.read_csv(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv',sep=',', names=["Port", "Performance"])
#         ports = experiment_analyzer.flow_names
#         print(ports)
#         new_df['ccalg'] = new_df.apply(lambda row: include_ccalg(row.Port.astype(int), ports), axis=1)
#         new_df['app_type'] = app_type
#         new_df['Metric'] = 'goodput_Mbps'
#         os.remove(ex.DATAPATH_PROCESSED +'/tmp_goodput.csv')
#         new_df.to_csv(ex.DATAPATH_PROCESSED +'/summary_perf.csv', header=False, index=False, mode = 'a')

def get_total_goodput(goodput_of_flows):
    print("Total goodput of all flows>>", goodput_of_flows.sum(axis = 0))
    # print("Total goodput of first two flows>>", goodput_of_flows[0:2].sum(axis = 0))
    # print("Total goodput of first and third flows>>", goodput_of_flows.loc[[50350, 56438]].sum(axis=0))

def get_total_goodput_of_given_flows(goodput_of_flows, ports_array):
    print("Total goodput of given ports>>", goodput_of_flows.loc[ports_array].sum(axis=0))

def calculateHarm(victimSolo, victimWithTestedService):
    harm = ((victimSolo - victimWithTestedService)/victimSolo)*100
    return harm

# def renameFlows():

#Uncomment following block to get the total data transferred, duration and the goodput of each flow 
all_analysers = cmn.get_all_experiment_analysers()
for analyser in all_analysers:
    print("~~~~~~~~",analyser, "~~~~~~")
    # save_transfer_size_by_port(all_analysers[analyser], analyser) #MB
    print(get_total_data_transferred(all_analysers[analyser]), "MB")
    # get_goodput_of_solo_exp(all_analysers[analyser], analyser)
    # get_webpage_load_time(all_analysers[analyser], analyser)
    # print(get_goodput(all_analysers[analyser], analyser))

    # tot_data = get_total_data_transferred(all_analysers[analyser])
    # print(get_total_data_transferred_for_given_flows(tot_data))

#TODO: Automate once the flow name fix is done
# print("Harm % >", calculateHarm(47.040408,  44.43066))

# goodput_of_each_flow = get_goodput_of_each_flow(analyzer)
# print(goodput_of_each_flow)
# victim_solo_goodput = get_total_goodput(goodput_of_each_flow)
# victim_with_tested_service = get_total_goodput_of_given_flows(goodput_of_each_flow,[])
# calculateHarm(victim_solo_goodput, victim_with_tested_service)

# analyzer = get_experiment_analyser()
# print(get_goodput_of_each_flow(analyzer))
# goodput_of_each_flow = get_goodput_of_each_flow(analyzer)
# get_total_goodput(goodput_of_each_flow)
# get_total_goodput_of_given_flows(goodput_of_each_flow, [50350, 56438])



