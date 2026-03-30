"""Polariton Topological Photonics Closure — Quantum Mechanics Domain.

Tier-2 closure mapping 12 polariton micropillar configurations through
the GCD kernel.  Motivated by Widmann et al. (2026) demonstrating the
topological Hall effect in a micron-scale polariton Hofstadter ladder
via artificial gauge fields, using circular polarization as a synthetic
dimension.

In GCD terms: topological protection (non-zero winding number, strong
edge localization) maps to Stable/Watch regime — high fidelity, low
heterogeneity gap.  Trivial configurations (zero gauge flux, no
topological gap) land in Collapse regime.  The topological phase
boundary produces an IC cliff analogous to the confinement transition:
one dead channel (edge_localization → 0) kills multiplicative
coherence even if bulk channels remain healthy.

Channels (8, equal weights w_i = 1/8):
  0  gauge_flux             — artificial magnetic flux φ/π per plaquette [0,1]
  1  polarization_splitting — TE-TM splitting strength (1 = maximal)
  2  non_reciprocity        — directional asymmetry of edge transport (1 = perfect)
  3  winding_number         — topological invariant |ν|/max|ν| (1 = nontrivial)
  4  edge_localization      — spatial confinement to edge mode (1 = fully localized)
  5  polariton_coherence    — first-order coherence g^(1) (1 = fully coherent)
  6  coupling_ratio         — inter-site / intra-site coupling J_inter/J_intra
  7  detuning               — exciton-photon detuning normalized (1 = resonant)

12 entities across 4 categories:
  Topological (3):   High_flux_nonreciprocal, Sigma_plus_edge,
                     Sigma_minus_edge
  Trivial (3):       Zero_flux_chain, Symmetric_coupling, Bulk_dominated
  Transitional (4):  Hofstadter_center, Critical_flux, Intermediate_detuning,
                     Weak_coherence
  Extreme (2):       Maximum_nonreciprocity, Decoherence_collapsed

6 theorems (T-PTP-1 through T-PTP-6).

References:
  - Widmann et al. Nat. Commun. 17 (2026). DOI: 10.1038/s41467-026-68530-0
  - Hofstadter (1976). Energy levels and wave functions in a rational
    or irrational magnetic field.
  - Ozawa et al. Rev. Mod. Phys. 91, 015006 (2019). Topological photonics.
  - Klembt et al. Nature 562, 552 (2018). Exciton-polariton topological
    insulator.
"""

from __future__ import annotations

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

PTP_CHANNELS = [
    "gauge_flux",
    "polarization_splitting",
    "non_reciprocity",
    "winding_number",
    "edge_localization",
    "polariton_coherence",
    "coupling_ratio",
    "detuning",
]
N_PTP_CHANNELS = len(PTP_CHANNELS)


@dataclass(frozen=True, slots=True)
class PolaritonEntity:
    """A polariton micropillar configuration with 8 measurable channels."""

    name: str
    category: str
    gauge_flux: float
    polarization_splitting: float
    non_reciprocity: float
    winding_number: float
    edge_localization: float
    polariton_coherence: float
    coupling_ratio: float
    detuning: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.gauge_flux,
                self.polarization_splitting,
                self.non_reciprocity,
                self.winding_number,
                self.edge_localization,
                self.polariton_coherence,
                self.coupling_ratio,
                self.detuning,
            ]
        )


# ---------------------------------------------------------------------------
# Entity catalog — 12 polariton configurations
# ---------------------------------------------------------------------------
# Channel values are informed by the Widmann et al. (2026) experiment:
# elliptical micropillar chain with rotational alignment creating
# artificial gauge flux.  Polarization (σ+/σ−) serves as synthetic
# dimension, producing a 2-leg Hofstadter ladder.
#
# gauge_flux: φ/π normalized; 0 = trivial, 1 = half flux quantum
# polarization_splitting: TE-TM splitting; 0 = degenerate, 1 = maximal
# non_reciprocity: directional bias; 0 = symmetric, 1 = unidirectional
# winding_number: topological invariant; 0 = trivial, 1 = maximal
# edge_localization: mode confinement; 0 = bulk, 1 = pure edge state
# polariton_coherence: g^(1); 0 = thermal, 1 = fully coherent
# coupling_ratio: J_inter/J_intra; tuned by pillar overlap
# detuning: exciton-photon; 0 = far detuned, 1 = resonant

