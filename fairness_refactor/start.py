import experiment_impl as impl
import logging 
import util 

def main(args):
    # print(args)
    for test in args.tests:
        logging.info('==================Test {} =================='.format(test))
        test_combination = test.split('-')
        test_name = test
        if len(test_combination) > 1 and ((any(i in test_combination for i in util.third_party_service) or (i in test_combination for i in util.local_services))):
            test = 'combinatory'
        switcher = {
            'iperf': impl.prepare_iperf_experiment,
            'localVideo': impl.prepare_local_video_experiment,
            'localWebsite': impl.prepare_local_website_experiment,
            'webVideo': impl.prepare_web_video_experiment,
            'website': impl.prepare_website_experiment, 
            'combinatory': impl.prepare_combinatory_experiment, # eg: 'iperf-iperf', 'iperf-webVideo', 'webVideo-webVideo'
        }
        func = switcher.get(test, lambda: "Invalid test!")
        func(args, test_name) # Execute the function
