from difflib import SequenceMatcher
import netsquid as ns

from netsquid.nodes import Node
from netsquid.components import QuantumChannel, ClassicalChannel

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import HybridDelayModel

from mdiEndUser import EndNodeProtocol
from mdiRelayNode import RelayNodeProtocol



def run_mdi_sims():
    
    KeyListA    = []
    KeyListB    = []
    KeyRateList = []

    return KeyListA, KeyListB, KeyRateList