"""Tests for interval discriminant closure (spacetime memory domain).

Validates 12 composition-regime entities, 8-channel trace construction,
Tier-1 kernel identities, and 6 theorems (T-ID-1 through T-ID-6).

The interval discriminant D = F² − IC² encodes the irreducible asymmetry
between arithmetic (F) and geometric (IC) composition — the structural
analog of the metric signature in Einstein's spacetime.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from closures.spacetime_memory.interval_discriminant import (
    ID_CHANNELS,
    ID_ENTITIES,
    N_ID_CHANNELS,
    IDKernelResult,
    compute_all_entities,
    compute_id_kernel,
    verify_all_theorems,
    verify_t_id_1,
    verify_t_id_2,
    verify_t_id_3,
    verify_t_id_4,
    verify_t_id_5,
    verify_t_id_6,
)


@pytest.fixture(scope="module")
def all_results() -> list[IDKernelResult]:
    return compute_all_entities()


class TestEntityCatalog:
    def test_entity_count(self):
        assert len(ID_ENTITIES) == 12

    def test_channel_count(self):
        assert N_ID_CHANNELS == 8
        assert len(ID_CHANNELS) == 8

    def test_all_categories_present(self):
        cats = {e.category for e in ID_ENTITIES}
        assert cats == {"null", "mild", "strong", "extreme"}

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_shape(self, entity):
        assert entity.trace_vector().shape == (8,)

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_bounds(self, entity):
        c = entity.trace_vector()
        assert np.all(c >= 0.0) and np.all(c <= 1.0)


class TestTier1Identities:
    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_duality_identity(self, entity):
        r = compute_id_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_integrity_bound(self, entity):
        r = compute_id_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_log_integrity_relation(self, entity):
        r = compute_id_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10


class TestDiscriminant:
    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_discriminant_non_negative(self, entity):
        r = compute_id_kernel(entity)
        assert r.D >= -1e-15

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_discriminant_factorisation(self, entity):
        r = compute_id_kernel(entity)
        expected = r.delta * (r.F + r.IC)
        assert abs(r.D - expected) < 1e-12

    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_delta_is_gap(self, entity):
        r = compute_id_kernel(entity)
        assert abs(r.delta - (r.F - r.IC)) < 1e-15


class TestTheorems:
    def test_t_id_1(self, all_results):
        assert verify_t_id_1(all_results)["passed"]

    def test_t_id_2(self, all_results):
        assert verify_t_id_2(all_results)["passed"]

    def test_t_id_3(self, all_results):
        assert verify_t_id_3(all_results)["passed"]

    def test_t_id_4(self, all_results):
        assert verify_t_id_4(all_results)["passed"]

    def test_t_id_5(self, all_results):
        assert verify_t_id_5(all_results)["passed"]

    def test_t_id_6(self, all_results):
        assert verify_t_id_6(all_results)["passed"]

    def test_all_theorems_pass(self):
        for t in verify_all_theorems():
            assert t["passed"], f"{t['name']} failed: {t}"


class TestRegimeClassification:
    @pytest.mark.parametrize("entity", ID_ENTITIES, ids=lambda e: e.name)
    def test_regime_is_valid(self, entity):
        r = compute_id_kernel(entity)
        assert r.regime in {"Stable", "Watch", "Collapse"}


class TestTwoChannelReduction:
    """Verify the explicit n=2 formula D = ((c₁ − c₂)/2)²."""

    @pytest.mark.parametrize(
        "c1,c2",
        [
            (0.5, 0.5),
            (0.9, 0.1),
            (0.99, 0.01),
            (0.7, 0.3),
            (0.8, 0.8),
        ],
        ids=lambda p: f"c1={p}" if isinstance(p, float) else None,
    )
    def test_two_channel_formula(self, c1, c2):
        from umcp.kernel_optimized import compute_kernel_outputs

        c = np.array([c1, c2])
        w = np.array([0.5, 0.5])
        out = compute_kernel_outputs(c, w)
        F = float(out["F"])
        IC = float(out["IC"])
        D_kernel = F**2 - IC**2
        D_explicit = ((c1 - c2) / 2.0) ** 2
        assert abs(D_kernel - D_explicit) < 1e-12

    @pytest.mark.parametrize(
        "c1,c2",
        [
            (0.9, 0.1),
            (0.99, 0.01),
            (0.7, 0.3),
        ],
    )
    def test_trace_recovery(self, c1, c2):
        """Verify c₁,₂ = F ± √D recovers the original channels."""
        from umcp.kernel_optimized import compute_kernel_outputs

        c = np.array([c1, c2])
        w = np.array([0.5, 0.5])
        out = compute_kernel_outputs(c, w)
        F = float(out["F"])
        IC = float(out["IC"])
        D = F**2 - IC**2
        c1_rec = F + np.sqrt(D)
        c2_rec = F - np.sqrt(D)
        assert abs(c1_rec - max(c1, c2)) < 1e-10
        assert abs(c2_rec - min(c1, c2)) < 1e-10
