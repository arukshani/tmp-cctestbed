import itertools
import logging
import cctestbedv2 as cctestbed
from config import * #HOST_CLIENT, HOST_SERVER defined in this
import flow_impl as flowImpl 
import combinatory_flow_impl as comFlowImpl 
import util 

from contextlib import ExitStack, contextmanager
import time
import util
import constant as const
import traceback

def prepare_iperf_experiment(args, test=None):
    if (args.competing_ccalgs) is None:
        raise Exception('Iperf test needs a value for competing_ccalgs')

    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()

    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    exp_params = list(itertools.product([args.nums_competing], args.competing_ccalgs, [args.duration], 
                        args.ntwrk_conditions, repetitions))
    print('Found {} iperf experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} iperf experiments. They are {}'.format(len(exp_params), exp_params))
    completed_experiment_procs = run_iperf_experiment(exp_params)
    util.cleanup_experiments(completed_experiment_procs)

def run_iperf_experiment(exp_params):
    completed_experiment_procs = []
    exp = ''
    num_completed_experiments = 0
    for params in exp_params:
        try:
            num_flows = params[0]
            ccalg = params[1]
            duration = params[2]
            btlbw, rtt, queue_size = params[3]

            util.log_current_experiment(num_completed_experiments, exp_params, params)
            if (util.is_rtt_too_small(rtt)):
                continue

            experiment_name = '{}-{}bw-{}rtt-{}q-{}iperf-{}s'.format(ccalg, btlbw, rtt, queue_size, num_flows, duration)
            flow_structure = util.get_flow_structure(ccalg, duration, rtt)
            flows = util.create_flows(flow_structure, const.FLOW_KIND_IPERF, num_flows, HOST_CLIENT, const.CLIENT_PORT, const.SERVER_PORT)
            exp = util.create_experiment(btlbw, queue_size, flows, experiment_name, HOST_CLIENT, HOST_SERVER, None)
            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)
            flowImpl.start_bess_for_iperf(exp, duration)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            util.handle_exception(e, exp)
    return completed_experiment_procs
 
def prepare_local_video_experiment(args, test=None):
    if (args.competing_ccalgs) is None:
        raise Exception('Local DASH video test needs a value for competing_ccalgs')

    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()

    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    exp_params = list(itertools.product([args.nums_competing], args.competing_ccalgs, [args.duration], 
                        args.ntwrk_conditions, repetitions))
    print('Found {} local video experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} local video experiments. They are {}'.format(len(exp_params), exp_params))
    completed_experiment_procs = run_local_video_experiment(exp_params)
    util.cleanup_experiments(completed_experiment_procs)

def run_local_video_experiment(exp_params):
    completed_experiment_procs = []
    exp = ''
    for params in exp_params:
        try:
            num_flows = params[0]
            ccalg = params[1]
            duration = params[2]
            btlbw, rtt, queue_size = params[3]

            experiment_name = '{}-{}bw-{}rtt-{}q-video-{}s'.format(ccalg, btlbw, rtt, queue_size, duration)
            flow_structure = util.get_flow_structure(ccalg, duration, rtt)
            flows = util.create_flows_local(flow_structure, const.FLOW_KIND_VIDEO, 1, HOST_CLIENT, const.CLIENT_PORT, const.SERVER_PORT) #Creating only 1 flow for video; TODO: see whether this is because we are starting only one server
            # util.update_apache_config(HOST_CLIENT, const.SERVER_PORT)
            exp = util.create_experiment(btlbw, queue_size, flows, experiment_name, HOST_CLIENT, HOST_SERVER, None)
            
            env_ccas_with_ports = str(const.SERVER_PORT + 1) + ':' + ccalg + '-'
            util.set_env_with_congestion(HOST_CLIENT, env_ccas_with_ports)
            
            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)
            flowImpl.start_bess_for_local_video(exp, duration)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            util.handle_exception(e, exp)
    return completed_experiment_procs

