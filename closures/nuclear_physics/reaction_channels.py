"""Nuclear Reaction Channels Closure — Nuclear Physics Domain.

Tier-2 closure mapping 12 nuclear reactions through the GCD kernel.
Each reaction is characterized by 8 channels from reaction physics.

Channels (8, equal weights w_i = 1/8):
  0  q_value_norm        — Q / Q_max (1 = highly exothermic)
  1  cross_section_norm   — σ / σ_max (1 = large cross section)
  2  threshold_low        — 1 − E_thresh / E_max (1 = no threshold)
  3  branching_ratio      — BR to primary channel (1 = single channel)
  4  neutron_economy      — neutron yield per reaction (1 = high yield)
  5  resonance_narrow     — 1 − Γ / Γ_max (1 = narrow resonance)
  6  product_stability    — product half-life / max_hl (1 = stable products)
  7  chain_sustainability  — criticality factor (1 = self-sustaining)

12 entities across 4 categories:
  Fission (3):   U235_thermal, Pu239_thermal, U233_thermal
  Fusion (3):    DT_fusion, DD_fusion, He3_He3_fusion
  Capture (3):   Au197_n_gamma, Fe56_n_gamma, B10_n_alpha
  Spallation (3): Pb208_spallation, W184_spallation, Hg_spallation

6 theorems (T-RC-1 through T-RC-6).
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

RC_CHANNELS = [
    "q_value_norm",
    "cross_section_norm",
    "threshold_low",
    "branching_ratio",
    "neutron_economy",
    "resonance_narrow",
    "product_stability",
    "chain_sustainability",
]
N_RC_CHANNELS = len(RC_CHANNELS)


@dataclass(frozen=True, slots=True)
class ReactionEntity:
    """A nuclear reaction with 8 measurable channels."""

    name: str
    category: str
    q_value_norm: float
    cross_section_norm: float
    threshold_low: float
    branching_ratio: float
    neutron_economy: float
    resonance_narrow: float
    product_stability: float
    chain_sustainability: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.q_value_norm,
                self.cross_section_norm,
                self.threshold_low,
                self.branching_ratio,
                self.neutron_economy,
                self.resonance_narrow,
                self.product_stability,
                self.chain_sustainability,
            ]
        )


RC_ENTITIES: tuple[ReactionEntity, ...] = (
    # Fission — high Q, thermal threshold, chain reactions
    ReactionEntity("U235_thermal", "fission", 0.85, 0.90, 0.95, 0.65, 0.90, 0.70, 0.60, 0.95),
    ReactionEntity("Pu239_thermal", "fission", 0.90, 0.95, 0.93, 0.70, 0.95, 0.65, 0.55, 0.97),
    ReactionEntity("U233_thermal", "fission", 0.82, 0.85, 0.94, 0.60, 0.88, 0.72, 0.58, 0.92),
    # Fusion — very high Q, high threshold (Coulomb barrier)
    ReactionEntity("DT_fusion", "fusion", 0.95, 0.80, 0.20, 0.95, 0.85, 0.50, 0.95, 0.70),
    ReactionEntity("DD_fusion", "fusion", 0.30, 0.40, 0.15, 0.50, 0.60, 0.45, 0.90, 0.30),
    ReactionEntity("He3_He3_fusion", "fusion", 0.55, 0.20, 0.10, 0.90, 0.05, 0.40, 0.95, 0.10),
    # Capture — low Q, resonance-dominated
    ReactionEntity("Au197_n_gamma", "capture", 0.15, 0.70, 0.90, 0.95, 0.05, 0.85, 0.90, 0.10),
    ReactionEntity("Fe56_n_gamma", "capture", 0.10, 0.30, 0.88, 0.90, 0.05, 0.80, 0.95, 0.08),
    ReactionEntity("B10_n_alpha", "capture", 0.25, 0.95, 0.92, 0.98, 0.10, 0.60, 0.85, 0.15),
    # Spallation — high-energy, many products, no chain
    ReactionEntity("Pb208_spallation", "spallation", 0.20, 0.25, 0.05, 0.15, 0.75, 0.20, 0.40, 0.05),
    ReactionEntity("W184_spallation", "spallation", 0.18, 0.20, 0.05, 0.12, 0.65, 0.15, 0.35, 0.05),
    ReactionEntity("Hg_spallation", "spallation", 0.15, 0.18, 0.05, 0.10, 0.60, 0.18, 0.30, 0.05),
)


@dataclass(frozen=True, slots=True)
class RCKernelResult:
    """Kernel output for a nuclear reaction entity."""

    name: str
    category: str
    F: float
    omega: float
    S: float
    C: float
    kappa: float
    IC: float
    regime: str


def _classify_regime(omega: float, F: float, S: float, C: float) -> str:
    if omega >= 0.30:
        return "Collapse"
    if omega < 0.038 and F > 0.90 and S < 0.15 and C < 0.14:
        return "Stable"
    return "Watch"


def compute_rc_kernel(entity: ReactionEntity) -> RCKernelResult:
    """Compute kernel invariants for a nuclear reaction entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_RC_CHANNELS) / N_RC_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return RCKernelResult(
        name=entity.name,
        category=entity.category,
        F=float(F),
        omega=float(omega),
        S=float(S),
        C=float(C),
        kappa=float(kappa),
        IC=float(IC),
        regime=regime,
    )


