"""Cross-domain bridge test: awareness ↔ consciousness ↔ clinical neuroscience.

Verifies Tier-1 kernel identities hold universally across all three
neuro-domain closures created in the deepening pass:
 • phylogenetic_progression (awareness_cognition): 12 entities
 • anesthesia_dynamics (consciousness_coherence): 12 entities
 • pharmacological_mapping (clinical_neuroscience): 12 entities

Additionally tests cross-domain structural phenomena:
 1. Duality identity F + ω = 1 holds for all 36 entities
 2. Integrity bound IC ≤ F holds for all 36 entities
 3. Log-integrity relation IC = exp(κ) holds for all 36 entities
 4. Geometric slaughter universality: heterogeneity gap > 0 for all entities
 5. Regime distribution: collapse dominates across all three domains
 6. Channel variance (C) discriminates pharmacological from biological systems
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from closures.awareness_cognition.phylogenetic_progression import (
    PP_ENTITIES,
    PPKernelResult,
    compute_pp_kernel,
)
from closures.awareness_cognition.phylogenetic_progression import (
    compute_all_entities as compute_pp,
)
from closures.clinical_neuroscience.pharmacological_mapping import (
    PM_ENTITIES,
    PMKernelResult,
    compute_pm_kernel,
)
from closures.clinical_neuroscience.pharmacological_mapping import (
    compute_all_entities as compute_pm,
)
from closures.consciousness_coherence.anesthesia_dynamics import (
    AD_ENTITIES,
    ADKernelResult,
    compute_ad_kernel,
)
from closures.consciousness_coherence.anesthesia_dynamics import (
    compute_all_entities as compute_ad,
)


@pytest.fixture(scope="module")
def pp_results() -> list[PPKernelResult]:
    return compute_pp()


@pytest.fixture(scope="module")
def ad_results() -> list[ADKernelResult]:
    return compute_ad()


@pytest.fixture(scope="module")
def pm_results() -> list[PMKernelResult]:
    return compute_pm()


@pytest.fixture(scope="module")
def all_triplets(pp_results, ad_results, pm_results):
    """Return (F, omega, IC, kappa, C, S) tuples for all 36 entities."""
    rows = []
    for r in pp_results:
        rows.append((r.F, r.omega, r.IC, r.kappa, r.C, r.S, "phylogenetic", r.name))
    for r in ad_results:
        rows.append((r.F, r.omega, r.IC, r.kappa, r.C, r.S, "anesthesia", r.name))
    for r in pm_results:
        rows.append((r.F, r.omega, r.IC, r.kappa, r.C, r.S, "pharmacological", r.name))
    return rows


# ── Tier-1 Identity Universality ──


class TestDualityUniversal:
    """F + ω = 1 must hold across all three domains."""

    @pytest.mark.parametrize("entity", PP_ENTITIES, ids=lambda e: e.name)
    def test_phylogenetic(self, entity):
        r = compute_pp_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", AD_ENTITIES, ids=lambda e: e.name)
    def test_anesthesia(self, entity):
        r = compute_ad_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", PM_ENTITIES, ids=lambda e: e.name)
    def test_pharmacological(self, entity):
        r = compute_pm_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12


class TestIntegrityBoundUniversal:
    """IC ≤ F must hold across all three domains."""

    @pytest.mark.parametrize("entity", PP_ENTITIES, ids=lambda e: e.name)
    def test_phylogenetic(self, entity):
        r = compute_pp_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", AD_ENTITIES, ids=lambda e: e.name)
    def test_anesthesia(self, entity):
        r = compute_ad_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", PM_ENTITIES, ids=lambda e: e.name)
    def test_pharmacological(self, entity):
        r = compute_pm_kernel(entity)
        assert r.IC <= r.F + 1e-12


class TestLogIntegrityUniversal:
    """IC = exp(κ) must hold across all three domains."""

    @pytest.mark.parametrize("entity", PP_ENTITIES, ids=lambda e: e.name)
    def test_phylogenetic(self, entity):
        r = compute_pp_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10

    @pytest.mark.parametrize("entity", AD_ENTITIES, ids=lambda e: e.name)
    def test_anesthesia(self, entity):
        r = compute_ad_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10

    @pytest.mark.parametrize("entity", PM_ENTITIES, ids=lambda e: e.name)
    def test_pharmacological(self, entity):
        r = compute_pm_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10


# ── Cross-Domain Structural Phenomena ──


class TestGeometricSlaughter:
    """Heterogeneity gap Δ = F − IC > 0 for all entities across all domains."""

    def test_all_gaps_positive(self, all_triplets):
        for F, _omega, IC, _kappa, _C, _S, domain, name in all_triplets:
            gap = F - IC
            assert gap >= -1e-12, f"{domain}/{name}: Δ = {gap}"

    def test_mean_gap_per_domain(self, pp_results, ad_results, pm_results):
        """Each domain has nonzero mean heterogeneity gap."""
        for label, results in [
            ("phylogenetic", pp_results),
            ("anesthesia", ad_results),
            ("pharmacological", pm_results),
        ]:
            gaps = [r.F - r.IC for r in results]
            assert np.mean(gaps) > 0, f"{label} mean gap = {np.mean(gaps)}"


class TestRegimeDistribution:
    """Collapse regime dominates all three neuro-domains."""

    def test_collapse_majority(self, pp_results, ad_results, pm_results):
        for label, results in [
            ("phylogenetic", pp_results),
            ("anesthesia", ad_results),
            ("pharmacological", pm_results),
        ]:
            collapse_frac = sum(1 for r in results if r.regime == "Collapse") / len(results)
            assert collapse_frac >= 0.5, f"{label}: {collapse_frac:.1%} Collapse"


class TestCurvatureDiscrimination:
    """Curvature C differs structurally across domain types.

    Pharmacological agents (designed for selectivity) → high C.
    Phylogenetic entities (evolved for integration) → C varies with era.
    """

    def test_pharmacological_mean_C_above_threshold(self, pm_results):
        mean_C = np.mean([r.C for r in pm_results])
        assert mean_C > 0.2, f"Pharma mean C = {mean_C}"

    def test_phylogenetic_C_range(self, pp_results):
        Cs = [r.C for r in pp_results]
        assert max(Cs) - min(Cs) > 0.1, f"Phylo C range = {max(Cs) - min(Cs)}"


class TestFidelityRange:
    """Fidelity F spans different ranges across domains, reflecting
    different channel-space characteristics."""

    def test_phylogenetic_spans_wide_F_range(self, pp_results):
        Fs = [r.F for r in pp_results]
        assert max(Fs) - min(Fs) > 0.5, f"PP F range: {min(Fs):.3f}–{max(Fs):.3f}"

    def test_pharmacological_concentrated_F(self, pm_results):
        Fs = [r.F for r in pm_results]
        # All drugs have moderate-to-low F (few channels near 1.0)
        assert max(Fs) < 0.5, f"PM max F = {max(Fs):.3f}"

    def test_anesthesia_spans_moderate_range(self, ad_results):
        Fs = [r.F for r in ad_results]
        assert max(Fs) - min(Fs) > 0.3, f"AD F range: {min(Fs):.3f}–{max(Fs):.3f}"