def prepare_local_website_experiment(args, test=None):
    if (args.competing_ccalgs) is None:
        raise Exception('Local website test needs a value for competing_ccalgs')

    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()

    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    exp_params = list(itertools.product([args.nums_competing], args.competing_ccalgs, [args.duration], 
                        args.ntwrk_conditions, repetitions))
    print('Found {} local website experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} local website experiments. They are {}'.format(len(exp_params), exp_params))
    completed_experiment_procs = run_local_website_experiment(exp_params)
    util.cleanup_experiments(completed_experiment_procs)

def run_local_website_experiment(exp_params):
    completed_experiment_procs = []
    exp = ''
    for params in exp_params:
        try:
            num_flows = params[0]
            ccalg = params[1]
            duration = params[2]
            btlbw, rtt, queue_size = params[3]

            experiment_name = '{}-{}bw-{}rtt-{}q-localWebsite-{}s'.format(ccalg, btlbw, rtt, queue_size, duration)
            flow_structure = util.get_flow_structure(ccalg, duration, rtt)
            flows = util.create_flows_local(flow_structure, const.FLOW_KIND_LOCAL_WEBSITE, 1, HOST_CLIENT, const.CLIENT_PORT, const.SERVER_PORT) #Creating only 1 flow for video; TODO: see whether this is because we are starting only one server
            exp = util.create_experiment(btlbw, queue_size, flows, experiment_name, HOST_CLIENT, HOST_SERVER, None)
            
            env_ccas_with_ports = str(const.SERVER_PORT + 1) + ':' + ccalg + '-'
            util.set_env_with_congestion(HOST_CLIENT, env_ccas_with_ports)
            
            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)
            flowImpl.start_bess_for_local_website(exp, duration)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            util.handle_exception(e, exp)
    return completed_experiment_procs

def prepare_web_video_experiment(args, test=None):
    if (args.websites) is None:
        raise Exception('Web Video needs a value for --website argument')

    websites = args.websites
    logging.info('Found {} websites'.format(len(websites)))
    
    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()

    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    #Here each website will be in a separate experiment. [website1, .....] [website2, ....]
    exp_params = list(itertools.product(websites, [args.nums_competing], [args.duration], args.ntwrk_conditions, repetitions))
    print('Found {} web video experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} web video experiments. They are {}'.format(len(exp_params), exp_params))
    # Found 1 web video experiments. They are [(['www.youtube.com', 'https://www.youtube.com/embed/aqz-KE-bpKQ?autoplay=1'], 1, 60, (50, 20, 256), 0)]
    completed_experiment_procs = run_web_video_experiment(exp_params)
    util.cleanup_experiments(completed_experiment_procs)
        
def run_web_video_experiment(exp_params):
    completed_experiment_procs = []
    exp = ''
    for params in exp_params:
        try:
            website, url = params[0]
            num_flows = params[1]
            duration = params[2]
            btlbw, rtt, queue_size = params[3]

            (url_ip, website_rtt, video_server_host, video_url_ip) = util.get_web_video_details(url)

            if website_rtt >= rtt:
                logging.warning('Skipping experiment with website RTT {} >= {}'.format(website_rtt, rtt))
                continue
                # return (-1, '')

            (host_client) = util.get_host_client(url_ip)
            server_nat_ip = HOST_CLIENT.ip_wan

            experiment_name = '{}bw-{}rtt-{}q-{}-{}s'.format(btlbw, rtt, queue_size, website, duration)
            delay =rtt-website_rtt
            flow_structure = util.get_flow_structure(website, duration, delay)
            flows = util.create_flows(flow_structure, const.FLOW_KIND_WEB_VIDEO, 1, host_client, const.CLIENT_PORT, const.SERVER_PORT)
            exp = util.create_experiment(btlbw, queue_size, flows, experiment_name, host_client, HOST_SERVER, server_nat_ip)
            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)

            web_data = util.create_web_info(website, url, website_rtt, rtt, delay, url_ip, duration, 1, video_url_ip, video_server_host)
            flowImpl.start_bess_for_web_video(exp, duration, web_data)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            util.handle_exception(e, exp)
    return completed_experiment_procs

