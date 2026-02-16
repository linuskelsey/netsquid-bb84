from netsquid.protocols import NodeProtocol
from netsquid.components import QuantumProgram
from netsquid.components.instructions import INSTR_MEASURE,INSTR_MEASURE_X
import netsquid as ns

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import Random_basis_gen,Compare_basis

import logging
logging.basicConfig(level=logging.INFO)
mylogger = logging.getLogger(__name__)