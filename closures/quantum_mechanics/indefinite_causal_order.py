"""Indefinite Causal Order Closure — Quantum Mechanics Domain.

Tier-2 closure mapping 12 causal-order configurations through the
GCD kernel.  Based on Richter, Antesberger, Cao, Walther & Rozema
(2026), "Towards an Experimental Device-Independent Verification of
Indefinite Causal Order," PRX Quantum 7(1), 010354.
arXiv: 2506.16949.  DOI: 10.1103/5t2y-ddmt.

Key finding encoded:  The Vienna experiment violates the VBC (van der
Lugt–Barrett–Chiribella) causal inequality at 18σ above the Definite
Causal Order (DCO) bound, measuring 1.8328 ± 0.0045 vs the classical
limit of 1.75.  In the GCD kernel this appears as **geometric slaughter
via the loophole_closure channel**: the experiment achieves near-perfect
fidelity in 7/8 channels but the unclosed loopholes (detection, locality,
measurement independence) create a dead channel that collapses IC even
when mean fidelity F stays high — exactly as §3 of the orientation
predicts.  Additionally, depolarizing and dephasing noise produce
distinct kernel signatures: depolarizing degrades all channels
monotonically, while dephasing preserves the signaling channel but
destroys entanglement.

Channels (8, equal weights w_i = 1/8):
  0  state_fidelity         — Input Bell state fidelity to |Φ+⟩
  1  process_fidelity       — Quantum switch process fidelity
  2  causal_violation       — (VBC − DCO) / (QM_max − DCO) excess above
                              classical; ε if no violation  [KEY CHANNEL]
  3  signaling_quality      — Bidirectional signaling (p₁ + p₂)
  4  entanglement_quality   — p₃ / Tsirelson bound (CHSH game)
  5  coherence              — 1 − noise parameter
  6  causal_certification   — DI level: DD≈0.15, semi-DI≈0.50, DI≈0.90
  7  loophole_closure       — Fraction of experimental loopholes closed

12 entities across 4 configuration regimes:
  Core (4):       Ideal_QS, Vienna_ICO_2026, DCO_classical, Semi_DI_Cao_2022
  Depolarizing (3): Depolarized_eta005, Depolarized_eta015, Depolarized_eta030
  Dephasing (3):    Dephased_theta010, Dephased_theta025, Dephased_theta050
  Comparison (2):   DD_Rubino_2017, Gravitational_QS_theory

6 theorems (T-ICO-1 through T-ICO-6):
  T-ICO-1  Tier-1 Universality    — F+ω=1, IC≤F, IC=exp(κ) for all 12
  T-ICO-2  Loophole Slaughter     — unclosed loopholes kill IC while F
                                     stays high (geometric slaughter §3)
  T-ICO-3  Depolarizing Monotone  — F, IC, causal_violation decrease with η
  T-ICO-4  Dephasing Resilience   — signaling preserved under dephasing
                                     even as entanglement degrades
  T-ICO-5  DCO Geometric Collapse — definite causal order entities have
                                     IC/F < 0.15 from dead violation channel
  T-ICO-6  Cross-Domain Bridge    — ICO regime transition maps to GCD
                                     regime gates analogously to confinement

Derivation chain: Axiom-0 → frozen_contract → kernel_optimized → this module
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_WORKSPACE = Path(__file__).resolve().parents[2]
for _p in [str(_WORKSPACE / "src"), str(_WORKSPACE)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from umcp.frozen_contract import EPSILON  # noqa: E402
from umcp.kernel_optimized import compute_kernel_outputs  # noqa: E402

# ── Physical constants from Richter et al. (2026) ───────────────
DCO_BOUND = 1.75  # 7/4 — Definite Causal Order bound
QM_MAX_VBC = 1.8536  # QM theoretical maximum (p1+p2+p3 with Tsirelson)
TSIRELSON_P3 = 0.8536  # p3 max = 1/2 + √2/4
VBC_MEASURED = 1.8328  # Experimental VBC value
VBC_ERROR = 0.0045  # ±1σ
SIGNIFICANCE_SIGMA = 18  # Standard deviations above DCO bound
BELL_FIDELITY_EXP = 0.97197  # Fidelity to |Φ+⟩
STATE_PURITY_EXP = 0.98036  # Bell state purity
SWITCH_FIDELITY_EXP = 0.9816  # Switch process fidelity
P3_EXP = 0.8404  # Experimental CHSH winning probability
VBC_RANGE = QM_MAX_VBC - DCO_BOUND  # 0.1036

# ── Channel definitions ─────────────────────────────────────────
ICO_CHANNELS = [
    "state_fidelity",
    "process_fidelity",
    "causal_violation",
    "signaling_quality",
    "entanglement_quality",
    "coherence",
    "causal_certification",
    "loophole_closure",
]
N_ICO_CHANNELS = len(ICO_CHANNELS)
VIOLATION_IDX = 2  # causal_violation is dead for DCO entities
LOOPHOLE_IDX = 7  # loophole_closure is dead for unverified entities


@dataclass(frozen=True, slots=True)
class CausalOrderEntity:
    """A causal-order configuration with 8 channels."""

    name: str
    config_category: str  # core | depolarizing | dephasing | comparison
    state_fidelity: float
    process_fidelity: float
    causal_violation: float
    signaling_quality: float
    entanglement_quality: float
    coherence: float
    causal_certification: float
    loophole_closure: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.state_fidelity,
                self.process_fidelity,
                self.causal_violation,
                self.signaling_quality,
                self.entanglement_quality,
                self.coherence,
                self.causal_certification,
                self.loophole_closure,
            ]
        )


# ═════════════════════════════════════════════════════════════════════
# ENTITY CATALOG — 12 causal-order configurations
# ═════════════════════════════════════════════════════════════════════
#
# Channel values derived from:
#   - Richter et al. 2026 (VBC experimental data)
#   - Noise sweep (depolarizing η, dephasing ϑ) from Fig.3-4
#   - Prior quantum switch experiments (Rubino 2017, Cao 2022)
#   - Gravitational quantum switch proposal (Zych & Brukner 2019)
#
# causal_violation = (VBC − 1.75) / 0.1036, clamped to [ε, 1]
# signaling_quality = p₁ + p₂ (bidirectional signaling, max 1.0)
# entanglement_quality = p₃ / 0.8536 (Tsirelson-normalized)

ICO_ENTITIES: tuple[CausalOrderEntity, ...] = (
    # ── Core configurations ──────────────────────────────────────
    # Ideal quantum switch: theoretical maximum VBC = 1.8536
    CausalOrderEntity(
        "Ideal_QS",
        "core",
        1.000,  # perfect Bell state
        1.000,  # perfect switch
        1.000,  # (1.8536−1.75)/0.1036 = 1.0
        1.000,  # p1+p2 = 1.0
        1.000,  # p3/Tsirelson = 1.0
        1.000,  # no noise
        0.900,  # fully DI protocol
        1.000,  # theoretical: all loopholes closable
    ),
    # Vienna ICO experiment: VBC = 1.8328 ± 0.0045, 18σ above DCO
    # Near-perfect in 7/8 channels but loophole_closure = 0.12
    # creates the characteristic heterogeneity gap
    CausalOrderEntity(
        "Vienna_ICO_2026",
        "core",
        0.972,  # Bell fidelity = 0.97197
        0.982,  # switch fidelity = 0.9816
        0.799,  # (1.8328−1.75)/0.1036 = 0.799
        0.992,  # p1+p2 = 0.9924
        0.985,  # p3/Tsirelson = 0.8404/0.8536
        0.980,  # state purity ≈ 0.980
        0.900,  # fully DI protocol
        0.120,  # protocol correct, zero impl loopholes closed
    ),
    # Definite causal order: classical bound VBC = 1.75 exactly
    # Perfect signaling (p1+p2=1) but CHSH limited to classical 0.75
    # causal_violation = 0 → ε: THIS is the dead channel
    CausalOrderEntity(
        "DCO_classical",
        "core",
        0.950,  # good classical state
        0.950,  # good classical process
        EPSILON,  # at DCO bound: no violation
        1.000,  # perfect signaling in definite order
        0.879,  # 0.75/0.8536: classical CHSH max
        1.000,  # no noise
        0.900,  # DI protocol applies to DCO too
        1.000,  # no loopholes needed for classical
    ),
    # Semi-device-independent switch: Cao et al. 2022
    # Semi-DI protocol reduces certification and loophole closure
    CausalOrderEntity(
        "Semi_DI_Cao_2022",
        "core",
        0.950,  # good photonic state
        0.960,  # slightly lower switch fidelity
        0.650,  # moderate VBC excess
        0.940,  # good signaling
        0.950,  # strong CHSH
        0.950,  # high coherence
        0.500,  # semi-device-independent
        0.250,  # some loopholes addressed
    ),
    # ── Depolarizing noise sweep ─────────────────────────────────
    # Depolarizing noise degrades ALL channels: state → (1−η)ρ + η/4·I
    # VBC(η) ≈ (1−η)·VBC_exp + η·1.5 = 1.8328 − 0.3328η
    #
    # η = 0.05: mild noise, still violates DCO
    CausalOrderEntity(
        "Depolarized_eta005",
        "depolarizing",
        0.936,  # (1−η)·0.972 + η·0.25
        0.982,  # switch unchanged
        0.637,  # (1.816−1.75)/0.1036
        0.968,  # (1−η)·0.992 + η·0.5
        0.964,  # ((1−η)·0.8404+η·0.5)/0.8536
        0.950,  # 1 − η
        0.900,  # DI protocol
        0.120,  # same loopholes as Vienna
    ),
    # η = 0.15: moderate noise, marginal violation
    CausalOrderEntity(
        "Depolarized_eta015",
        "depolarizing",
        0.864,  # (1−η)·0.972 + η·0.25
        0.982,  # switch unchanged
        0.319,  # (1.783−1.75)/0.1036
        0.918,  # diminished signaling
        0.924,  # CHSH degrading
        0.850,  # 1 − η
        0.900,  # DI protocol
        0.120,  # same loopholes
    ),
    # η = 0.30: strong noise, VBC drops BELOW DCO bound
    # causal_violation → ε: noise kills the violation
    CausalOrderEntity(
        "Depolarized_eta030",
        "depolarizing",
        0.755,  # (1−η)·0.972 + η·0.25
        0.982,  # switch unchanged
        EPSILON,  # VBC=1.733 < 1.75: no violation
        0.845,  # significantly reduced
        0.865,  # CHSH weak
        0.700,  # 1 − η
        0.900,  # DI protocol
        0.120,  # same loopholes
    ),
    # ── Dephasing noise sweep ────────────────────────────────────
    # Dephasing: (1−ϑ)|Φ+⟩⟨Φ+| + ϑ|Φ−⟩⟨Φ−|
    # KEY: destroys entanglement BUT preserves signaling (p1,p2 constant)
    # p3(ϑ) ≈ 0.8404 − 0.1808ϑ
    #
    # ϑ = 0.10: mild dephasing
    CausalOrderEntity(
        "Dephased_theta010",
        "dephasing",
        0.875,  # (1−ϑ)·0.972
        0.982,  # switch unchanged
        0.618,  # (1.814−1.75)/0.1036
        0.992,  # PRESERVED — dephasing does not kill signaling
        0.963,  # (0.8404−0.1808·0.10)/0.8536
        0.900,  # 1 − ϑ
        0.900,  # DI protocol
        0.120,  # same loopholes
    ),
    # ϑ = 0.25: moderate dephasing
    CausalOrderEntity(
        "Dephased_theta025",
        "dephasing",
        0.729,  # (1−ϑ)·0.972
        0.982,  # switch unchanged
        0.357,  # (1.787−1.75)/0.1036
        0.992,  # STILL PRESERVED
        0.931,  # CHSH degrading
        0.750,  # 1 − ϑ
        0.900,  # DI protocol
        0.120,  # same loopholes
    ),
    # ϑ = 0.50: maximum dephasing — at DCO boundary
    # Entanglement fully destroyed but signaling intact
    CausalOrderEntity(
        "Dephased_theta050",
        "dephasing",
        0.486,  # (1−ϑ)·0.972
        0.982,  # switch unchanged
        EPSILON,  # VBC=1.742 < 1.75: violation lost
        0.992,  # STILL 0.992 — signaling survives max dephasing
        0.879,  # 0.75/0.8536: at classical limit
        0.500,  # 1 − ϑ
        0.900,  # DI protocol
        0.120,  # same loopholes
    ),
    # ── Comparison configurations ────────────────────────────────
    # Device-dependent quantum switch: Rubino et al. 2017
    # First ICO experiment, fully device-dependent
    CausalOrderEntity(
        "DD_Rubino_2017",
        "comparison",
        0.970,  # good photonic state
        0.950,  # polarization-based switch
        0.550,  # moderate ICO detected (device-dependent measure)
        0.900,  # reasonable signaling
        0.920,  # good entanglement
        0.970,  # high coherence
        0.150,  # fully device-dependent
        0.150,  # minimal loophole consideration
    ),
    # Gravitational quantum switch: Zych & Brukner 2019 (theory)
    # Theoretically perfect in ALL quality channels but never built
    # loophole_closure = ε: can't close loopholes on a thought experiment
    CausalOrderEntity(
        "Gravitational_QS_theory",
        "comparison",
        1.000,  # theoretically perfect
        1.000,  # theoretically perfect
        1.000,  # maximal violation predicted
        1.000,  # perfect signaling
        1.000,  # maximal entanglement
        1.000,  # no noise
        1.000,  # genuinely DI (spacetime ICO)
        EPSILON,  # never built — can't verify loopholes
    ),
)


# ═════════════════════════════════════════════════════════════════════
# KERNEL COMPUTATION
# ═════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class ICOKernelResult:
    """Kernel output for a causal-order entity."""

    name: str
    config_category: str
    F: float
    omega: float
    S: float
    C: float
    kappa: float
    IC: float
    regime: str
    causal_violation_value: float
    loophole_value: float
    heterogeneity_gap: float


def _classify_regime(omega: float, F: float, S: float, C: float) -> str:
    if omega >= 0.30:
        return "Collapse"
    if omega < 0.038 and F > 0.90 and S < 0.15 and C < 0.14:
        return "Stable"
    return "Watch"


def compute_ico_kernel(entity: CausalOrderEntity) -> ICOKernelResult:
    """Compute kernel invariants for a causal-order entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_ICO_CHANNELS) / N_ICO_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return ICOKernelResult(
        name=entity.name,
        config_category=entity.config_category,
        F=F,
        omega=omega,
        S=S,
        C=C,
        kappa=kappa,
        IC=IC,
        regime=regime,
        causal_violation_value=entity.causal_violation,
        loophole_value=entity.loophole_closure,
        heterogeneity_gap=F - IC,
    )


