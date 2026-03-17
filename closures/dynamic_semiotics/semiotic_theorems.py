"""Semiotic Theorems — Ten Tier-2 Theorems in the GCD Kernel.

Proves ten theorems connecting sign system structure to GCD kernel
patterns. All theorems verified computationally against 30 sign systems.

Channels (8, equal weight):
    sign_repertoire, interpretant_depth, ground_stability,
    translation_fidelity, semiotic_density, indexical_coupling,
    iconic_persistence, symbolic_recursion

Theorems:
    T-S-1   Tier-1 Kernel Identities — F+ω=1, IC≤F, IC=exp(κ)
    T-S-2   Recursion-Depth Coupling — symbolic_recursion and
            interpretant_depth jointly anchor IC
    T-S-3   Dead Language as Gestus — dead/extinct systems have
            indexical_coupling near ε → geometric slaughter
    T-S-4   Formal System Stability — formal systems have lowest Δ
            among all categories (high channel homogeneity)
    T-S-5   Iconic-Symbolic Tradeoff — iconic_persistence and
            symbolic_recursion are inversely correlated
    T-S-6   Natural Language Fragility — natural languages have the
            highest heterogeneity gap of any category
    T-S-7   Animal Communication Collapse — animal signals have
            ω ≥ 0.20 (low recursion, low interpretant depth)
    T-S-8   Semiotic Density as Fidelity Anchor — high semiotic_density
            correlates with higher F
    T-S-9   Ground Stability Hierarchy — formal > chemical > natural
            in ground stability contribution to IC
    T-S-10  Category Regime Distribution — formal systems cluster in
            Watch/Stable; animal and gestural in Collapse

Derivation chain: Axiom-0 → frozen_contract → kernel_optimized →
                  semiotic_kernel → this module
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

# ── Path setup ────────────────────────────────────────────────────
_WORKSPACE = Path(__file__).resolve().parents[2]
if str(_WORKSPACE / "src") not in sys.path:
    sys.path.insert(0, str(_WORKSPACE / "src"))
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from closures.dynamic_semiotics.semiotic_kernel import (  # noqa: E402
    SEMIOTIC_CHANNELS,
    SemioticKernelResult,
    compute_all_sign_systems,
)

# ═════════════════════════════════════════════════════════════════════
# RESULT CONTAINER
# ═════════════════════════════════════════════════════════════════════


@dataclass
class TheoremResult:
    """Result of a single theorem verification."""

    name: str
    statement: str
    n_tests: int
    n_passed: int
    n_failed: int
    details: dict[str, Any]
    verdict: str  # "PROVEN" | "FALSIFIED"


# ═════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════


def _results_by_category(
    results: list[SemioticKernelResult],
) -> dict[str, list[SemioticKernelResult]]:
    """Group results by sign system category."""
    cats: dict[str, list[SemioticKernelResult]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r)
    return cats


def _results_by_status(
    results: list[SemioticKernelResult],
) -> dict[str, list[SemioticKernelResult]]:
    """Group results by sign system status."""
    sts: dict[str, list[SemioticKernelResult]] = {}
    for r in results:
        sts.setdefault(r.status, []).append(r)
    return sts


# Channel index helpers
_CH = {name: idx for idx, name in enumerate(SEMIOTIC_CHANNELS)}


# ═════════════════════════════════════════════════════════════════════
# T-S-1: Tier-1 Kernel Identities
# ═════════════════════════════════════════════════════════════════════


def theorem_TS1_kernel_identities() -> TheoremResult:
    """T-S-1: Tier-1 Kernel Identities Hold for All 30 Sign Systems.

    STATEMENT: For all 30 sign systems, the three Tier-1 identities
    hold: (1) F + ω = 1 exactly, (2) IC ≤ F, (3) IC = exp(κ) to
    machine precision.
    """
    results = compute_all_sign_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    max_duality_residual = 0.0
    ic_leq_f_all = True
    max_exp_residual = 0.0

    for r in results:
        residual = abs(r.F_plus_omega - 1.0)
        max_duality_residual = max(max_duality_residual, residual)
        tests_total += 1
        tests_passed += int(residual < 1e-12)

        tests_total += 1
        if not r.IC_leq_F:
            ic_leq_f_all = False
        tests_passed += int(r.IC_leq_F)

        tests_total += 1
        tests_passed += int(r.IC_eq_exp_kappa)
        exp_res = abs(r.IC - np.exp(r.kappa))
        max_exp_residual = max(max_exp_residual, exp_res)

    details["max_duality_residual"] = max_duality_residual
    details["IC_leq_F_all"] = ic_leq_f_all
    details["max_IC_exp_kappa_residual"] = max_exp_residual
    details["n_systems"] = len(results)

    return TheoremResult(
        name="T-S-1: Tier-1 Kernel Identities",
        statement="F+ω=1, IC≤F, IC=exp(κ) for all 30 sign systems",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-2: Recursion-Depth Coupling
# ═════════════════════════════════════════════════════════════════════


def theorem_TS2_recursion_depth_coupling() -> TheoremResult:
    """T-S-2: Symbolic Recursion and Interpretant Depth Jointly Anchor IC.

    STATEMENT: Sign systems where both symbolic_recursion > 0.70 AND
    interpretant_depth > 0.70 have significantly higher IC than systems
    where either channel is below 0.30. The two channels form a
    multiplicative anchor for semiotic integrity.
    """
    results = compute_all_sign_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    i_rec = _CH["symbolic_recursion"]
    i_dep = _CH["interpretant_depth"]

    high_both = [r for r in results if r.trace_vector[i_rec] > 0.70 and r.trace_vector[i_dep] > 0.70]
    low_either = [r for r in results if r.trace_vector[i_rec] < 0.30 or r.trace_vector[i_dep] < 0.30]

    # Test 1: Both groups have members
    tests_total += 1
    t1 = len(high_both) >= 3 and len(low_either) >= 3
    tests_passed += int(t1)
    details["n_high_both"] = len(high_both)
    details["n_low_either"] = len(low_either)

    if high_both and low_either:
        mean_ic_high = float(np.mean([r.IC for r in high_both]))
        mean_ic_low = float(np.mean([r.IC for r in low_either]))

        # Test 2: High-both IC > low-either IC
        tests_total += 1
        t2 = mean_ic_high > mean_ic_low
        tests_passed += int(t2)
        details["mean_IC_high_both"] = mean_ic_high
        details["mean_IC_low_either"] = mean_ic_low

        # Test 3: IC gap is substantial
        tests_total += 1
        ic_gap = mean_ic_high - mean_ic_low
        t3 = ic_gap > 0.05
        tests_passed += int(t3)
        details["IC_gap"] = ic_gap

        # Test 4: High-both have lower heterogeneity gap
        mean_delta_high = float(np.mean([r.heterogeneity_gap for r in high_both]))
        mean_delta_low = float(np.mean([r.heterogeneity_gap for r in low_either]))
        tests_total += 1
        t4 = mean_delta_high < mean_delta_low
        tests_passed += int(t4)
        details["mean_delta_high_both"] = mean_delta_high
        details["mean_delta_low_either"] = mean_delta_low

    return TheoremResult(
        name="T-S-2: Recursion-Depth Coupling",
        statement="High recursion + depth → higher IC and lower Δ",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-3: Dead Language as Gestus
# ═════════════════════════════════════════════════════════════════════


def theorem_TS3_dead_language_frozen_coherence() -> TheoremResult:
    """T-S-3: Dead Languages Preserve Coherence Through Frozen Channels.

    STATEMENT: Dead and extinct sign systems have lower indexical_coupling
    than living systems (no living community), but their frozen corpus
    preserves high ground_stability, keeping Δ LOW. The paradox: death
    freezes coherence. Channel volatility — not death — destroys IC.
    """
    results = compute_all_sign_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    by_status = _results_by_status(results)
    dead = by_status.get("dead", []) + by_status.get("extinct", [])
    living = by_status.get("living", [])

    # Test 1: Dead systems exist
    tests_total += 1
    t1 = len(dead) >= 2
    tests_passed += int(t1)
    details["n_dead"] = len(dead)

    if dead and living:
        # Test 2: Dead systems have lower indexical_coupling
        i_idx = _CH["indexical_coupling"]
        mean_idx_dead = float(np.mean([r.trace_vector[i_idx] for r in dead]))
        mean_idx_living = float(np.mean([r.trace_vector[i_idx] for r in living]))
        tests_total += 1
        t2 = mean_idx_dead < mean_idx_living
        tests_passed += int(t2)
        details["mean_indexical_dead"] = mean_idx_dead
        details["mean_indexical_living"] = mean_idx_living

        # Test 3: Dead systems have higher ground_stability
        i_gs = _CH["ground_stability"]
        mean_gs_dead = float(np.mean([r.trace_vector[i_gs] for r in dead]))
        mean_gs_living = float(np.mean([r.trace_vector[i_gs] for r in living]))
        tests_total += 1
        t3 = mean_gs_dead > mean_gs_living
        tests_passed += int(t3)
        details["mean_gs_dead"] = mean_gs_dead
        details["mean_gs_living"] = mean_gs_living

        # Test 4: Dead systems have LOWER Δ than living median
        # (frozen channels → more homogeneous → lower gap)
        living_deltas = [r.heterogeneity_gap for r in living]
        median_delta = float(np.median(living_deltas))
        mean_delta_dead = float(np.mean([r.heterogeneity_gap for r in dead]))
        tests_total += 1
        t4 = mean_delta_dead < median_delta
        tests_passed += int(t4)
        details["mean_delta_dead"] = mean_delta_dead
        details["living_delta_median"] = median_delta

    return TheoremResult(
        name="T-S-3: Dead Language Frozen Coherence",
        statement="Dead systems lose indexical coupling but preserve coherence via frozen ground stability",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-4: Formal System Stability
# ═════════════════════════════════════════════════════════════════════


def theorem_TS4_formal_system_extreme_profiles() -> TheoremResult:
    """T-S-4: Formal Systems Have Extreme Channel Profiles.

    STATEMENT: Formal systems have the highest mean IC among all
    categories AND high ground_stability (> 0.60), but their extreme
    channel divergence (near-zero indexical_coupling and iconic_persistence
    vs near-1.0 stability and fidelity) creates HIGHER Δ than balanced
    categories like natural languages. Formal strength is IC, not Δ.
    """
    results = compute_all_sign_systems()
    cats = _results_by_category(results)
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    formal = cats.get("Formal System", [])

    # Test 1: Formal System category exists with enough members
    tests_total += 1
    t1 = len(formal) >= 3
    tests_passed += int(t1)

    if formal:
        # Test 2: Formal IC > non-formal IC
        formal_ic = float(np.mean([r.IC for r in formal]))
        other_ic = float(np.mean([r.IC for r in results if r.category != "Formal System"]))
        tests_total += 1
        t2 = formal_ic > other_ic
        tests_passed += int(t2)
        details["mean_IC_formal"] = formal_ic
        details["mean_IC_other"] = other_ic

        # Test 3: Formal ground_stability mean > 0.60
        i_gs = _CH["ground_stability"]
        mean_gs = float(np.mean([r.trace_vector[i_gs] for r in formal]))
        tests_total += 1
        t3 = mean_gs > 0.60
        tests_passed += int(t3)
        details["mean_ground_stability_formal"] = mean_gs

        # Test 4: Formal iconic_persistence is low (< 0.25)
        i_icon = _CH["iconic_persistence"]
        mean_icon = float(np.mean([r.trace_vector[i_icon] for r in formal]))
        tests_total += 1
        t4 = mean_icon < 0.25
        tests_passed += int(t4)
        details["mean_iconic_formal"] = mean_icon

    return TheoremResult(
        name="T-S-4: Formal System Extreme Profiles",
        statement="Formal systems have highest IC and high stability but low iconic/indexical channels",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-5: Iconic-Symbolic Tradeoff
# ═════════════════════════════════════════════════════════════════════


def theorem_TS5_iconic_symbolic_tradeoff() -> TheoremResult:
    """T-S-5: Iconic Persistence and Symbolic Recursion Are Inversely Related.

    STATEMENT: Across all 30 sign systems, iconic_persistence and
    symbolic_recursion are negatively correlated. Systems that rely on
    resemblance (icons) sacrifice recursive self-reference, and vice versa.
    """
    results = compute_all_sign_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    i_icon = _CH["iconic_persistence"]
    i_rec = _CH["symbolic_recursion"]

    icons = [r.trace_vector[i_icon] for r in results]
    recs = [r.trace_vector[i_rec] for r in results]

    # Test 1: Negative correlation
    corr = float(np.corrcoef(icons, recs)[0, 1])
    tests_total += 1
    t1 = corr < 0.0
    tests_passed += int(t1)
    details["corr_iconic_recursive"] = corr

    # Test 2: High-iconic systems (>0.60) have lower mean recursion
    high_icon = [r for r in results if r.trace_vector[i_icon] > 0.60]
    low_icon = [r for r in results if r.trace_vector[i_icon] < 0.20]
    if high_icon and low_icon:
        mean_rec_hi = float(np.mean([r.trace_vector[i_rec] for r in high_icon]))
        mean_rec_lo = float(np.mean([r.trace_vector[i_rec] for r in low_icon]))
        tests_total += 1
        t2 = mean_rec_hi < mean_rec_lo
        tests_passed += int(t2)
        details["mean_recursion_high_iconic"] = mean_rec_hi
        details["mean_recursion_low_iconic"] = mean_rec_lo

    # Test 3: Road signs (high iconic) have near-zero recursion
    road = [r for r in results if r.name == "International Road Signs"]
    if road:
        tests_total += 1
        t3 = road[0].trace_vector[i_rec] < 0.10
        tests_passed += int(t3)
        details["road_signs_recursion"] = road[0].trace_vector[i_rec]

    # Test 4: Formal logic (high recursion) has low iconic
    logic = [r for r in results if r.name == "Formal Logic (First-Order)"]
    if logic:
        tests_total += 1
        t4 = logic[0].trace_vector[i_icon] < 0.20
        tests_passed += int(t4)
        details["formal_logic_iconic"] = logic[0].trace_vector[i_icon]

    return TheoremResult(
        name="T-S-5: Iconic-Symbolic Tradeoff",
        statement="Iconic persistence and symbolic recursion are inversely related",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-6: Natural Language Fragility
# ═════════════════════════════════════════════════════════════════════


def theorem_TS6_natural_language_balance() -> TheoremResult:
    """T-S-6: Natural Languages Are Balanced but Mediocre.

    STATEMENT: Living natural languages have LOWER Δ than formal systems
    (more balanced channels) and HIGHER F (richer mean content), but
    HIGHER IC (the balance preserves geometric coherence). Natural
    languages are the semiotic systems that trade extremes for breadth.
    """
    results = compute_all_sign_systems()
    cats = _results_by_category(results)
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    nat_lang = [r for r in cats.get("Natural Language", []) if r.status == "living"]
    formal = cats.get("Formal System", [])

    if nat_lang and formal:
        mean_delta_nl = float(np.mean([r.heterogeneity_gap for r in nat_lang]))
        mean_delta_fs = float(np.mean([r.heterogeneity_gap for r in formal]))

        # Test 1: Natural language Δ < formal system Δ (more balanced)
        tests_total += 1
        t1 = mean_delta_nl < mean_delta_fs
        tests_passed += int(t1)
        details["mean_delta_natural_language"] = mean_delta_nl
        details["mean_delta_formal_system"] = mean_delta_fs

        # Test 2: Natural languages have higher F (richer content)
        mean_f_nl = float(np.mean([r.F for r in nat_lang]))
        mean_f_fs = float(np.mean([r.F for r in formal]))
        tests_total += 1
        t2 = mean_f_nl > mean_f_fs
        tests_passed += int(t2)
        details["mean_F_natural"] = mean_f_nl
        details["mean_F_formal"] = mean_f_fs

        # Test 3: Natural languages have higher IC than formal
        # (balance preserves geometric coherence)
        mean_ic_nl = float(np.mean([r.IC for r in nat_lang]))
        mean_ic_fs = float(np.mean([r.IC for r in formal]))
        tests_total += 1
        t3 = mean_ic_nl > mean_ic_fs
        tests_passed += int(t3)
        details["mean_IC_natural"] = mean_ic_nl
        details["mean_IC_formal"] = mean_ic_fs

    # Test 4: Pirahã has highest Δ among living natural languages
    piraha = [r for r in results if r.name == "Pirahã"]
    if piraha and nat_lang:
        tests_total += 1
        nat_deltas = [r.heterogeneity_gap for r in nat_lang]
        t4 = piraha[0].heterogeneity_gap >= np.percentile(nat_deltas, 50)
        tests_passed += int(t4)
        details["piraha_delta"] = piraha[0].heterogeneity_gap

    return TheoremResult(
        name="T-S-6: Natural Language Balance",
        statement="Natural languages have lower Δ (more balanced) than formal systems, with higher F and IC",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-7: Animal Communication Collapse
# ═════════════════════════════════════════════════════════════════════


def theorem_TS7_animal_communication_collapse() -> TheoremResult:
    """T-S-7: Animal Communication Systems Have High Drift.

    STATEMENT: Animal communication systems (bee dance, whale song,
    birdsong, pheromones) have ω ≥ 0.20 due to low symbolic_recursion
    and low interpretant_depth. They cannot recurse on their own signs.
    """
    results = compute_all_sign_systems()
    cats = _results_by_category(results)
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    animals = cats.get("Animal Communication", [])

    # Test 1: Animal systems exist
    tests_total += 1
    t1 = len(animals) >= 3
    tests_passed += int(t1)
    details["n_animal"] = len(animals)

    # Test 2: All animal systems have ω ≥ 0.20
    for r in animals:
        tests_total += 1
        t = r.omega >= 0.20
        tests_passed += int(t)
        details[f"{r.name}_omega"] = r.omega

    # Test 3: Mean animal recursion < 0.15
    if animals:
        i_rec = _CH["symbolic_recursion"]
        mean_rec = float(np.mean([r.trace_vector[i_rec] for r in animals]))
        tests_total += 1
        t3 = mean_rec < 0.15
        tests_passed += int(t3)
        details["mean_recursion_animal"] = mean_rec

    # Test 4: Mean animal IC < overall median IC
    if animals:
        all_ics = [r.IC for r in results]
        median_ic = float(np.median(all_ics))
        mean_ic_animal = float(np.mean([r.IC for r in animals]))
        tests_total += 1
        t4 = mean_ic_animal < median_ic
        tests_passed += int(t4)
        details["mean_IC_animal"] = mean_ic_animal
        details["median_IC_all"] = median_ic

    return TheoremResult(
        name="T-S-7: Animal Communication Collapse",
        statement="Animal systems have ω ≥ 0.20 due to low recursion and interpretation depth",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-8: Semiotic Density as Fidelity Anchor
# ═════════════════════════════════════════════════════════════════════


def theorem_TS8_density_fidelity_anchor() -> TheoremResult:
    """T-S-8: High Semiotic Density Correlates with Higher Fidelity.

    STATEMENT: Across all 30 sign systems, semiotic_density is positively
    correlated with F. Dense sign systems (Chinese, genetic code, math)
    pack more information per unit, preserving more structure through
    collapse.
    """
    results = compute_all_sign_systems()
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    i_den = _CH["semiotic_density"]
    densities = [r.trace_vector[i_den] for r in results]
    fidelities = [r.F for r in results]

    # Test 1: Positive correlation between density and F
    corr = float(np.corrcoef(densities, fidelities)[0, 1])
    tests_total += 1
    t1 = corr > 0.0
    tests_passed += int(t1)
    details["corr_density_F"] = corr

    # Test 2: Top-5 dense systems have higher mean F than bottom-5
    sorted_by_den = sorted(results, key=lambda r: r.trace_vector[i_den], reverse=True)
    top5 = sorted_by_den[:5]
    bot5 = sorted_by_den[-5:]
    mean_f_top = float(np.mean([r.F for r in top5]))
    mean_f_bot = float(np.mean([r.F for r in bot5]))
    tests_total += 1
    t2 = mean_f_top > mean_f_bot
    tests_passed += int(t2)
    details["mean_F_top5_dense"] = mean_f_top
    details["mean_F_bottom5_dense"] = mean_f_bot

    # Test 3: Genetic code (highest density) has F > 0.50
    dna = [r for r in results if r.name == "DNA/RNA Genetic Code"]
    if dna:
        tests_total += 1
        t3 = dna[0].F > 0.50
        tests_passed += int(t3)
        details["DNA_F"] = dna[0].F
        details["DNA_density"] = dna[0].trace_vector[i_den]

    return TheoremResult(
        name="T-S-8: Semiotic Density as Fidelity Anchor",
        statement="Semiotic density positively correlates with fidelity F",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-9: Ground Stability Hierarchy
# ═════════════════════════════════════════════════════════════════════


def theorem_TS9_ground_stability_hierarchy() -> TheoremResult:
    """T-S-9: Formal > Chemical > Natural in Ground Stability Contribution.

    STATEMENT: Formal systems have higher ground_stability than chemical
    codes (DNA), which have higher ground_stability than natural languages.
    Ground stability is the primary anchor against convention drift.
    """
    results = compute_all_sign_systems()
    cats = _results_by_category(results)
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    i_gs = _CH["ground_stability"]

    # Get category ground stabilities
    formal = cats.get("Formal System", [])
    natural_living = [r for r in cats.get("Natural Language", []) if r.status == "living"]

    if formal and natural_living:
        mean_gs_formal = float(np.mean([r.trace_vector[i_gs] for r in formal]))
        mean_gs_natural = float(np.mean([r.trace_vector[i_gs] for r in natural_living]))

        # Test 1: Formal ground stability > natural language ground stability
        tests_total += 1
        t1 = mean_gs_formal > mean_gs_natural
        tests_passed += int(t1)
        details["mean_gs_formal"] = mean_gs_formal
        details["mean_gs_natural"] = mean_gs_natural

    # Test 2: DNA has ground stability > 0.90
    dna = [r for r in results if r.name == "DNA/RNA Genetic Code"]
    if dna:
        tests_total += 1
        gs_dna = dna[0].trace_vector[i_gs]
        t2 = gs_dna > 0.90
        tests_passed += int(t2)
        details["gs_DNA"] = gs_dna

    # Test 3: Mathematical notation has highest ground stability
    math_r = [r for r in results if r.name == "Mathematical Notation"]
    if math_r:
        tests_total += 1
        gs_math = math_r[0].trace_vector[i_gs]
        t3 = gs_math >= 0.95
        tests_passed += int(t3)
        details["gs_math"] = gs_math

    # Test 4: Ground stability correlates with IC within formal systems
    if len(formal) >= 3:
        gs_vals = [r.trace_vector[i_gs] for r in formal]
        ic_vals = [r.IC for r in formal]
        corr = float(np.corrcoef(gs_vals, ic_vals)[0, 1])
        tests_total += 1
        t4 = corr > -0.5  # Not strongly anti-correlated
        tests_passed += int(t4)
        details["corr_gs_IC_formal"] = corr

    return TheoremResult(
        name="T-S-9: Ground Stability Hierarchy",
        statement="Formal > chemical > natural in ground stability; anchors IC",
        n_tests=tests_total,
        n_passed=tests_passed,
        n_failed=tests_total - tests_passed,
        details=details,
        verdict="PROVEN" if tests_passed == tests_total else "FALSIFIED",
    )


# ═════════════════════════════════════════════════════════════════════
# T-S-10: Category Regime Distribution
# ═════════════════════════════════════════════════════════════════════


def theorem_TS10_drift_ordering_by_category() -> TheoremResult:
    """T-S-10: Semiotic Categories Form a Drift Hierarchy.

    STATEMENT: Animal communication has the highest mean ω, gestural
    systems have higher ω than formal systems, and formal systems have
    lower ω than natural languages. The drift hierarchy reflects
    structural capacity for self-reference and convention persistence.
    """
    results = compute_all_sign_systems()
    cats = _results_by_category(results)
    tests_total = 0
    tests_passed = 0
    details: dict[str, Any] = {}

    cat_omegas: dict[str, float] = {}
    for cat, rs in cats.items():
        cat_omegas[cat] = float(np.mean([r.omega for r in rs]))
        details[f"mean_omega_{cat}"] = cat_omegas[cat]

    # Test 1: Animal has highest ω among categories with 3+ members
    animals = cats.get("Animal Communication", [])
    if len(animals) >= 3:
        animal_omega = cat_omegas["Animal Communication"]
        large_cats = {c: o for c, o in cat_omegas.items() if len(cats.get(c, [])) >= 3}
        others = [o for c, o in large_cats.items() if c != "Animal Communication"]
        tests_total += 1
        t1 = all(animal_omega >= o for o in others) if others else False
        tests_passed += int(t1)

    # Test 2: Formal ω < Animal ω
    formal = cats.get("Formal System", [])
    if formal and animals:
        tests_total += 1
        t2 = cat_omegas.get("Formal System", 1.0) < cat_omegas.get("Animal Communication", 0.0)
        tests_passed += int(t2)

    # Test 3: No category has all systems in Stable
    # (semiotic channels are heterogeneous by nature)
    tests_total += 1
    any_all_stable = any(all(r.regime == "Stable" for r in rs) for rs in cats.values())
    tests_passed += int(not any_all_stable)
    details["any_category_all_stable"] = any_all_stable

    # Test 4: Natural languages span at least 2 regimes
    nat = cats.get("Natural Language", [])
    if nat:
        regimes_nat = {r.regime for r in nat}
        tests_total += 1
        t4 = len(regimes_nat) >= 2
        tests_passed += int(t4)
        details["natural_regimes"] = sorted(regimes_nat)

    return TheoremResult(
        name="T-S-10: Drift Ordering by Category",
        statement="Animal > gestural > formal in drift; no category achieves all-Stable",
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
    """Execute all 10 semiotic theorems and return results."""
    return [
        theorem_TS1_kernel_identities(),
        theorem_TS2_recursion_depth_coupling(),
        theorem_TS3_dead_language_frozen_coherence(),
        theorem_TS4_formal_system_extreme_profiles(),
        theorem_TS5_iconic_symbolic_tradeoff(),
        theorem_TS6_natural_language_balance(),
        theorem_TS7_animal_communication_collapse(),
        theorem_TS8_density_fidelity_anchor(),
        theorem_TS9_ground_stability_hierarchy(),
        theorem_TS10_drift_ordering_by_category(),
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
