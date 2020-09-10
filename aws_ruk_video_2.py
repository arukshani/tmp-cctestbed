import boto3
import botocore
import os
import stat
import yaml
import time
import logging
import paramiko
import command
import cctestbedv2 as cctestbed
import cctestbed_generate_experiments as generate_experiments
from contextlib import contextmanager, ExitStack
import getpass
import glob
import json
import multiprocessing as mp
import pandas as pd
from data_analysis.experiment import untarfile
from data_analysis.experiment import Experiment
from datetime import datetime
import ccalg_predict
import traceback
import argparse
import aws_util

from logging.config import fileConfig
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini')
fileConfig(log_file_path)

QUEUE_SIZE_TABLE = {
    35: {5:16, 10:32, 15:64},
    85: {5:64, 10:128, 15:128},
    130: {5:64, 10:128, 15:256},
    275: {5:128, 10:256, 15:512}}

def _main(git_secret, force_create_instance=False, regions=None, networks=None, force=False):
    skip_regions = ['eu-north-1', 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-2', 'us-west-1', 'us-west-2'] #['us-east-1']
    # skip_regions = []
    if regions is None:
        regions=aws_util.get_all_regions()

    if networks is None:
        ntwrk_conditions = [(1,35,16), (1,85,32), (3,35,32), (3,85,64), (5,35,32), (5,85,64)]

    else:
        ntwrk_conditions = networks
    
    logging.info('Found {} regions: {}'.format(len(regions), regions))
    # TODO: wait for all created images to be created
    created_images = []
    num_completed_regions = 0
    for region in regions:
        if region in skip_regions:
            logging.warning('Skipping region {}'.format(region))
            continue
        instance = aws_util.get_instance(region)
        ec2_region = aws_util.get_ec2(region)
        if (instance is None) or (force_create_instance):
            if aws_util.get_key_name(ec2_region, 'rukshani') is None:
                logging.warning('Creating key pair for region {}'.format(region))
                aws_util.create_key_pair(ec2_region, region)
            image = aws_util.get_region_image(region)
            if image is None:
                image_id = None
            else:
                image_id = image.id
            logging.info('Creating instance for region {} with image {}'.format(region, image.id))
            instance = aws_util._region_start_instance(ec2_region, image_id)
            try:
                instance.wait_until_running()
                instance.load()
                if image is None: #If image is there, assumption is that it has all the cctestbed and everything setup
                    logging.info('Setting up cctestbed on instance')
                    aws_util.setup_ec2(ec2_region, instance, git_secret, ec2_username='ubuntu')
            except Exception as e:
                instance.stop()
                raise e
        aws_util.wait_for_ssh(ec2_region, instance, ec2_username='ubuntu')
        #need to install kernel modules every time
        aws_util.install_kernel_modules(ec2_region, instance, ec2_username='ubuntu')
        # try:
            # num_completed_exps = 0
            # for btlbw, rtt, queue_size in ntwrk_conditions:
                # for ccalg in ['reno','cubic','bbr']:
                    # num_completed_exps += 1
                    # print('Running experiment {}/{} region={}, ccalg={}, btlbw={}, rtt={}, queue_size={}'.format(num_completed_exps, len(ntwrk_conditions) * 3, region, ccalg, btlbw, rtt, queue_size))
                    # run_ec2_experiment(ec2_region, instance, ccalg, btlbw, rtt,
                                    #    queue_size, region, loss_rate=0, force=force)
        # except Exception as e:
            # logging.error('Error running experiment for instance: {}-{}'.format(region, ccalg))
            # logging.error(e)
            # logging.error(traceback.print_exc())
            # print('Error running experiment for instance: {}-{}'.format(region, ccalg))
            # print(e)
            # print(traceback.print_exc())
        # finally:
            # logging.info('Stopping instance')
            # instance.stop()
            # wait_time = 0
            # while (instance.state['Name'] != 'stopped' and wait_time < 300):
                # time.sleep(5)
                # wait_time += 5
                # instance.load()
            # if get_region_image(region) is None:
                #create ec2 image before terminating
                # logging.info('Creating image for region {}'.format(region))
                # try:
                    # instance.create_image(Name=region)
                # except Exception as e:
                    # logging.error('Error while trying to create image: {}', e)
        # num_completed_regions += 1
        # print('Completed experiments for {}/{} regions'.format(num_completed_regions, len(regions)))

def parse_args():
    parser = argparse.ArgumentParser(description='Run controlled video experiments')
    parser.add_argument('--regions','-r', required=False, nargs='+', default=None,
                        help='AWS regions to perform experiment. Default is all 15 AWS regions')
    parser.add_argument('--network', '-n', nargs=3, action='append', metavar=('BTLBW','RTT', 'QUEUE_SIZE'),
                        dest='networks', type=int,
                        help='Network conditions to use for experiments')
    parser.add_argument('--force','-f', action='store_true', help='Force experiments tthat were already run to run again')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    git_secret = getpass.getpass('Github secret: Special characters need to be in encoded form >>')
    _main(git_secret, False, regions=args.regions, networks=args.networks, force=args.force)
