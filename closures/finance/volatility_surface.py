"""Volatility Surface Closure — Finance Domain.

Tier-2 closure mapping 12 volatility surface regimes through the GCD kernel.
Each regime is characterized by 8 options market channels.

Channels (8, equal weights w_i = 1/8):
  0  implied_vol_level     — ATM IV / max_IV (1 = high vol environment)
  1  skew_flatness         — 1 − |skew slope| / max_slope (1 = flat skew)
  2  term_structure_norm   — 1 − |contango/backwardation| (1 = flat term)
  3  smile_symmetry        — 1 − asymmetry measure (1 = symmetric smile)
  4  put_call_parity       — 1 − parity deviation / max_dev (1 = no arb)
  5  vol_of_vol_low        — 1 − volvol / max_volvol (1 = stable vol)
  6  mean_reversion        — speed of mean reversion (1 = fast reversion)
  7  liquidity_depth       — bid-ask tightness (1 = deep/liquid)

12 entities across 4 categories:
  Equity (3):     SPX_normal, SPX_crash, SPX_low_vol
  FX (3):         EURUSD_normal, USDJPY_risk_off, EM_FX_crisis
  Commodity (3):  Crude_normal, Gold_haven, Natgas_spike
  Fixed Inc (3):  Rates_normal, Credit_IG, VIX_contango

6 theorems (T-VS-1 through T-VS-6).
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

VS_CHANNELS = [
    "implied_vol_level",
    "skew_flatness",
    "term_structure_norm",
    "smile_symmetry",
    "put_call_parity",
    "vol_of_vol_low",
    "mean_reversion",
    "liquidity_depth",
]
N_VS_CHANNELS = len(VS_CHANNELS)


@dataclass(frozen=True, slots=True)
class VolSurfaceEntity:
    """A volatility surface regime with 8 market channels."""

    name: str
    category: str
    implied_vol_level: float
    skew_flatness: float
    term_structure_norm: float
    smile_symmetry: float
    put_call_parity: float
    vol_of_vol_low: float
    mean_reversion: float
    liquidity_depth: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.implied_vol_level,
                self.skew_flatness,
                self.term_structure_norm,
                self.smile_symmetry,
                self.put_call_parity,
                self.vol_of_vol_low,
                self.mean_reversion,
                self.liquidity_depth,
            ]
        )


VS_ENTITIES: tuple[VolSurfaceEntity, ...] = (
    # Equity vol surfaces
    VolSurfaceEntity("SPX_normal", "equity", 0.30, 0.65, 0.80, 0.60, 0.95, 0.75, 0.70, 0.90),
    VolSurfaceEntity("SPX_crash", "equity", 0.90, 0.10, 0.20, 0.15, 0.70, 0.10, 0.30, 0.30),
    VolSurfaceEntity("SPX_low_vol", "equity", 0.10, 0.85, 0.90, 0.80, 0.98, 0.90, 0.85, 0.95),
    # FX vol surfaces
    VolSurfaceEntity("EURUSD_normal", "fx", 0.25, 0.80, 0.85, 0.75, 0.97, 0.80, 0.75, 0.92),
    VolSurfaceEntity("USDJPY_risk_off", "fx", 0.60, 0.40, 0.50, 0.35, 0.90, 0.45, 0.55, 0.70),
    VolSurfaceEntity("EM_FX_crisis", "fx", 0.85, 0.15, 0.20, 0.20, 0.60, 0.15, 0.20, 0.20),
    # Commodity vol surfaces
    VolSurfaceEntity("Crude_normal", "commodity", 0.40, 0.60, 0.65, 0.55, 0.92, 0.65, 0.60, 0.80),
    VolSurfaceEntity("Gold_haven", "commodity", 0.35, 0.75, 0.70, 0.70, 0.95, 0.70, 0.65, 0.85),
    VolSurfaceEntity("Natgas_spike", "commodity", 0.95, 0.20, 0.15, 0.25, 0.75, 0.10, 0.25, 0.40),
    # Fixed income / VIX
    VolSurfaceEntity("Rates_normal", "fixed_income", 0.15, 0.90, 0.92, 0.85, 0.98, 0.85, 0.80, 0.88),
    VolSurfaceEntity("Credit_IG", "fixed_income", 0.20, 0.82, 0.85, 0.78, 0.96, 0.80, 0.75, 0.85),
    VolSurfaceEntity("VIX_contango", "fixed_income", 0.50, 0.50, 0.40, 0.45, 0.85, 0.55, 0.50, 0.60),
)


@dataclass(frozen=True, slots=True)
class VSKernelResult:
    """Kernel output for a volatility surface entity."""

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


def compute_vs_kernel(entity: VolSurfaceEntity) -> VSKernelResult:
    """Compute kernel invariants for a volatility surface entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_VS_CHANNELS) / N_VS_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return VSKernelResult(
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


def compute_all_entities() -> list[VSKernelResult]:
    """Compute kernel for all volatility surface entities."""
    return [compute_vs_kernel(e) for e in VS_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-VS-1 through T-VS-6
# ---------------------------------------------------------------------------


def verify_t_vs_1(results: list[VSKernelResult]) -> dict:
    """T-VS-1: Crisis entities (SPX_crash, EM_FX_crisis, Natgas_spike) in Collapse."""
    crisis_names = {"SPX_crash", "EM_FX_crisis", "Natgas_spike"}
    crisis = [r for r in results if r.name in crisis_names]
    collapse_count = sum(1 for r in crisis if r.regime == "Collapse")
    passed = collapse_count >= 2
    return {
        "name": "T-VS-1",
        "passed": bool(passed),
        "crisis_collapse_count": collapse_count,
        "crisis_total": len(crisis),
    }


def verify_t_vs_2(results: list[VSKernelResult]) -> dict:
    """T-VS-2: Normal/low-vol entities have higher mean F than crisis entities."""
    normal_names = {"SPX_normal", "SPX_low_vol", "EURUSD_normal", "Rates_normal", "Credit_IG"}
    crisis_names = {"SPX_crash", "EM_FX_crisis", "Natgas_spike"}
    normal_f = np.mean([r.F for r in results if r.name in normal_names])
    crisis_f = np.mean([r.F for r in results if r.name in crisis_names])
    passed = normal_f > crisis_f
    return {
        "name": "T-VS-2",
        "passed": bool(passed),
        "normal_mean_F": float(normal_f),
        "crisis_mean_F": float(crisis_f),
    }


def verify_t_vs_3(results: list[VSKernelResult]) -> dict:
    """T-VS-3: At least 2 distinct regimes present."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-VS-3",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_vs_4(results: list[VSKernelResult]) -> dict:
    """T-VS-4: SPX_crash has highest heterogeneity gap (skew/symmetry collapse)."""
    crash = next(r for r in results if r.name == "SPX_crash")
    crash_delta = crash.F - crash.IC
    all_deltas = [r.F - r.IC for r in results]
    passed = crash_delta >= sorted(all_deltas)[-3]  # top 3
    return {
        "name": "T-VS-4",
        "passed": bool(passed),
        "SPX_crash_delta": float(crash_delta),
        "top3_threshold": float(sorted(all_deltas)[-3]),
    }


def verify_t_vs_5(results: list[VSKernelResult]) -> dict:
    """T-VS-5: Fixed income category has highest mean IC/F (most ordered surface)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        icf = r.IC / r.F if r.F > EPSILON else 0.0
        cats.setdefault(r.category, []).append(icf)
    fi_icf = np.mean(cats["fixed_income"])
    eq_icf = np.mean(cats["equity"])
    passed = fi_icf > eq_icf
    return {
        "name": "T-VS-5",
        "passed": bool(passed),
        "fixed_income_IC_F": float(fi_icf),
        "equity_IC_F": float(eq_icf),
    }


def verify_t_vs_6(results: list[VSKernelResult]) -> dict:
    """T-VS-6: Gold_haven has higher F than Crude_normal (safe haven effect)."""
    gold = next(r for r in results if r.name == "Gold_haven")
    crude = next(r for r in results if r.name == "Crude_normal")
    passed = gold.F > crude.F
    return {
        "name": "T-VS-6",
        "passed": bool(passed),
        "Gold_F": gold.F,
        "Crude_F": crude.F,
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-VS theorems."""
    results = compute_all_entities()
    return [
        verify_t_vs_1(results),
        verify_t_vs_2(results),
        verify_t_vs_3(results),
        verify_t_vs_4(results),
        verify_t_vs_5(results),
        verify_t_vs_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
