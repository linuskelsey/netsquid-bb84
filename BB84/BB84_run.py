import sys
scriptpath = "lib/"
sys.path.append(scriptpath)

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)

def run_BB84_sim():
    return