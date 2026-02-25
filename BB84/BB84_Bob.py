import netsquid as ns

from netsquid.protocols import NodeProtocol
from netsquid.components import QSource
from netsquid.components.qsource import SourceStatus

import sys
scriptpath = "lib/"
sys.path.append(scriptpath)
from lib.functions import rng_bin_lst



class BobProtocol(NodeProtocol):
    def __init__(self, node, photonCount, portNames=["B.Q.In","B.C.In","B.C.Out"]):
        super().__init__()
        self.node         = node
        self.photon_count = photonCount
        self.port_qi_name = portNames[0]
        self.port_ci_name = portNames[1]
        self.port_co_name = portNames[2]
        self.basis_list   = rng_bin_lst(photonCount)

        self.meas_results = []
        self.mask         = []
        self.key          = []
        self.end_time     = None

        self.bits = []


    def receive_and_measure(self):
        """
        Receive qubit batch on B.Q.In, measure in pre-assigned bases, store outcomes
        """
        # wait for qubit array input to port
        port = self.node.ports[self.port_qi_name]
        yield self.await_port_input(port)
        qubit_batch = port.rx_input().items
        
        # measure and store
        for i, q in enumerate(qubit_batch):
            basis = self.basis_list[i]
            if basis: ns.qubits.operate(q,ns.H)  # if: X basis, then: rotate
            meas = ns.qubits.measure(q)[0]       # Z basis measurement
            self.meas_results.append(meas)       # outcome bit
            self.bits.append((basis, meas))
        
        self.key = self.meas_results


    def basis_reconciliation(self):
        """
        Receive basis choices from Alice, send Bob's and sift common bits into self.key
        """
        # send to Alice
        self.node.ports[self.port_co_name].tx_output(self.basis_list)

        # identify classical in port and await Alice's basis list
        port = self.node.ports[self.port_ci_name]
        yield self.await_port_input(port)
        alice_bases = port.rx_input().items

        self.mask = [i for i, b in enumerate(alice_bases) if b == self.basis_list[i]]
        
        # finalise key output by matching bases
        # self.key = [bit for i, bit in enumerate(self.meas_results) if self.basis_list[i] == alice_bases[i]]


    def run(self):
        """
        Run Bob's protocol in full
        """
        # Wait for Alice's qubits + auto‑measure
        yield from self.receive_and_measure()
        
        # Basis exchange + sift
        yield from self.basis_reconciliation()

        # set end time of simulation
        self.end_time = ns.sim_time()