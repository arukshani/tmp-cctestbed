import boto3
import os
import botocore
import logging
import time
import sys
import command

from logging.config import fileConfig
log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging_config.ini')
fileConfig(log_file_path)

def install_kernel_modules(ec2, instance, ec2_username='ubuntu'):
    cmds = [
        'cd /opt/cctestbed/tcp_bbr_measure && sudo insmod tcp_probe_ray.ko',
        'sudo modprobe tcp_bbr',
        'sudo ethtool -K eth0 tx off sg off tso off'
    ]
    for cmd in cmds:
        exit_status, stdout = run_ec2_command(ec2, instance, cmd, ec2_username)
        print("install_kernel_modules:", exit_status)
        logging.info(stdout)


def run_ec2_command(ec2, instance, cmd, ec2_username='ubuntu'):
    key_pair_path = get_key_pair_path(ec2)
    with command.get_ssh_client(ip_addr=instance.public_ip_address,
                                username=ec2_username,
                                key_filename=key_pair_path) as ssh_client:
        _, stdout, stderr = command.exec_command(ssh_client,
                                                 instance.public_ip_address,
                                                 cmd)
        # actually should return a bad exit status
        exit_status =  stdout.channel.recv_exit_status()
        return exit_status, stdout.read()

def update_kernel(ec2, instance, ec2_username='ubuntu'):
    cmd = ('cd /opt/cctestbed '
           '&& ./setup-kernel.sh upgrade_kernel ')
    return run_ec2_command(ec2, instance, cmd, ec2_username)    
    
def install_iperf3(ec2, instance, ec2_username='ubuntu'):
    cmd = ('cd /opt/cctestbed '
           '&& ./setup-kernel.sh install_iperf3 ')
    return run_ec2_command(ec2, instance, cmd, ec2_username)

#If git_secret has special characters, those needs to be encoded.
def clone_cctestbed(ec2, instance, git_secret, ec2_username='ubuntu'):
    key_pair_path = get_key_pair_path(ec2)
    cmd = ('cd /opt '
           '&& sudo chown -R ubuntu /opt '
           '&& git clone git@github.com:rware/cctestbed.git ')
    cmd = ('cd /opt'
           '&& sudo chown -R ubuntu /opt '
           '&& git clone https://arukshani:{}@github.com/rware/cctestbed.git').format(git_secret)
    with command.get_ssh_client(ip_addr=instance.public_ip_address,
                                username=ec2_username,
                                key_filename=key_pair_path) as ssh_client:
        session = ssh_client.get_transport().open_session()
        #paramiko.agent.AgentRequestHandler(session)
        session.set_combine_stderr(True)
        stdout = session.makefile()
        try:
            logging.info('Running cmd ({}): {}'.format(
                instance.public_ip_address, cmd.replace(git_secret, '****')))
            session.exec_command(cmd)
            exit_status =  session.recv_exit_status()
            print(exit_status)
            return exit_status, stdout.read()
        except:
            stdout.close()

def wait_for_ssh(ec2, instance, ec2_username='ubuntu'):
    while True:
        try:
            print(instance.public_ip_address, "--", ec2_username, "--", get_key_pair_path(ec2))
            with command.get_ssh_client(ip_addr=instance.public_ip_address,
                                        username=ec2_username,
                                        key_filename=get_key_pair_path(ec2)) as ssh_client:
                _, stdout, stderr = command.exec_command(ssh_client,
                                                         instance.public_ip_address,
                                                         'echo "TESTING SSH CONNECTION"')
                break
        except:
            logging.info('Waiting 60s for machine to boot. Might contain an error!')
            print("Error>>", sys.exc_info()[0])
            time.sleep(60)

def setup_ec2(ec2, instance, git_secret, ec2_username='ubuntu'):
    wait_for_ssh(ec2, instance)
    logging.info('Cloning cctestbed')
    exit_status, stdout = clone_cctestbed(ec2, instance, git_secret, ec2_username)
    logging.info(stdout)
    logging.info('Updating kernel')
    exit_status, stdout = update_kernel(ec2, instance, ec2_username)
    logging.info(stdout)
    # make sure machine has time to reboot
    logging.info('Waiting 60s for machine to reboot')    
    time.sleep(60)
    wait_for_ssh(ec2, instance)
    exit_status, stdout = install_iperf3(ec2, instance, ec2_username)
    logging.info(stdout)
    cmds = [
    'cd /opt/cctestbed/tcp_bbr_measure && make',
    'echo net.core.wmem_max = 16777216 | sudo tee -a /etc/sysctl.conf',
    'echo net.core.rmem_max = 16777216 | sudo tee -a /etc/sysctl.conf',
    'echo net.core.wmem_default = 16777216 | sudo tee -a /etc/sysctl.conf', 
    'echo net.core.rmem_default = 16777216 | sudo tee -a /etc/sysctl.conf',
    'echo net.ipv4.tcp_wmem = 10240 16777216 16777216 | sudo tee -a /etc/sysctl.conf',
    'net.ipv4.tcp_rmem = 10240 16777216 16777216 | sudo tee -a /etc/sysctl.conf',
    'sudo sysctl -p'
    ]
    for cmd in cmds:
        exit_status, stdout = run_ec2_command(ec2, instance, cmd)
        logging.info(stdout)  