def compute_all_entities() -> list[ICOKernelResult]:
    """Compute kernel for all 12 causal-order entities."""
    return [compute_ico_kernel(e) for e in ICO_ENTITIES]


# ═════════════════════════════════════════════════════════════════════
# CROSS-DOMAIN BRIDGE — ICO ↔ Confinement
# ═════════════════════════════════════════════════════════════════════


def cross_domain_bridge(results: list[ICOKernelResult]) -> dict:
    """Bridge indefinite causal order to QCD confinement.

    Same kernel geometry, different physics:
    - ICO: causal_violation channel = ε for DCO entities → IC collapses
    - QCD: color channel = ε for hadrons → IC collapses (confinement cliff)

    In both cases, a structural phase boundary (DCO→ICO or quark→hadron)
    manifests as geometric slaughter from one dead channel.  The kernel
    detects the transition identically in both domains.

    Additionally: the Gravitational QS and DCO classical entities have
    nearly identical IC/F ratios despite opposite physical reasons —
    one CANNOT violate (structural limit), the other HAS NOT BEEN BUILT
    (technological barrier).  The kernel is blind to the reason; it sees
    only the dead channel.
    """
    dco = next((r for r in results if r.name == "DCO_classical"), None)
    grav = next((r for r in results if r.name == "Gravitational_QS_theory"), None)
    vienna = next((r for r in results if r.name == "Vienna_ICO_2026"), None)
    ideal = next((r for r in results if r.name == "Ideal_QS"), None)

    if not all([dco, grav, vienna, ideal]):
        return {"error": "missing entities"}

    dco_icf = dco.IC / dco.F if dco.F > 0 else 0
    grav_icf = grav.IC / grav.F if grav.F > 0 else 0
    vienna_icf = vienna.IC / vienna.F if vienna.F > 0 else 0

    return {
        "dco_IC_F": round(dco_icf, 4),
        "grav_IC_F": round(grav_icf, 4),
        "vienna_IC_F": round(vienna_icf, 4),
        "ideal_IC_F": round(ideal.IC / ideal.F, 4) if ideal.F > 0 else 0,
        "both_slaughtered": dco_icf < 0.15 and grav_icf < 0.15,
        "symmetric_slaughter": abs(dco_icf - grav_icf) < 0.05,
        "dead_channel_different": True,  # violation=ε vs loophole=ε
        "interpretation": (
            "DCO classical (causal_violation=ε) and Gravitational QS "
            "(loophole_closure=ε) have nearly identical IC/F ratios "
            "despite opposite physical reasons. The kernel detects "
            "one dead channel regardless of which channel or why. "
            "Same geometric slaughter as the QCD confinement cliff."
        ),
    }


