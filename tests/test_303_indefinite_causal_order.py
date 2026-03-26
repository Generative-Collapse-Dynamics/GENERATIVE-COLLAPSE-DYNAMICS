"""Tests for indefinite causal order (ICO) closure.

Validates 6 ICO Theorems (T-ICO-1 through T-ICO-6), 12 causal-order
configurations (Richter et al. 2026), Tier-1 identity universality,
and the cross-domain bridge connecting to QCD confinement geometric
slaughter.

Test count target: ~82 tests covering:
    - Entity catalog validation (12 entities, 8 channels, 4 categories)
    - Tier-1 identity universality (duality, integrity bound, log-bridge)
    - 6 theorem proofs
    - Regime classification
    - Cross-domain bridge diagnostics
"""

from __future__ import annotations

import math

import pytest

from closures.quantum_mechanics.indefinite_causal_order import (
    BELL_FIDELITY_EXP,
    DCO_BOUND,
    ICO_CHANNELS,
    ICO_ENTITIES,
    N_ICO_CHANNELS,
    QM_MAX_VBC,
    SWITCH_FIDELITY_EXP,
    VBC_MEASURED,
    VBC_RANGE,
    CausalOrderEntity,
    ICOKernelResult,
    compute_all_entities,
    cross_domain_bridge,
    run_all_ico_theorems,
    verify_all_theorems,
    verify_t_ico_1,
    verify_t_ico_2,
    verify_t_ico_3,
    verify_t_ico_4,
    verify_t_ico_5,
    verify_t_ico_6,
)

# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def all_results() -> list[ICOKernelResult]:
    """Compute all 12 entity kernels once for entire test module."""
    return compute_all_entities()


@pytest.fixture(scope="module")
def all_theorems() -> list[dict]:
    """Run all 6 theorems once."""
    return verify_all_theorems()


@pytest.fixture(scope="module")
def bridge(all_results: list[ICOKernelResult]) -> dict:
    """Compute cross-domain bridge once."""
    return cross_domain_bridge(all_results)


# ═══════════════════════════════════════════════════════════════
# SECTION 1: ENTITY CATALOG
# ═══════════════════════════════════════════════════════════════


class TestEntityCatalog:
    """Validate the static entity data structures."""

    def test_entity_count(self) -> None:
        assert len(ICO_ENTITIES) == 12

    def test_channel_count(self) -> None:
        assert N_ICO_CHANNELS == 8

    def test_channel_names(self) -> None:
        assert len(ICO_CHANNELS) == 8
        assert "causal_violation" in ICO_CHANNELS
        assert "loophole_closure" in ICO_CHANNELS

    def test_unique_names(self) -> None:
        names = [e.name for e in ICO_ENTITIES]
        assert len(names) == len(set(names))

    def test_category_distribution(self) -> None:
        cats = [e.config_category for e in ICO_ENTITIES]
        assert cats.count("core") == 4
        assert cats.count("depolarizing") == 3
        assert cats.count("dephasing") == 3
        assert cats.count("comparison") == 2

    def test_all_entities_are_dataclass(self) -> None:
        for e in ICO_ENTITIES:
            assert isinstance(e, CausalOrderEntity)

    @pytest.mark.parametrize("idx", range(12))
    def test_trace_vector_length(self, idx: int) -> None:
        tv = ICO_ENTITIES[idx].trace_vector()
        assert len(tv) == N_ICO_CHANNELS

    @pytest.mark.parametrize("idx", range(12))
    def test_trace_vector_bounds(self, idx: int) -> None:
        tv = ICO_ENTITIES[idx].trace_vector()
        for v in tv:
            assert 0.0 <= v <= 1.0, f"Channel value {v} out of [0,1]"

    def test_vienna_bell_fidelity(self) -> None:
        vienna = next(e for e in ICO_ENTITIES if e.name == "Vienna_ICO_2026")
        assert vienna.state_fidelity == pytest.approx(0.972, abs=0.002)

    def test_vienna_switch_fidelity(self) -> None:
        vienna = next(e for e in ICO_ENTITIES if e.name == "Vienna_ICO_2026")
        assert vienna.process_fidelity == pytest.approx(0.982, abs=0.002)

    def test_ideal_qs_near_perfect(self) -> None:
        ideal = next(e for e in ICO_ENTITIES if e.name == "Ideal_QS")
        tv = ideal.trace_vector()
        # 7 of 8 channels at 1.0 (cert=0.9 is the only one below)
        assert sum(1 for v in tv if v >= 0.90) == 8

    def test_dco_violation_near_zero(self) -> None:
        dco = next(e for e in ICO_ENTITIES if e.name == "DCO_classical")
        assert dco.causal_violation < 1e-6

    def test_gravitational_loophole_near_zero(self) -> None:
        grav = next(e for e in ICO_ENTITIES if e.name == "Gravitational_QS_theory")
        assert grav.loophole_closure < 1e-6


