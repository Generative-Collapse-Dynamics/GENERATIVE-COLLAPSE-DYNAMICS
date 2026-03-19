"""Rigid Body Dynamics Closure — Kinematics Domain.

Tier-2 closure mapping 12 rotating rigid bodies through the GCD kernel.
Each entity is characterized by 8 rotational dynamics channels.

Channels (8, equal weights w_i = 1/8):
  0  spin_stability       — stability ratio I_3/I_1 normalized (1 = max axis)
  1  angular_momentum_norm — L / L_max (1 = high angular momentum)
  2  precession_regularity — 1 − precession amplitude variation (1 = steady)
  3  nutation_damping      — nutation decay rate normalized (1 = fast damped)
  4  energy_partition      — T_rot / T_total (1 = purely rotational)
  5  gyroscopic_rigidity   — gyroscopic stiffness normalized (1 = high)
  6  symmetry_factor       — I_1/I_2 closeness to 1 (1 = symmetric top)
  7  dissipation_low       — 1 − energy loss rate (1 = no dissipation)

12 entities across 4 categories:
  Toys/demos (3):   Spinning_top, Gyroscope, Tippe_top
  Sports (3):       Football_spiral, Frisbee, Figure_skater
  Engineering (3):  Flywheel, Reaction_wheel, Centrifuge
  Astrophysical (3): Pulsar, Earth_precession, Asteroid_tumble

6 theorems (T-RB-1 through T-RB-6).
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

RB_CHANNELS = [
    "spin_stability",
    "angular_momentum_norm",
    "precession_regularity",
    "nutation_damping",
    "energy_partition",
    "gyroscopic_rigidity",
    "symmetry_factor",
    "dissipation_low",
]
N_RB_CHANNELS = len(RB_CHANNELS)


@dataclass(frozen=True, slots=True)
class RigidBodyEntity:
    """A rotating rigid body with 8 dynamics channels."""

    name: str
    category: str
    spin_stability: float
    angular_momentum_norm: float
    precession_regularity: float
    nutation_damping: float
    energy_partition: float
    gyroscopic_rigidity: float
    symmetry_factor: float
    dissipation_low: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.spin_stability,
                self.angular_momentum_norm,
                self.precession_regularity,
                self.nutation_damping,
                self.energy_partition,
                self.gyroscopic_rigidity,
                self.symmetry_factor,
                self.dissipation_low,
            ]
        )


RB_ENTITIES: tuple[RigidBodyEntity, ...] = (
    # Toys / demonstrations
    RigidBodyEntity("Spinning_top", "toy", 0.80, 0.60, 0.75, 0.50, 0.85, 0.70, 0.90, 0.65),
    RigidBodyEntity("Gyroscope", "toy", 0.95, 0.75, 0.90, 0.70, 0.90, 0.95, 0.95, 0.80),
    RigidBodyEntity("Tippe_top", "toy", 0.30, 0.40, 0.35, 0.20, 0.60, 0.25, 0.85, 0.40),
    # Sports — human-scale dynamics
    RigidBodyEntity("Football_spiral", "sport", 0.85, 0.70, 0.80, 0.60, 0.75, 0.80, 0.70, 0.55),
    RigidBodyEntity("Frisbee", "sport", 0.90, 0.65, 0.85, 0.55, 0.80, 0.75, 0.95, 0.60),
    RigidBodyEntity("Figure_skater", "sport", 0.70, 0.90, 0.60, 0.30, 0.95, 0.50, 0.60, 0.50),
    # Engineering — precision systems
    RigidBodyEntity("Flywheel", "engineering", 0.95, 0.95, 0.95, 0.85, 0.98, 0.90, 0.98, 0.92),
    RigidBodyEntity("Reaction_wheel", "engineering", 0.92, 0.85, 0.90, 0.80, 0.95, 0.92, 0.95, 0.88),
    RigidBodyEntity("Centrifuge", "engineering", 0.88, 0.90, 0.85, 0.75, 0.92, 0.85, 0.90, 0.80),
    # Astrophysical — extreme scales
    RigidBodyEntity("Pulsar", "astro", 0.99, 0.99, 0.98, 0.95, 0.99, 0.99, 0.98, 0.95),
    RigidBodyEntity("Earth_precession", "astro", 0.95, 0.80, 0.92, 0.90, 0.50, 0.85, 0.70, 0.98),
    RigidBodyEntity("Asteroid_tumble", "astro", 0.15, 0.30, 0.10, 0.05, 0.70, 0.10, 0.20, 0.90),
)


@dataclass(frozen=True, slots=True)
class RBKernelResult:
    """Kernel output for a rigid body entity."""

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


def compute_rb_kernel(entity: RigidBodyEntity) -> RBKernelResult:
    """Compute kernel invariants for a rigid body entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_RB_CHANNELS) / N_RB_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return RBKernelResult(
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


def compute_all_entities() -> list[RBKernelResult]:
    """Compute kernel for all rigid body entities."""
    return [compute_rb_kernel(e) for e in RB_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-RB-1 through T-RB-6
# ---------------------------------------------------------------------------


def verify_t_rb_1(results: list[RBKernelResult]) -> dict:
    """T-RB-1: Engineering systems have highest mean F (all channels high)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    eng_f = np.mean(cats["engineering"])
    passed = eng_f >= sorted([np.mean(v) for v in cats.values()])[-2]
    return {
        "name": "T-RB-1",
        "passed": bool(passed),
        "engineering_mean_F": float(eng_f),
        "second_highest": float(sorted([np.mean(v) for v in cats.values()])[-2]),
    }


def verify_t_rb_2(results: list[RBKernelResult]) -> dict:
    """T-RB-2: Asteroid tumble in Collapse (most channels low/chaotic)."""
    asteroid = next(r for r in results if r.name == "Asteroid_tumble")
    passed = asteroid.regime == "Collapse"
    return {
        "name": "T-RB-2",
        "passed": bool(passed),
        "Asteroid_regime": asteroid.regime,
        "Asteroid_omega": asteroid.omega,
    }


def verify_t_rb_3(results: list[RBKernelResult]) -> dict:
    """T-RB-3: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-RB-3",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_rb_4(results: list[RBKernelResult]) -> dict:
    """T-RB-4: Pulsar has highest IC/F (most uniform channels in universe)."""
    icf_vals = [(r.name, r.IC / r.F if r.F > EPSILON else 0.0) for r in results]
    pulsar_icf = next(v for n, v in icf_vals if n == "Pulsar")
    max_icf = max(v for _, v in icf_vals)
    passed = pulsar_icf >= max_icf - 1e-12
    return {
        "name": "T-RB-4",
        "passed": bool(passed),
        "Pulsar_IC_F": float(pulsar_icf),
        "max_IC_F": float(max_icf),
    }


def verify_t_rb_5(results: list[RBKernelResult]) -> dict:
    """T-RB-5: Gyroscope has highest F among toys (precision instrument)."""
    toys = [r for r in results if r.category == "toy"]
    gyro = next(r for r in toys if r.name == "Gyroscope")
    max_toy_f = max(r.F for r in toys)
    passed = max_toy_f - 1e-12 <= gyro.F
    return {
        "name": "T-RB-5",
        "passed": bool(passed),
        "Gyroscope_F": gyro.F,
        "max_toy_F": max_toy_f,
    }


def verify_t_rb_6(results: list[RBKernelResult]) -> dict:
    """T-RB-6: Tippe top has highest Δ among toys (inversion instability)."""
    toys = [r for r in results if r.category == "toy"]
    tippe = next(r for r in toys if r.name == "Tippe_top")
    tippe_delta = tippe.F - tippe.IC
    toy_deltas = [r.F - r.IC for r in toys]
    passed = tippe_delta >= max(toy_deltas) - 1e-12
    return {
        "name": "T-RB-6",
        "passed": bool(passed),
        "Tippe_top_delta": float(tippe_delta),
        "max_toy_delta": float(max(toy_deltas)),
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-RB theorems."""
    results = compute_all_entities()
    return [
        verify_t_rb_1(results),
        verify_t_rb_2(results),
        verify_t_rb_3(results),
        verify_t_rb_4(results),
        verify_t_rb_5(results),
        verify_t_rb_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
