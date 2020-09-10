from command import RemoteCommand, run_local_command, get_ssh_client, exec_command

from collections import namedtuple, OrderedDict
from datetime import datetime
from contextlib import contextmanager, ExitStack
from json import JSONEncoder
import argparse
import json
import os
import pwd
import subprocess
import shlex
import time
import tarfile
import logging
import glob
import random
import yaml
import paramiko

from logging.config import fileConfig

Host = namedtuple('Host', ['ifname_remote', 'ifname_local', 'ip_wan', 'ip_lan', 'pci', 'key_filename', 'username'])

def run_webrtc_flow(stack, config):
    # run bess and monitor
    start_bess()
    # give bess some time to start
    time.sleep(5)
    # give bess some time to start
    time.sleep(3)
    show_bess_pipeline()
    start_webrtc_experiment(config)


def start_bess():
    cmd = '/opt/bess/bessctl/bessctl daemon start'
    try:
        run_local_command(cmd, timeout=120)
    except Exception as e:
        pass
    cmd = ("/opt/bess/bessctl/bessctl run {} "
           "\"CCTESTBED_EXPERIMENT_DESCRIPTION='{}'\"").format(
               "active-middlebox-pmd", "/tmp/webrtc-tmp.json")
    run_local_command(cmd)
    
def show_bess_pipeline():
        cmd = '/opt/bess/bessctl/bessctl show pipeline'
        logging.info('\n'+run_local_command(cmd))
        cmd = '/opt/bess/bessctl/bessctl command module queue0 get_status EmptyArg'
        logging.info('\n'+run_local_command(cmd))
        cmd = '/opt/bess/bessctl/bessctl command module queue_delay0 get_status EmptyArg'
        logging.info('\n'+run_local_command(cmd))

def start_webrtc_experiment(config):

    client = Host(**config['client'])
    server = Host(**config['server'])

    print(client)
    print(server)

    #################################################

    # # start apache server which is running on the cctestbed-client
    # with get_ssh_client(
    #         flow.client.ip_wan,
    #         flow.client.username,
    #         key_filename=flow.client.key_filename) as ssh_client:
    #     start_apache_cmd = "sudo service apache2 start"
    #     exec_command(
    #         ssh_client, flow.client.ip_wan, start_apache_cmd)
    # # change default cclag for client
    # with get_ssh_client(
    #         flow.client.ip_wan,
    #         flow.client.username,
    #         key_filename=flow.client.key_filename) as ssh_client:
    #     change_ccalg = 'echo {} | sudo tee /proc/sys/net/ipv4/tcp_congestion_control'.format(flow.ccalg)
    #     exec_command(ssh_client, flow.client.ip_wan, change_ccalg)

    # #TODO: should change ccalg back to default after running flow

    # # delay flow start for start time plus 3 seconds
    # web_download_cmd = 'timeout {}s google-chrome --disable-gpu --headless --remote-debugging-port=9222 --autoplay-policy=no-user-gesture-required "http://{}:1234/"'.format(flow.end_time, self.client.ip_lan)
    # start_download = RemoteCommand(
    #     web_download_cmd,
    #     self.server.ip_wan,
    #     username=self.server.username,
    #     key_filename=self.server.key_filename,
    #     pgrep_string='google-chrome'.format(
    #         self.client.ip_lan))
    # stack.enter_context(start_download())
    # return start_download

def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(description='Run congestion control experiments')
    parser.add_argument('config_file', help='Configuration file describing experiment')
    args = parser.parse_args()
    return args

def load_config_file(config_filename):
    """Parse YAML config file"""
    with open(config_filename) as f:
        config = yaml.safe_load(f)
    return config

def main(args):
    config = load_config_file(args.config_file)
    try:
        with ExitStack() as stack:
            run_webrtc_flow(stack, config)
    except Exception as e:
        raise e

if __name__ == '__main__':
    # configure logging
    fileConfig('logging_config.ini')
    args = parse_args()
    main(args)

