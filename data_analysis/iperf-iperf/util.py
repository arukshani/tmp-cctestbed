#More is better
def calculateHarm_more(victimSolo, victimWithTestedService):
    # print(victimSolo, victimWithTestedService)
    percentage = ((victimSolo - victimWithTestedService)/victimSolo)*100
    harm = ((victimSolo - victimWithTestedService)/victimSolo)
    return harm, percentage

#Less is better
def calculateHarm_less(victimSolo, victimWithTestedService):
    print(victimSolo, victimWithTestedService)
    percentage = ((victimWithTestedService - victimSolo)/victimWithTestedService)*100
    harm = ((victimWithTestedService - victimSolo)/victimWithTestedService)
    return harm, percentage

def include_network_solo(desc):
    # print(desc)
    network_id = desc.split('-', 4)
    network = network_id[1] + "-" + network_id[2] + "-" + network_id[3]
    if network == "50bw-20rtt-256q":
        return "Homelink"
    elif network == "2bw-20rtt-16q":
        return "3G"

def include_network_combi(desc):
    # print(desc)
    network_id = desc.split('-', 4)
    network = network_id[0] + "-" + network_id[1] + "-" + network_id[2]
    if network == "50bw-20rtt-256q":
        return "Homelink"
    elif network == "2bw-20rtt-16q":
        return "3G"

def include_cca_combi(desc):
    # print(desc)
    jumble = desc.split('-', 8)
    cca = jumble[7]
    return cca

def include_cca_second(desc):
    # print(desc)
    jumble = desc.split('-', 9)
    cca = jumble[8]
    return cca

def include_cca_solo(desc):
    # print(desc)
    jumble = desc.split('-', 1)
    cca = jumble[0]
    return cca