def prepare_website_experiment(args, test=None):
    if (args.websites) is None:
        raise Exception('Web Video needs a value for --website argument')

    websites = args.websites
    logging.info('Found {} websites'.format(len(websites)))
    
    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()

    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    #Here each website will be in a separate experiment. [website1, .....] [website2, ....]
    exp_params = list(itertools.product(websites, [args.nums_competing], [args.duration], args.ntwrk_conditions, repetitions))
    print('Found {} website experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} website experiments. They are {}'.format(len(exp_params), exp_params))
    # Found 1 web video experiments. They are [(['www.youtube.com', 'https://www.youtube.com/embed/aqz-KE-bpKQ?autoplay=1'], 1, 60, (50, 20, 256), 0)]
    completed_experiment_procs = run_website_experiment(exp_params)
    util.cleanup_experiments(completed_experiment_procs)

def run_website_experiment(exp_params):
    completed_experiment_procs = []
    exp = ''
    for params in exp_params:
        try:
            website, url = params[0]
            num_flows = params[1]
            duration = params[2]
            btlbw, rtt, queue_size = params[3]

            (url_ip, website_rtt) = util.get_website_details(url)
            print(website, url, url_ip, website_rtt)
            if website_rtt >= rtt:
                logging.warning('Skipping experiment with website RTT {} >= {}'.format(website_rtt, rtt))
                continue
                # return (-1, '')

            (host_client) = util.get_host_client(url_ip)
            server_nat_ip = HOST_CLIENT.ip_wan

            experiment_name = '{}bw-{}rtt-{}q-{}-{}s'.format(btlbw, rtt, queue_size, website, duration)
            delay = rtt-website_rtt
            flow_structure = util.get_flow_structure(website, duration, delay)
            web_data = util.create_web_info(website, url, website_rtt, rtt, delay, url_ip, duration, num_flows)
            flows = util.create_flows(flow_structure, const.FLOW_KIND_WEBSITE, num_flows, host_client, const.CLIENT_PORT, const.SERVER_PORT, web_data)
            exp = util.create_experiment(btlbw, queue_size, flows, experiment_name, host_client, HOST_SERVER, server_nat_ip)
            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)

            flowImpl.start_bess_for_website(exp, duration, web_data)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            util.handle_exception(e, exp)
    return completed_experiment_procs

def prepare_combinatory_experiment(args, test=None):
    print('prepare_combination_experiment', test)
    if args.ntwrk_conditions is None:
        args.ntwrk_conditions = util.get_default_networking_conditions()
    
    repetitions = util.get_repititions(args.repeat)
    print('Arguments>>', args)

    test_combination = test.split('-')

    includeWebsite = False
    includeCCA = False

    for test_part in test_combination:
        if test_part in util.third_party_service:
            includeWebsite = True

        if test_part in util.local_services:
            includeCCA = True

        if includeWebsite and includeCCA:
            break

    exp_params = []
    
    if includeWebsite and includeCCA:
        #args with [] will be in a single experiment while args without [] will yield separate experiments
        exp_params = list(itertools.product([args.nums_competing], [args.duration], 
                        args.ntwrk_conditions, repetitions, [args.websites], [args.competing_ccalgs])) #exp_params represent separate experiments

    elif includeWebsite:
        exp_params = list(itertools.product([args.nums_competing], [args.duration], 
                        args.ntwrk_conditions, repetitions, [args.websites])) #exp_params represent separate experiments

    elif includeCCA:
        exp_params = list(itertools.product([args.nums_competing], [args.duration], 
                        args.ntwrk_conditions, repetitions, [args.competing_ccalgs]))
    print('Found {} combinatory experiments. They are {}'.format(len(exp_params), exp_params))
    logging.info('Found {} combinatory experiments. They are {}'.format(len(exp_params), exp_params))
    completed_experiment_procs = run_combination_experiment(exp_params, includeWebsite, includeCCA, test_combination, test)
    util.cleanup_experiments(completed_experiment_procs)