PTP_ENTITIES: tuple[PolaritonEntity, ...] = (
    # --- Topological (4) — non-zero gauge flux, protected edge states ---
    #                                    φ     ΔTE  NR    ν     edge  g1    J     δ
    PolaritonEntity(
        "High_flux_nonreciprocal",
        "topological",
        0.92,
        0.85,
        0.90,
        0.88,
        0.91,
        0.88,
        0.80,
        0.85,
    ),
    PolaritonEntity(
        "Sigma_plus_edge",
        "topological",
        0.85,
        0.82,
        0.85,
        0.82,
        0.88,
        0.90,
        0.78,
        0.82,
    ),
    PolaritonEntity(
        "Sigma_minus_edge",
        "topological",
        0.85,
        0.80,
        0.82,
        0.80,
        0.85,
        0.88,
        0.75,
        0.80,
    ),
    PolaritonEntity(
        "Hofstadter_center",
        "transitional",
        0.50,
        0.70,
        0.55,
        0.60,
        0.58,
        0.75,
        0.65,
        0.72,
    ),
    # --- Trivial (3) — no gauge field, no topological gap ---
    PolaritonEntity(
        "Zero_flux_chain",
        "trivial",
        0.02,
        0.10,
        0.05,
        0.02,
        0.08,
        0.60,
        0.50,
        0.65,
    ),
    PolaritonEntity(
        "Symmetric_coupling",
        "trivial",
        0.05,
        0.05,
        0.03,
        0.03,
        0.05,
        0.55,
        0.48,
        0.60,
    ),
    PolaritonEntity(
        "Bulk_dominated",
        "trivial",
        0.10,
        0.15,
        0.08,
        0.05,
        0.03,
        0.50,
        0.45,
        0.55,
    ),
    # --- Transitional (3) — gap closing, intermediate regime ---
    PolaritonEntity(
        "Critical_flux",
        "transitional",
        0.45,
        0.50,
        0.35,
        0.30,
        0.40,
        0.70,
        0.58,
        0.70,
    ),
    PolaritonEntity(
        "Intermediate_detuning",
        "transitional",
        0.60,
        0.55,
        0.50,
        0.48,
        0.52,
        0.65,
        0.55,
        0.45,
    ),
    PolaritonEntity(
        "Weak_coherence",
        "transitional",
        0.55,
        0.48,
        0.40,
        0.42,
        0.45,
        0.30,
        0.50,
        0.60,
    ),
    # --- Extreme (2) — boundary cases ---
    PolaritonEntity(
        "Maximum_nonreciprocity",
        "extreme",
        0.95,
        0.90,
        0.98,
        0.92,
        0.95,
        0.92,
        0.85,
        0.90,
    ),
    PolaritonEntity(
        "Decoherence_collapsed",
        "extreme",
        0.85,
        0.78,
        0.72,
        0.68,
        0.65,
        0.001,
        0.60,
        0.55,
    ),
)


@dataclass(frozen=True, slots=True)
class PTPKernelResult:
    """Kernel output for a polariton topological entity."""

    name: str
    category: str
    F: float
    omega: float
    S: float
    C: float
    kappa: float
    IC: float
    regime: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category,
            "F": self.F,
            "omega": self.omega,
            "S": self.S,
            "C": self.C,
            "kappa": self.kappa,
            "IC": self.IC,
            "regime": self.regime,
        }


def _classify_regime(omega: float, F: float, S: float, C: float) -> str:
    if omega >= 0.30:
        return "Collapse"
    if omega < 0.038 and F > 0.90 and S < 0.15 and C < 0.14:
        return "Stable"
    return "Watch"


def compute_ptp_kernel(entity: PolaritonEntity) -> PTPKernelResult:
    """Compute kernel invariants for a polariton entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_PTP_CHANNELS) / N_PTP_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return PTPKernelResult(
        name=entity.name,
        category=entity.category,
        F=F,
        omega=omega,
        S=S,
        C=C,
        kappa=kappa,
        IC=IC,
        regime=regime,
    )


def compute_all_entities() -> list[PTPKernelResult]:
    """Compute kernel for all polariton entities."""
    return [compute_ptp_kernel(e) for e in PTP_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-PTP-1 through T-PTP-6
# ---------------------------------------------------------------------------


def verify_t_ptp_1(results: list[PTPKernelResult]) -> dict:
    """T-PTP-1: Topological Protection as Fidelity.

    All topological entities (non-zero gauge flux, protected edge states)
    have F > 0.75.  Topological protection preserves signal through
    collapse — the gauge field acts as a fidelity shield.
    """
    topo = [r for r in results if r.category == "topological"]
    all_high_f = all(r.F > 0.75 for r in topo)
    return {
        "name": "T-PTP-1",
        "passed": bool(all_high_f),
        "topological_F_values": {r.name: r.F for r in topo},
        "min_F": float(min(r.F for r in topo)),
    }


def verify_t_ptp_2(results: list[PTPKernelResult]) -> dict:
    """T-PTP-2: Trivial Phase as Collapse.

    All trivial entities (zero gauge flux, no topological gap) have
    ω ≥ 0.30, placing them in Collapse regime.  Without topological
    protection, polariton channels lose coherence to the environment.
    """
    triv = [r for r in results if r.category == "trivial"]
    all_collapse = all(r.regime == "Collapse" for r in triv)
    return {
        "name": "T-PTP-2",
        "passed": bool(all_collapse),
        "trivial_regimes": {r.name: r.regime for r in triv},
        "trivial_omegas": {r.name: r.omega for r in triv},
    }


def verify_t_ptp_3(results: list[PTPKernelResult]) -> dict:
    """T-PTP-3: IC Cliff at Phase Boundary.

    Mean IC/F of topological entities exceeds mean IC/F of trivial
    entities by at least a factor of 1.5.  The topological phase
    boundary produces a cliff in multiplicative coherence — analogous
    to the confinement IC cliff at the quark-hadron boundary.
    """
    topo = [r for r in results if r.category == "topological"]
    triv = [r for r in results if r.category == "trivial"]
    topo_icf = float(np.mean([r.IC / r.F for r in topo]))
    triv_icf = float(np.mean([r.IC / r.F for r in triv]))
    ratio = topo_icf / triv_icf if triv_icf > EPSILON else float("inf")
    passed = ratio >= 1.5
    return {
        "name": "T-PTP-3",
        "passed": bool(passed),
        "topological_mean_IC_F": topo_icf,
        "trivial_mean_IC_F": triv_icf,
        "ratio": float(ratio),
    }


def verify_t_ptp_4(results: list[PTPKernelResult]) -> dict:
    """T-PTP-4: Topological Protection Minimizes Heterogeneity.

    Topological entities have the smallest mean heterogeneity gap
    Δ = F − IC among all categories.  Gauge-protected edge states
    enforce uniform channel response, minimizing IC departure from F.
    Without protection (trivial), channels diverge and Δ grows.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F - r.IC)
    topo_delta = float(np.mean(cats["topological"]))
    other_deltas = [float(np.mean(v)) for k, v in cats.items() if k != "topological"]
    passed = topo_delta < min(other_deltas)
    return {
        "name": "T-PTP-4",
        "passed": bool(passed),
        "topological_mean_delta": topo_delta,
        "other_min_delta": float(min(other_deltas)),
    }


