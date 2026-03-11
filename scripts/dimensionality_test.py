"""
Dimensionality Independence Test
================================
Question: Is the PCA compression ratio of the kernel algebra
independent of channel count n?

If yes: dimensionality is emergent from coherence structure, not primitive.
If no: dimensionality retains an irreducible role.
"""

from __future__ import annotations

import numpy as np
from numpy.linalg import svd

EPSILON = 1e-8


def compute_kernel(c: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """K: [0,1]^n x Delta^n -> (F, omega, S, C, kappa, IC)."""
    n = len(c)
    if w is None:
        w = np.ones(n) / n
    c_safe = np.clip(c, EPSILON, 1 - EPSILON)

    F = float(np.dot(w, c_safe))
    omega = 1.0 - F
    kappa = float(np.dot(w, np.log(c_safe)))
    IC = np.exp(kappa)
    S = float(-np.dot(w, c_safe * np.log(c_safe) + (1 - c_safe) * np.log(1 - c_safe)))
    C = float(np.std(c_safe) / 0.5)

    return np.array([F, omega, S, C, kappa, IC])


def main() -> None:
    print("=" * 72)
    print("  DIMENSIONALITY INDEPENDENCE TEST")
    print("  Does the kernel algebra's rank depend on channel count n?")
    print("=" * 72)
    print()

    rng = np.random.default_rng(42)
    N_SAMPLES = 10_000
    channel_counts = [4, 6, 8, 10, 12, 16, 32, 64]

    header = f"  {'n':>4s}  {'PC1':>7s}  {'PC2':>7s}  {'PC3':>7s}  {'PC4':>7s}  {'PC5':>7s}  {'PC6':>7s}  {'n99':>4s}  {'n999':>5s}"
    print(header)
    print("  " + "-" * len(header))

    results = {}

    for n in channel_counts:
        outputs = np.zeros((N_SAMPLES, 6))
        for i in range(N_SAMPLES):
            c = rng.uniform(0.01, 0.99, size=n)
            outputs[i] = compute_kernel(c)

        means = outputs.mean(axis=0)
        stds = outputs.std(axis=0) + 1e-15
        outputs_norm = (outputs - means) / stds

        _, s, _ = svd(outputs_norm, full_matrices=False)
        var_explained = s**2 / (s**2).sum()
        cumvar = np.cumsum(var_explained)

        n_eff_99 = int(np.sum(cumvar < 0.99)) + 1
        n_eff_999 = int(np.sum(cumvar < 0.999)) + 1

        results[n] = {
            "var_explained": var_explained,
            "n_eff_99": n_eff_99,
            "n_eff_999": n_eff_999,
        }

        pcs = "  ".join(f"{v * 100:6.2f}%" for v in var_explained)
        print(f"  {n:4d}  {pcs}  {n_eff_99:4d}  {n_eff_999:5d}")

    print()

    n_effs_99 = [results[n]["n_eff_99"] for n in channel_counts]
    if len(set(n_effs_99)) == 1:
        print(f"  ** UNIVERSAL: n_eff(99%) = {n_effs_99[0]} for ALL n in {channel_counts}")
        print(f"     The kernel has FIXED RANK {n_effs_99[0]}, independent of input dimension.")
    else:
        print(f"  ** VARIES: n_eff(99%) = {dict(zip(channel_counts, n_effs_99, strict=True))}")

    # Structural reason
    print()
    print("  STRUCTURAL DECOMPOSITION")
    print("  " + "-" * 50)
    print("  Algebraic constraints on 6 outputs (F, w, S, C, k, IC):")
    print("    (1) w = 1 - F         [duality identity, exact]")
    print("    (2) IC = exp(k)       [log-integrity relation, exact]")
    print("  These remove 2 DOF => max algebraic rank = 4")
    print()

    # Correlation structure
    print("  Statistical correlations (beyond algebra):")
    for n in [8, 16, 64]:
        outputs = np.zeros((N_SAMPLES, 6))
        for i in range(N_SAMPLES):
            c = rng.uniform(0.01, 0.99, size=n)
            outputs[i] = compute_kernel(c)

        corr_S_k = np.corrcoef(outputs[:, 2], outputs[:, 4])[0, 1]
        corr_S_F = np.corrcoef(outputs[:, 2], outputs[:, 0])[0, 1]
        corr_C_F = np.corrcoef(outputs[:, 3], outputs[:, 0])[0, 1]
        corr_C_S = np.corrcoef(outputs[:, 3], outputs[:, 2])[0, 1]

        print(
            f"    n={n:3d}: corr(S,k)={corr_S_k:+.4f}  "
            f"corr(S,F)={corr_S_F:+.4f}  "
            f"corr(C,F)={corr_C_F:+.4f}  "
            f"corr(C,S)={corr_C_S:+.4f}"
        )

    # Compression table
    print()
    print("  COMPRESSION TABLE")
    print("  " + "-" * 50)
    print(f"  {'n (input)':>12s} -> {'R^6':>5s} -> {'n_eff':>5s}   ratio")
    for n in channel_counts:
        r = results[n]
        compression = n / r["n_eff_99"]
        print(f"  {n:12d} -> {6:5d} -> {r['n_eff_99']:5d}   {compression:.1f}:1")

    print()
    print("  If n_eff is constant, then ALL input dimensionality is narrative.")
    print("  The kernel sees only its own algebraic structure, not n.")
    print()

    # CLT convergence: does higher n make the kernel outputs MORE deterministic?
    print("  CENTRAL LIMIT CONVERGENCE")
    print("  " + "-" * 50)
    print(f"  {'n':>4s}  {'std(F)':>10s}  {'std(S)':>10s}  {'std(C)':>10s}  {'std(IC)':>10s}")
    for n in channel_counts:
        outputs = np.zeros((N_SAMPLES, 6))
        for i in range(N_SAMPLES):
            c = rng.uniform(0.01, 0.99, size=n)
            outputs[i] = compute_kernel(c)
        stds = outputs.std(axis=0)
        print(f"  {n:4d}  {stds[0]:10.6f}  {stds[2]:10.6f}  {stds[3]:10.6f}  {stds[5]:10.6f}")

    print()
    print("  As n -> inf, std -> 0: all traces converge to the SAME kernel point.")
    print("  More dimensions = LESS information, not more.")
    print("  Dimensionality dilutes; coherence concentrates.")


if __name__ == "__main__":
    main()