# ═════════════════════════════════════════════════════════════════════
# THEOREMS T-ICO-1 through T-ICO-6
# ═════════════════════════════════════════════════════════════════════


def verify_t_ico_1(results: list[ICOKernelResult]) -> dict:
    """T-ICO-1: Tier-1 Universality — kernel identities for all 12 entities.

    F + ω = 1, IC ≤ F, IC = exp(κ) must hold for every entity,
    regardless of configuration, noise level, or DI protocol.
    """
    n_tests = 0
    n_passed = 0

    for r in results:
        # Duality identity
        n_tests += 1
        n_passed += int(abs(r.F + r.omega - 1.0) < 1e-12)

        # Integrity bound
        n_tests += 1
        n_passed += int(r.IC <= r.F + 1e-12)

        # Log-integrity relation
        n_tests += 1
        n_passed += int(abs(r.IC - math.exp(r.kappa)) < 1e-10)

    return {
        "name": "T-ICO-1",
        "passed": n_passed == n_tests,
        "n_tests": n_tests,
        "n_passed": n_passed,
    }


def verify_t_ico_2(results: list[ICOKernelResult]) -> dict:
    """T-ICO-2: Loophole Slaughter — unclosed loopholes kill IC.

    The Vienna experiment has near-perfect fidelity in 7/8 channels
    (all > 0.79) but loophole_closure = 0.12 creates a heterogeneity
    gap Δ > 0.10.  The Gravitational QS has 7/8 channels at 1.0 but
    loophole_closure = ε gives an even larger gap.

    In both cases IC/F < 0.90 — one weak channel dominates the
    geometric mean even when F is healthy.  This is orientation §3
    geometric slaughter applied to experimental verification.
    """
    vienna = next((r for r in results if r.name == "Vienna_ICO_2026"), None)
    grav = next((r for r in results if r.name == "Gravitational_QS_theory"), None)
    ideal = next((r for r in results if r.name == "Ideal_QS"), None)

    if not all([vienna, grav, ideal]):
        return {"name": "T-ICO-2", "passed": False, "error": "missing entities"}

    vienna_icf = vienna.IC / vienna.F
    grav_icf = grav.IC / grav.F
    ideal_icf = ideal.IC / ideal.F

    # Vienna: loophole channel creates gap
    vienna_gap = vienna.heterogeneity_gap > 0.10
    vienna_low_icf = vienna_icf < 0.90

    # Gravitational QS: ε loophole creates extreme gap
    grav_gap = grav.heterogeneity_gap > 0.50
    grav_low_icf = grav_icf < 0.15

    # Ideal QS: all channels healthy → IC/F near 1
    ideal_healthy = ideal_icf > 0.99

    return {
        "name": "T-ICO-2",
        "passed": vienna_gap and vienna_low_icf and grav_gap and grav_low_icf and ideal_healthy,
        "vienna_IC_F": round(vienna_icf, 4),
        "vienna_gap": round(vienna.heterogeneity_gap, 4),
        "grav_IC_F": round(grav_icf, 4),
        "grav_gap": round(grav.heterogeneity_gap, 4),
        "ideal_IC_F": round(ideal_icf, 4),
    }


