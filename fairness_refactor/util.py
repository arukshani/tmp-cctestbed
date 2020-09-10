import cctestbedv2 as cctestbed
import flow_impl as flowImpl
import constant as const
import logging
from contextlib import ExitStack, contextmanager
import time 
import traceback
from urllib.parse import urlsplit, urlunsplit
import json 
from config import * #HOST_CLIENT, HOST_SERVER defined in this
import subprocess
import os 

third_party_service = ['webVideo', 'website'] 
local_services = ['iperf', 'localVideo', 'localWebsite']
apache_service_needed = ['localVideo', 'localWebsite']

@contextmanager
def add_dns_rule(exp, website, url_ip):
    with cctestbed.get_ssh_client(exp.server.ip_wan,
                                  exp.server.username,
                                  key_filename=exp.server.key_filename) as ssh_client:
        add_dns_cmd = "echo '{}   {}' | sudo tee -a /etc/hosts".format(url_ip, website)
        cctestbed.exec_command(ssh_client, exp.server.ip_wan, add_dns_cmd)
    try:
        yield
    finally:
        with cctestbed.get_ssh_client(exp.server.ip_wan,
                                      exp.server.username,
                                      key_filename=exp.server.key_filename) as ssh_client:
            # will delete last line of /etc/hosts file
            # TODO: should probs check that it's the line we want to delete
            del_dns_cmd = "sudo sed -i '$ d' /etc/hosts"
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, del_dns_cmd)

@contextmanager
def add_dnat_rule(exp, url_ip):
    print('exp.server_nat_ip>', exp.server_nat_ip)
    with cctestbed.get_ssh_client(exp.server_nat_ip,
                                  exp.server.username,
                                  exp.server.key_filename) as ssh_client:
        dnat_rule_cmd = 'sudo iptables -t nat -A POSTROUTING --source {} -o enp1s0f0 -j SNAT --to {} && sudo iptables -t nat -A PREROUTING -i enp1s0f0 --source {} -j DNAT --to-destination {}'.format(
                HOST_SERVER.ip_lan,
                HOST_CLIENT.ip_wan,
                url_ip,
                exp.server.ip_lan)
        print("dnat_rule_cmd>>", dnat_rule_cmd)
        cctestbed.exec_command(ssh_client, exp.server_nat_ip, dnat_rule_cmd)
    try:
        yield
    finally:
        # remove DNAT rule once down with this context
        with cctestbed.get_ssh_client(exp.server_nat_ip,
                                      exp.server.username,
                                      exp.server.key_filename) as ssh_client:
            # TODO: remove hard coding of the ip addr here
            dnat_delete_cmd = 'sudo iptables -t nat --delete PREROUTING 1 && sudo iptables -t nat --delete POSTROUTING 1'
            cctestbed.exec_command(ssh_client,
                                   exp.server.ip_wan,
                                   dnat_delete_cmd)   

@contextmanager
def add_dnat_rule_video(exp, url_ip, video_url_ip):
    print('exp.server_nat_ip>', exp.server_nat_ip)
    with cctestbed.get_ssh_client(exp.server_nat_ip,
                                  exp.server.username,
                                  exp.server.key_filename) as ssh_client:
        print("NAT source {} destination {}",url_ip, exp.server.ip_lan)
        dnat_rule_cmd1 = 'sudo iptables -t nat -A PREROUTING -i enp1s0f0 --source {} -j DNAT --to-destination {}'.format(url_ip, exp.server.ip_lan)
        print("NAT IP {}",exp.server_nat_ip)
        cctestbed.exec_command(ssh_client, exp.server_nat_ip, dnat_rule_cmd1)

        #Add rule for video data
        print("NAT source {} destination {}",video_url_ip, exp.server.ip_lan)
        dnat_rule_cmd2 = 'sudo iptables -t nat -A PREROUTING -i enp1s0f0 --source {} -j DNAT --to-destination {}'.format(video_url_ip, exp.server.ip_lan)
        print("Video NAT IP {}",exp.server_nat_ip)
        cctestbed.exec_command(ssh_client, exp.server_nat_ip, dnat_rule_cmd2)

    try:
        yield
    finally:
        # remove DNAT rule once down with this context
        with cctestbed.get_ssh_client(exp.server_nat_ip,
                                      exp.server.username,
                                      exp.server.key_filename) as ssh_client:
            # TODO: remove hard coding of the ip addr here
            dnat_delete_cmd = 'sudo iptables -t nat --delete PREROUTING 1'
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, dnat_delete_cmd) 
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, dnat_delete_cmd) 

