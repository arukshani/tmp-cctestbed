import cctestbedv2 as cctestbed
import time
import logging
import util 
import constant as const 
from contextlib import ExitStack, contextmanager
import json 
import os 
import subprocess
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~START THE BESS MONITOR~~~~~~~~~~~~~~~~~~~~~

def start_bess_for_local_website(exp, duration):
    with ExitStack() as stack:
        exp._run_tcpdump('server', stack)
        exp._run_tcpdump('server', stack, capture_http=True)
        cctestbed.stop_bess()
        stack.enter_context(exp._run_bess(
            ping_source='client',
            skip_ping=False,
            bess_config_name='active-middlebox-pmd-fairness'))
        # give bess time to start
        time.sleep(5)
        exp._show_bess_pipeline()
        stack.enter_context(exp._run_bess_monitor())
        util.start_apache_server(exp.flows[0])
        ssh_client = util.get_ssh_client_for_server_node(exp)
        with ssh_client as ssh_client:
            ssh_client, stdout = start_single_local_website_flow(ssh_client, exp.flows[0], exp, stack)
        logging.info('Waiting for flow to finish')
        # wait for flow to finish
        # local_website_flow._wait()
        # add add a time buffer before finishing up experiment
        logging.info('Video flow finished')
        # add add a time buffer before finishing up experiment
        time.sleep(duration+5)
        exp._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))
        util.stop_local_server_and_cleanup(exp)

def start_bess_for_local_video(exp, duration):
    with ExitStack() as stack:
        exp._run_tcpdump('server', stack)
        exp._run_tcpdump('server', stack, capture_http=True)
        cctestbed.stop_bess()
        stack.enter_context(exp._run_bess(
            ping_source='client',
            skip_ping=False,
            bess_config_name='active-middlebox-pmd-fairness'))
        # give bess time to start
        time.sleep(5)
        exp._show_bess_pipeline()
        stack.enter_context(exp._run_bess_monitor())
        util.start_apache_server(exp.flows[0])
        video_flow = start_single_local_video_flow(exp.flows[0], exp, stack)
        logging.info('Waiting for flow to finish')
        # wait for flow to finish
        video_flow._wait()
        # add add a time buffer before finishing up experiment
        logging.info('Video flow finished')
        # add add a time buffer before finishing up experiment
        time.sleep(5)
        exp._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))
        util.stop_local_server_and_cleanup(exp)

def start_bess_for_iperf(exp, duration):
    with ExitStack() as stack:
        exp._run_tcpdump('server', stack)
        cctestbed.stop_bess()
        stack.enter_context(exp._run_bess(ping_source='client',
                                        skip_ping=False,
                                        bess_config_name='active-middlebox-pmd-fairness'))
        # give bess time to start
        time.sleep(5)
        exp._show_bess_pipeline()
        stack.enter_context(exp._run_bess_monitor())
        start_iperf_flows(exp, stack)
        time.sleep(duration+5)
        exp._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))