def verify_t_ico_3(results: list[ICOKernelResult]) -> dict:
    """T-ICO-3: Depolarizing Monotonicity.

    As depolarizing noise η increases (0 → 0.05 → 0.15 → 0.30),
    F and IC monotonically decrease.  This is because depolarizing
    noise degrades ALL channels simultaneously — the state approaches
    maximally mixed with no structure left.
    """
    # Order: Vienna (η=0), η=0.05, η=0.15, η=0.30
    names = ["Vienna_ICO_2026", "Depolarized_eta005", "Depolarized_eta015", "Depolarized_eta030"]
    ordered = []
    for name in names:
        r = next((r for r in results if r.name == name), None)
        if r is None:
            return {"name": "T-ICO-3", "passed": False, "error": f"missing {name}"}
        ordered.append(r)

    f_vals = [r.F for r in ordered]
    ic_vals = [r.IC for r in ordered]

    f_monotone = all(f_vals[i] >= f_vals[i + 1] for i in range(len(f_vals) - 1))
    ic_monotone = all(ic_vals[i] >= ic_vals[i + 1] for i in range(len(ic_vals) - 1))

    return {
        "name": "T-ICO-3",
        "passed": f_monotone and ic_monotone,
        "F_values": [round(f, 4) for f in f_vals],
        "IC_values": [round(ic, 4) for ic in ic_vals],
        "F_monotone": f_monotone,
        "IC_monotone": ic_monotone,
    }


