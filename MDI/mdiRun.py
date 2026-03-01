from difflib import SequenceMatcher
import netsquid as ns

from netsquid.nodes import Node
from netsquid.components import QuantumChannel, ClassicalChannel

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
from lib.functions import HybridDelayModel

from mdiEndUser import EndNodeProtocol
from mdiRelayNode import RelayNodeProtocol



def run_mdi_sims(runtimes=10,
                 qDelay=0,
                 fibreLen=1,
                 qSpeed=0.8,
                 photonCount=1024,
                 sourceFreq=1e7):
    
    KeyListA    = []
    KeyListB    = []
    KeyRateList = []

    for _ in range(runtimes):
        ns.sim_reset()

        # nodes =================================================
        alice   = Node("Alice", port_names=["A.Q.Out", "A.C.Out", "A.C.In"])
        bob     = Node("Bob", port_names=["B.Q.Out", "B.C.Out", "B.C.In"])
        charlie = Node("Charlie", port_names=["C.Q.In.A", "C.Q.In.B", "C.C.In.A", "C.C.In.B", "C.C.Out.A", "C.C.Out.B"])

        # channels ==============================================
        ### quantum
        QChann1 = QuantumChannel("[A: -Q-> :C]",
                                delay=qDelay,
                                length=fibreLen,
                                models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)})
        
        QChann2 = QuantumChannel("[B: -Q-> :C]",
                                delay=qDelay,
                                length=fibreLen,
                                models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)})
        
        alice.connect_to(charlie,
                         QChann1,
                         local_port_name=alice.ports["A.Q.Out"].name,
                         remote_port_name=charlie.ports["C.Q.In.A"].name)
        
        bob.connect_to(charlie,
                         QChann2,
                         local_port_name=bob.ports["B.Q.Out"].name,
                         remote_port_name=charlie.ports["C.Q.In.B"].name)
        
        ### classical
        CChann1 = ClassicalChannel("[A: -C-> :C]",
                                delay=0,
                                length=fibreLen,
                                # models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)}
                                )
        
        CChann2 = ClassicalChannel("[B: -C-> :C]",
                                delay=0,
                                length=fibreLen,
                                # models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)}
                                )
        
        CChann3 = ClassicalChannel("[C: -C-> :A]",
                                delay=0,
                                length=fibreLen,
                                # models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)}
                                )
        
        CChann4 = ClassicalChannel("[C: -C-> :B]",
                                delay=0,
                                length=fibreLen,
                                # models={"delay_model": HybridDelayModel(SoL_fraction=qSpeed,stddev=0.05)}
                                )
        
        alice.connect_to(charlie,
                         CChann1,
                         local_port_name=alice.ports["A.C.Out"].name,
                         remote_port_name=charlie.ports["C.C.In.A"].name)
        
        bob.connect_to(charlie,
                         CChann2,
                         local_port_name=bob.ports["B.C.Out"].name,
                         remote_port_name=charlie.ports["C.C.In.B"].name)
        
        charlie.connect_to(alice,
                         CChann3,
                         local_port_name=charlie.ports["C.C.Out.A"].name,
                         remote_port_name=alice.ports["A.C.In"].name)
        
        charlie.connect_to(bob,
                         CChann4,
                         local_port_name=charlie.ports["C.C.Out.B"].name,
                         remote_port_name=bob.ports["B.C.In"].name)
        
        # protocols =============================================
        aliceProt = EndNodeProtocol(alice, 'alice', photonCount, sourceFreq, 
                                    portNames=["A.Q.Out", "A.C.Out", "A.C.In"])
        bobProt = EndNodeProtocol(bob, 'bob', photonCount, sourceFreq,
                                  portNames=["B.Q.Out", "B.C.Out", "B.C.In"])
        charlieProt = RelayNodeProtocol(charlie, 'charlie', photonCount,
                                        portNames=["C.Q.In.A", "C.Q.In.B", "C.C.In.A", "C.C.In.B", "C.C.Out.A", "C.C.Out.B"])
        
        bobProt.flipper = True

        charlieProt.start()
        aliceProt.start()
        bobProt.start()

        startTime = ns.util.simtools.sim_time(magnitude=ns.NANOSECOND)
        stats = ns.sim_run(end_time=ns.SECOND)

        if aliceProt.end_time is not None and bobProt.end_time is not None:
            endTime = max(aliceProt.end_time, bobProt.end_time)
        else:
            print(f"WARNING: protocols did not complete in run {_+1}/{runtimes}, skipping")
            continue

        keyA, keyB = aliceProt.key, bobProt.key

        KeyListA.append(keyA)
        KeyListB.append(keyB)

    return KeyListA, KeyListB, KeyRateList