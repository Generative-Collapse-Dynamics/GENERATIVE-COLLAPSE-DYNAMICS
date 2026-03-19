"""Tests for molecular evolution closure (evolution domain).

Validates 12 entities, 8-channel trace construction,
Tier-1 kernel identities, and 6 theorems (T-ME-1 through T-ME-6).
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from closures.evolution.molecular_evolution import (
    ME_CHANNELS,
    ME_ENTITIES,
    N_ME_CHANNELS,
    MEKernelResult,
    compute_all_entities,
    compute_me_kernel,
    verify_all_theorems,
    verify_t_me_1,
    verify_t_me_2,
    verify_t_me_3,
    verify_t_me_4,
    verify_t_me_5,
    verify_t_me_6,
)


@pytest.fixture(scope="module")
def all_results() -> list[MEKernelResult]:
    return compute_all_entities()


class TestEntityCatalog:
    def test_entity_count(self):
        assert len(ME_ENTITIES) == 12

    def test_channel_count(self):
        assert N_ME_CHANNELS == 8
        assert len(ME_CHANNELS) == 8

    def test_all_categories_present(self):
        cats = {e.category for e in ME_ENTITIES}
        assert cats == {"highly_conserved", "moderate", "rapid", "ultra_conserved"}

    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_shape(self, entity):
        assert entity.trace_vector().shape == (8,)

    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_bounds(self, entity):
        c = entity.trace_vector()
        assert np.all(c >= 0.0) and np.all(c <= 1.0)


class TestTier1Identities:
    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_duality_identity(self, entity):
        r = compute_me_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_integrity_bound(self, entity):
        r = compute_me_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_log_integrity_relation(self, entity):
        r = compute_me_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10


class TestTheorems:
    def test_t_me_1(self, all_results):
        assert verify_t_me_1(all_results)["passed"]

    def test_t_me_2(self, all_results):
        assert verify_t_me_2(all_results)["passed"]

    def test_t_me_3(self, all_results):
        assert verify_t_me_3(all_results)["passed"]

    def test_t_me_4(self, all_results):
        assert verify_t_me_4(all_results)["passed"]

    def test_t_me_5(self, all_results):
        assert verify_t_me_5(all_results)["passed"]

    def test_t_me_6(self, all_results):
        assert verify_t_me_6(all_results)["passed"]

    def test_all_theorems_pass(self):
        for t in verify_all_theorems():
            assert t["passed"], f"{t['name']} failed: {t}"


class TestRegimeClassification:
    @pytest.mark.parametrize("entity", ME_ENTITIES, ids=lambda e: e.name)
    def test_regime_is_valid(self, entity):
        r = compute_me_kernel(entity)
        assert r.regime in ("Stable", "Watch", "Collapse")
