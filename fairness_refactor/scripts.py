import subprocess
import os 
import constant as c

#~~~~~~~~~~~~~~~~~~~~~~~~~~~Network conditions~~~~~~~~~~~~~~~~~~~~~~~~~~~
homelink = [50,20,256]
_3G = [2,20,16]

networks = [homelink, _3G]
# solo_experiment_list = []
# combi_experiment_list = []
all_experiments = []
#~~~~~~~~~~~~~~~~~~~~~~~~~~Solo experiments~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#iperf and localVideo 
# SOLO_LOCAL_EXPERIMENTS = ['iperf', 'localVideo']
SOLO_LOCAL_EXPERIMENTS = ['iperf']
for local_exp in SOLO_LOCAL_EXPERIMENTS:
    for network in networks:
        command = ("python3.6 fairness_refactor/solo.py --test {} --num_competing 1 " 
                    "--competing_ccalg reno --competing_ccalg cubic --competing_ccalg bbr --network {} {} {} "
                    "--repeat 10 --duration 240").format(local_exp, network[0], network[1], network[2])
        all_experiments.append(command)

#youtube
for network in networks:
    command = ("python3.6 fairness_refactor/solo.py --test {} --num_competing 1 --duration 240 " 
                " --network {} {} {} "
                "--repeat 10 "
                "--website {} {} "
                ).format('webVideo', network[0], network[1], network[2], c.YOUTUBE_WEB, c.YOUTUBE_URL)
    # all_experiments.append(command)
#~~~~~~~~~~~~~~~~~~~~~~~~~~Combinatory experiments~~~~~~~~~~~~~~~~~~~~~~~~

#NOTE: Position of the arguments matters for combinatory experiments

#iperf-webVideo
for network in networks:
    for cca in c.CCAS:
        command  = ("python3.6 fairness_refactor/combinatory.py --test iperf-webVideo "
                                "--num_competing 1 --num_competing 1 " #1 iperf flow & 1 webVideo flow
                                "--competing_ccalg {} --competing_ccalg none " #none for third party services
                                "--network {} {} {} "
                                "--repeat 10 "
                                "--duration 240 "
                                "--website '' '' " #leave blank for parts that don't need links
                                "--website {} {} "
                                ).format(cca, network[0], network[1], network[2], c.YOUTUBE_WEB, c.YOUTUBE_URL)
        # all_experiments.append(command)

#iperf-localVideo
for network in networks:
    for cca in c.CCA_COMBINATION:
        command  = ("python3.6 fairness_refactor/combinatory.py --test iperf-localVideo "
                                "--num_competing 1 --num_competing 1 " #1 iperf flow & 1 webVideo flow
                                "--competing_ccalg {} --competing_ccalg {} " #none for third party services
                                "--network {} {} {} "
                                "--repeat 10 "
                                "--duration 240 "
                                "--website '' '' " #leave blank for parts that don't need links
                                "--website '' '' "
                                ).format(cca[0], cca[1], network[0], network[1], network[2])
        # all_experiments.append(command)

#iperf-iperf
for network in networks:
    for cca in c.CCA_COMBINATION:
        command  = ("python3.6 fairness_refactor/combinatory.py --test iperf-iperf "
                                "--num_competing 1 --num_competing 1 " #1 iperf flow & 1 webVideo flow
                                "--competing_ccalg {} --competing_ccalg {} " #none for third party services
                                "--network {} {} {} "
                                "--repeat 10 "
                                "--duration 240 "
                                "--website '' '' " #leave blank for parts that don't need links
                                "--website '' '' "
                                ).format(cca[0], cca[1], network[0], network[1], network[2])
        all_experiments.append(command)

#####################################
outF = open("fairness_refactor/commands.txt", "a")
exp_list = all_experiments
for experiment in exp_list:
    outF.write(experiment)
    outF.write("\n")
outF.close()


# for experiment in experiment_list:
    # subprocess.call(experiment, shell=True)
    # subprocess.call("wait $!", shell=True)
    # hello = os.system(experiment)
    # process = subprocess.Popen(experiment, shell=True, stdout=subprocess.PIPE)
    # process.wait()
    # result = run(experiment)
    # print("FINISHED:")