@contextmanager
def add_route(exp, url_ip, gateway_ip=None):
    with cctestbed.get_ssh_client(exp.server.ip_wan,
                                  exp.server.username,
                                  key_filename=exp.server.key_filename) as ssh_client:
        if gateway_ip is None:
            gateway_ip = exp.client.ip_lan
        print("gateway_ip>>", gateway_ip)
        add_route_cmd = 'sudo route add {} gw {}'.format(url_ip, gateway_ip)
        print("add_route_cmd>>", add_route_cmd)
        cctestbed.exec_command(ssh_client, exp.server.ip_wan, add_route_cmd)
    try:
        yield
    finally:
        with cctestbed.get_ssh_client(exp.server.ip_wan,
                                      exp.server.username,
                                      key_filename=exp.server.key_filename) as ssh_client:
            del_route_cmd1 = 'sudo route del {}'.format(url_ip)
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, del_route_cmd1)

@contextmanager
def add_route_video(exp, url_ip, video_url_ip, gateway_ip=None):
    with cctestbed.get_ssh_client(exp.server.ip_wan,
                                  exp.server.username,
                                  key_filename=exp.server.key_filename) as ssh_client:
        if gateway_ip is None:
            gateway_ip = exp.client.ip_lan
        add_route_cmd1 = 'sudo route add {} gw {}'.format(url_ip, gateway_ip)
        print("Route command :", add_route_cmd1)
        cctestbed.exec_command(ssh_client, exp.server.ip_wan, add_route_cmd1)

        #Add route for video data
        add_route_cmd2 = 'sudo route add {} gw {}'.format(video_url_ip, gateway_ip)
        print("Route command :", add_route_cmd2)
        cctestbed.exec_command(ssh_client, exp.server.ip_wan, add_route_cmd2)
    try:
        yield
    finally:
        with cctestbed.get_ssh_client(exp.server.ip_wan,
                                      exp.server.username,
                                      key_filename=exp.server.key_filename) as ssh_client:
            del_route_cmd1 = 'sudo route del {}'.format(url_ip)
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, del_route_cmd1)
            del_route_cmd2 = 'sudo route del {}'.format(video_url_ip)
            cctestbed.exec_command(ssh_client, exp.server.ip_wan, del_route_cmd2) 

def get_video_server_ip(hostname):
    video_ip_addrs = cctestbed.run_local_command(
        "nslookup {} | awk '/^Address: / {{ print $2 ; exit }}'".format(hostname), shell=True)

    # print("Video IPs: ", video_ip_addrs)

    video_ip_addr = video_ip_addrs.split('\n')[0]
    # print("ipaddress of video server {}", video_ip_addr)
    if video_ip_addr.strip() == '':
        raise ValueError('Could not find IP addr for {}'.format(video_url))
    return video_ip_addr

def get_video_server_host(url):
    videoUrls = cctestbed.run_local_command("youtube-dl --youtube-skip-dash-manifest -g {}".format(url), shell=True)
    # print(videoUrls)
    video_url = videoUrls.split('\n')[0]
    audio_url = videoUrls.split('\n')[1]
    # print("Video URL: ", video_url)
    # print("Audio URL: ", audio_url)
    url_parts = list(urlsplit(video_url.strip()))
    hostname = url_parts[1]
    # print("video hostname {}", hostname)
    return hostname

def get_nping_rtt(url_ip):
    cmd = "nping -v-1 -H -c 5 {} | grep -oP 'Avg rtt:\s+\K.*(?=ms)'".format(url_ip)
    rtt = cctestbed.run_local_command(cmd, shell=True)
    return rtt

def get_website_ip(url):
    url_parts = list(urlsplit(url.strip()))
    hostname = url_parts[1]
    ip_addrs = cctestbed.run_local_command(
        "nslookup {} | awk '/^Address: / {{ print $2 ; exit }}'".format(hostname), shell=True)
    ip_addr = ip_addrs.split('\n')[0]
    if ip_addr.strip() == '':
        raise ValueError('Could not find IP addr for {}'.format(url))
    return ip_addr

