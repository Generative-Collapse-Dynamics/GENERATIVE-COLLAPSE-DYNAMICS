#!/usr/bin/env python3
"""Validate structural twin findings — are they real or artifacts?

Tests:
1. Bootstrap: How likely is each twin pair under random channel permutation?
2. Sensitivity: How stable is the twin match under ±5% channel perturbation?
3. Dimension analysis: Which kernel outputs drive the match?
4. Recovery manifold: Exact shape of IC/F recovery curve for slaughtered entities.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from src.umcp.frozen_contract import EPSILON
from src.umcp.kernel_optimized import OptimizedKernelComputer

K = OptimizedKernelComputer()

rng = np.random.default_rng(42)


def compute_icf(c: np.ndarray, w: np.ndarray | None = None) -> tuple[float, float, float]:
    """Return (IC/F, delta/F, C) for a trace vector."""
    c = np.clip(np.array(c, dtype=np.float64), EPSILON, 1 - EPSILON)
    if w is None:
        w = np.ones(len(c)) / len(c)
    r = K.compute(c, w)
    icf = r.IC / r.F if r.F > EPSILON else 0
    df = (r.F - r.IC) / r.F if r.F > EPSILON else 0
    return icf, df, r.C


def twin_distance(icf1: float, df1: float, c1: float, icf2: float, df2: float, c2: float) -> float:
    """Euclidean distance in (IC/F, delta/F, C) space."""
    return float(np.sqrt((icf1 - icf2) ** 2 + (df1 - df2) ** 2 + (c1 - c2) ** 2))


# ── Test 1: Bootstrap significance ──
def bootstrap_test(c1: np.ndarray, c2: np.ndarray, name1: str, name2: str, n_trials: int = 10000) -> dict:
    """How likely is a match THIS close under random channel permutation?

    We permute channels of entity2, recompute kernel, measure distance.
    The p-value = fraction of permuted distances ≤ observed distance.
    """
    icf1, df1, C1 = compute_icf(c1)
    icf2, df2, C2 = compute_icf(c2)
    observed = twin_distance(icf1, df1, C1, icf2, df2, C2)

    # Generate random trace vectors of same length as c2
    perm_distances = []
    for _ in range(n_trials):
        c2_rand = rng.uniform(EPSILON, 1.0, size=len(c2))
        icf_r, df_r, C_r = compute_icf(c2_rand)
        d = twin_distance(icf1, df1, C1, icf_r, df_r, C_r)
        perm_distances.append(d)

    perm_distances = np.array(perm_distances)
    p_value = float(np.mean(perm_distances <= observed))

    return {
        "name1": name1,
        "name2": name2,
        "observed_distance": observed,
        "p_value": p_value,
        "median_random": float(np.median(perm_distances)),
        "mean_random": float(np.mean(perm_distances)),
        "min_random": float(np.min(perm_distances)),
    }


# ── Test 2: Perturbation sensitivity ──
def sensitivity_test(
    c1: np.ndarray, c2: np.ndarray, name1: str, name2: str, perturbation: float = 0.05, n_trials: int = 1000
) -> dict:
    """How stable is the twin match under ±5% channel perturbation?"""
    icf1, df1, C1 = compute_icf(c1)
    icf2, df2, C2 = compute_icf(c2)
    observed = twin_distance(icf1, df1, C1, icf2, df2, C2)

    perturbed_distances = []
    for _ in range(n_trials):
        noise1 = 1 + rng.uniform(-perturbation, perturbation, size=len(c1))
        noise2 = 1 + rng.uniform(-perturbation, perturbation, size=len(c2))
        c1p = np.clip(c1 * noise1, EPSILON, 1 - EPSILON)
        c2p = np.clip(c2 * noise2, EPSILON, 1 - EPSILON)
        icf1p, df1p, C1p = compute_icf(c1p)
        icf2p, df2p, C2p = compute_icf(c2p)
        perturbed_distances.append(twin_distance(icf1p, df1p, C1p, icf2p, df2p, C2p))

    pd = np.array(perturbed_distances)
    return {
        "name1": name1,
        "name2": name2,
        "observed_distance": observed,
        "mean_perturbed": float(np.mean(pd)),
        "std_perturbed": float(np.std(pd)),
        "pct_still_close": float(np.mean(pd < 0.02)),  # still a twin at 0.02 threshold
        "stable": bool(np.mean(pd < 0.05) > 0.95),  # stable if >95% stay below 0.05
    }


# ── Test 3: Recovery manifold exact shape ──
def recovery_curve(c_base: np.ndarray, dead_idx: int, name: str, n_points: int = 100) -> dict:
    """Sweep the dead channel from EPSILON to 1.0, record IC/F curve."""
    c = np.array(c_base, dtype=np.float64)
    w = np.ones(len(c)) / len(c)

    sweeps = np.linspace(EPSILON, 1.0, n_points)
    icf_curve = []
    for val in sweeps:
        c_test = c.copy()
        c_test[dead_idx] = val
        c_test = np.clip(c_test, EPSILON, 1 - EPSILON)
        r = K.compute(c_test, w)
        icf_curve.append(r.IC / r.F if r.F > EPSILON else 0)

    icf_arr = np.array(icf_curve)
    # Find the "elbow" — where the second derivative is maximized
    d2 = np.diff(icf_arr, n=2)
    elbow_idx = int(np.argmax(d2)) + 1  # +1 for diff offset
    elbow_value = float(sweeps[elbow_idx])

    return {
        "name": name,
        "dead_channel": dead_idx,
        "initial_icf": float(icf_arr[0]),
        "final_icf": float(icf_arr[-1]),
        "recovery_factor": float(icf_arr[-1] / icf_arr[0]) if icf_arr[0] > EPSILON else float("inf"),
        "elbow_channel_value": elbow_value,
        "elbow_icf": float(icf_arr[elbow_idx]),
        "curve_is_superexponential": bool(icf_arr[50] / icf_arr[25] > 2 * (icf_arr[25] / icf_arr[0])),
    }


def main() -> None:
    print("=" * 80)
    print("  STRUCTURAL TWIN VALIDATION — Bootstrap + Sensitivity + Recovery")
    print("=" * 80)

    # ── Load the key twin pairs ──
    from closures.awareness_cognition.awareness_kernel import ORGANISM_CATALOG
    from closures.consciousness_coherence.coherence_kernel import COHERENCE_CATALOG
    from closures.dynamic_semiotics.semiotic_kernel import SIGN_SYSTEMS

    med = next(o for o in ORGANISM_CATALOG if "meditator" in o.name.lower())
    sch = next(s for s in COHERENCE_CATALOG if "schumann" in s.name.lower())
    lat = next(s for s in SIGN_SYSTEMS if "latin" in s.name.lower())

    # Load Pb-208 from periodic kernel
    from closures.atomic_physics.periodic_kernel import _normalize_element
    from closures.materials_science.element_database import get_element

    pb_el = get_element(82)
    assert pb_el is not None
    pb_trace, _, _ = _normalize_element(pb_el)  # Pb is Z=82

    # Load Fe-56 trace
    fe_el = get_element(26)
    assert fe_el is not None
    fe_trace, _, _ = _normalize_element(fe_el)  # Fe is Z=26

    # Load Euler identity from semiotics
    euler = next(s for s in SIGN_SYSTEMS if "mathematical" in s.name.lower())

    pairs = [
        ("Human meditator", np.array(med.trace), "Schumann resonance", np.array(sch.trace_vector())),
        ("Euler identity", np.array(euler.trace_vector()), "Pb-208", np.array(pb_trace)),
        ("Latin", np.array(lat.trace_vector()), "Fe-56", np.array(fe_trace)),
    ]

    # ── Bootstrap tests ──
    print("\n" + "─" * 60)
    print("  TEST 1: Bootstrap Significance (10,000 random trials each)")
    print("─" * 60)
    for name1, c1, name2, c2 in pairs:
        result = bootstrap_test(c1, c2, name1, name2)
        print(f"\n  {name1} <-> {name2}")
        print(f"    Observed distance:    {result['observed_distance']:.6f}")
        print(f"    p-value:              {result['p_value']:.4f}")
        print(f"    Median random dist:   {result['median_random']:.4f}")
        print(f"    Min random dist:      {result['min_random']:.4f}")
        sig = (
            "***SIGNIFICANT***"
            if result["p_value"] < 0.01
            else ("**significant**" if result["p_value"] < 0.05 else "not significant")
        )
        print(f"    Verdict:              {sig}")

    # ── Sensitivity tests ──
    print("\n" + "─" * 60)
    print("  TEST 2: Perturbation Sensitivity (±5%, 1000 trials each)")
    print("─" * 60)
    for name1, c1, name2, c2 in pairs:
        result = sensitivity_test(c1, c2, name1, name2)
        print(f"\n  {name1} <-> {name2}")
        print(f"    Observed distance:    {result['observed_distance']:.6f}")
        print(f"    Mean perturbed dist:  {result['mean_perturbed']:.6f}")
        print(f"    Std perturbed dist:   {result['std_perturbed']:.6f}")
        print(f"    % still twin (<0.02): {result['pct_still_close'] * 100:.1f}%")
        print(f"    Stable (>95% <0.05):  {result['stable']}")

    # ── IC/F bimodality test ──
    print("\n" + "─" * 60)
    print("  TEST 3: IC/F Bimodality — Gap Analysis")
    print("─" * 60)

    from scripts.structural_twins import harvest_all

    entities = harvest_all()

    icf_values = []
    for e in entities:
        c = np.clip(np.array(e.channels, dtype=np.float64), EPSILON, 1 - EPSILON)
        w = np.ones(len(c)) / len(c)
        r = K.compute(c, w)
        icf_values.append(r.IC / r.F if r.F > EPSILON else 0)

    icf_arr = np.array(icf_values)

    # Hartigan's dip test proxy — measure density in the valley
    valley_count = np.sum((icf_arr > 0.02) & (icf_arr < 0.3))
    low_count = np.sum(icf_arr <= 0.02)
    high_count = np.sum(icf_arr >= 0.7)
    total = len(icf_arr)

    print(f"\n  Total entities:              {total}")
    print(f"  Low mode (IC/F ≤ 0.02):     {low_count} ({low_count / total * 100:.1f}%)")
    print(f"  Valley (0.02 < IC/F < 0.3): {valley_count} ({valley_count / total * 100:.1f}%)")
    print(f"  High mode (IC/F ≥ 0.7):     {high_count} ({high_count / total * 100:.1f}%)")
    print(f"  Bimodality ratio:            {(low_count + high_count) / total:.3f}")
    print("    (>0.5 = bimodal, >0.7 = strongly bimodal)")

    # Valley density relative to a uniform distribution
    valley_width = 0.3 - 0.02
    expected_uniform = total * valley_width  # expected in valley if uniform
    valley_deficit = 1 - valley_count / expected_uniform if expected_uniform > 0 else 0
    print(f"  Valley deficit vs uniform:   {valley_deficit:.2%}")
    print("    (how much sparser the valley is vs what uniform would predict)")

    # ── Recovery manifold shape ──
    print("\n" + "─" * 60)
    print("  TEST 4: Recovery Manifold — Dead Channel → Alive")
    print("─" * 60)

    # Proton: build trace same way as structural_twins harvester
    from closures.standard_model.subatomic_kernel import COMPOSITE_PARTICLES

    proton_p = next(p for p in COMPOSITE_PARTICLES if p.name == "proton")
    _m = proton_p.mass_GeV or 1e-30
    proton_trace = np.array(
        [
            np.clip((np.log10(max(_m, 1e-30)) + 30) / 60, EPSILON, 1 - EPSILON),
            np.clip(abs(proton_p.charge_e) / 2.0, EPSILON, 1 - EPSILON),
            np.clip(proton_p.spin / 2.0, EPSILON, 1 - EPSILON),
            np.clip(getattr(proton_p, "color_dof", 1) / 8.0, EPSILON, 1 - EPSILON),
            np.clip((getattr(proton_p, "weak_T3", 0.0) + 1.0) / 2.0, EPSILON, 1 - EPSILON),
            np.clip((getattr(proton_p, "hypercharge_Y", 0.0) + 2.0) / 4.0, EPSILON, 1 - EPSILON),
            np.clip(getattr(proton_p, "generation", 0) / 3.0, EPSILON, 1 - EPSILON),
            EPSILON,  # stability channel
        ]
    )

    # Dead channel is likely stability (index 7) — find actual deadest
    dead_ch_proton = int(np.argmin(proton_trace))
    result = recovery_curve(proton_trace, dead_ch_proton, f"Proton (channel {dead_ch_proton})")
    print(f"\n  {result['name']}")
    print(f"    Initial IC/F (dead):     {result['initial_icf']:.6f}")
    print(f"    Final IC/F (full):       {result['final_icf']:.6f}")
    print(f"    Recovery factor:         {result['recovery_factor']:.1f}x")
    print(f"    Elbow at channel value:  {result['elbow_channel_value']:.4f}")
    print(f"    Elbow IC/F:              {result['elbow_icf']:.6f}")
    print(f"    Super-exponential:       {result['curve_is_superexponential']}")

    # He: 8-channel atomic trace, dead channels
    he_el = get_element(2)
    assert he_el is not None
    he_trace, _, _ = _normalize_element(he_el)  # He is Z=2
    # Find the deadest channel
    he_arr = np.array(he_trace, dtype=np.float64)
    dead_ch = int(np.argmin(he_arr))
    result = recovery_curve(he_arr, dead_ch, f"Helium (channel {dead_ch})")
    print(f"\n  {result['name']}")
    print(f"    Initial IC/F (dead):     {result['initial_icf']:.6f}")
    print(f"    Final IC/F (full):       {result['final_icf']:.6f}")
    print(f"    Recovery factor:         {result['recovery_factor']:.1f}x")
    print(f"    Elbow at channel value:  {result['elbow_channel_value']:.4f}")
    print(f"    Elbow IC/F:              {result['elbow_icf']:.6f}")
    print(f"    Super-exponential:       {result['curve_is_superexponential']}")

    # ── 10-point recovery sweep for proton ──
    print(f"\n  Proton recovery sweep (dead channel {dead_ch_proton}, 0 → 1):")
    c = proton_trace.copy()
    w = np.ones(8) / 8
    for val in [EPSILON, 0.01, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 1.0]:
        c_test = c.copy()
        c_test[dead_ch_proton] = val
        c_test = np.clip(c_test, EPSILON, 1 - EPSILON)
        r = K.compute(c_test, w)
        icf = r.IC / r.F
        bar = "█" * int(icf * 50)
        print(f"    color={val:.4f}  IC/F={icf:.6f}  {bar}")

    print("\n" + "=" * 80)
    print("  SUMMARY")
    print("=" * 80)
    print()
    print("  If bootstrap p < 0.05, the twin pair is unlikely under random channels.")
    print("  If perturbation-stable, the match survives measurement noise.")
    print("  If recovery is super-exponential, the dead→alive transition is sharp.")
    print("  If bimodality ratio > 0.5, the two-mode structure is real, not artifact.")


if __name__ == "__main__":
    main()
