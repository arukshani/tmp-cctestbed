import sys
sys.path.append('/opt/cctestbed/')

import cctestbedv2 as cctestbed
import experiment_impl as impl
import start

import logging
from logging.config import fileConfig
import os
import argparse
import util 

def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(
        description='Run ccctestbed experiment to measure interaction between flows')
    #webVideo and localVideo solo only supports 1 flow at the moment. iperf solo works with any number of flows
    parser.add_argument('--test, -t', nargs='*', help='iperf, localWebsite, localVideo, webVideo, website and any combinations', dest='tests')
    parser.add_argument(
        '--website, -w', nargs=2, action='append', metavar=('WEBSITE', 'FILE_URL'), dest='websites',
        help='Url of file to download from website. File should be sufficently big to enable classification.')
    parser.add_argument(
        '--network, -n', nargs=3, action='append', metavar=('BTLBW','RTT', 'QUEUE_SIZE'), dest='ntwrk_conditions', default=None, type=int,
        help='Network conditions for download from website.')
    parser.add_argument(
        '--num_competing','-c', type=int, dest='nums_competing', default=1) #for single experiments just include one value, for combinations a list [1, 2]
    parser.add_argument(
        '--competing_ccalg','-a', choices=['cubic','bbr', 'reno', 'none'], dest='competing_ccalgs', action='append')
    parser.add_argument(
        '--duration', '-d', type=int, default=60)
    parser.add_argument(
        '--chrome', '-s', action='store_true', help='Run website traffic with headless chrome')
    parser.add_argument(
        '--repeat', '-r', type=int, default=1)
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # configure logging
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logging_config.ini')
    fileConfig(log_file_path)
    logging.getLogger("paramiko").setLevel(logging.WARNING)
    args = parse_args()
    logging.info('Arguments: {}'.format(args))
    start.main(args)