def start_bess_for_web_video(exp, duration, web_data):
    with ExitStack() as stack:
        stack.enter_context(util.add_dnat_rule_video(exp, web_data['url_ip'], web_data['video_url_ip']))
        stack.enter_context(util.add_route_video(exp, web_data['url_ip'], web_data['video_url_ip']))
        stack.enter_context(util.add_dns_rule(exp, web_data['website'], web_data['url_ip']))
        stack.enter_context(util.add_dns_rule(exp, web_data['video_server_host'], web_data['video_url_ip']))
        exp._run_tcpdump('server', stack)
        # run the flow
        # turns out there is a bug when using subprocess and Popen in Python 3.5
        # so skip ping needs to be true
        # https://bugs.python.org/issue27122
        cctestbed.stop_bess()
        stack.enter_context(exp._run_bess(ping_source='server', skip_ping=False, bess_config_name='active-middlebox-pmd-fairness'))
        # give bess some time to start
        time.sleep(5)
        exp._show_bess_pipeline()
        stack.enter_context(exp._run_bess_monitor())
        stack.enter_context(exp._run_rtt_monitor())
        (stdout, flow_start_time) = start_single_web_video_flow(exp, stack, web_data['url'], duration)

        # exit_status = stdout.channel.recv_exit_status()
        time.sleep(duration+5)
        flow_end_time = time.time()
        logging.info('Flow ran for {} seconds'.format(flow_end_time - flow_start_time))

        exp._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))
        exp._copy_ssl_key_log_file()
        logging.info('Dumping website data to log: {}'.format(exp.logs['website_log']))
        with open(exp.logs['website_log'], 'w') as f:
            website_info = {}
            website_info['website'] = web_data['website']
            website_info['url'] = web_data['url']
            website_info['website_rtt'] = web_data['website_rtt']
            website_info['experiment_rtt'] = web_data['experiment_rtt']
            website_info['delay'] = web_data['delay']
            website_info['url_ip'] = web_data['url_ip']
            website_info['flow_runtime'] = flow_end_time - flow_start_time 
            json.dump(website_info, f)

        # if exit_status != 0:
        #     if exit_status == 124: # timeout exit status
        #         print('Timeout. Flow longer than {}s.'.format(duration+5))
        #         logging.warning('Timeout. Flow longer than {}s.'.format(duration+5))
        #     else:
        #         logging.error(stdout.read())
        #         raise RuntimeError('Error running flow.')

def start_bess_for_website(exp, duration, web_data):
    with ExitStack() as stack:
        print(web_data)
        stack.enter_context(util.add_dnat_rule(exp, web_data['url_ip']))
        stack.enter_context(util.add_route(exp, web_data['url_ip']))
        stack.enter_context(util.add_dns_rule(exp, web_data['website'], web_data['url_ip']))
        exp._run_tcpdump('server', stack)
        # run the flow
        # turns out there is a bug when using subprocess and Popen in Python 3.5
        # so skip ping needs to be true
        # https://bugs.python.org/issue27122
        cctestbed.stop_bess()
        stack.enter_context(exp._run_bess(ping_source='server', skip_ping=False, bess_config_name='active-middlebox-pmd-fairness'))
        # give bess some time to start
        time.sleep(5)
        exp._show_bess_pipeline()
        stack.enter_context(exp._run_bess_monitor())
        stack.enter_context(exp._run_rtt_monitor())
        ssh_client = cctestbed.get_ssh_client(exp.server.ip_wan, exp.server.username, key_filename=exp.server.key_filename)
        
        with ssh_client as ssh_client:
            start_website_flows(ssh_client, exp, stack)
            # exit_status = stdout.channel.recv_exit_status()
            time.sleep(duration+5)
        # flow_end_time = time.time()
        logging.info('Flow ran for {} seconds'.format(duration+5))

        exp._show_bess_pipeline()
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        print(cctestbed.run_local_command(cmd))

        logging.info('Dumping website data to log: {}'.format(exp.logs['website_log']))
        with open(exp.logs['website_log'], 'w') as f:
            website_info = {}
            website_info['website'] = web_data['website']
            website_info['url'] = web_data['url']
            website_info['website_rtt'] = web_data['website_rtt']
            website_info['experiment_rtt'] = web_data['experiment_rtt']
            website_info['delay'] = web_data['delay']
            website_info['url_ip'] = web_data['url_ip']
            website_info['flow_runtime'] = duration+5
            json.dump(website_info, f)

        # if exit_status != 0:
        #     if exit_status == 124: # timeout exit status
        #         print('Timeout. Flow longer than {}s.'.format(duration+5))
        #         logging.warning('Timeout. Flow longer than {}s.'.format(duration+5))
        #     else:
        #         logging.error(stdout.read())
        #         raise RuntimeError('Error running flow.')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ACTUAL IMPLENTATION OF DIFFERENT TYPES OF FLOWS, STARTS HERE~~~~~~~~~~~~~~~~~~~~~~~~~