# ═══════════════════════════════════════════════════════════════
# SECTION 2: PHYSICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════


class TestPhysicalConstants:
    """Validate physical constants from Richter et al. (2026)."""

    def test_dco_bound(self) -> None:
        assert pytest.approx(1.75) == DCO_BOUND

    def test_qm_max_vbc(self) -> None:
        assert pytest.approx(1.8536, abs=0.001) == QM_MAX_VBC

    def test_vbc_measured(self) -> None:
        assert pytest.approx(1.8328, abs=0.001) == VBC_MEASURED

    def test_vbc_exceeds_dco(self) -> None:
        assert VBC_MEASURED > DCO_BOUND

    def test_vbc_range(self) -> None:
        assert pytest.approx(QM_MAX_VBC - DCO_BOUND) == VBC_RANGE

    def test_bell_fidelity(self) -> None:
        assert pytest.approx(0.97197, abs=0.0001) == BELL_FIDELITY_EXP

    def test_switch_fidelity(self) -> None:
        assert pytest.approx(0.9816, abs=0.001) == SWITCH_FIDELITY_EXP


# ═══════════════════════════════════════════════════════════════
# SECTION 3: TIER-1 IDENTITY UNIVERSALITY
# ═══════════════════════════════════════════════════════════════


class TestTier1Identities:
    """Tier-1 identities must hold for ALL 12 entities."""

    @pytest.mark.parametrize("idx", range(12))
    def test_duality_identity(self, all_results: list[ICOKernelResult], idx: int) -> None:
        """F + ω = 1 exactly."""
        r = all_results[idx]
        assert r.F + r.omega == pytest.approx(1.0, abs=1e-10)

    @pytest.mark.parametrize("idx", range(12))
    def test_integrity_bound(self, all_results: list[ICOKernelResult], idx: int) -> None:
        """IC ≤ F (integrity cannot exceed fidelity)."""
        r = all_results[idx]
        assert r.IC <= r.F + 1e-10

    @pytest.mark.parametrize("idx", range(12))
    def test_log_integrity_bridge(self, all_results: list[ICOKernelResult], idx: int) -> None:
        """IC = exp(κ)."""
        r = all_results[idx]
        assert math.exp(r.kappa) == pytest.approx(r.IC, rel=1e-6)

    @pytest.mark.parametrize("idx", range(12))
    def test_heterogeneity_gap_nonneg(self, all_results: list[ICOKernelResult], idx: int) -> None:
        """Δ = F − IC ≥ 0."""
        r = all_results[idx]
        assert r.heterogeneity_gap >= -1e-10


# ═══════════════════════════════════════════════════════════════
# SECTION 4: THEOREMS
# ═══════════════════════════════════════════════════════════════


