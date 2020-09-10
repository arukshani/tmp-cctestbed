import common as cmn
import experiment as ex

def toMb(x):
   return (x * cmn.BYTES_TO_BITS) * cmn.BITS_TO_MEGABITS

def bitrate(x, window_size):
   return x / (window_size * cmn.MILLISECONDS_TO_SECONDS)

def plot_queue_occupancy(experiment_analyzer, file_name):
    with experiment_analyzer.hdf_queue() as hdf_queue:
        df_queue = hdf_queue.select('df_queue')
        queue_occupancy = df_queue[df_queue['src'].unique()]
        queue_occupancy.index = (queue_occupancy.index - queue_occupancy.index[0]).total_seconds()
        plt = queue_occupancy.plot(kind='line', figsize=(25,10))
        plt.set_xlabel('time (seconds)')
        plt.set_ylabel('num packets in queue')
        fig = plt.get_figure()
        fig.savefig(ex.DATAPATH_PROCESSED + "/queue_occupancy_" + file_name + ".png")

def plot_goodput(experiment_analyzer, window_size, file_name):
    # use RTT from first flow if window size is not specified
    if window_size is None:
        window_size = experiment_analyzer.experiment.flows[0].rtt
    # transfer_time = window_size * cmn.MILLISECONDS_TO_SECONDS
    with experiment_analyzer.hdf_queue() as hdf_queue:
        # src_query = 'src=' + ' | src='.join(map(lambda x: str(5555+x),
        #                                         range(len(experiment_analyzer.experiment.flows))))
        # dequeued = hdf_queue.select('df_queue',
        #                             where='dequeued=1 & ({})'.format(src_query),
        #                             columns=['src', 'datalen'])
        df_queue = hdf_queue.select('df_queue')
        dequeued = df_queue[df_queue.dequeued==1]
        goodput = (dequeued
                        .groupby('src')
                        .datalen
                        .resample('{}ms'.format(window_size))
                        .sum().apply(toMb).apply(bitrate, args = ([window_size]))
                        .unstack(level='src')
                        .fillna(0))
        # transfer_size = (transfer_size * cmn.BYTES_TO_BITS) * cmn.BITS_TO_MEGABITS
        # goodput = transfer_size / transfer_time
        goodput.index = (goodput.index - goodput.index[0]).total_seconds()
        # goodput = goodput.rename(columns=experiment_analyzer.flow_names)
        # goodput = goodput[list(experiment_analyzer.flow_names.values())]
        plt = goodput.plot(kind='line', figsize=(25,10))
        plt.set_xlabel('time (seconds)')
        plt.set_ylabel('goodput (mbps)')
        fig = plt.get_figure()
        fig.savefig(ex.DATAPATH_PROCESSED + "/goodput_"+ file_name+ ".png")

all_analysers = cmn.get_all_experiment_analysers()

for analyser in all_analysers:
    print("~~~~~~~~",analyser, "~~~~~~")
    plot_queue_occupancy(all_analysers[analyser], analyser)
    plot_goodput(all_analysers[analyser], 100, analyser)