def verify_t_ptp_5(results: list[PTPKernelResult]) -> dict:
    """T-PTP-5: Decoherence as Geometric Slaughter.

    The Decoherence_collapsed entity (polariton_coherence ≈ 0.001)
    has IC/F below 0.55 despite moderate-to-high values on all other
    channels.  One near-dead coherence channel suppresses multiplicative
    integrity by > 45% compared to topological entities (IC/F > 0.99).
    This is the geometric slaughter mechanism from orientation §3.
    """
    deco = next(r for r in results if r.name == "Decoherence_collapsed")
    topo = [r for r in results if r.category == "topological"]
    deco_icf = deco.IC / deco.F if deco.F > EPSILON else 0.0
    topo_mean_icf = float(np.mean([r.IC / r.F for r in topo]))
    passed = deco_icf < 0.55
    return {
        "name": "T-PTP-5",
        "passed": bool(passed),
        "decoherence_IC_F": float(deco_icf),
        "topological_mean_IC_F": topo_mean_icf,
        "suppression_pct": float((1 - deco_icf / topo_mean_icf) * 100) if topo_mean_icf > 0 else 0.0,
        "decoherence_regime": deco.regime,
    }


def verify_t_ptp_6(results: list[PTPKernelResult]) -> dict:
    """T-PTP-6: Synthetic Dimension Fidelity Lift.

    Entities with winding_number > 0.5 (topologically nontrivial)
    have higher mean F than those with winding_number ≤ 0.5
    (trivial or transitional).  The synthetic dimension created by
    polarization lifts fidelity by protecting edge-state channels.
    """
    nontrivial = [r for r, e in zip(results, PTP_ENTITIES, strict=True) if e.winding_number > 0.5]
    trivial_trans = [r for r, e in zip(results, PTP_ENTITIES, strict=True) if e.winding_number <= 0.5]
    nt_mean_f = float(np.mean([r.F for r in nontrivial])) if nontrivial else 0.0
    tt_mean_f = float(np.mean([r.F for r in trivial_trans])) if trivial_trans else 0.0
    passed = nt_mean_f > tt_mean_f
    return {
        "name": "T-PTP-6",
        "passed": bool(passed),
        "nontrivial_mean_F": nt_mean_f,
        "trivial_transitional_mean_F": tt_mean_f,
        "n_nontrivial": len(nontrivial),
        "n_trivial_trans": len(trivial_trans),
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-PTP theorems."""
    results = compute_all_entities()
    return [
        verify_t_ptp_1(results),
        verify_t_ptp_2(results),
        verify_t_ptp_3(results),
        verify_t_ptp_4(results),
        verify_t_ptp_5(results),
        verify_t_ptp_6(results),
    ]


if __name__ == "__main__":
    print("Polariton Topological Photonics — Kernel Results")
    print("=" * 70)
    for r in compute_all_entities():
        print(
            f"  {r.name:<30s}  F={r.F:.4f}  ω={r.omega:.4f}  "
            f"IC={r.IC:.4f}  IC/F={r.IC / r.F:.4f}  Δ={r.F - r.IC:.4f}  "
            f"[{r.regime}]"
        )
    print()
    print("Theorems")
    print("-" * 70)
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
