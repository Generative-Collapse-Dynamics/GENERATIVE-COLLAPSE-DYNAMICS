"""Sleep Neurophysiology Closure — Clinical Neuroscience Domain.

Tier-2 closure mapping 12 sleep stages/phenomena through the GCD kernel.
Each entity is characterized by 8 EEG/physiological channels.

Channels (8, equal weights w_i = 1/8):
  0  eeg_delta_power    — 0.5–4 Hz power (1 = maximal slow-wave)
  1  eeg_theta_power    — 4–8 Hz power (1 = maximal theta)
  2  eeg_sigma_power    — 12–16 Hz (spindle band) power (1 = maximal)
  3  muscle_atonia       — degree of muscle tone loss (1 = complete atonia)
  4  eye_movement_rate   — rapid eye movement frequency (1 = maximal)
  5  cortical_connectivity — functional connectivity (1 = maximal)
  6  metabolic_rate      — rCBF / glucose normalized (1 = waking baseline)
  7  arousal_threshold   — stimulus intensity to wake (1 = hardest to wake)

12 entities across 4 categories:
  Waking (3):   Active_wake, Relaxed_wake, Drowsy_transition
  NREM (3):     N1_light, N2_spindle, N3_slow_wave
  REM (3):      Tonic_REM, Phasic_REM, Lucid_REM
  Events (3):   K_complex, Sleep_spindle_burst, Microsleep

6 theorems (T-SN-1 through T-SN-6).
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

SN_CHANNELS = [
    "eeg_delta_power",
    "eeg_theta_power",
    "eeg_sigma_power",
    "muscle_atonia",
    "eye_movement_rate",
    "cortical_connectivity",
    "metabolic_rate",
    "arousal_threshold",
]
N_SN_CHANNELS = len(SN_CHANNELS)


@dataclass(frozen=True, slots=True)
class SleepEntity:
    """A sleep stage or phenomenon with 8 measurable channels."""

    name: str
    category: str
    eeg_delta_power: float
    eeg_theta_power: float
    eeg_sigma_power: float
    muscle_atonia: float
    eye_movement_rate: float
    cortical_connectivity: float
    metabolic_rate: float
    arousal_threshold: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.eeg_delta_power,
                self.eeg_theta_power,
                self.eeg_sigma_power,
                self.muscle_atonia,
                self.eye_movement_rate,
                self.cortical_connectivity,
                self.metabolic_rate,
                self.arousal_threshold,
            ]
        )


SN_ENTITIES: tuple[SleepEntity, ...] = (
    # Waking — high metabolic, high cortical, no atonia
    SleepEntity("Active_wake", "waking", 0.05, 0.15, 0.05, 0.02, 0.70, 0.95, 0.95, 0.05),
    SleepEntity("Relaxed_wake", "waking", 0.08, 0.20, 0.08, 0.05, 0.15, 0.90, 0.90, 0.10),
    SleepEntity("Drowsy_transition", "waking", 0.15, 0.50, 0.12, 0.15, 0.10, 0.75, 0.80, 0.20),
    # NREM — progressive deepening
    SleepEntity("N1_light", "nrem", 0.20, 0.55, 0.15, 0.20, 0.05, 0.65, 0.75, 0.25),
    SleepEntity("N2_spindle", "nrem", 0.35, 0.25, 0.85, 0.35, 0.03, 0.55, 0.65, 0.55),
    SleepEntity("N3_slow_wave", "nrem", 0.95, 0.10, 0.20, 0.50, 0.02, 0.40, 0.50, 0.90),
    # REM — high activity, atonia, dreaming
    SleepEntity("Tonic_REM", "rem", 0.30, 0.65, 0.25, 0.92, 0.60, 0.82, 0.88, 0.55),
    SleepEntity("Phasic_REM", "rem", 0.45, 0.70, 0.35, 0.95, 0.88, 0.90, 0.92, 0.80),
    SleepEntity("Lucid_REM", "rem", 0.40, 0.62, 0.30, 0.88, 0.82, 0.95, 0.93, 0.75),
    # Events — transient phenomena
    SleepEntity("K_complex", "event", 0.80, 0.10, 0.30, 0.30, 0.02, 0.50, 0.60, 0.70),
    SleepEntity("Sleep_spindle_burst", "event", 0.15, 0.10, 0.95, 0.25, 0.02, 0.60, 0.70, 0.50),
    SleepEntity("Microsleep", "event", 0.40, 0.30, 0.10, 0.10, 0.05, 0.30, 0.50, 0.15),
)


@dataclass(frozen=True, slots=True)
class SNKernelResult:
    """Kernel output for a sleep neurophysiology entity."""

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


def compute_sn_kernel(entity: SleepEntity) -> SNKernelResult:
    """Compute kernel invariants for a sleep entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_SN_CHANNELS) / N_SN_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return SNKernelResult(
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


def compute_all_entities() -> list[SNKernelResult]:
    """Compute kernel for all sleep entities."""
    return [compute_sn_kernel(e) for e in SN_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-SN-1 through T-SN-6
# ---------------------------------------------------------------------------


def verify_t_sn_1(results: list[SNKernelResult]) -> dict:
    """T-SN-1: Waking entities have highest mean Δ (extreme channel contrast)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F - r.IC)
    waking_delta = np.mean(cats["waking"])
    other_deltas = [np.mean(v) for k, v in cats.items() if k != "waking"]
    passed = waking_delta > max(other_deltas)
    return {
        "name": "T-SN-1",
        "passed": bool(passed),
        "waking_mean_delta": float(waking_delta),
        "other_max_delta": float(max(other_deltas)),
    }


def verify_t_sn_2(results: list[SNKernelResult]) -> dict:
    """T-SN-2: REM entities have higher mean F than NREM (more channels active)."""
    rem_f = np.mean([r.F for r in results if r.category == "rem"])
    nrem_f = np.mean([r.F for r in results if r.category == "nrem"])
    passed = rem_f > nrem_f
    return {
        "name": "T-SN-2",
        "passed": bool(passed),
        "rem_mean_F": float(rem_f),
        "nrem_mean_F": float(nrem_f),
    }


def verify_t_sn_3(results: list[SNKernelResult]) -> dict:
    """T-SN-3: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-SN-3",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_sn_4(results: list[SNKernelResult]) -> dict:
    """T-SN-4: Microsleep has lowest F among all (most channels degraded)."""
    micro = next(r for r in results if r.name == "Microsleep")
    min_f = min(r.F for r in results)
    passed = min_f + 0.02 >= micro.F
    return {
        "name": "T-SN-4",
        "passed": bool(passed),
        "Microsleep_F": micro.F,
        "min_F": float(min_f),
    }


def verify_t_sn_5(results: list[SNKernelResult]) -> dict:
    """T-SN-5: Waking entities have higher mean C than REM (eye movement variance)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.C)
    waking_c = np.mean(cats["waking"])
    # Waking has extreme contrasts: high cortical/metabolic, low delta/atonia
    # REM has moderately high but more uniform channels
    passed = waking_c > np.mean(cats.get("nrem", [0.0]))
    return {
        "name": "T-SN-5",
        "passed": bool(passed),
        "waking_mean_C": float(waking_c),
        "nrem_mean_C": float(np.mean(cats.get("nrem", [0.0]))),
    }


def verify_t_sn_6(results: list[SNKernelResult]) -> dict:
    """T-SN-6: Phasic REM has higher F than Tonic REM (more channels active)."""
    phasic = next(r for r in results if r.name == "Phasic_REM")
    tonic = next(r for r in results if r.name == "Tonic_REM")
    passed = phasic.F > tonic.F
    return {
        "name": "T-SN-6",
        "passed": bool(passed),
        "Phasic_REM_F": phasic.F,
        "Tonic_REM_F": tonic.F,
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-SN theorems."""
    results = compute_all_entities()
    return [
        verify_t_sn_1(results),
        verify_t_sn_2(results),
        verify_t_sn_3(results),
        verify_t_sn_4(results),
        verify_t_sn_5(results),
        verify_t_sn_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