def start_web_video_flows(exp, stack):
    all_stdout = []
    contains_webvideo_flows = False 
    for idx, flow in enumerate(exp.flows):
        if flow.kind != const.FLOW_KIND_WEB_VIDEO:
            continue
        (return_stdout, flow_start_time) = start_single_web_video_flow(exp, stack, flow.webInfo['url'], flow.webInfo['original_duration'])
        all_stdout.append(return_stdout)
        contains_webvideo_flows = True 
    return contains_webvideo_flows

def start_single_web_video_flow(exp, stack, url, duration):
    with cctestbed.get_ssh_client(exp.server.ip_wan, exp.server.username, key_filename=exp.server.key_filename) as ssh_client:
        # start_flow_cmd = 'timeout {}s /tmp/chrome-linux/chrome --headless --ssl-key-log-file=/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log --remote-debugging-port=9222 --autoplay-policy=no-user-gesture-required --window-size={},{} --start-maximized {}'.format(duration+5, exp.name, exp.exp_time, 1920, 1080, url)
        start_flow_cmd = 'timeout {}s google-chrome  --headless --flag-switches-begin --disable-quic --flag-switches-end --ssl-key-log-file=/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log --remote-debugging-port=9222 --autoplay-policy=no-user-gesture-required --window-size={},{} --start-maximized {}'.format(duration+5, exp.name, exp.exp_time, 3840, 2160, url)
        
        print("start_flow_cmd>>",start_flow_cmd)
        # won't return until flow is done
        flow_start_time = time.time()
        exp.logs['ssl_key_log'] = '/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
        ssl_key_log_cmd = 'export SSLKEYLOGFILE=/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
        _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, ssl_key_log_cmd) #This is to decrypt traffic
        _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, 'source /etc/environment')
        _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, start_flow_cmd)
        # exit_status = stdout.channel.recv_exit_status()
        return (stdout, flow_start_time)

def start_website_flows(ssh_client, exp, stack):
    all_stdout = []
    contains_website_flows = False
    for idx, flow in enumerate(exp.flows):
        if flow.kind != const.FLOW_KIND_WEBSITE:
            continue
        ssh_client, return_stdout, flow_start_time = start_single_website_flow(ssh_client, exp, stack, flow.webInfo['url'], flow.webInfo['original_duration'])
        flow_start_time = time.time()
        print("return time after starting>", flow_start_time)
        all_stdout.append(return_stdout)
        contains_website_flows = True 
    return contains_website_flows