def log_current_experiment(num_completed_experiments, exp_params, params):
    num_completed_experiments += 1
    print('Running experiment {}/{} params={}'.format(
        num_completed_experiments, len(exp_params), params))

def is_rtt_too_small(rtt):
    too_small_rtt = 0
    if rtt <= too_small_rtt:
        print('Skipping experiment RTT too small')
        return True
    return False 
    
def run_post_experiment_process(experiment_name, exp, completed_experiment_procs):
    proc = exp._compress_logs_url()
    (proc, exp_name) = (proc, '{}-{}'.format(experiment_name, exp.exp_time))
    if proc == -1:
        print('Proc is -1')
        # too_small_rtt = max(too_small_rtt, rtt)
    elif proc is not None:
        print('Experiment exp_name={}'.format(exp_name))
        completed_experiment_procs.append(proc)
    # time.sleep(60)
    return completed_experiment_procs

def handle_exception(e, exp):
    logging.error('Error running experiment: {}'.format(exp.name))
    logging.error(e)
    logging.error(traceback.print_exc())
    print('Error running experiment {}'.format(exp.name))
    print(e)
    print(traceback.print_exc())
    exit(1)

def cleanup_experiments(completed_experiment_procs):
    for proc in completed_experiment_procs:
        logging.info('Waiting for subprocess to finish PID={}'.format(proc.pid))
        proc.wait()
        if proc.returncode != 0:
            logging.warning('Error cleaning up experiment PID={}'.format(proc.pid))

def get_default_networking_conditions():
    homelink = [50,20,256]
    mobile_3G = [2,20,16]
    return [homelink, mobile_3G]
    # mobile_3G = (5,35,16)
    # return [mobile_3G]

def clean_tcpdump(exp):
    logging.info('Making sure tcpdump is cleaned up ')
    with cctestbed.get_ssh_client(
            exp.server.ip_wan,
            username=exp.server.username,
            key_filename=exp.server.key_filename) as ssh_client:
        cctestbed.exec_command(
            ssh_client,
            exp.server.ip_wan,
            'sudo pkill -9 tcpdump')

def create_experiment(btlbw, queue_size, flows, experiment_name, host_client, host_server, server_nat_ip):
    exp = cctestbed.Experiment(name=experiment_name,
                               btlbw=btlbw,
                               queue_size=queue_size,
                               flows=flows,
                               server=host_server,
                               client=host_client,
                               config_filename='None',
                               server_nat_ip=server_nat_ip)
    return exp

def create_flows(flow_structure, flow_kind, num_flows, client, client_port, server_port, webInfo=None): #Initialize one type flows
    # server_port = const.SERVER_PORT
    # client_port = const.CLIENT_PORT
    flows = []
    for x in range(num_flows):
        server_port += 1
        client_port += 1
        flows.append(cctestbed.Flow(ccalg=flow_structure['ccalg'],
                                    start_time=flow_structure['start_time'],
                                    end_time=flow_structure['end_time'], rtt=flow_structure['rtt'],
                                    server_port=server_port, client_port=client_port,
                                    client_log=None, server_log=None, kind=flow_kind,
                                    client=client, webInfo=webInfo))
    return flows

#Use this functions with local video and local website experiments
def create_flows_local(flow_structure, flow_kind, num_flows, client, client_port, server_port, webInfo=None): #Initialize one type flows
    # server_port = const.SERVER_PORT
    # client_port = const.CLIENT_PORT

    flows = []
    for x in range(num_flows):
        server_port += 1 #Issue request to the same server port; That's why this is commented.
        client_port += 1

        update_apache_config(client, server_port)
        print("client and server port of each flow", flow_structure['ccalg'], client_port, server_port)
        flows.append(cctestbed.Flow(ccalg=flow_structure['ccalg'],
                                    start_time=flow_structure['start_time'],
                                    end_time=flow_structure['end_time'], rtt=flow_structure['rtt'],
                                    server_port=server_port, client_port=client_port,
                                    client_log=None, server_log=None, kind=flow_kind,
                                    client=client, webInfo=webInfo))
    return flows

