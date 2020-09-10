import itertools
import logging
import cctestbedv2 as cctestbed
from config import * #HOST_CLIENT, HOST_SERVER defined in this
import util
import constant as const 
from contextlib import ExitStack, contextmanager
import flow_impl as flowImpl 
import time 
from threading import Thread
import json 

def start_bess_for_combinatory_flows(experiment, includeWebsite, duration):
    with ExitStack() as stack:

        util.prerequisite_for_combinatory_tests(experiment, stack, includeWebsite)

        ssh_client = util.get_ssh_client_for_server_node(experiment)
        with ssh_client as ssh_client:

            local_web_service_required, single_local_flow_details = util.isApacheNeeded(experiment)
            print("local_web_service_required & single_local_flow_details>", local_web_service_required, single_local_flow_details)
            if local_web_service_required:
                print("Start Apache")
                util.start_apache_server(single_local_flow_details)

            #TODO:Measure RTT of third party services again after remaining delay is set


            #iperf
            flowImpl.start_iperf_flows(experiment, stack)
            #Web video  
            contains_webvideo_flows = flowImpl.start_web_video_flows(experiment, stack)
            #Local video
            contains_localvideo_flows = flowImpl.start_local_video_flows(experiment, stack)
            #Local website
            contains_local_website_flows = flowImpl.start_local_website_flows(ssh_client, experiment, stack)
            #Website 
            contains_website_flows = flowImpl.start_website_flows(ssh_client, experiment, stack)

            time.sleep(duration+5)

        #Save website info onto a file
        if contains_webvideo_flows:
            clean_up_web_video(experiment, duration)
            
        if contains_webvideo_flows or contains_website_flows:    
            util.write_webdata_to_log(experiment, duration)

        if contains_localvideo_flows or contains_local_website_flows:
            util.stop_local_server_and_cleanup(experiment)

        experiment._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))

def clean_up_web_video(exp, duration):
    exp._copy_ssl_key_log_file()

def create_web_video_flows(primaryWebsite, secondaryLink, rtt, duration, number_of_flows, ccalg, client_port, server_port):
    url_ip, website_rtt, video_server_host, video_url_ip = util.get_web_video_details(secondaryLink)

    if website_rtt >= rtt:
        logging.warning('Skipping experiment with website RTT {} >= {}'.format(website_rtt, rtt))
        raise Exception('Website RTT{} >= {}', website_rtt, rtt)
        
    (host_client) = util.get_host_client(url_ip)
    delay = rtt-website_rtt
    flow_structure = util.get_flow_structure(primaryWebsite, duration, delay)

    web_data = util.create_web_info(primaryWebsite, secondaryLink, website_rtt, rtt, delay, url_ip, duration, number_of_flows, video_url_ip, video_server_host)

    flows = util.create_flows(flow_structure, const.FLOW_KIND_WEB_VIDEO, number_of_flows, host_client, client_port, server_port, web_data)
    return flows, host_client

def create_website_flows(primaryWebsite, secondaryLink, rtt, duration, number_of_flows, ccalg, client_port, server_port):
    url_ip, website_rtt = util.get_website_details(secondaryLink)

    if website_rtt >= rtt:
        logging.warning('Skipping experiment with website RTT {} >= {}'.format(website_rtt, rtt))
        raise Exception('Website RTT{} >= {}', website_rtt, rtt)
        
    (host_client) = util.get_host_client(url_ip)
    delay = rtt - website_rtt
    flow_structure = util.get_flow_structure(primaryWebsite, duration, delay)

    web_data = util.create_web_info(primaryWebsite, secondaryLink, website_rtt, rtt, delay,url_ip, duration, number_of_flows)

    flows = util.create_flows(flow_structure, const.FLOW_KIND_WEBSITE, number_of_flows, host_client, client_port, server_port, web_data)
    return flows, host_client

def create_iperf_flows(primaryWebsite, secondaryLink, rtt, duration, number_of_flows, ccalg, client_port, server_port):
    flow_structure = util.get_flow_structure(ccalg, duration, rtt)
    flows = util.create_flows(flow_structure, const.FLOW_KIND_IPERF, number_of_flows, HOST_CLIENT, client_port, server_port)
    return flows, HOST_CLIENT

def create_local_video_flows(primaryWebsite, secondaryLink, rtt, duration, number_of_flows, ccalg, client_port, server_port):
    flow_structure = util.get_flow_structure(ccalg, duration, rtt)
    flows = util.create_flows_local(flow_structure, const.FLOW_KIND_VIDEO, number_of_flows, HOST_CLIENT, client_port, server_port) #Creating only 1 flow for video; TODO: see whether this is because we are starting only one server
    return flows, HOST_CLIENT

def create_local_website_flows(primaryWebsite, secondaryLink, rtt, duration, number_of_flows, ccalg, client_port, server_port):
    flow_structure = util.get_flow_structure(ccalg, duration, rtt)
    flows = util.create_flows_local(flow_structure, const.FLOW_KIND_LOCAL_WEBSITE, number_of_flows, HOST_CLIENT, client_port, server_port) #Creating only 1 flow for video; TODO: see whether this is because we are starting only one server
    return flows, HOST_CLIENT