def start_single_website_flow(ssh_client, exp, stack, url, duration):
    # filename = os.path.basename(url) 
    filename  = "temp_donw" #tmp file name
    print(filename)
    if filename.strip() == '':
        logging.warning('Could not get filename from URL')
    # start_flow_cmd = 'timeout {}s wget --no-check-certificate --no-cache --delete-after --connect-timeout=10 --tries=3 --bind-address {}  -P /tmp/ {} || rm -f /tmp/{}.tmp*'.format(duration+5, exp.server.ip_lan, url, filename)
    start_flow_cmd = 'timeout {}s wget --no-check-certificate --no-cache --connect-timeout=10 --tries=3 --bind-address {}  -P /tmp/ {} || rm -f /tmp/{}.tmp*'.format(duration+5, exp.server.ip_lan, url, filename)
    # start_flow_cmd = 'curl --interface {} -L -H "Cache-Control: no-cache" {} -o {} || rm -f /tmp/{}.tmp*'.format(exp.server.ip_lan, url, filename, filename)
    # start_flow_cmd = 'wget --no-check-certificate --no-cache --delete-after --connect-timeout=10 --tries=3 --bind-address {}  -P /tmp/ {} || rm -f /tmp/{}.tmp*'.format(exp.server.ip_lan, url, filename)
    print("start_flow_cmd>>",start_flow_cmd)
    # won't return until flow is done
    flow_start_time = time.time()
    exp.logs['ssl_key_log'] = '/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
    ssl_key_log_cmd = 'export SSLKEYLOGFILE=/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
    _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, ssl_key_log_cmd) #This is to decrypt traffic
    _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, 'source /etc/environment')
    # process = subprocess.Popen([start_flow_cmd])
    # p1 = subprocess.call(start_flow_cmd)
    # stdout = None 
    print("Just before starting>", flow_start_time)
    _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, start_flow_cmd)
    print("Just after starting>", time.time())
    # exit_status = stdout.channel.recv_exit_status()
    # exit_status = stdout.channel.recv_exit_status()
    # print(stdout)
    return ssh_client, stdout, flow_start_time

    # stdout = None
    # flow_start_time = None 
    # # with cctestbed.get_ssh_client(exp.server.ip_wan, exp.server.username, key_filename=exp.server.key_filename) as ssh_client:
    # with ssh_client as ssh_client:
    #     filename = os.path.basename(url)
    #     print(filename)
    #     if filename.strip() == '':
    #         logging.warning('Could not get filename from URL')
    #     start_flow_cmd = 'timeout {}s wget --no-check-certificate --no-cache --delete-after --connect-timeout=10 --tries=3 --bind-address {}  -P /tmp/ {} || rm -f /tmp/{}.tmp*'.format(duration+5, exp.server.ip_lan, url, filename)
    #     # start_flow_cmd = 'wget --no-check-certificate --no-cache --delete-after --connect-timeout=10 --tries=3 --bind-address {}  -P /tmp/ {} || rm -f /tmp/{}.tmp*'.format(exp.server.ip_lan, url, filename)
    #     print("start_flow_cmd>>",start_flow_cmd)
    #     # won't return until flow is done
    #     flow_start_time = time.time()
    #     # exp.logs['ssl_key_log'] = '/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
    #     # ssl_key_log_cmd = 'export SSLKEYLOGFILE=/users/rukshani/SSLkeylogs/sslkeylog-{}-{}.log'.format(exp.name, exp.exp_time)
    #     # _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, ssl_key_log_cmd) #This is to decrypt traffic
    #     # _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, 'source /etc/environment')
    #     # process = subprocess.Popen([start_flow_cmd])
    #     # p1 = subprocess.call(start_flow_cmd)
    #     # stdout = None 
    #     _, stdout, _ = cctestbed.exec_command(ssh_client, exp.server.ip_wan, start_flow_cmd)
    #     # exit_status = stdout.channel.recv_exit_status()
    #     # exit_status = stdout.channel.recv_exit_status()
    #     print(stdout)
    # return ssh_client, stdout, flow_start_time

def start_local_video_flows(exp, stack):
    contains_local_video_flows = False
    for idx, flow in enumerate(exp.flows):
        if flow.kind != const.FLOW_KIND_VIDEO:
            continue
        # if idx == 0:
        #     start_apache_server(flow)
        start_single_local_video_flow(flow, exp, stack)
        contains_local_video_flows = True 
    return contains_local_video_flows

#TODO:Refactor this method
def start_single_local_video_flow(flow, experiment, stack):

    # change default cclag for client
    # with cctestbed.get_ssh_client(
    #         flow.client.ip_wan,
    #         flow.client.username,
    #         key_filename=flow.client.key_filename) as ssh_client:
    #     change_ccalg = 'echo {} | sudo tee /proc/sys/net/ipv4/tcp_congestion_control'.format(flow.ccalg)
    #     cctestbed.exec_command(ssh_client, flow.client.ip_wan, change_ccalg)

    #TODO: should change ccalg back to default after running flow

    # delay flow start for start time plus 3 seconds
    web_download_cmd = 'source /etc/environment ; timeout {}s google-chrome --disable-gpu --headless --remote-debugging-port=9222 --autoplay-policy=no-user-gesture-required --window-size={},{} --start-maximized "http://{}:{}/"'.format(flow.end_time, 3840, 2160, experiment.client.ip_lan, flow.server_port)
    print("local_video_download_cmd>", web_download_cmd)
    start_download = cctestbed.RemoteCommand(
        web_download_cmd,
        experiment.server.ip_wan,
        username=experiment.server.username,
        key_filename=experiment.server.key_filename,
        pgrep_string='google-chrome'.format(
            experiment.client.ip_lan))
    stack.enter_context(start_download())
    return start_download

