"""Tests for quantum material simulation closure (quantum mechanics domain).

Validates 12 entities, 8-channel trace construction,
Tier-1 kernel identities, and 7 theorems (T-QSM-1 through T-QSM-7).

Motivated by Lee et al. 2026 (arXiv:2603.15608): 50-qubit IBM quantum
processor reproduces INS spectra of KCuF3 and CsCoX3. GCD translation:
noiseless MPS = Watch regime, noisy quantum hardware = Collapse regime.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from closures.quantum_mechanics.quantum_material_simulation import (
    N_QSM_CHANNELS,
    QSM_CHANNELS,
    QSM_ENTITIES,
    QSMKernelResult,
    compute_all_entities,
    compute_qsm_kernel,
    verify_all_theorems,
    verify_t_qsm_1,
    verify_t_qsm_2,
    verify_t_qsm_3,
    verify_t_qsm_4,
    verify_t_qsm_5,
    verify_t_qsm_6,
    verify_t_qsm_7,
)


@pytest.fixture(scope="module")
def all_results() -> list[QSMKernelResult]:
    return compute_all_entities()


# ---------------------------------------------------------------------------
# Entity catalog structure tests
# ---------------------------------------------------------------------------


class TestEntityCatalog:
    def test_entity_count(self):
        assert len(QSM_ENTITIES) == 12

    def test_channel_count(self):
        assert N_QSM_CHANNELS == 8
        assert len(QSM_CHANNELS) == 8

    def test_all_categories_present(self):
        cats = {e.category for e in QSM_ENTITIES}
        assert cats == {"noiseless", "quantum", "finite_size"}

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_shape(self, entity):
        assert entity.trace_vector().shape == (8,)

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_trace_vector_bounds(self, entity):
        c = entity.trace_vector()
        assert np.all(c >= 0.0) and np.all(c <= 1.0)

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_unique_names(self, entity):
        names = [e.name for e in QSM_ENTITIES]
        assert names.count(entity.name) == 1


# ---------------------------------------------------------------------------
# Tier-1 kernel identity tests (F + ω = 1, IC ≤ F, IC = exp(κ))
# ---------------------------------------------------------------------------


class TestTier1Identities:
    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_duality_identity(self, entity):
        r = compute_qsm_kernel(entity)
        assert abs(r.F + r.omega - 1.0) < 1e-12

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_integrity_bound(self, entity):
        r = compute_qsm_kernel(entity)
        assert r.IC <= r.F + 1e-12

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_log_integrity_relation(self, entity):
        r = compute_qsm_kernel(entity)
        assert abs(r.IC - math.exp(r.kappa)) < 1e-10

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_kernel_values_finite(self, entity):
        r = compute_qsm_kernel(entity)
        assert all(math.isfinite(v) for v in [r.F, r.omega, r.S, r.C, r.kappa, r.IC])

    @pytest.mark.parametrize("entity", QSM_ENTITIES, ids=lambda e: e.name)
    def test_regime_valid(self, entity):
        r = compute_qsm_kernel(entity)
        assert r.regime in {"Stable", "Watch", "Collapse"}


# ---------------------------------------------------------------------------
# Theorem tests (T-QSM-1 through T-QSM-7)
# ---------------------------------------------------------------------------


class TestTheorems:
    def test_t_qsm_1(self, all_results):
        assert verify_t_qsm_1(all_results)["passed"]

    def test_t_qsm_2(self, all_results):
        assert verify_t_qsm_2(all_results)["passed"]

    def test_t_qsm_3(self, all_results):
        assert verify_t_qsm_3(all_results)["passed"]

    def test_t_qsm_4(self, all_results):
        assert verify_t_qsm_4(all_results)["passed"]

    def test_t_qsm_5(self, all_results):
        assert verify_t_qsm_5(all_results)["passed"]

    def test_t_qsm_6(self, all_results):
        assert verify_t_qsm_6(all_results)["passed"]

    def test_t_qsm_7(self, all_results):
        assert verify_t_qsm_7(all_results)["passed"]

    def test_all_theorems_pass(self, all_results):
        for t in verify_all_theorems():
            assert t["passed"], f"{t['name']} failed"


# ---------------------------------------------------------------------------
# Structural tests — regime distribution, ordering, materials
# ---------------------------------------------------------------------------


class TestStructural:
    def test_at_least_two_regimes(self, all_results):
        regimes = {r.regime for r in all_results}
        assert len(regimes) >= 2

    def test_noiseless_all_watch(self, all_results):
        noiseless = [r for r in all_results if r.category == "noiseless"]
        assert all(r.regime == "Watch" for r in noiseless)

    def test_mps_higher_f_than_quantum(self, all_results):
        mps_kcuf3 = next(r for r in all_results if r.name == "KCuF3_MPS_50q")
        hw_kcuf3 = next(r for r in all_results if r.name == "KCuF3_ibm_boston_50q")
        assert mps_kcuf3.F > hw_kcuf3.F

    def test_boston_better_than_kingston(self, all_results):
        boston = next(r for r in all_results if r.name == "KCuF3_ibm_boston_50q")
        kingston = next(r for r in all_results if r.name == "KCuF3_ibm_kingston_50q")
        assert boston.F > kingston.F

    def test_xx_model_highest_f_quantum(self, all_results):
        quantum = [r for r in all_results if r.category == "quantum"]
        xx = next(r for r in all_results if r.name == "XX_model_quantum")
        assert max(r.F for r in quantum) == xx.F

    def test_more_qubits_higher_f(self, all_results):
        q10 = next(r for r in all_results if r.name == "KCuF3_quantum_10q")
        q20 = next(r for r in all_results if r.name == "KCuF3_quantum_20q")
        q30 = next(r for r in all_results if r.name == "KCuF3_quantum_30q")
        assert q10.F > q20.F > q30.F

    def test_nnn_larger_delta_than_nn(self, all_results):
        nnn = next(r for r in all_results if r.name == "CsCoX3_NNN_quantum")
        sol = next(r for r in all_results if r.name == "Two_soliton_quantum")
        delta_nnn = nnn.F - nnn.IC
        delta_sol = sol.F - sol.IC
        assert delta_nnn > delta_sol

    def test_all_materials_present(self, all_results):
        materials = {r.material for r in all_results}
        assert "KCuF3" in materials
        assert "CsCoX3" in materials
        assert "XX_chain" in materials
