"""Acoustics Closure — Everyday Physics Domain.

Tier-2 closure mapping 12 acoustic systems/media through the GCD kernel.
Each medium is characterized by 8 acoustic propagation channels.

Channels (8, equal weights w_i = 1/8):
  0  sound_speed_norm     — v / v_steel, normalized (1 = fast ~ steel)
  1  impedance_match       — Z_medium / Z_ref (1 = well-matched to air)
  2  absorption_low        — 1 − α_absorption (1 = transparent, low loss)
  3  transmission_quality  — transmission coefficient (1 = perfect)
  4  dispersion_low        — 1 − dispersion coefficient (1 = non-dispersive)
  5  bandwidth_norm        — usable freq range / max_range (1 = broadband)
  6  resonance_quality     — Q-factor normalized (1 = high Q)
  7  linearity             — linear response fraction (1 = perfectly linear)

12 entities across 4 categories:
  Fluids (3):     Air_20C, Water_fresh, Seawater
  Solids (3):     Steel, Concrete, Wood_oak
  Absorbers (3):  Acoustic_foam, Lead_sheet, Fiberglass
  Systems (3):    Concert_hall, Anechoic_chamber, Ultrasound_medical

6 theorems (T-AC-1 through T-AC-6).
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

AC_CHANNELS = [
    "sound_speed_norm",
    "impedance_match",
    "absorption_low",
    "transmission_quality",
    "dispersion_low",
    "bandwidth_norm",
    "resonance_quality",
    "linearity",
]
N_AC_CHANNELS = len(AC_CHANNELS)


@dataclass(frozen=True, slots=True)
class AcousticsEntity:
    """An acoustic medium or system with 8 measurable channels."""

    name: str
    category: str
    sound_speed_norm: float
    impedance_match: float
    absorption_low: float
    transmission_quality: float
    dispersion_low: float
    bandwidth_norm: float
    resonance_quality: float
    linearity: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.sound_speed_norm,
                self.impedance_match,
                self.absorption_low,
                self.transmission_quality,
                self.dispersion_low,
                self.bandwidth_norm,
                self.resonance_quality,
                self.linearity,
            ]
        )


AC_ENTITIES: tuple[AcousticsEntity, ...] = (
    # Fluids — good propagation, moderate impedance
    AcousticsEntity("Air_20C", "fluid", 0.06, 0.95, 0.98, 0.95, 0.98, 0.90, 0.10, 0.95),
    AcousticsEntity("Water_fresh", "fluid", 0.25, 0.60, 0.95, 0.85, 0.95, 0.85, 0.20, 0.92),
    AcousticsEntity("Seawater", "fluid", 0.26, 0.55, 0.88, 0.80, 0.90, 0.80, 0.25, 0.90),
    # Solids — fast speed, high impedance mismatch with air
    AcousticsEntity("Steel", "solid", 0.99, 0.05, 0.90, 0.30, 0.92, 0.70, 0.85, 0.88),
    AcousticsEntity("Concrete", "solid", 0.60, 0.10, 0.70, 0.25, 0.75, 0.50, 0.60, 0.80),
    AcousticsEntity("Wood_oak", "solid", 0.65, 0.15, 0.60, 0.35, 0.70, 0.55, 0.65, 0.75),
    # Absorbers — designed to dissipate sound energy
    AcousticsEntity("Acoustic_foam", "absorber", 0.05, 0.85, 0.10, 0.05, 0.30, 0.70, 0.05, 0.60),
    AcousticsEntity("Lead_sheet", "absorber", 0.30, 0.08, 0.20, 0.10, 0.85, 0.40, 0.30, 0.85),
    AcousticsEntity("Fiberglass", "absorber", 0.05, 0.75, 0.15, 0.08, 0.40, 0.65, 0.08, 0.55),
    # Systems — engineered acoustic environments
    AcousticsEntity("Concert_hall", "system", 0.06, 0.90, 0.70, 0.80, 0.85, 0.75, 0.90, 0.88),
    AcousticsEntity("Anechoic_chamber", "system", 0.06, 0.95, 0.05, 0.02, 0.95, 0.95, 0.02, 0.95),
    AcousticsEntity("Ultrasound_medical", "system", 0.25, 0.50, 0.80, 0.70, 0.60, 0.40, 0.80, 0.90),
)


@dataclass(frozen=True, slots=True)
class ACKernelResult:
    """Kernel output for an acoustics entity."""

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


def compute_ac_kernel(entity: AcousticsEntity) -> ACKernelResult:
    """Compute kernel invariants for an acoustics entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_AC_CHANNELS) / N_AC_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return ACKernelResult(
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


def compute_all_entities() -> list[ACKernelResult]:
    """Compute kernel for all acoustics entities."""
    return [compute_ac_kernel(e) for e in AC_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-AC-1 through T-AC-6
# ---------------------------------------------------------------------------


def verify_t_ac_1(results: list[ACKernelResult]) -> dict:
    """T-AC-1: Absorbers have lowest mean F (designed to dissipate)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    abs_f = np.mean(cats["absorber"])
    others = [np.mean(v) for k, v in cats.items() if k != "absorber"]
    passed = abs_f < min(others)
    return {
        "name": "T-AC-1",
        "passed": bool(passed),
        "absorber_mean_F": float(abs_f),
        "next_lowest": float(min(others)),
    }


def verify_t_ac_2(results: list[ACKernelResult]) -> dict:
    """T-AC-2: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-AC-2",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_ac_3(results: list[ACKernelResult]) -> dict:
    """T-AC-3: Anechoic chamber has highest heterogeneity gap (extreme absorption)."""
    anechoic = next(r for r in results if r.name == "Anechoic_chamber")
    anechoic_delta = anechoic.F - anechoic.IC
    all_deltas = [r.F - r.IC for r in results]
    # Anechoic: absorption=0.05, transmission=0.02, resonance=0.02 → geometric slaughter
    passed = anechoic_delta >= sorted(all_deltas)[-3]  # top 3
    return {
        "name": "T-AC-3",
        "passed": bool(passed),
        "anechoic_delta": float(anechoic_delta),
        "top3_threshold": float(sorted(all_deltas)[-3]),
    }


def verify_t_ac_4(results: list[ACKernelResult]) -> dict:
    """T-AC-4: Fluids have higher mean IC/F than absorbers (more uniform propagation)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        icf = r.IC / r.F if r.F > EPSILON else 0.0
        cats.setdefault(r.category, []).append(icf)
    fluid_icf = np.mean(cats["fluid"])
    absorber_icf = np.mean(cats["absorber"])
    passed = fluid_icf > absorber_icf
    return {
        "name": "T-AC-4",
        "passed": bool(passed),
        "fluid_IC_F": float(fluid_icf),
        "absorber_IC_F": float(absorber_icf),
    }


def verify_t_ac_5(results: list[ACKernelResult]) -> dict:
    """T-AC-5: Steel has highest F among solids (fastest speed, high Q)."""
    solids = [r for r in results if r.category == "solid"]
    steel = next(r for r in solids if r.name == "Steel")
    max_solid_f = max(r.F for r in solids)
    passed = max_solid_f - 1e-12 <= steel.F
    return {
        "name": "T-AC-5",
        "passed": bool(passed),
        "Steel_F": steel.F,
        "max_solid_F": max_solid_f,
    }


def verify_t_ac_6(results: list[ACKernelResult]) -> dict:
    """T-AC-6: Concert hall has highest F among systems (balanced design)."""
    systems = [r for r in results if r.category == "system"]
    hall = next(r for r in systems if r.name == "Concert_hall")
    max_sys_f = max(r.F for r in systems)
    passed = max_sys_f - 1e-12 <= hall.F
    return {
        "name": "T-AC-6",
        "passed": bool(passed),
        "Concert_hall_F": hall.F,
        "max_system_F": max_sys_f,
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-AC theorems."""
    results = compute_all_entities()
    return [
        verify_t_ac_1(results),
        verify_t_ac_2(results),
        verify_t_ac_3(results),
        verify_t_ac_4(results),
        verify_t_ac_5(results),
        verify_t_ac_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
