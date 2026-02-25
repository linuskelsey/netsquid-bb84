import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append("lib/")  # For functions.py
sys.path.append("BB84/") # For BB84 protocols

import numpy as np
from difflib import SequenceMatcher

from BB84.BB84_run import run_BB84_sims



def main(runtimes=10, fibre_len=100, photon_count=32, source_freq=1e7, q_speed=0.8):
    """
    Run BB84 simulations.
    
    Args:
        runtimes: Number of simulation runs.
        fibre_len: Fibre length (km).
        photon_count: Photons per run.
        source_freq: Source frequency (Hz).
        q_speed: Quantum channel speed of light fraction.
    """
    print(f"Running BB84 sims: {runtimes} runs, {photon_count} photons, {fibre_len} km fibre")
    key_list_a, key_list_b, key_rates = run_BB84_sims(
        runtimes=runtimes,
        fibreLen=fibre_len,
        photonCount=photon_count,
        sourceFreq=source_freq,
        qSpeed=q_speed
    )

if __name__ == "__main__":
    main()