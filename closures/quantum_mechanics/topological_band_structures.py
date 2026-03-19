"""Topological Band Structures Closure — Quantum Mechanics Domain.

Tier-2 closure mapping 12 topological materials through the GCD kernel.
Each material is characterized by 8 channels from band structure properties.

Channels (8, equal weights w_i = 1/8):
  0  band_gap_normalized     — E_gap / 1eV, capped at 1.0 (1 = large gap)
  1  spin_orbit_coupling     — SOC strength normalized (1 = strong)
  2  chern_number_presence   — |C|/max|C|, topological invariant (1 = nontrivial)
  3  surface_state_robustness — surface state protection (1 = robust)
  4  dirac_cone_integrity    — linear dispersion quality (1 = perfect cone)
  5  inversion_symmetry      — presence of spatial inversion (1 = preserved)
  6  time_reversal_protection — TRS protection of edge states (1 = protected)
  7  bulk_boundary_correspondence — strength of BBC (1 = clear)

12 entities across 4 categories:
  Strong TI (3):    Bi2Se3, Bi2Te3, Sb2Te3
  Topological SM (3): Cd3As2, Na3Bi, TaAs
  2D materials (3):  Graphene, Stanene, WTe2_monolayer
  Trivial ref (3):   Silicon, GaAs, Diamond

6 theorems (T-TB-1 through T-TB-6).
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

TB_CHANNELS = [
    "band_gap_normalized",
    "spin_orbit_coupling",
    "chern_number_presence",
    "surface_state_robustness",
    "dirac_cone_integrity",
    "inversion_symmetry",
    "time_reversal_protection",
    "bulk_boundary_correspondence",
]
N_TB_CHANNELS = len(TB_CHANNELS)


@dataclass(frozen=True, slots=True)
class TopoBandEntity:
    """A topological material with 8 measurable channels."""

    name: str
    category: str
    band_gap_normalized: float
    spin_orbit_coupling: float
    chern_number_presence: float
    surface_state_robustness: float
    dirac_cone_integrity: float
    inversion_symmetry: float
    time_reversal_protection: float
    bulk_boundary_correspondence: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.band_gap_normalized,
                self.spin_orbit_coupling,
                self.chern_number_presence,
                self.surface_state_robustness,
                self.dirac_cone_integrity,
                self.inversion_symmetry,
                self.time_reversal_protection,
                self.bulk_boundary_correspondence,
            ]
        )


TB_ENTITIES: tuple[TopoBandEntity, ...] = (
    # Strong topological insulators — large gap, strong SOC, nontrivial Chern
    TopoBandEntity("Bi2Se3", "strong_TI", 0.30, 0.90, 0.95, 0.92, 0.88, 0.95, 0.90, 0.93),
    TopoBandEntity("Bi2Te3", "strong_TI", 0.15, 0.85, 0.90, 0.88, 0.85, 0.90, 0.88, 0.90),
    TopoBandEntity("Sb2Te3", "strong_TI", 0.10, 0.82, 0.88, 0.85, 0.80, 0.88, 0.85, 0.87),
    # Topological semimetals — gapless, strong dispersion
    TopoBandEntity("Cd3As2", "semimetal", 0.02, 0.70, 0.80, 0.75, 0.95, 0.85, 0.80, 0.85),
    TopoBandEntity("Na3Bi", "semimetal", 0.01, 0.65, 0.75, 0.70, 0.92, 0.80, 0.78, 0.80),
    TopoBandEntity("TaAs", "semimetal", 0.01, 0.60, 0.85, 0.80, 0.90, 0.10, 0.20, 0.82),
    # 2D materials — varied topological properties
    TopoBandEntity("Graphene", "two_d", 0.01, 0.05, 0.10, 0.20, 0.95, 0.95, 0.30, 0.15),
    TopoBandEntity("Stanene", "two_d", 0.08, 0.75, 0.80, 0.82, 0.85, 0.90, 0.85, 0.80),
    TopoBandEntity("WTe2_monolayer", "two_d", 0.06, 0.70, 0.75, 0.78, 0.70, 0.15, 0.75, 0.72),
    # Trivial reference — no topological features
    TopoBandEntity("Silicon", "trivial", 0.95, 0.05, 0.02, 0.02, 0.05, 0.95, 0.10, 0.02),
    TopoBandEntity("GaAs", "trivial", 0.90, 0.15, 0.03, 0.03, 0.08, 0.90, 0.12, 0.03),
    TopoBandEntity("Diamond", "trivial", 0.99, 0.02, 0.01, 0.01, 0.02, 0.98, 0.05, 0.01),
)


@dataclass(frozen=True, slots=True)
class TBKernelResult:
    """Kernel output for a topological band entity."""

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


def compute_tb_kernel(entity: TopoBandEntity) -> TBKernelResult:
    """Compute kernel invariants for a topological band entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_TB_CHANNELS) / N_TB_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return TBKernelResult(
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


def compute_all_entities() -> list[TBKernelResult]:
    """Compute kernel for all topological band entities."""
    return [compute_tb_kernel(e) for e in TB_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-TB-1 through T-TB-6
# ---------------------------------------------------------------------------


def verify_t_tb_1(results: list[TBKernelResult]) -> dict:
    """T-TB-1: Semimetals have highest mean heterogeneity gap (Weyl node channels)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F - r.IC)
    sm_delta = np.mean(cats["semimetal"])
    other_deltas = [np.mean(v) for k, v in cats.items() if k != "semimetal"]
    passed = sm_delta > max(other_deltas)
    return {
        "name": "T-TB-1",
        "passed": bool(passed),
        "semimetal_mean_delta": float(sm_delta),
        "other_max_delta": float(max(other_deltas)),
    }


def verify_t_tb_2(results: list[TBKernelResult]) -> dict:
    """T-TB-2: Strong TI materials have highest IC/F (most uniform channels)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        icf = r.IC / r.F if r.F > EPSILON else 0.0
        cats.setdefault(r.category, []).append(icf)
    sti_icf = np.mean(cats["strong_TI"])
    other_icf = [np.mean(v) for k, v in cats.items() if k != "strong_TI"]
    passed = sti_icf > max(other_icf)
    return {
        "name": "T-TB-2",
        "passed": bool(passed),
        "strong_TI_IC_F": float(sti_icf),
        "other_max_IC_F": float(max(other_icf)),
    }


def verify_t_tb_3(results: list[TBKernelResult]) -> dict:
    """T-TB-3: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-TB-3",
        "passed": bool(passed),
        "regimes_present": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_tb_4(results: list[TBKernelResult]) -> dict:
    """T-TB-4: Trivial materials have lowest mean IC/F (zero topological protection)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        icf = r.IC / r.F if r.F > EPSILON else 0.0
        cats.setdefault(r.category, []).append(icf)
    triv_icf = np.mean(cats["trivial"])
    other_icf = [np.mean(v) for k, v in cats.items() if k != "trivial"]
    passed = triv_icf < min(other_icf)
    return {
        "name": "T-TB-4",
        "passed": bool(passed),
        "trivial_mean_IC_F": float(triv_icf),
        "other_min_IC_F": float(min(other_icf)),
    }


def verify_t_tb_5(results: list[TBKernelResult]) -> dict:
    """T-TB-5: Bi2Se3 has highest F among strong TI materials."""
    sti = [r for r in results if r.category == "strong_TI"]
    bi2se3 = next(r for r in sti if r.name == "Bi2Se3")
    max_sti_f = max(r.F for r in sti)
    passed = max_sti_f - 1e-12 <= bi2se3.F
    return {
        "name": "T-TB-5",
        "passed": bool(passed),
        "Bi2Se3_F": bi2se3.F,
        "max_strong_TI_F": max_sti_f,
    }


def verify_t_tb_6(results: list[TBKernelResult]) -> dict:
    """T-TB-6: Semimetals have higher curvature than strong TI (gapless → spread)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.C)
    sm_c = np.mean(cats["semimetal"])
    sti_c = np.mean(cats["strong_TI"])
    passed = sm_c > sti_c
    return {
        "name": "T-TB-6",
        "passed": bool(passed),
        "semimetal_mean_C": float(sm_c),
        "strong_TI_mean_C": float(sti_c),
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-TB theorems."""
    results = compute_all_entities()
    return [
        verify_t_tb_1(results),
        verify_t_tb_2(results),
        verify_t_tb_3(results),
        verify_t_tb_4(results),
        verify_t_tb_5(results),
        verify_t_tb_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
