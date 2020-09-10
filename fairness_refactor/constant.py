SERVER_PORT = 5201
CLIENT_PORT = 5555
FLOW_KIND_IPERF = "iperf"
FLOW_KIND_VIDEO = "video"
FLOW_KIND_WEB_VIDEO = "chrome"
FLOW_KIND_WEBSITE = "website"
FLOW_KIND_LOCAL_WEBSITE = "apache"

YOUTUBE_WEB = "www.youtube.com"
# YOUTUBE_URL = "https://www.youtube.com/embed/aqz-KE-bpKQ?autoplay=1"
YOUTUBE_URL = "https://www.youtube.com/embed/mMFqGL7k-PU?autoplay=1"

CCAS = ['reno', 'cubic', 'bbr']

RENO_RENO = ['reno', 'reno']
CUBIC_CUBIC = ['cubic', 'cubic']
BBR_BBR = ['bbr', 'bbr']
VEGAS_VEGAS = ['vegas', 'vegas']
YEAH_YEAH = ['yeah', 'yeah']
WEST_WEST = ['westwood', 'westwood']

RENO_CUBIC = ['reno', 'cubic']
RENO_BBR = ['reno', 'bbr']
CUBIC_BBR = ['cubic', 'bbr']

BBR_CUBIC = ['bbr', 'cubic']
CUBIC_RENO = ['cubic', 'reno']
BBR_RENO = ['bbr', 'reno']

VEGAS_BBR = ['vegas', 'bbr']
BBR_VEGAS = ['bbr', 'vegas']
VEGAS_RENO = ['vegas', 'reno']
VEGAS_CUBIC = ['vegas', 'cubic']

# CCA_COMBINATION = [RENO_RENO, CUBIC_CUBIC, BBR_BBR, RENO_CUBIC, RENO_BBR, CUBIC_BBR, BBR_CUBIC, CUBIC_RENO, BBR_RENO]
# CCA_COMBINATION = [RENO_RENO, CUBIC_CUBIC, BBR_BBR, RENO_CUBIC, RENO_BBR, CUBIC_BBR, BBR_CUBIC, CUBIC_RENO, BBR_RENO, VEGAS_VEGAS, WEST_WEST, VEGAS_BBR, BBR_VEGAS, VEGAS_RENO, VEGAS_CUBIC]
CCA_COMBINATION = [CUBIC_CUBIC]
# CCA_COMBINATION = [RENO_RENO, CUBIC_CUBIC, BBR_BBR, RENO_CUBIC, RENO_BBR, CUBIC_BBR]

HOMELINK_BTLBW = 50
HOMELINK_RTT = 20
HOMELINK_QUEUE_SIZE = 256

_3G_BTLBW = 2
_3G_RTT = 20
_3G__QUEUE_SIZE = 16

