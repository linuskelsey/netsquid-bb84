import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import Random_basis_gen

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)