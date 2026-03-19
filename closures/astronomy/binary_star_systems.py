"""Binary Star Systems Closure — Astronomy Domain.

Tier-2 closure mapping 12 canonical binary star systems through the GCD kernel.
Each system is characterized by 8 channels from observational properties.

Channels (8, equal weights w_i = 1/8):
  0  mass_ratio_balance     — q = M2/M1 closeness to unity (1 = equal mass)
  1  orbital_stability       — long-term orbital regularity (1 = stable circular)
  2  tidal_synchronization   — spin-orbit tidal locking (1 = fully synchronized)
  3  luminosity_balance      — L2/L1 closeness to unity (1 = equal luminosity)
  4  spectral_resolution     — ability to resolve both components (1 = clear)
  5  roche_containment       — fraction of Roche lobe NOT filled (1 = detached)
  6  eccentricity_low        — 1 - e, circularity of orbit (1 = circular)
  7  mass_transfer_absence   — absence of active mass transfer (1 = no transfer)

12 entities across 4 categories:
  Visual (3):     Alpha_Centauri, Sirius, Procyon
  Eclipsing (3):  Algol, Beta_Lyrae, W_UMa_contact
  X-ray (3):      Cygnus_X1, Scorpius_X1, Her_X1
  Compact (3):    Hulse_Taylor_PSR, J0737_double_PSR, GW150914_progenitor

6 theorems (T-BS-1 through T-BS-6).
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

BS_CHANNELS = [
    "mass_ratio_balance",
    "orbital_stability",
    "tidal_synchronization",
    "luminosity_balance",
    "spectral_resolution",
    "roche_containment",
    "eccentricity_low",
    "mass_transfer_absence",
]
N_BS_CHANNELS = len(BS_CHANNELS)


@dataclass(frozen=True, slots=True)
class BinaryStarEntity:
    """A binary star system with 8 measurable channels."""

    name: str
    category: str
    mass_ratio_balance: float
    orbital_stability: float
    tidal_synchronization: float
    luminosity_balance: float
    spectral_resolution: float
    roche_containment: float
    eccentricity_low: float
    mass_transfer_absence: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.mass_ratio_balance,
                self.orbital_stability,
                self.tidal_synchronization,
                self.luminosity_balance,
                self.spectral_resolution,
                self.roche_containment,
                self.eccentricity_low,
                self.mass_transfer_absence,
            ]
        )


BS_ENTITIES: tuple[BinaryStarEntity, ...] = (
    # Visual binaries — well-separated, stable
    BinaryStarEntity("Alpha_Centauri", "visual", 0.85, 0.98, 0.30, 0.60, 0.95, 0.99, 0.52, 0.99),
    BinaryStarEntity("Sirius", "visual", 0.42, 0.97, 0.25, 0.05, 0.90, 0.99, 0.41, 0.99),
    BinaryStarEntity("Procyon", "visual", 0.55, 0.96, 0.20, 0.03, 0.85, 0.99, 0.60, 0.99),
    # Eclipsing binaries — close, some mass transfer
    BinaryStarEntity("Algol", "eclipsing", 0.22, 0.88, 0.90, 0.15, 0.80, 0.50, 0.95, 0.30),
    BinaryStarEntity("Beta_Lyrae", "eclipsing", 0.30, 0.82, 0.95, 0.20, 0.55, 0.10, 0.90, 0.10),
    BinaryStarEntity("W_UMa_contact", "eclipsing", 0.85, 0.70, 0.99, 0.75, 0.30, 0.02, 0.99, 0.05),
    # X-ray binaries — accretion-powered, high drift
    BinaryStarEntity("Cygnus_X1", "xray", 0.07, 0.80, 0.85, 0.01, 0.40, 0.20, 0.88, 0.05),
    BinaryStarEntity("Scorpius_X1", "xray", 0.10, 0.75, 0.90, 0.01, 0.30, 0.15, 0.95, 0.02),
    BinaryStarEntity("Her_X1", "xray", 0.15, 0.78, 0.88, 0.02, 0.35, 0.25, 0.60, 0.08),
    # Compact binaries — relativistic, GW emitters
    BinaryStarEntity("Hulse_Taylor_PSR", "compact", 0.96, 0.92, 0.05, 0.01, 0.10, 0.99, 0.38, 0.99),
    BinaryStarEntity("J0737_double_PSR", "compact", 0.93, 0.90, 0.08, 0.90, 0.15, 0.99, 0.12, 0.99),
    BinaryStarEntity("GW150914_progenitor", "compact", 0.82, 0.50, 0.02, 0.80, 0.01, 0.99, 0.05, 0.99),
)


@dataclass(frozen=True, slots=True)
class BSKernelResult:
    """Kernel output for a binary star entity."""

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


def compute_bs_kernel(entity: BinaryStarEntity) -> BSKernelResult:
    """Compute kernel invariants for a binary star entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_BS_CHANNELS) / N_BS_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return BSKernelResult(
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


def compute_all_entities() -> list[BSKernelResult]:
    """Compute kernel for all binary star entities."""
    return [compute_bs_kernel(e) for e in BS_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-BS-1 through T-BS-6
# ---------------------------------------------------------------------------


def verify_t_bs_1(results: list[BSKernelResult]) -> dict:
    """T-BS-1: Visual binaries have highest mean F (most detached, stable)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    vis_f = np.mean(cats["visual"])
    other_f = [np.mean(v) for k, v in cats.items() if k != "visual"]
    passed = vis_f > max(other_f)
    return {
        "name": "T-BS-1",
        "passed": bool(passed),
        "visual_mean_F": float(vis_f),
        "other_max_F": float(max(other_f)),
    }


def verify_t_bs_2(results: list[BSKernelResult]) -> dict:
    """T-BS-2: Compact binaries have highest heterogeneity gap (extreme channels)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F - r.IC)
    compact_delta = np.mean(cats["compact"])
    other_deltas = [np.mean(v) for k, v in cats.items() if k != "compact"]
    passed = compact_delta > max(other_deltas)
    return {
        "name": "T-BS-2",
        "passed": bool(passed),
        "compact_mean_delta": float(compact_delta),
        "other_max_delta": float(max(other_deltas)),
    }


def verify_t_bs_3(results: list[BSKernelResult]) -> dict:
    """T-BS-3: At least 2 distinct regimes present across all systems."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-BS-3",
        "passed": bool(passed),
        "regimes_present": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_bs_4(results: list[BSKernelResult]) -> dict:
    """T-BS-4: Mass transfer systems (eclipsing) have lower IC/F than detached."""
    ecl = [r for r in results if r.category == "eclipsing"]
    vis = [r for r in results if r.category == "visual"]
    ecl_icf = np.mean([r.IC / r.F for r in ecl if r.F > EPSILON])
    vis_icf = np.mean([r.IC / r.F for r in vis if r.F > EPSILON])
    passed = ecl_icf < vis_icf
    return {
        "name": "T-BS-4",
        "passed": bool(passed),
        "eclipsing_IC_F": float(ecl_icf),
        "visual_IC_F": float(vis_icf),
    }


def verify_t_bs_5(results: list[BSKernelResult]) -> dict:
    """T-BS-5: Compact binaries have higher curvature than visual binaries."""
    compact = [r for r in results if r.category == "compact"]
    visual = [r for r in results if r.category == "visual"]
    compact_c = np.mean([r.C for r in compact])
    visual_c = np.mean([r.C for r in visual])
    passed = compact_c > visual_c
    return {
        "name": "T-BS-5",
        "passed": bool(passed),
        "compact_mean_C": float(compact_c),
        "visual_mean_C": float(visual_c),
    }


def verify_t_bs_6(results: list[BSKernelResult]) -> dict:
    """T-BS-6: Alpha_Centauri has highest F (most balanced, stable system)."""
    ac = next(r for r in results if r.name == "Alpha_Centauri")
    max_f = max(r.F for r in results)
    passed = max_f - 1e-12 <= ac.F
    return {
        "name": "T-BS-6",
        "passed": bool(passed),
        "Alpha_Centauri_F": ac.F,
        "max_F": max_f,
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-BS theorems."""
    results = compute_all_entities()
    return [
        verify_t_bs_1(results),
        verify_t_bs_2(results),
        verify_t_bs_3(results),
        verify_t_bs_4(results),
        verify_t_bs_5(results),
        verify_t_bs_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