def start_local_website_flows(ssh_client, exp, stack):
    contains_local_website_flows = False
    ssh_array = []
    for idx, flow in enumerate(exp.flows):
        if flow.kind != const.FLOW_KIND_LOCAL_WEBSITE:
            continue
        # if idx == 0:
        #     start_apache_server(flow)
        contains_local_website_flows = True 
        ret_ssh_client, stdout = start_single_local_website_flow(ssh_client, flow, exp, stack)
        ssh_array.append(ret_ssh_client)
    return contains_local_website_flows

def start_single_local_website_flow(ssh_client, flow, experiment, stack):
    web_download_cmd = 'wget --quiet --background --span-hosts --no-cache --delete-after --bind-address {} -P /tmp/ "http://{}:{}/www.nytimes.com"'.format(experiment.server.ip_lan, experiment.client.ip_lan, flow.server_port)
    # web_download_cmd = 'wget --quiet --background --span-hosts --no-cache --bind-address {} -P /tmp/ "http://{}:{}/www.nytimes.com"'.format(experiment.server.ip_lan, experiment.client.ip_lan, flow.server_port)
    
    print("web_download_cmd>", web_download_cmd)
    # start_download = cctestbed.RemoteCommand(
    #         web_download_cmd,
    #         experiment.server.ip_wan,
    #         username=experiment.server.username,
    #         key_filename=experiment.server.key_filename,
    #         pgrep_string='http://{}:{}/www.nytimes.com'.format(
    #             experiment.client.ip_lan, flow.server_port))
    # stack.enter_context(start_download())
    # return start_download
    _, stdout, _ = cctestbed.exec_command(ssh_client, experiment.server.ip_wan, web_download_cmd)
    return ssh_client, stdout

#TODO:Refactor this method too
def start_iperf_flows(experiment, stack):
    for flow in experiment.flows:
        if flow.kind != 'iperf':
            continue
        start_server_cmd = ('iperf3 --server '
                            '--bind {} '
                            '--port {} '
                            '--one-off '
                            '--affinity {} '
                            '--logfile {} ').format(
                                experiment.server.ip_lan,
                                flow.server_port,
                                1,
                                flow.server_log)
        start_server = cctestbed.RemoteCommand(start_server_cmd,
                                            experiment.server.ip_wan,
                                            username=experiment.server.username,
                                            logs=[flow.server_log],
                                            key_filename=experiment.server.key_filename)
        stack.enter_context(start_server())

    for idx, flow in enumerate(experiment.flows):
        if flow.kind != 'iperf':
            continue
        # make sure first flow runs for the whole time regardless of start time
        # note this assumes self.flows is sorted by start time
        flow_duration = flow.end_time - flow.start_time
        if idx == 0:
            flow_duration = flow.end_time
        start_client_cmd = ('iperf3 --client {} '
                            '--port {} '
                            '--verbose '
                            '--bind {} '
                            '--cport {} '
                            '--linux-congestion {} '
                            '--interval 0.5 '
                            '--time {} '
                            #'--length 1024K '#1024K '
                            '--affinity {} '
                            #'--set-mss 500 ' # default is 1448
                            #'--window 100K '
                            '--zerocopy '
                            '--json '
                            '--logfile {} ').format(experiment.server.ip_lan,
                                                    flow.server_port,
                                                    flow.client.ip_lan,
                                                    flow.client_port,
                                                    flow.ccalg,
                                                    flow_duration,
                                                    idx % 32,
                                                    flow.client_log)
        start_client = cctestbed.RemoteCommand(
            start_client_cmd,
            flow.client.ip_wan,
            username=flow.client.username,
            logs=[flow.client_log],
            key_filename=flow.client.key_filename)
        stack.enter_context(start_client())