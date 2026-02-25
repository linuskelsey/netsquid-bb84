import netsquid as ns

from netsquid.protocols import NodeProtocol
from netsquid.components import Clock
from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import rng_bin_lst, SinglePhotonSource



class EndNodeProtocol(NodeProtocol):
    """
    Protocol to run on End User node in point-to-point BB84.

    Attributes:
        

    Parameters:
        
    """