def update_apache_config(host_client, server_port):
    #Add listener ports to config file
    print("update httpd.conf with listener port > ", server_port)
    # cmd = 'ssh -o StrictHostKeyChecking=no cctestbed-client "echo $"Listen {}:{}\n" | sudo tee -a /tmp/ruk/loc/conf/httpd.conf"'.format(host_client.ip_lan, server_port)
    # proc = subprocess.run(cmd, shell=True)
    with cctestbed.get_ssh_client(
        host_client.ip_wan,
        host_client.username,
        key_filename=host_client.key_filename) as ssh_client:
        cmd = 'echo Listen {}:{} | sudo tee -a /tmp/ruk/loc/conf/httpd.conf'.format(host_client.ip_lan, server_port)
        cctestbed.exec_command(
            ssh_client, host_client.ip_wan, cmd)

def set_env_with_congestion(host_client, env_ccas_with_ports):
    #Set an environment variable with ports and their respective ccas
    # os.environ["APACHE_CCA_PORTS"] = env_ccas_with_ports
    # print(os.environ["APACHE_CCA_PORTS"])
    
    cmd = 'echo APACHE_CCA_PORTS={} | sudo tee -a /etc/environment'.format(env_ccas_with_ports)
    # cmd = 'sudo sh -c echo APACHE_CCA_PORTS={} >> /etc/environment'.format(env_ccas_with_ports)
    cmd = cmd + " ; source /etc/environment ; export APACHE_CCA_PORTS"
    print("running cmd >", cmd)
    with cctestbed.get_ssh_client(
        host_client.ip_wan,
        host_client.username,
        key_filename=host_client.key_filename) as ssh_client:
        cctestbed.exec_command(
            ssh_client, host_client.ip_wan, cmd)
        # cctestbed.exec_command(ssh_client, host_client.ip_wan, 'source /etc/environment')
        # cctestbed.exec_command(ssh_client, host_client.ip_wan, 'export APACHE_CCA_PORTS')

def get_flow_structure(ccalg, duration, rtt):
    flow = {'ccalg':ccalg,
            'end_time': duration,
            'rtt': rtt,
            'start_time': 0}
    return flow

def get_repititions(repeat):
    return list(range(repeat))

def get_web_video_details(url):
    url_ip = get_website_ip(url)
    logging.info('Got primary website IP: {}'.format(url_ip))
    website_rtt = int(float(get_nping_rtt(url_ip)))
    logging.info('Got primary website RTT: {}'.format(website_rtt))

    video_server_host = get_video_server_host(url)
    video_url_ip = get_video_server_ip(video_server_host)
    logging.info('Got video server IP: {}'.format(video_url_ip))
    return url_ip, website_rtt, video_server_host, video_url_ip

def get_website_details(url):
    url_ip = get_website_ip(url)
    logging.info('Got primary website IP: {}'.format(url_ip))
    website_rtt = int(float(get_nping_rtt(url_ip)))
    logging.info('Got primary website RTT: {}'.format(website_rtt))
    return url_ip, website_rtt

def get_host_client(url_ip):
    host_client = HOST_CLIENT_TEMPLATE
    host_client['ip_wan'] = url_ip
    host_client = cctestbed.Host(**host_client)
    return host_client

def create_web_info(website, url, website_rtt, exp_rtt, delay, url_ip, original_duration, number_of_flows, video_url_ip=None, video_server_host=None):
    web_data = {}
    web_data['website'] = website
    web_data['url'] = url
    web_data['website_rtt'] = website_rtt
    web_data['experiment_rtt'] = exp_rtt
    web_data['delay'] = delay
    web_data['url_ip'] = url_ip
    web_data['video_url_ip'] = video_url_ip
    web_data['video_server_host'] = video_server_host
    web_data['original_duration'] = original_duration
    web_data['number_of_flows'] = number_of_flows
    return web_data

