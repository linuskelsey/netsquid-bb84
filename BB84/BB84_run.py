import netsquid as ns

from netsquid.nodes import Node
from netsquid.components import QuantumChannel, ClassicalChannel

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import HybridDelayModel



def run_BB84_sims(runtimes=10,
                  fibreLen=1,
                  qDelay=0,
                  qSpeed=0.8):
    
    KeyListA    = []
    KeyListB    = []
    KeyRateList = []

    for _ in range(runtimes):

        ns.sim_reset()

        # nodes =================================================
        alice = Node("Alice", port_names=["A.Q.Out", "A.C.Out", "A.C.In"])
        bob   = Node("Bob", port_names=["B.Q.In", "B.C.Out", "B.C.In"])

        # channels ==============================================
        QChann = QuantumChannel("[A: -Q-> :B]",
                                delay=qDelay,
                                length=fibreLen,
                                models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)})
        
        alice.connect_to(bob,
                         QChann,
                         local_port_name=alice.ports["A.Q.Out"].name,
                         remote_port_name=bob.ports["B.Q.In"].name)
        

        CChann1 = ClassicalChannel("[A: -C-> :B]",
                                delay=0,
                                length=fibreLen,
                                models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)})
        
        CChann2 = ClassicalChannel("[B: -C-> :A]",
                                delay=0,
                                length=fibreLen,
                                models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)})
        
        alice.connect_to(bob,
                         CChann1,
                         local_port_name=alice.ports["A.C.Out"].name,
                         remote_port_name=bob.ports["B.C.In"].name)
        
        bob.connect_to(alice,
                       CChann2,
                       local_port_name=bob.ports["B.C.Out"].name,
                       remote_port_name=alice.ports["A.C.In"].name)
        
        # protocols =============================================