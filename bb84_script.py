import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append("lib/")  # For functions.py
sys.path.append("BB84/") # For BB84 protocols

import numpy as np
from difflib import SequenceMatcher

from BB84.BB84_run import run_BB84_sims



def print_results(key_list_a, key_list_b, key_rate_list):
    """
    Print simulation statistics.
    """
    print("\n=== BB84 Simulation Results ===")

    key_list_a = [[str(bit) for bit in _] for _ in key_list_a]
    key_list_b = [[str(bit) for bit in _] for _ in key_list_b]
    
    # Average sifted key length
    avg_key_len_a = np.mean([len(k) for k in key_list_a])
    avg_key_len_b = np.mean([len(k) for k in key_list_b])
    print(f"\nAverage Alice sifted key length:   {avg_key_len_a:.1f}")
    print(f"Average Bob sifted key length:     {avg_key_len_b:.1f}")
    
    # QBER (bit error rate) across runs
    qber = 1 - np.mean([SequenceMatcher(None, ka, kb).ratio() for ka, kb in zip(key_list_a, key_list_b)])
    print(f"\nAverage QBER:                      {qber:.2%}")

    print(f"Full key match ratio:              {SequenceMatcher(None, key_list_a[0], key_list_b[0]).ratio():.3f}")
    
    # Key rate (bits/ns, scaled to bits/s)
    avg_key_rate = np.mean(key_rate_list)
    print(f"\nAverage key rate:                  {avg_key_rate * 1e9:.2e} bits/s")
    
    print("\nRaw keys (first run sample, first 50 bits):")
    print(f"Alice: {''.join(key_list_a[0][:50])}...")  # First 50 bits
    print(f"Bob:   {''.join(key_list_b[0][:50])}...")

def main(runtimes=1, fibre_len=1, photon_count=1024, source_freq=1e7, q_speed=0.8):
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
    key_a, key_b, key_rates = run_BB84_sims(
        runtimes=runtimes,
        fibreLen=fibre_len,
        photonCount=photon_count,
        sourceFreq=source_freq,
        qSpeed=q_speed
    )
    print_results(key_a, key_b, key_rates)

if __name__ == "__main__":
    main()