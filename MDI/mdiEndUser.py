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
    def __init__(self, node, name, photonCount, portNames=[]):
        super().__init__()
        self.node = node
        self.name = name
        self.photon_count = photonCount
        self.port_qo_name = portNames[0]
        self.relay_port_co_name = portNames[1]
        self.relay_port_ci_name = portNames[2]