def _region_start_instance(ec2, image_id=None):
    """Start an EC2 instance in this region"""
    # find an availabilty zone
    all_zones = ec2.describe_availability_zones()
    available_zone = None
    region_name = None
    for zone in all_zones['AvailabilityZones']:
        if zone['State'] == 'available':
            available_zone = zone['ZoneName']
            region_name = zone['RegionName']
            break
    # force specifici availability zone us-west-1c
    # TODO: remove this hard coding and keep retrying zones
    # until succesful if there is an error
    if region_name == 'us-west-1':
        available_zone = 'us-west-1c'
    if region_name == 'ap-northeast-1':
        available_zone = 'ap-northeast-1c'
    if available_zone is None:
        raise RuntimeError('Could not find any available zones')
    # get key name
    # key_name = get_key_name(ec2)
    key_name = '{}_cloudlab'.format(os.environ['USER'])
    if image_id is None:
        image_id = list(boto3
                        .resource('ec2', region_name=region_name)
                        .images
                        .filter(Filters=[{'Name':'name',
                                          'Values': ['ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-201806*']}])
                        .all())[0].id
    assert(key_name is not None)
    # create 1 ubuntu t2.micro instance
    print("_region_start_instance>>", region_name, " image>>", image_id, " available_zone>>", available_zone, " key_name>>", key_name)
    instance = boto3.resource('ec2', region_name=region_name).create_instances(
        ImageId=image_id,
        InstanceType='t2.micro',
        Placement={
            'AvailabilityZone':available_zone},
        KeyName=key_name,
        NetworkInterfaces=[
            {'AssociatePublicIpAddress':True,
             'DeviceIndex':0}],
        MaxCount=1,
        MinCount=1)

    ssh_allow_rule = {'FromPort': 22,
                      'IpProtocol': 'tcp',
                      'IpRanges': [{'CidrIp':'0.0.0.0/0'}],
                      'Ipv6Ranges':[],
                      'PrefixListIds':[],
                      'ToPort': 22,
                      'UserIdGroupPairs': []}
    try:
        response = ec2.authorize_security_group_ingress(GroupName='default',
                                                        IpPermissions=[ssh_allow_rule])
    except botocore.exceptions.ClientError as e:
        if not (e.response['Error']['Code'] == 'InvalidPermission.Duplicate'):
            raise e

    return instance[0]

def get_region_image(region):
    aws_images = list(boto3
                      .resource('ec2', region_name=region)
                      .images
                      .filter(Filters=[{'Name':'name', 'Values':['LatestImage']}], # Here 'LatestImage' is the AMI Name
                              Owners=['self'])
                      .all())
    if len(aws_images) == 0:
        print("get_region_image:No images found for the region>>", region)
        return None
    assert(len(aws_images) == 1)
    print("Found image for region >>", aws_images[0].id, region)
    return aws_images[0] #For the time being get the image that has cctestbed setup in it

def get_key_pair_path(ec2):
    """Get key pairs for this EC2 region"""
    # assume only one key pair per region and
    # keys are always stored in ~/.ssh/<KeyName>.pem
    key_pair_name = get_key_name(ec2, 'rukshani')
    print("Key pair name: ", key_pair_name)
    if key_pair_name is None:
        return None
    else:
        key_pair_path = '/users/rukshani/.ssh/{}.pem'.format(key_pair_name)
        assert(os.path.isfile(key_pair_path))
        return key_pair_path

def create_key_pair(ec2, region_name):
    response = ec2.create_key_pair(KeyName='rukshani_cloudlab')
    key_pair_name = response['KeyName']
    key_pair_path = '/users/rukshani/.ssh/{}.pem'.format(key_pair_name)
    with open(key_pair_path, 'w') as f:
        f.write(response['KeyMaterial'])
    os.chmod(key_pair_path, stat.S_IRUSR | stat.S_IWUSR)
    return key_pair_path

def get_key_name(ec2, username):
    response = ec2.describe_key_pairs()
    key_pairs = response['KeyPairs']
    if len(key_pairs) == 0:
        return None
    else:
        # key name must start with the user
        for key_pair in key_pairs:
            if key_pair['KeyName'].startswith(username):
                print("get_key_name>>", key_pair['KeyName'])
                return key_pair['KeyName']
        return None

def get_ec2(region_name=None):
    """Get a boto3 client for EC2 with givien region"""
    return boto3.client('ec2', region_name=region_name)

def get_instance(region):
    """Return instance object from this region. Assumes there is only one"""
    running_filter = [{'Name': 'instance-state-name',
                                 'Values': ['running']}]
    # could have also done boto3.resource('ec2', region_name=region)
    session = boto3.Session(region_name=region)
    instances = list(session.resource('ec2', region).instances
                     .filter(Filters=running_filter).all())
    # instances = list(boto3
    #                  .resource('ec2',region_name=region)
    #                  .instances
    #                  .filter(Filters=running_filter).all())
    print("get_instance len(instances) >> ", len(instances))
    if len(instances) == 0:
        return None
    assert(len(instances) == 1) #CLARIFY: Reason for this assumption??
    instance = instances[0]
    return instance

def get_all_regions():
    """Get all EC2 regions"""
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    regions = [region['RegionName'] for region in response['Regions']]
    #print("All Regions : ", regions)
    return regions