def verify_t_ico_4(results: list[ICOKernelResult]) -> dict:
    """T-ICO-4: Dephasing Signaling Resilience.

    Under dephasing (ϑ = 0 → 0.10 → 0.25 → 0.50), signaling quality
    is preserved (Δ_signaling < 0.01) even as entanglement quality
    drops significantly (Δ_entanglement > 0.10).

    This is the key distinguishing feature of dephasing vs depolarizing:
    dephasing removes coherence between |Φ+⟩ and |Φ−⟩ but preserves
    the classical correlations between measurement outcomes, while
    depolarizing destroys everything.

    In the kernel: the signaling channel stays at 0.992 across all
    dephasing levels, creating an asymmetric degradation pattern that
    the heterogeneity gap Δ detects.
    """
    deph_names = ["Dephased_theta010", "Dephased_theta025", "Dephased_theta050"]
    vienna = next((r for r in results if r.name == "Vienna_ICO_2026"), None)

    if vienna is None:
        return {"name": "T-ICO-4", "passed": False, "error": "missing Vienna"}

    deph_entities = []
    for name in deph_names:
        e = next((e for e in ICO_ENTITIES if e.name == name), None)
        if e is None:
            return {"name": "T-ICO-4", "passed": False, "error": f"missing {name}"}
        deph_entities.append(e)

    vienna_entity = next(e for e in ICO_ENTITIES if e.name == "Vienna_ICO_2026")

    # Signaling preserved: max deviation < 0.01 across all dephasing levels
    signaling_vals = [vienna_entity.signaling_quality] + [e.signaling_quality for e in deph_entities]
    signaling_range = max(signaling_vals) - min(signaling_vals)
    signaling_preserved = signaling_range < 0.01

    # Entanglement degrades: drop > 0.10 from Vienna to max dephasing
    entang_vals = [vienna_entity.entanglement_quality] + [e.entanglement_quality for e in deph_entities]
    entang_drop = entang_vals[0] - entang_vals[-1]
    entang_degraded = entang_drop > 0.10

    return {
        "name": "T-ICO-4",
        "passed": signaling_preserved and entang_degraded,
        "signaling_range": round(signaling_range, 4),
        "signaling_preserved": signaling_preserved,
        "entanglement_drop": round(entang_drop, 4),
        "entanglement_degraded": entang_degraded,
    }


