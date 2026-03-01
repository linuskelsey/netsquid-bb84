import netsquid as ns

from netsquid.components.qsource import SourceStatus
from netsquid.protocols import NodeProtocol



class RelayNodeProtocol(NodeProtocol):
    """
    Protocol to run on End User node in point-to-point BB84.

    Attributes:
        

    Parameters:
        
    """
    def __init__(self, node, name, photonCount, portNames=["Q0.In", "Q1.In", "C0.In", "C1.In", "C0.Out", "C1.Out"]):
        super().__init__()
        # distinguish node on which the protocol runs
        self.node = node
        self.name = name.title()
        # number of photons to expect
        self.photon_count = photonCount
        # ports, 0/1 denotes side, i/o denotes in/out
        self.port_q0_i_name = portNames[0]
        self.port_q1_i_name = portNames[1]
        self.port_c0_i_name = portNames[2]
        self.port_c1_i_name = portNames[3]
        self.port_c0_o_name = portNames[4]
        self.port_c1_o_name = portNames[5]
        # measurement list
        self.meas = []


    def bsm_total(self):
        """
        Perform Bell State Measurements on received qubits.

        Simplified for current modelling with no synchronisation or memory constraints.
        """
        # receive from 1
        port = self.node.ports[self.port_q0_i_name]
        yield self.await_port_input(port)
        q_list0 = port.rx_input().items
        # receive from 2
        port = self.node.ports[self.port_q1_i_name]
        yield self.await_port_input(port)
        q_list1 = port.rx_input().items

        for q0, q1 in zip(q_list0, q_list1):
            # BSM
            ns.qubits.operate([q0,q1], ns.CNOT)
            ns.qubits.operate(q0, ns.H)

            a, _ = ns.qubits.measure(q0)
            b, _ = ns.qubits.measure(q1)

            # psi minus
            if a == 1 and b == 1:
                self.meas.append(-1)
            # psi plus
            elif a == 0 and b == 1:
                self.meas.append(1)
            # otherwise (modelling the BS/PBS setup of Lo et al. 2012)
            else:
                self.meas.append(0)
    

    def basis_matching(self):
        """
        Receive basis lists from EndNodes and communicate back those bits to discard
        """
        # receive from 1
        port = self.node.ports[self.port_c0_i_name]
        yield self.await_port_input(port)
        basis_list0 = port.rx_input().items
        # receive from 2
        port = self.node.ports[self.port_c1_i_name]
        yield self.await_port_input(port)
        basis_list1 = port.rx_input().items
        
        discard=[]
        for i, b in enumerate(basis_list0):
            if b != basis_list1[i]:
                discard.append(i)

        self.node.ports[self.port_c0_o_name].tx_output(discard if len(discard) > 0 else [-1])
        self.node.ports[self.port_c1_o_name].tx_output(discard if len(discard) > 0 else [-1])


    def run(self):
        """
        Run RelayNodeProtocol.
        """
        # BSMs
        yield from self.bsm_total()

        # send measurement results
        self.node.ports[self.port_c0_o_name].tx_output(self.meas)
        self.node.ports[self.port_c1_o_name].tx_output(self.meas)

        #receive bases and send matching to end nodes
        yield from self.basis_matching()