def compute_all_entities() -> list[RCKernelResult]:
    """Compute kernel for all nuclear reaction entities."""
    return [compute_rc_kernel(e) for e in RC_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-RC-1 through T-RC-6
# ---------------------------------------------------------------------------


def verify_t_rc_1(results: list[RCKernelResult]) -> dict:
    """T-RC-1: Fission reactions have highest mean F (all channels moderate-high)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    fiss_f = np.mean(cats["fission"])
    others = [np.mean(v) for k, v in cats.items() if k != "fission"]
    passed = fiss_f > max(others)
    return {
        "name": "T-RC-1",
        "passed": bool(passed),
        "fission_mean_F": float(fiss_f),
        "next_highest": float(max(others)),
    }


def verify_t_rc_2(results: list[RCKernelResult]) -> dict:
    """T-RC-2: Spallation reactions are in Collapse regime (most channels low)."""
    spall = [r for r in results if r.category == "spallation"]
    collapse_count = sum(1 for r in spall if r.regime == "Collapse")
    passed = collapse_count >= 2
    return {
        "name": "T-RC-2",
        "passed": bool(passed),
        "spallation_collapse_count": collapse_count,
        "spallation_total": len(spall),
    }


def verify_t_rc_3(results: list[RCKernelResult]) -> dict:
    """T-RC-3: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-RC-3",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_rc_4(results: list[RCKernelResult]) -> dict:
    """T-RC-4: He3_He3 fusion has highest curvature among fusion reactions."""
    fusion = [r for r in results if r.category == "fusion"]
    he3 = next(r for r in fusion if r.name == "He3_He3_fusion")
    max_fusion_c = max(r.C for r in fusion)
    passed = max_fusion_c - 1e-12 <= he3.C
    return {
        "name": "T-RC-4",
        "passed": bool(passed),
        "He3_He3_C": he3.C,
        "max_fusion_C": float(max_fusion_c),
    }


def verify_t_rc_5(results: list[RCKernelResult]) -> dict:
    """T-RC-5: Pu239 has highest F among fission reactions."""
    fission = [r for r in results if r.category == "fission"]
    pu239 = next(r for r in fission if r.name == "Pu239_thermal")
    max_fiss_f = max(r.F for r in fission)
    passed = max_fiss_f - 1e-12 <= pu239.F
    return {
        "name": "T-RC-5",
        "passed": bool(passed),
        "Pu239_F": pu239.F,
        "max_fission_F": max_fiss_f,
    }


def verify_t_rc_6(results: list[RCKernelResult]) -> dict:
    """T-RC-6: Spallation reactions have higher IC/F than capture (more uniform channels)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        icf = r.IC / r.F if r.F > EPSILON else 0.0
        cats.setdefault(r.category, []).append(icf)
    spal_icf = np.mean(cats["spallation"])
    cap_icf = np.mean(cats["capture"])
    passed = spal_icf > cap_icf
    return {
        "name": "T-RC-6",
        "passed": bool(passed),
        "spallation_IC_F": float(spal_icf),
        "capture_IC_F": float(cap_icf),
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-RC theorems."""
    results = compute_all_entities()
    return [
        verify_t_rc_1(results),
        verify_t_rc_2(results),
        verify_t_rc_3(results),
        verify_t_rc_4(results),
        verify_t_rc_5(results),
        verify_t_rc_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