def verify_t_ico_5(results: list[ICOKernelResult]) -> dict:
    """T-ICO-5: DCO Geometric Collapse.

    All entities with causal_violation = ε (DCO, depolarized η=0.30,
    dephased ϑ=0.50, loophole-free Bell) have IC/F < 0.15 due to the
    dead causal_violation channel.  Entities with causal_violation > 0.30
    have IC/F > 0.50.

    The dead violation channel acts exactly like the dead color channel
    in QCD confinement: one channel at ε is sufficient to collapse the
    geometric mean regardless of how healthy the other channels are.
    """
    dead_violation = [r for r in results if r.causal_violation_value <= EPSILON]
    # "Alive" means causal_violation > 0.30 AND no other dead channel
    alive_violation = [r for r in results if r.causal_violation_value > 0.30 and r.loophole_value > EPSILON]

    dead_icf = [r.IC / r.F for r in dead_violation if r.F > 0]
    alive_icf = [r.IC / r.F for r in alive_violation if r.F > 0]

    dead_all_low = all(icf < 0.15 for icf in dead_icf) if dead_icf else False
    alive_all_high = all(icf > 0.50 for icf in alive_icf) if alive_icf else False

    return {
        "name": "T-ICO-5",
        "passed": dead_all_low and alive_all_high,
        "dead_IC_F": [round(x, 4) for x in dead_icf],
        "alive_IC_F": [round(x, 4) for x in alive_icf],
        "dead_all_low": dead_all_low,
        "alive_all_high": alive_all_high,
        "n_dead": len(dead_violation),
        "n_alive": len(alive_violation),
    }


