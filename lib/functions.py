import numpy as np

from netsquid.components import QSource
from netsquid.components.qsource import SourceStatus
from netsquid.components.models import DelayModel



class HybridDelayModel(DelayModel):
    def __init__(self, SoL_fraction=0.5, stddev=0.05):
        super().__init__()
        # speed of light is ~ 300,000,000 m/s
        self.properties["speed"] = SoL_fraction * 3e8
        self.properties["stddev"] = stddev
        self.required_properties = ["length"] # in m

    def generate_delay(self, **kwargs):
        avg_speed = self.properties["speed"]
        stddev = self.properties["stddev"]
        # The 'rng' property contains a random number generator
        # We can use that to generate a random speed
        speed = self.properties["rng"].normal(avg_speed, avg_speed * stddev)
        delay = 1e9 * kwargs["length"] / speed  # in nanoseconds
        return delay
    

def rng_bin_lst(n):
    return np.random.choice([0,1], size=n).tolist()


class SinglePhotonSource(QSource):
    def __init__(self, name, sourceFreq, efficiency=1, status=SourceStatus.EXTERNAL):
        super().__init__(name, frequency=sourceFreq, status=status)
        self.efficiency = efficiency