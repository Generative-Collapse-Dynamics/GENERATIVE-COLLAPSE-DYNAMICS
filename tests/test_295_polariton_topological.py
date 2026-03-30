"""Tests for polariton topological photonics closure (quantum mechanics domain).

Validates 12 entities, 8-channel trace construction,
Tier-1 kernel identities, and 6 theorems (T-PTP-1 through T-PTP-6).

Motivated by Widmann et al. Nat. Commun. 17 (2026): artificial gauge
fields create topological, non-reciprocal edge transport in a polariton
Hofstadter ladder without strong magnetic fields.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from closures.quantum_mechanics.polariton_topological_photonics import (
    N_PTP_CHANNELS,
    PTP_CHANNELS,
    PTP_ENTITIES,
    PTPKernelResult,
    compute_all_entities,
    compute_ptp_kernel,
    verify_all_theorems,
    verify_t_ptp_1,
    verify_t_ptp_2,
    verify_t_ptp_3,
    verify_t_ptp_4,
    verify_t_ptp_5,
    verify_t_ptp_6,
)


@pytest.fixture(scope="module")
def all_results() -> list[PTPKernelResult]:
    return compute_all_entities()


# ---------------------------------------------------------------------------
# Entity catalog structure tests
# ---------------------------------------------------------------------------


class TestEntityCatalog:
    def test_entity_count(self):
        assert len(PTP_ENTITIES) == 12

    def test_channel_count(self):
        assert N_PTP_CHANNELS == 8
        assert len(PTP_CHANNELS) == 8

    def test_all_categories_present(self):
        cats = {e.category for e in PTP_ENTITIES}
        assert cats == {"extreme", "topological", "transitional", "trivial"}

    def test_category_counts(self):
        cats: dict[str, int] = {}
        for e in PTP_ENTITIES:
            cats[e.category] = cats.get(e.category, 0) + 1
        assert cats == {
            "topological": 3,
            "trivial": 3,
            "transitional": 4,
            "extreme": 2,
        }

    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_shape(self, entity):
        assert entity.trace_vector().shape == (8,)

    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_bounds(self, entity):
        c = entity.trace_vector()
        assert np.all(c >= 0.0) and np.all(c <= 1.0)

    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_unique_names(self, entity):
        names = [e.name for e in PTP_ENTITIES]
        assert names.count(entity.name) == 1


# ---------------------------------------------------------------------------
# Tier-1 kernel identity tests (F + ω = 1, IC ≤ F, IC = exp(κ))
# ---------------------------------------------------------------------------


class TestTier1Identities:
    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_duality_identity(self, entity):
        r = compute_ptp_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_integrity_bound(self, entity):
        r = compute_ptp_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", PTP_ENTITIES, ids=lambda e: e.name)
    def test_log_integrity_relation(self, entity):
        r = compute_ptp_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10


# ---------------------------------------------------------------------------
# Theorem tests
# ---------------------------------------------------------------------------


class TestTheorems:
    def test_t_ptp_1(self, all_results):
        res = verify_t_ptp_1(all_results)
        assert res["passed"], f"T-PTP-1 failed: {res}"

    def test_t_ptp_2(self, all_results):
        res = verify_t_ptp_2(all_results)
        assert res["passed"], f"T-PTP-2 failed: {res}"

    def test_t_ptp_3(self, all_results):
        res = verify_t_ptp_3(all_results)
        assert res["passed"], f"T-PTP-3 failed: {res}"

    def test_t_ptp_4(self, all_results):
        res = verify_t_ptp_4(all_results)
        assert res["passed"], f"T-PTP-4 failed: {res}"

    def test_t_ptp_5(self, all_results):
        res = verify_t_ptp_5(all_results)
        assert res["passed"], f"T-PTP-5 failed: {res}"

    def test_t_ptp_6(self, all_results):
        res = verify_t_ptp_6(all_results)
        assert res["passed"], f"T-PTP-6 failed: {res}"

    def test_verify_all_theorems(self):
        results = verify_all_theorems()
        assert len(results) == 6
        for t in results:
            assert t["passed"], f"{t['name']} failed: {t}"


# ---------------------------------------------------------------------------
# Structural tests
# ---------------------------------------------------------------------------


class TestStructural:
    def test_topological_entities_watch_regime(self, all_results):
        topo = [r for r in all_results if r.category == "topological"]
        for r in topo:
            assert r.regime == "Watch", f"{r.name} in {r.regime}, expected Watch"

    def test_trivial_entities_collapse_regime(self, all_results):
        triv = [r for r in all_results if r.category == "trivial"]
        for r in triv:
            assert r.regime == "Collapse", f"{r.name} in {r.regime}, expected Collapse"

    def test_maximum_nonreciprocity_highest_f(self, all_results):
        max_nr = next(r for r in all_results if r.name == "Maximum_nonreciprocity")
        assert max(r.F for r in all_results) == max_nr.F

    def test_decoherence_lowest_ic_f(self, all_results):
        deco = next(r for r in all_results if r.name == "Decoherence_collapsed")
        non_triv = [r for r in all_results if r.category != "trivial"]
        deco_icf = deco.IC / deco.F
        for r in non_triv:
            if r.name != "Decoherence_collapsed":
                assert deco_icf < r.IC / r.F

    def test_at_least_two_regimes(self, all_results):
        regimes = {r.regime for r in all_results}
        assert len(regimes) >= 2

    def test_all_results_have_to_dict(self, all_results):
        for r in all_results:
            d = r.to_dict()
            assert "F" in d and "omega" in d and "IC" in d

    def test_channels_match_expected(self):
        assert PTP_CHANNELS == [
            "gauge_flux",
            "polarization_splitting",
            "non_reciprocity",
            "winding_number",
            "edge_localization",
            "polariton_coherence",
            "coupling_ratio",
            "detuning",
        ]

    def test_kernel_result_fields(self, all_results):
        for r in all_results:
            assert hasattr(r, "F")
            assert hasattr(r, "omega")
            assert hasattr(r, "S")
            assert hasattr(r, "C")
            assert hasattr(r, "kappa")
            assert hasattr(r, "IC")
            assert hasattr(r, "regime")
