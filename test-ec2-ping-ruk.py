from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import aws_util

# def testPing():
#      with get_ssh_client('35.174.170.1', username='ubuntu', key_filename='/users/rukshani/.ssh/rukshani_cloudlab.pem') as ssh_client:
#         _, stdout, stderr = ssh_client.exec_command('ping -c 10 -I 172.31.87.253 128.105.145.35 | tail -1 | awk "{print $4}"')
#         line = stdout.readline()
#         stderr = stderr.read()
#         print(line)
#         print(stderr)


# with get_ssh_client('35.170.191.239', username='ubuntu', key_filename='/users/rukshani/.ssh/rukshani_cloudlab.pem') as ssh_client:
#     _, stdout, stderr = ssh_client.exec_command('ping -c 10 -I 172.31.87.253 128.105.145.35 | tail -1 | awk "{print $4}"')
#     line = stdout.readline()
#     stderr = stderr.read()
#     print(line)
#     print(stderr)

instance = aws_util.get_instance('us-east-1')
ec2 = aws_util.get_ec2('us-east-1')
with get_ssh_client(ip_addr='34.205.63.233', username='ubuntu',
                                        key_filename='/users/rukshani/.ssh/rukshani_cloudlab.pem') as ssh_client:
    _, stdout, stderr = ssh_client.exec_command('echo "TESTING SSH CONNECTION"')
    line = stdout.readline()
    stderr = stderr.read()
    print(line)
    print(stderr)
