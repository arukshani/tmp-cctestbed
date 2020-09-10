import experiment as ex

BYTES_TO_BITS = 8
BITS_TO_MEGABITS = 1.0 / 1000000.0
MILLISECONDS_TO_SECONDS = 1.0 / 1000.0
BYTES_TO_MEGABYTES = 1.0 / 1000000.0

bitrate_itag_map = {
                'itag-249': 57000,
                'itag-250': 75000,
                'itag-140': 130000,
                'itag-251': 143000,
                'itag-256': 196000,
                'itag-258': 389000,
                # 'itag-394': 92000,
                'itag-160': 138000,
                'itag-278': 145000,
                'itag-133': 330000,
                # 'itag-395': 224000,
                'itag-242': 332000,
                # 'itag-396': 405000,
                'itag-243': 571000,
                # 'itag-397': 710000,
                'itag-134': 732000,
                'itag-244': 993000,
                'itag-135': 1408000,
                'itag-247': 2014000,
                'itag-136': 2546000,
                'itag-302': 3028000,
                'itag-248': 3027000,
                'itag-298': 4028000,
                'itag-137': 5166000,
                'itag-303': 4666000,
                'itag-299': 6702000,
                'itag-271': 8498000,
                'itag-308': 12612000,
                'itag-313': 16729000,
                'itag-315': 24952000,
                'itag-18': 644000,
                'itag-22': 1702000,
                }

def get_all_experiment_analysers():
    experiment_analyzers = ex.load_experiments(['*'], 
                                    remote=False, force_local=True, load_queue=True, remove_duplicates=False)
    return experiment_analyzers

def get_given_experiment_analyser(file_pattern):
    experiment_analyzers = ex.load_experiments(['*'+file_pattern+'*'], 
                                    remote=False, force_local=True, load_queue=True)
    experiment_analyzer = experiment_analyzers[file_pattern]
    # print("analyser flow names>> ", analyser.flow_names)
    return experiment_analyzer

def get_experiment_analysers(file_pattern):
    experiment_analyzers = ex.load_experiments(['*'+file_pattern+'*'], 
                                    remote=False, force_local=True, load_queue=True, remove_duplicates=False)
    return experiment_analyzers

def include_group_solo(desc):
    # print(desc)
    group_id = desc.split('-', 4)
    group = group_id[0] + "-" + group_id[1] + "-" + group_id[2] + "-" + group_id[3]
    return group

#only works for 2 types of combinations
def include_group_combi(desc):
    group_id = desc.split('-', 9)
    group = group_id[0] + "-" + group_id[1] + "-" + group_id[2] + "-" + group_id[3] + "-" + group_id[4] + "-" + group_id[5]+ "-" + group_id[6]+ "-" + group_id[7] + "-" + group_id[8]
    # print(group)
    return group