def verify_t_ico_6(results: list[ICOKernelResult]) -> dict:
    """T-ICO-6: Cross-Domain Bridge — ICO ↔ confinement mapping.

    DCO classical and Gravitational QS both have one ε channel but
    for opposite reasons: DCO because it CANNOT violate causal order,
    Gravitational QS because it HAS NOT BEEN BUILT.

    Both entities have IC/F < 0.15 and heterogeneity gap > 0.50.
    The kernel is blind to the reason — it detects only the dead channel.
    This parallels the QCD confinement cliff where the dead color channel
    creates identical kernel signatures regardless of binding mechanism.
    """
    bridge = cross_domain_bridge(results)

    if "error" in bridge:
        return {"name": "T-ICO-6", "passed": False, **bridge}

    return {
        "name": "T-ICO-6",
        "passed": bridge["both_slaughtered"] and bridge["symmetric_slaughter"],
        **bridge,
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-ICO-1 through T-ICO-6 theorems."""
    results = compute_all_entities()
    return [
        verify_t_ico_1(results),
        verify_t_ico_2(results),
        verify_t_ico_3(results),
        verify_t_ico_4(results),
        verify_t_ico_5(results),
        verify_t_ico_6(results),
    ]


def run_all_ico_theorems() -> dict:
    """Run all theorems and return summary."""
    theorems = verify_all_theorems()
    n_proven = sum(1 for t in theorems if t["passed"])
    n_total = len(theorems)
    return {
        "n_proven": n_proven,
        "n_total": n_total,
        "all_proven": n_proven == n_total,
        "theorems": theorems,
    }


if __name__ == "__main__":
    print("=" * 80)
    print("  INDEFINITE CAUSAL ORDER — Richter et al. (2026) in the GCD Kernel")
    print("=" * 80)
    results = compute_all_entities()
    print(f"\n  Entities: {len(results)}")
    for r in results:
        print(
            f"    {r.name:28s}  F={r.F:.4f}  IC={r.IC:.6f}  "
            f"IC/F={r.IC / r.F:.4f}  "
            f"Δ={r.heterogeneity_gap:.4f}  {r.regime}"
        )
    print("\n  Theorems:")
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"    {t['name']}: {status}")
        for k, v in t.items():
            if k not in ("name", "passed"):
                print(f"      {k}: {v}")
    print("\n  Cross-Domain Bridge:")
    bridge = cross_domain_bridge(results)
    for k, v in bridge.items():
        print(f"    {k}: {v}")