class TestTheorems:
    """Test each of the 6 ICO theorems."""

    def test_t_ico_1_tier1_universality(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_1(all_results)
        assert result["passed"], f"T-ICO-1 FAILED: {result}"

    def test_t_ico_2_loophole_slaughter(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_2(all_results)
        assert result["passed"], f"T-ICO-2 FAILED: {result}"

    def test_t_ico_3_depolarizing_monotone(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_3(all_results)
        assert result["passed"], f"T-ICO-3 FAILED: {result}"

    def test_t_ico_4_dephasing_resilience(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_4(all_results)
        assert result["passed"], f"T-ICO-4 FAILED: {result}"

    def test_t_ico_5_dco_geometric_collapse(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_5(all_results)
        assert result["passed"], f"T-ICO-5 FAILED: {result}"

    def test_t_ico_6_cross_domain_bridge(self, all_results: list[ICOKernelResult]) -> None:
        result = verify_t_ico_6(all_results)
        assert result["passed"], f"T-ICO-6 FAILED: {result}"

    def test_all_theorems_pass(self, all_theorems: list[dict]) -> None:
        for t in all_theorems:
            assert t["passed"], f"{t['name']} FAILED"

    def test_run_all_summary(self) -> None:
        summary = run_all_ico_theorems()
        assert summary["all_proven"]
        assert summary["n_proven"] == 6
        assert summary["n_total"] == 6


# ═══════════════════════════════════════════════════════════════
# SECTION 5: REGIME CLASSIFICATION
# ═══════════════════════════════════════════════════════════════


class TestRegimeClassification:
    """Validate regime labels for key entities."""

    def test_ideal_qs_stable(self, all_results: list[ICOKernelResult]) -> None:
        ideal = next(r for r in all_results if r.name == "Ideal_QS")
        assert ideal.regime == "Stable"

    def test_vienna_watch(self, all_results: list[ICOKernelResult]) -> None:
        vienna = next(r for r in all_results if r.name == "Vienna_ICO_2026")
        assert vienna.regime == "Watch"

    def test_dco_not_stable(self, all_results: list[ICOKernelResult]) -> None:
        dco = next(r for r in all_results if r.name == "DCO_classical")
        assert dco.regime != "Stable"

    def test_heavy_depolarizing_collapse(self, all_results: list[ICOKernelResult]) -> None:
        dep030 = next(r for r in all_results if r.name == "Depolarized_eta030")
        assert dep030.regime == "Collapse"

    def test_heavy_dephasing_collapse(self, all_results: list[ICOKernelResult]) -> None:
        dph050 = next(r for r in all_results if r.name == "Dephased_theta050")
        assert dph050.regime == "Collapse"

    def test_grav_not_stable(self, all_results: list[ICOKernelResult]) -> None:
        grav = next(r for r in all_results if r.name == "Gravitational_QS_theory")
        assert grav.regime != "Stable"


# ═══════════════════════════════════════════════════════════════
# SECTION 6: KERNEL VALUES
# ═══════════════════════════════════════════════════════════════


class TestKernelValues:
    """Validate specific kernel output values."""

    def test_ideal_qs_high_fidelity(self, all_results: list[ICOKernelResult]) -> None:
        ideal = next(r for r in all_results if r.name == "Ideal_QS")
        assert ideal.F > 0.98

    def test_ideal_qs_ic_near_f(self, all_results: list[ICOKernelResult]) -> None:
        ideal = next(r for r in all_results if r.name == "Ideal_QS")
        assert ideal.IC / ideal.F > 0.99

    def test_dco_ic_slaughtered(self, all_results: list[ICOKernelResult]) -> None:
        dco = next(r for r in all_results if r.name == "DCO_classical")
        assert dco.IC / dco.F < 0.15

    def test_grav_ic_slaughtered(self, all_results: list[ICOKernelResult]) -> None:
        grav = next(r for r in all_results if r.name == "Gravitational_QS_theory")
        assert grav.IC / grav.F < 0.15

    def test_dco_grav_symmetric_slaughter(self, all_results: list[ICOKernelResult]) -> None:
        """DCO and Grav have nearly identical IC/F despite different dead channels."""
        dco = next(r for r in all_results if r.name == "DCO_classical")
        grav = next(r for r in all_results if r.name == "Gravitational_QS_theory")
        assert abs(dco.IC / dco.F - grav.IC / grav.F) < 0.02

    def test_vienna_gap_from_loophole(self, all_results: list[ICOKernelResult]) -> None:
        vienna = next(r for r in all_results if r.name == "Vienna_ICO_2026")
        assert vienna.heterogeneity_gap > 0.05

    def test_depolarizing_f_monotone(self, all_results: list[ICOKernelResult]) -> None:
        dep_names = ["Depolarized_eta005", "Depolarized_eta015", "Depolarized_eta030"]
        dep = [next(r for r in all_results if r.name == n) for n in dep_names]
        assert dep[0].F > dep[1].F > dep[2].F

    def test_dephasing_signaling_preserved(self, all_results: list[ICOKernelResult]) -> None:
        """All dephasing entities should have signaling near nominal."""
        dph_names = ["Dephased_theta010", "Dephased_theta025", "Dephased_theta050"]
        for name in dph_names:
            next(r for r in all_results if r.name == name)
            entity = next(e for e in ICO_ENTITIES if e.name == name)
            assert entity.signaling_quality > 0.98


# ═══════════════════════════════════════════════════════════════
# SECTION 7: CROSS-DOMAIN BRIDGE
# ═══════════════════════════════════════════════════════════════


class TestCrossDomainBridge:
    """Validate the ICO ↔ confinement cross-domain bridge."""

    def test_bridge_has_interpretation(self, bridge: dict) -> None:
        assert "interpretation" in bridge

    def test_both_slaughtered(self, bridge: dict) -> None:
        assert bridge["both_slaughtered"]

    def test_symmetric_slaughter(self, bridge: dict) -> None:
        assert bridge["symmetric_slaughter"]

    def test_dead_channel_different(self, bridge: dict) -> None:
        assert bridge["dead_channel_different"]

    def test_dco_ic_f_value(self, bridge: dict) -> None:
        assert bridge["dco_IC_F"] == pytest.approx(0.1148, abs=0.01)

    def test_grav_ic_f_value(self, bridge: dict) -> None:
        assert bridge["grav_IC_F"] == pytest.approx(0.1143, abs=0.01)
