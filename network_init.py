from netsquid.nodes import Node, DirectConnection
from netsquid.components import QuantumChannel, ClassicalChannel
from netsquid.components.models import DelayModel


class BB84DelayModel(DelayModel):
    """
    Delay Model for Quantum state transmission.

    Parameters:
        - speed_of_light_fraction: float, default 0.5, average speed of transmission in units of c
        - standard_deviation: float, default 0.05, standard deviation for state transmission speed

    Returns:
        BB84DelayModel object with generate_delay method to extract delay in nanoseconds

    Assumptions:
        - Speed of light is 300,000 km/s
    """
    def __init__(self, speed_of_light_fraction=0.5, standard_deviation=0.05):
        super.__init__()
        # model SoL as 300,000 km/s
        self.properties["speed"] = speed_of_light_fraction * 3e5
        self.properties["std"] = standard_deviation
        self.required_properties = ['length']  # in km

    def generate_delay(self, **kwargs):
        avg_speed = self.properties["speed"]
        std = self.properties["std"]
        # The 'rng' property contains a random number generator
        # We can use that to generate a random speed
        speed = self.properties["rng"].normal(avg_speed, avg_speed * std)
        delay = 1e9 * kwargs['length'] / speed  # in nanoseconds
        return delay


def net_init(node1 : str, node2 : str, distance : float, sol_fraction=0.5, std=0.05):
    """
    Initialise NetSquid-native network representation for BB84.

    Creates two nodes (e.g., Alice and Bob), a unidirectional quantum channel
    from node1 to node2 with propagation delay, and bidirectional classical
    channels for basis/bit exchanges.

    Parameters:
        - node1: str, name of first node (sender)
        - node2: str, name of second node (receiver)
        - distance: float, distance in km for channel lengths and delays
        - sol_fraction: float, default 0.5, fraction of speed of light for transmission
        - std: float, default 0.05, standard deviation for transmission speed variability

    Returns:
        Tuple of two Node objects (node1_obj, node2_obj) ready for components/protocols.
    
    Assumptions:
        - Nodes start without subcomponents; add quantum processors, ports manually.
        - No loss/decoherence yet - add via QuantumLossModel or Fibre for realism.
        - Speed of light modelled as 300,000 km/s base.
    """
    node1_obj = Node(name=node1)
    node2_obj = Node(name=node2)

    delay_model = BB84DelayModel(sol_fraction,std)

    # Quantum Channel (node1 -> node2)
    qChannel_1 = QuantumChannel(name=f"qchannel[{node1} to {node2}]",
                                length=distance,
                                models={"delay_model": delay_model})
    qconn = DirectConnection(name=f"qconn[{node1}|{node2}]",
                             channel_AtoB=qChannel_1)
    node1_obj.connect_to(remote_node=node2_obj,
                         connection=qconn,
                         local_port_name=f"[{node1}] Q-O",
                         remote_port_name=f"[{node2}] Q-I")
    
    # Classical Channels (node1 <-> node2)
    cChannel_1 = ClassicalChannel(name=f"cchannel[{node1} to {node2}]",
                                  length=distance,
                                  models={"delay_model": delay_model})
    cChannel_2 = ClassicalChannel(name=f"cchannel[{node2} to {node1}]",
                                  length=distance,
                                  models={"delay_model": delay_model})
    cconn = DirectConnection(name=f"cconn[{node1}|{node2}]",
                             channel_AtoB=cChannel_1,
                             channel_BtoA=cChannel_2)
    node1_obj.connect_to(remote_node=node2_obj, 
                         connection=cconn,
                         local_port_name=f"[{node1}] C-IO",
                         remote_port_name=f"[{node2}] C-IO")
    
    return node1_obj, node2_obj