def run_combination_experiment(exp_params, includeWebsite, includeCCA, test_combination, test):
    completed_experiment_procs = []
    exp = None 
    num_completed_experiments = 0
    for params in exp_params:
        try:
            num_flows = params[0]
            duration = params[1]
            btlbw, rtt, queue_size = params[2]
            # primaryWebsite = None
            # secondaryLink = None
            ccalgs = None 
            websites = None 

            if includeWebsite and includeCCA:
                websites = params[4]
                ccalgs = params[5]
                # primaryWebsite, secondaryLink = websites[0][0], websites[0][1]
            elif includeCCA:
                ccalgs = params[4]
            elif includeWebsite:
                websites = params[4]
                # primaryWebsite, secondaryLink = websites[0][0], websites[0][1]

            number_of_competing_flows = ''
            for num_flow in num_flows:
                number_of_competing_flows += str(num_flow)
                number_of_competing_flows += '-'

            competing_ccas = ''
            if ccalgs is not None:
                for cca in ccalgs:
                    competing_ccas += cca
                    competing_ccas += '-'

            # util.log_current_experiment(num_completed_experiments, exp_params, params)
            if (util.is_rtt_too_small(rtt)):
                continue

            experiment_name = '{}bw-{}rtt-{}q-{}test-{}{}-{}s'.format(btlbw, rtt, queue_size, test, number_of_competing_flows, competing_ccas, duration)
            all_flows = []
            host_client = HOST_CLIENT
            server_port = const.SERVER_PORT
            client_port = const.CLIENT_PORT
            print("starting client and server port >", client_port, server_port)
            env_ccas_with_ports = '' 
            for index, part in enumerate(test_combination):
                switcher = {
                    'iperf': comFlowImpl.create_iperf_flows,
                    'webVideo': comFlowImpl.create_web_video_flows,
                    'website': comFlowImpl.create_website_flows,
                    'localVideo': comFlowImpl.create_local_video_flows,
                    'localWebsite': comFlowImpl.create_local_website_flows
                }
                func = switcher.get(part, lambda: "Invalid test!")
                #TODO: Unnecassary paras need to be passed. Fix this.
                ccal = None 
                if ccalgs is not None:
                    ccal = ccalgs[index]

                primaryLink, secondaryLink = None, None 
                if websites is not None:
                    primaryLink,  secondaryLink = websites[index][0], websites[index][1] 

                print("Primary and secondary links >> ", primaryLink, "------", secondaryLink)

                # flows, host_client = func(primaryWebsite, secondaryLink, rtt, duration, num_flows[index], ccal, client_port, server_port) # Execute the function
                flows, host_client = func(primaryLink, secondaryLink, rtt, duration, num_flows[index], ccal, client_port, server_port) # Execute the function
                all_flows.extend(flows) 

                #This is needed, otherwise combinaton flows will have same port
                skip_server_port_increment = False
                if part == 'localVideo' or part == 'localWebsite' or part == 'iperf':
                    for i in range(num_flows[index]):
                        # print(i)
                        # if i > 0 and part == 'localVideo':
                        #     skip_server_port_increment = True 
                        
                        # if skip_server_port_increment == False:
                        #     server_port += 1
                        # client_port += 1

                        server_port += 1
                        client_port += 1
                        if part != 'iperf':
                            env_ccas_with_ports += str(server_port) + ':' + ccal + '-'

                print("next client and server port >", client_port, server_port)
                    
            # if test_combination in util.third_party_service:
            if any(i in test_combination for i in util.third_party_service):
                host_client = util.get_host_client(util.get_website_ip(secondaryLink))
            exp = util.create_experiment(btlbw, queue_size, all_flows, experiment_name, host_client, HOST_SERVER, HOST_CLIENT.ip_wan)
            
            if any(i in test_combination for i in util.apache_service_needed):
                print('env_ccas_with_ports>', env_ccas_with_ports)
                util.set_env_with_congestion(HOST_CLIENT, env_ccas_with_ports) #This should be done only for local website and video

            logging.info('Running experiment: {}'.format(exp.name))
            util.clean_tcpdump(exp)
            comFlowImpl.start_bess_for_combinatory_flows(exp, includeWebsite, duration)
            completed_experiment_procs = util.run_post_experiment_process(experiment_name, exp, completed_experiment_procs)
        except Exception as e:
            print(e)
            util.handle_exception(e, exp)
    return completed_experiment_procs