#Before the start of the BESS
def prerequisite_for_combinatory_tests(experiment, stack, includeWebsite):
    for flow in experiment.flows:
            if flow.kind == const.FLOW_KIND_WEB_VIDEO: #TODO:Check whether these rules already exist
                stack.enter_context(add_dnat_rule_video(experiment, flow.webInfo['url_ip'], flow.webInfo['video_url_ip']))
                stack.enter_context(add_route_video(experiment, flow.webInfo['url_ip'], flow.webInfo['video_url_ip']))
                stack.enter_context(add_dns_rule(experiment, flow.webInfo['website'], flow.webInfo['url_ip']))
                stack.enter_context(add_dns_rule(experiment, flow.webInfo['video_server_host'], flow.webInfo['video_url_ip']))
            
            if flow.kind == const.FLOW_KIND_WEBSITE: #TODO:Check whether these rules already exist
                stack.enter_context(add_dnat_rule(experiment, flow.webInfo['url_ip']))
                stack.enter_context(add_route(experiment, flow.webInfo['url_ip']))
                stack.enter_context(add_dns_rule(experiment, flow.webInfo['website'], flow.webInfo['url_ip']))

    experiment._run_tcpdump('server', stack)
    experiment._run_tcpdump('client', stack)
    cctestbed.stop_bess()
    stack.enter_context(experiment._run_bess(ping_source='server', skip_ping=False, bess_config_name='active-middlebox-pmd-fairness'))
    # give bess some time to start
    time.sleep(5)
    experiment._show_bess_pipeline()
    stack.enter_context(experiment._run_bess_monitor())
    if includeWebsite:
        stack.enter_context(experiment._run_rtt_monitor())

def get_ssh_client_for_client_node():
    print("get_ssh_client_for_client_node")

def get_ssh_client_for_server_node(exp):
    return cctestbed.get_ssh_client(exp.server.ip_wan, exp.server.username, key_filename=exp.server.key_filename)
    # print("get_ssh_client_for_server_node")

def stop_local_server_and_cleanup(exp):
    print("stop_local_server_and_cleanup")
    flow = exp.flows[0] #TODO:Pick a local website or local video service flow
    with cctestbed.get_ssh_client(
            flow.client.ip_wan,
            flow.client.username,
            key_filename=flow.client.key_filename) as ssh_client:
        stop_apache_cmd = "sudo /tmp/ruk/loc/bin/apachectl -k stop"
        unset_env_var = "unset APACHE_CCA_PORTS"
        remove_listener_ports = "cd /tmp/ruk/loc/conf && sed -i.bak '/^Listen/d' httpd.conf"
        cctestbed.exec_command(ssh_client, flow.client.ip_wan, stop_apache_cmd)
        cctestbed.exec_command(ssh_client, flow.client.ip_wan, unset_env_var)
        cctestbed.exec_command(ssh_client, flow.client.ip_wan, remove_listener_ports)

def isApacheNeeded(exp):
    return_flow = None
    start_spache = False
    for idx, flow in enumerate(exp.flows):
        if flow.kind == const.FLOW_KIND_VIDEO or flow.kind == const.FLOW_KIND_LOCAL_WEBSITE:
            return_flow = flow
            start_spache = True 
            break
    return start_spache, return_flow

def start_apache_server(flow):
    # start apache server which is running on the cctestbed-client
    with cctestbed.get_ssh_client(
            flow.client.ip_wan,
            flow.client.username,
            key_filename=flow.client.key_filename) as ssh_client:
        # start_apache_cmd = "sudo service apache2 start"
        start_apache_cmd = "source /etc/environment ; sudo /tmp/ruk/loc/bin/apachectl -k start"
        cctestbed.exec_command(
            ssh_client, flow.client.ip_wan, start_apache_cmd)

def write_webdata_to_log(exp, duration):
    logging.info('Dumping website data to log: {}'.format(exp.logs['website_log']))
    all_website_info = {'websites':[]}
    for idx, flow in enumerate(exp.flows):
        if flow.kind != const.FLOW_KIND_WEB_VIDEO:
            continue
        website_info = {}
        website_info['website'] = flow.webInfo['website']
        website_info['url'] = flow.webInfo['url']
        website_info['website_rtt'] = flow.webInfo['website_rtt']
        website_info['experiment_rtt'] = flow.webInfo['experiment_rtt']
        website_info['delay'] = flow.webInfo['delay']
        website_info['url_ip'] = flow.webInfo['url_ip']
        # website_info['flow_runtime'] = flow_end_time - flow_start_time
        website_info['flow_runtime'] = duration   
        website_info['number_of_flows'] = flow.webInfo['number_of_flows']
        all_website_info['websites'].append(website_info)
    with open(exp.logs['website_log'], 'w') as f:
        json.dump(all_website_info, f)