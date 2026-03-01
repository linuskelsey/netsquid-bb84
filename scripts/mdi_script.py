"""
MDI-QKD Simulation Runner
=========================
Executes the MDI-QKD netsquid simulation and prints performance metrics.

Usage:
    python run_mdi.py [--runtimes N] [--photons N] [--fibre F] [--freq F] [--speed S]

Defaults:
    runtimes    10
    photons     1024
    fibre       1       (km)
    freq        1e7     (Hz)
    speed       0.8     (fraction of c)
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append("MDI/") # For MDI protocols

from MDI.mdiRun import run_mdi_sims


def qber(keyA, keyB):
    """Compute QBER between two key lists."""
    if not keyA or not keyB:
        return None
    length = min(len(keyA), len(keyB))
    if length == 0:
        return None
    errors = sum(a != b for a, b in zip(keyA[:length], keyB[:length]))
    return errors / length


def key_rate(keyA, keyB, photon_count):
    """Compute sifted key rate as fraction of photon count."""
    sifted = min(len(keyA), len(keyB))
    return sifted / photon_count if photon_count > 0 else 0


def print_run_summary(run_idx, keyA, keyB, photon_count):
    """Print per-run metrics."""
    q = qber(keyA, keyB)
    kr = key_rate(keyA, keyB, photon_count)
    q_str = f"{q*100:.2f}%" if q is not None else "N/A"
    print(f"  Run {run_idx+1:>3}: key_len={len(keyA):>5} | QBER={q_str:>7} | key_rate={kr:.4f}")


def print_aggregate_summary(KeyListA, KeyListB, photon_count):
    """Print aggregate metrics across all runs."""
    qbers       = []
    key_rates   = []
    key_lengths = []

    for keyA, keyB in zip(KeyListA, KeyListB):
        q = qber(keyA, keyB)
        if q is not None:
            qbers.append(q)
        key_rates.append(key_rate(keyA, keyB, photon_count))
        key_lengths.append(min(len(keyA), len(keyB)))

    avg_qber     = sum(qbers) / len(qbers) if qbers else float('nan')
    avg_kr       = sum(key_rates) / len(key_rates) if key_rates else float('nan')
    avg_key_len  = sum(key_lengths) / len(key_lengths) if key_lengths else float('nan')

    print()
    print("=" * 55)
    print("  Aggregate Results")
    print("=" * 55)
    print(f"  Runs completed  : {len(KeyListA)}")
    print(f"  Avg key length  : {avg_key_len:.1f}")
    print(f"  Avg QBER        : {avg_qber*100:.2f}%")
    print(f"  Avg key rate    : {avg_kr:.4f}")
    print("=" * 55)


def main():
    parser = argparse.ArgumentParser(description="Run MDI-QKD netsquid simulation.")
    parser.add_argument("--runtimes", type=int,   default=10,    help="Number of simulation runs")
    parser.add_argument("--photons",  type=int,   default=1024,  help="Photons per run")
    parser.add_argument("--fibre",    type=float, default=1.0,   help="Fibre length in km")
    parser.add_argument("--freq",     type=float, default=1e7,   help="Source frequency in Hz")
    parser.add_argument("--speed",    type=float, default=0.8,   help="Speed of light fraction")
    args = parser.parse_args()

    print()
    print("=" * 55)
    print("  MDI-QKD Simulation")
    print("=" * 55)
    print(f"  Runtimes   : {args.runtimes}")
    print(f"  Photons    : {args.photons}")
    print(f"  Fibre      : {args.fibre} km")
    print(f"  Frequency  : {args.freq:.2e} Hz")
    print(f"  Speed      : {args.speed}c")
    print("=" * 55)
    print()

    KeyListA, KeyListB, KeyRateList = run_mdi_sims(
        runtimes    = args.runtimes,
        fibreLen    = args.fibre,
        photonCount = args.photons,
        sourceFreq  = args.freq,
        qSpeed      = args.speed
    )

    print("\n  Per-run results:")
    print("-" * 55)
    for i, (keyA, keyB) in enumerate(zip(KeyListA, KeyListB)):
        print_run_summary(i, keyA, keyB, args.photons)

    print_aggregate_summary(KeyListA, KeyListB, args.photons)


if __name__ == "__main__":
    main()