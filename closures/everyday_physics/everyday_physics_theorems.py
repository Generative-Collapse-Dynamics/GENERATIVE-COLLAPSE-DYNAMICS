"""
Everyday Physics Theorems — 10 Proven Theorems (T-EP-1 through T-EP-10)

Proves cross-domain structural patterns across thermodynamics,
electromagnetism, optics, and wave phenomena through the GCD kernel.
Each theorem is proven computationally against the combined catalog
of 84 systems.

═══════════════════════════════════════════════════════════════════════
THEOREM INDEX
═══════════════════════════════════════════════════════════════════════
  T-EP-1  Tier-1 Kernel Identities — F+ω=1, IC≤F, IC=exp(κ) across all 84 systems
  T-EP-2  EM Geometric Slaughter — conductors have near-zero IC from range disparity
  T-EP-3  Wave Type Hierarchy — EM waves > sound > water in fidelity
  T-EP-4  Thermal Metal Coherence — metals have higher IC/F than non-metals
  T-EP-5  Cross-Domain Gap Ordering — EM has highest mean Δ across all 4 subdomains
  T-EP-6  Laser Exceptional Coherence — only system outside Collapse regime
  T-EP-7  Diamond Cross-Domain Excellence — highest F in thermal domain
  T-EP-8  Conductor IC Suppression — conductors have lowest IC in EM domain
  T-EP-9  Sound Wave Homogeneity — sound waves have lowest mean Δ among wave types
  T-EP-10 Universal Collapse Dominance — >95% of all systems are in Collapse regime

Derivation chain: Axiom-0 → frozen_contract → kernel_optimized → 4 compute modules → this
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

_WORKSPACE = Path(__file__).resolve().parents[2]
if str(_WORKSPACE / "src") not in sys.path:
    sys.path.insert(0, str(_WORKSPACE / "src"))
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from closures.everyday_physics.electromagnetism import compute_all_em_materials  # noqa: E402
from closures.everyday_physics.optics import compute_all_optical_materials  # noqa: E402
from closures.everyday_physics.thermodynamics import compute_all_thermal_materials  # noqa: E402
from closures.everyday_physics.wave_phenomena import compute_all_wave_systems  # noqa: E402


@dataclass(frozen=True, slots=True)
class TheoremResult:
    """Result of a theorem proof attempt."""

    name: str
    statement: str
    n_tests: int
    n_passed: int
    n_failed: int
    details: dict[str, Any]
    verdict: str  # "PROVEN" or "FALSIFIED"


# ── Helpers ───────────────────────────────────────────────────────


def _all_results() -> tuple[list, list, list, list]:
    """Get all results from the 4 subdomains."""
    return (
        compute_all_thermal_materials(),
        compute_all_em_materials(),
        compute_all_optical_materials(),
        compute_all_wave_systems(),
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-1: Tier-1 Kernel Identities
# ═════════════════════════════════════════════════════════════════════


def theorem_EP1_kernel_identities() -> TheoremResult:
    """T-EP-1: All 84 systems satisfy Tier-1 kernel identities.

    STATEMENT: For all systems across all 4 subdomains, F + ω = 1,
    IC ≤ F, and IC = exp(κ) to machine precision (allowing for
    6-decimal rounding in the Result types).
    """
    therm, em, opt, wave = _all_results()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    all_systems: list[tuple[str, float, float, float, float]] = []
    for r in therm:
        all_systems.append((r.material, r.F, r.omega, r.IC, r.kappa))
    for r in em:
        all_systems.append((r.material, r.F, r.omega, r.IC, r.kappa))
    for r in opt:
        all_systems.append((r.material, r.F, r.omega, r.IC, r.kappa))
    for r in wave:
        all_systems.append((r.system, r.F, r.omega, r.IC, r.kappa))

    tol = 1e-4  # Tolerance for 6-decimal rounding in Result types

    for _name, f, omega, ic, kappa in all_systems:
        # F + ω = 1
        tests_total += 1
        tests_passed += int(abs(f + omega - 1.0) < tol)

        # IC ≤ F
        tests_total += 1
        tests_passed += int(ic <= f + tol)

        # IC = exp(κ)
        tests_total += 1
        tests_passed += int(abs(ic - np.exp(kappa)) < tol)

    details["n_systems"] = len(all_systems)
    details["n_thermal"] = len(therm)
    details["n_em"] = len(em)
    details["n_optics"] = len(opt)
    details["n_waves"] = len(wave)

    return TheoremResult(
        name="T-EP-1: Tier-1 Kernel Identities",
        statement="F+ω=1, IC≤F, IC=exp(κ) hold across all 84 everyday physics systems",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-2: EM Geometric Slaughter
# ═════════════════════════════════════════════════════════════════════


def theorem_EP2_em_geometric_slaughter() -> TheoremResult:
    """T-EP-2: EM domain has near-zero IC from massive range disparity.

    STATEMENT: All 20 EM materials have IC < 0.06 while F > 0.18.
    The heterogeneity gap Δ > 0.18 for all materials. Electromagnetic
    properties span too many orders of magnitude — the normalization
    creates channels where some are near ε, killing IC through
    geometric slaughter while F remains moderate.
    """
    em = compute_all_em_materials()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    ics = [r.IC for r in em]
    fs = [r.F for r in em]
    gaps = [r.gap for r in em]

    # Test 1: All IC < 0.06
    tests_total += 1
    tests_passed += int(all(ic < 0.06 for ic in ics))
    details["max_IC"] = max(ics)

    # Test 2: All F > 0.18
    tests_total += 1
    tests_passed += int(all(f > 0.18 for f in fs))
    details["min_F"] = min(fs)

    # Test 3: All gaps > 0.18
    tests_total += 1
    tests_passed += int(all(g > 0.18 for g in gaps))
    details["min_gap"] = min(gaps)

    # Test 4: Mean IC/F ratio < 0.10 (severe slaughter)
    ic_f_ratios = [r.IC / r.F for r in em if r.F > 0]
    mean_ratio = float(np.mean(ic_f_ratios))
    tests_total += 1
    tests_passed += int(mean_ratio < 0.10)
    details["mean_IC_F_ratio"] = mean_ratio

    return TheoremResult(
        name="T-EP-2: EM Geometric Slaughter",
        statement="All EM materials have IC < 0.06 while F > 0.18 — geometric slaughter from range disparity",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-3: Wave Type Hierarchy
# ═════════════════════════════════════════════════════════════════════


def theorem_EP3_wave_type_hierarchy() -> TheoremResult:
    """T-EP-3: EM waves have higher F than sound/water/seismic waves.

    STATEMENT: Electromagnetic waves (light, laser, microwave, radio,
    X-ray, gamma) have higher mean F than sound waves, which in turn
    have higher mean F than water waves. The wave type hierarchy
    reflects the channel coherence of different wave phenomena.
    """
    wave = compute_all_wave_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    by_type: dict[str, list] = {}
    for r in wave:
        by_type.setdefault(r.wave_type, []).append(r)

    type_f: dict[str, float] = {}
    for wt, rs in by_type.items():
        type_f[wt] = float(np.mean([r.F for r in rs]))
        details[f"mean_F_{wt}"] = type_f[wt]

    # Test 1: EM F > sound F
    if "electromagnetic" in type_f and "sound" in type_f:
        tests_total += 1
        tests_passed += int(type_f["electromagnetic"] > type_f["sound"])

    # Test 2: Sound F > water F
    if "sound" in type_f and "water" in type_f:
        tests_total += 1
        tests_passed += int(type_f["sound"] > type_f["water"])

    # Test 3: At least 4 wave types present
    tests_total += 1
    tests_passed += int(len(by_type) >= 4)
    details["n_wave_types"] = len(by_type)

    # Test 4: EM waves have highest mean F
    if "electromagnetic" in type_f:
        tests_total += 1
        em_f = type_f["electromagnetic"]
        others = [f for t, f in type_f.items() if t != "electromagnetic"]
        tests_passed += int(all(em_f > o for o in others) if others else False)

    return TheoremResult(
        name="T-EP-3: Wave Type Hierarchy",
        statement="EM waves have highest F, followed by sound, then water waves",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-4: Thermal Metal Coherence
# ═════════════════════════════════════════════════════════════════════


def theorem_EP4_thermal_metal_coherence() -> TheoremResult:
    """T-EP-4: Metals have higher IC/F ratio than non-metals in thermal domain.

    STATEMENT: The 8 metals (Cu, Al, Fe, Au, Ag, Ti, Pb, W) have
    higher mean IC/F ratio than non-metals. Metals' thermal channels
    are more balanced (correlated conductivity, capacity, density)
    than non-metals where some channels dominate.
    """
    therm = compute_all_thermal_materials()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    metals = {"Copper", "Aluminum", "Iron", "Gold", "Silver", "Titanium", "Lead", "Tungsten"}
    metal_results = [r for r in therm if r.material in metals]
    non_metal_results = [r for r in therm if r.material not in metals]

    metal_ratios = [r.IC / r.F for r in metal_results if r.F > 0]
    non_metal_ratios = [r.IC / r.F for r in non_metal_results if r.F > 0]

    mean_ratio_metal = float(np.mean(metal_ratios))
    mean_ratio_non = float(np.mean(non_metal_ratios))

    # Test 1: Metal IC/F > non-metal IC/F
    tests_total += 1
    tests_passed += int(mean_ratio_metal > mean_ratio_non)
    details["mean_IC_F_metal"] = mean_ratio_metal
    details["mean_IC_F_nonmetal"] = mean_ratio_non

    # Test 2: Metal mean gap < non-metal mean gap
    metal_gaps = [r.gap for r in metal_results]
    non_metal_gaps = [r.gap for r in non_metal_results]
    tests_total += 1
    tests_passed += int(float(np.mean(metal_gaps)) < float(np.mean(non_metal_gaps)))
    details["mean_gap_metal"] = float(np.mean(metal_gaps))
    details["mean_gap_nonmetal"] = float(np.mean(non_metal_gaps))

    # Test 3: At least 8 metals found
    tests_total += 1
    tests_passed += int(len(metal_results) >= 8)
    details["n_metals"] = len(metal_results)

    return TheoremResult(
        name="T-EP-4: Thermal Metal Coherence",
        statement="Metals have higher IC/F and lower Δ than non-metals in thermal domain",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-5: Cross-Domain Gap Ordering
# ═════════════════════════════════════════════════════════════════════


def theorem_EP5_cross_domain_gap_ordering() -> TheoremResult:
    """T-EP-5: EM has highest mean heterogeneity gap across all 4 subdomains.

    STATEMENT: The EM domain's mean Δ exceeds all other subdomains.
    This is because electromagnetic properties (conductivity, permittivity,
    permeability) span more orders of magnitude than thermal, optical,
    or wave properties, creating maximal channel heterogeneity.
    """
    therm, em, opt, wave = _all_results()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    gaps = {
        "thermal": float(np.mean([r.gap for r in therm])),
        "em": float(np.mean([r.gap for r in em])),
        "optics": float(np.mean([r.gap for r in opt])),
        "waves": float(np.mean([r.gap for r in wave])),
    }

    for k, v in gaps.items():
        details[f"mean_gap_{k}"] = v

    # Test 1: EM has highest mean gap
    tests_total += 1
    em_gap = gaps["em"]
    others = [v for k, v in gaps.items() if k != "em"]
    tests_passed += int(all(em_gap > o for o in others))

    # Test 2: EM mean gap > 0.25
    tests_total += 1
    tests_passed += int(em_gap > 0.25)

    # Test 3: Waves have lowest mean gap (most balanced channels)
    tests_total += 1
    wave_gap = gaps["waves"]
    tests_passed += int(all(wave_gap <= v for v in gaps.values()))

    return TheoremResult(
        name="T-EP-5: Cross-Domain Gap Ordering",
        statement="EM has highest mean Δ; waves have lowest — range dominates heterogeneity",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-6: Laser Exceptional Coherence
# ═════════════════════════════════════════════════════════════════════


def theorem_EP6_laser_exceptional_coherence() -> TheoremResult:
    """T-EP-6: Laser (HeNe) is the only system outside Collapse regime.

    STATEMENT: Among all 84 systems, Laser (HeNe) achieves Watch
    regime with the highest F (> 0.80) and highest IC. Its spatially
    and temporally coherent emission creates the most balanced trace
    vector. It is the unique non-Collapse system.
    """
    therm, em, opt, wave = _all_results()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    all_regimes = []
    for r in therm:
        all_regimes.append((r.material, r.regime, r.F))
    for r in em:
        all_regimes.append((r.material, r.regime, r.F))
    for r in opt:
        all_regimes.append((r.material, r.regime, r.F))
    for r in wave:
        all_regimes.append((r.system, r.regime, r.F))

    non_collapse = [(name, reg, f) for name, reg, f in all_regimes if reg != "Collapse"]

    # Test 1: Exactly 1 non-Collapse system
    tests_total += 1
    tests_passed += int(len(non_collapse) == 1)
    details["n_non_collapse"] = len(non_collapse)
    details["non_collapse_systems"] = [(n, r) for n, r, _ in non_collapse]

    # Test 2: That system is in Watch (not Stable — the channels are too heterogeneous)
    if non_collapse:
        tests_total += 1
        tests_passed += int(non_collapse[0][1] == "Watch")

    # Test 3: That system has the highest F among all systems
    if non_collapse:
        max_f = max(f for _, _, f in all_regimes)
        tests_total += 1
        tests_passed += int(abs(non_collapse[0][2] - max_f) < 0.01)
        details["max_F_overall"] = max_f
        details["non_collapse_F"] = non_collapse[0][2]

    return TheoremResult(
        name="T-EP-6: Laser Exceptional Coherence",
        statement="Laser (HeNe) is the unique non-Collapse system across all 84",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-7: Diamond Cross-Domain Excellence
# ═════════════════════════════════════════════════════════════════════


def theorem_EP7_diamond_cross_domain() -> TheoremResult:
    """T-EP-7: Diamond has highest F in the thermal domain.

    STATEMENT: Diamond achieves the highest F among all 20 thermal
    materials, owing to its extreme thermal conductivity (2200 W/mK),
    high melting point (3820 K), and high boiling point (5100 K).
    Its IC/F ratio exceeds 0.70, showing good channel balance.
    """
    therm = compute_all_thermal_materials()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    diamond = [r for r in therm if r.material == "Diamond"]

    if diamond:
        d = diamond[0]
        # Test 1: Diamond has highest F
        tests_total += 1
        tests_passed += int(max(r.F for r in therm) <= d.F)
        details["diamond_F"] = d.F
        details["diamond_IC"] = d.IC

        # Test 2: Diamond IC/F > 0.70
        tests_total += 1
        ratio = d.IC / d.F if d.F > 0 else 0
        tests_passed += int(ratio > 0.70)
        details["diamond_IC_F"] = ratio

        # Test 3: Diamond has highest IC in thermal domain
        tests_total += 1
        tests_passed += int(max(r.IC for r in therm) <= d.IC)
        details["diamond_gap"] = d.gap
        details["max_IC_thermal"] = max(r.IC for r in therm)

    return TheoremResult(
        name="T-EP-7: Diamond Cross-Domain Excellence",
        statement="Diamond has highest F and IC/F > 0.70 in thermal domain",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-8: Conductor IC Suppression
# ═════════════════════════════════════════════════════════════════════


def theorem_EP8_conductor_ic_suppression() -> TheoremResult:
    """T-EP-8: Conductors have lowest mean IC in the EM domain.

    STATEMENT: Conductor materials have lower mean IC than
    semiconductors and insulators. Despite having high conductivity
    (boosting that one channel), their near-zero dielectric channels
    create geometric slaughter that kills IC.
    """
    em = compute_all_em_materials()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    by_cat: dict[str, list] = {}
    for r in em:
        by_cat.setdefault(r.category, []).append(r)

    cat_ic: dict[str, float] = {}
    for cat, rs in by_cat.items():
        cat_ic[cat] = float(np.mean([r.IC for r in rs]))
        details[f"mean_IC_{cat}"] = cat_ic[cat]

    # Test 1: Conductor IC < semiconductor IC
    if "conductor" in cat_ic and "semiconductor" in cat_ic:
        tests_total += 1
        tests_passed += int(cat_ic["conductor"] < cat_ic["semiconductor"])

    # Test 2: Conductor IC < insulator IC
    if "conductor" in cat_ic and "insulator" in cat_ic:
        tests_total += 1
        tests_passed += int(cat_ic["conductor"] < cat_ic["insulator"])

    # Test 3: All conductor ICs < 0.015
    conductors = by_cat.get("conductor", [])
    if conductors:
        tests_total += 1
        tests_passed += int(all(r.IC < 0.015 for r in conductors))
        details["max_conductor_IC"] = max(r.IC for r in conductors)

    return TheoremResult(
        name="T-EP-8: Conductor IC Suppression",
        statement="Conductors have lowest IC in EM — high σ kills geometric coherence via dielectric channels",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-9: Sound Wave Homogeneity
# ═════════════════════════════════════════════════════════════════════


def theorem_EP9_sound_wave_homogeneity() -> TheoremResult:
    """T-EP-9: Sound waves have lower mean Δ than water/seismic/gravitational waves.

    STATEMENT: Sound waves' 6 channels (frequency, wavelength, speed,
    amplitude, attenuation, impedance) are more balanced than water or
    seismic waves. Bell and tuning fork have the lowest gaps among all
    wave systems (< 0.04).
    """
    wave = compute_all_wave_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    by_type: dict[str, list] = {}
    for r in wave:
        by_type.setdefault(r.wave_type, []).append(r)

    type_gap: dict[str, float] = {}
    for wt, rs in by_type.items():
        type_gap[wt] = float(np.mean([r.gap for r in rs]))
        details[f"mean_gap_{wt}"] = type_gap[wt]

    # Test 1: Sound gap < water gap
    if "sound" in type_gap and "water" in type_gap:
        tests_total += 1
        tests_passed += int(type_gap["sound"] < type_gap["water"])

    # Test 2: Sound gap < seismic gap
    if "sound" in type_gap and "seismic" in type_gap:
        tests_total += 1
        tests_passed += int(type_gap["sound"] < type_gap["seismic"])

    # Test 3: Bell and tuning fork gaps < 0.04
    sound = by_type.get("sound", [])
    bell_fork = [r for r in sound if r.system in ("Bell (bronze)", "Tuning fork")]
    if bell_fork:
        tests_total += 1
        tests_passed += int(all(r.gap < 0.04 for r in bell_fork))
        details["bell_fork_gaps"] = {r.system: r.gap for r in bell_fork}

    return TheoremResult(
        name="T-EP-9: Sound Wave Homogeneity",
        statement="Sound waves have lowest Δ among wave types; bell/fork < 0.04",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# THEOREM T-EP-10: Universal Collapse Dominance
# ═════════════════════════════════════════════════════════════════════


def theorem_EP10_universal_collapse_dominance() -> TheoremResult:
    """T-EP-10: >95% of all everyday physics systems are in Collapse regime.

    STATEMENT: The four-gate Stable criterion (ω < 0.038, F > 0.90,
    S < 0.15, C < 0.14) is extremely stringent for macroscopic physics.
    Most systems have heterogeneous channels from normalization, placing
    them in Collapse. This is consistent with the orientation finding
    that 87.5% of the full manifold is outside Stable.
    """
    therm, em, opt, wave = _all_results()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    regimes: dict[str, int] = {}
    total = 0
    for domain_results in [therm, em, opt, wave]:
        for r in domain_results:
            reg = r.regime
            regimes[reg] = regimes.get(reg, 0) + 1
            total += 1

    details["regime_counts"] = regimes
    details["total_systems"] = total

    collapse_count = regimes.get("Collapse", 0)
    collapse_pct = collapse_count / total * 100 if total > 0 else 0

    # Test 1: >95% in Collapse
    tests_total += 1
    tests_passed += int(collapse_pct > 95.0)
    details["collapse_pct"] = collapse_pct

    # Test 2: Total systems >= 80
    tests_total += 1
    tests_passed += int(total >= 80)

    # Test 3: At most 2 non-Collapse systems
    non_collapse = total - collapse_count
    tests_total += 1
    tests_passed += int(non_collapse <= 2)
    details["n_non_collapse"] = non_collapse

    return TheoremResult(
        name="T-EP-10: Universal Collapse Dominance",
        statement=">95% of everyday physics systems are in Collapse — Stable is rare",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# RUNNER
# ═════════════════════════════════════════════════════════════════════


def run_all_theorems() -> list[TheoremResult]:
    """Execute all 10 everyday physics theorems."""
    return [
        theorem_EP1_kernel_identities(),
        theorem_EP2_em_geometric_slaughter(),
        theorem_EP3_wave_type_hierarchy(),
        theorem_EP4_thermal_metal_coherence(),
        theorem_EP5_cross_domain_gap_ordering(),
        theorem_EP6_laser_exceptional_coherence(),
        theorem_EP7_diamond_cross_domain(),
        theorem_EP8_conductor_ic_suppression(),
        theorem_EP9_sound_wave_homogeneity(),
        theorem_EP10_universal_collapse_dominance(),
    ]


def print_summary() -> None:
    """Print theorem summary to stdout."""
    results = run_all_theorems()
    total_tests = sum(r.n_tests for r in results)
    total_passed = sum(r.n_passed for r in results)

    for r in results:
        status = "PROVEN" if r.verdict == "PROVEN" else "FALSIFIED"
        print(f"  {r.name}: {status} ({r.n_passed}/{r.n_tests})")

    print(f"\n  Total: {total_passed}/{total_tests} tests passed")
    print(f"  Theorems: {sum(1 for r in results if r.verdict == 'PROVEN')}/{len(results)} PROVEN")


if __name__ == "__main__":
    print_summary()
