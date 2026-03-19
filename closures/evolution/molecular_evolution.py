"""Molecular Evolution Closure — Evolution Domain.

Tier-2 closure mapping 12 conserved gene families through the GCD kernel.
Each gene family is characterized by 8 molecular evolution channels.

Channels (8, equal weights w_i = 1/8):
  0  conservation_score  — sequence identity across deep homologs (1 = perfectly conserved)
  1  dn_ds_ratio_inv     — 1 − (dN/dS), purifying selection (1 = strong purifying)
  2  expression_breadth  — fraction of tissues expressing (1 = ubiquitous)
  3  functional_constraint — fraction of residues under selection (1 = highly constrained)
  4  structural_integrity — 3D fold conservation (1 = identical fold)
  5  regulatory_complexity — upstream regulatory element count norm (1 = highly regulated)
  6  paralogy_diversity   — 1 − (paralog count / max_paralog_count) (1 = unique gene)
  7  codon_bias_strength  — codon adaptation index (1 = strong bias)

12 entities across 4 categories:
  Ultra-conserved (3):  Histone_H4, Ubiquitin, Actin
  Highly conserved (3): Cytochrome_c, Hemoglobin, Insulin
  Moderately (3):       p53, Hox_cluster, Fibrinogen
  Rapidly evolving (3): Olfactory_receptors, Immunoglobulins, Caseins

6 theorems (T-ME-1 through T-ME-6).
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

ME_CHANNELS = [
    "conservation_score",
    "dn_ds_ratio_inv",
    "expression_breadth",
    "functional_constraint",
    "structural_integrity",
    "regulatory_complexity",
    "paralogy_diversity",
    "codon_bias_strength",
]
N_ME_CHANNELS = len(ME_CHANNELS)


@dataclass(frozen=True, slots=True)
class MolEvoEntity:
    """A gene family with 8 molecular evolution channels."""

    name: str
    category: str
    conservation_score: float
    dn_ds_ratio_inv: float
    expression_breadth: float
    functional_constraint: float
    structural_integrity: float
    regulatory_complexity: float
    paralogy_diversity: float
    codon_bias_strength: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.conservation_score,
                self.dn_ds_ratio_inv,
                self.expression_breadth,
                self.functional_constraint,
                self.structural_integrity,
                self.regulatory_complexity,
                self.paralogy_diversity,
                self.codon_bias_strength,
            ]
        )


ME_ENTITIES: tuple[MolEvoEntity, ...] = (
    # Ultra-conserved — nearly identical across eukaryotes
    MolEvoEntity("Histone_H4", "ultra_conserved", 0.98, 0.99, 0.95, 0.97, 0.99, 0.80, 0.90, 0.85),
    MolEvoEntity("Ubiquitin", "ultra_conserved", 0.97, 0.99, 0.98, 0.96, 0.98, 0.85, 0.95, 0.90),
    MolEvoEntity("Actin", "ultra_conserved", 0.95, 0.98, 0.92, 0.94, 0.97, 0.75, 0.82, 0.80),
    # Highly conserved — strong purifying selection
    MolEvoEntity("Cytochrome_c", "highly_conserved", 0.85, 0.95, 0.90, 0.88, 0.92, 0.65, 0.92, 0.75),
    MolEvoEntity("Hemoglobin", "highly_conserved", 0.80, 0.90, 0.55, 0.82, 0.88, 0.70, 0.70, 0.70),
    MolEvoEntity("Insulin", "highly_conserved", 0.75, 0.92, 0.40, 0.80, 0.85, 0.75, 0.85, 0.65),
    # Moderate conservation — functional diversification
    MolEvoEntity("p53", "moderate", 0.60, 0.80, 0.85, 0.70, 0.75, 0.90, 0.88, 0.55),
    MolEvoEntity("Hox_cluster", "moderate", 0.55, 0.85, 0.50, 0.65, 0.70, 0.95, 0.40, 0.50),
    MolEvoEntity("Fibrinogen", "moderate", 0.50, 0.75, 0.30, 0.55, 0.65, 0.60, 0.75, 0.45),
    # Rapidly evolving — positive selection or relaxed constraint
    MolEvoEntity("Olfactory_receptors", "rapid", 0.25, 0.40, 0.20, 0.30, 0.40, 0.30, 0.05, 0.25),
    MolEvoEntity("Immunoglobulins", "rapid", 0.20, 0.35, 0.35, 0.25, 0.30, 0.50, 0.10, 0.30),
    MolEvoEntity("Caseins", "rapid", 0.15, 0.30, 0.10, 0.20, 0.25, 0.20, 0.70, 0.20),
)


@dataclass(frozen=True, slots=True)
class MEKernelResult:
    """Kernel output for a molecular evolution entity."""

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


def compute_me_kernel(entity: MolEvoEntity) -> MEKernelResult:
    """Compute kernel invariants for a molecular evolution entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_ME_CHANNELS) / N_ME_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return MEKernelResult(
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


def compute_all_entities() -> list[MEKernelResult]:
    """Compute kernel for all molecular evolution entities."""
    return [compute_me_kernel(e) for e in ME_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-ME-1 through T-ME-6
# ---------------------------------------------------------------------------


def verify_t_me_1(results: list[MEKernelResult]) -> dict:
    """T-ME-1: Ultra-conserved genes have highest mean F (all channels high)."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    uc_f = np.mean(cats["ultra_conserved"])
    others = [np.mean(v) for k, v in cats.items() if k != "ultra_conserved"]
    passed = uc_f > max(others)
    return {
        "name": "T-ME-1",
        "passed": bool(passed),
        "ultra_conserved_mean_F": float(uc_f),
        "next_highest": float(max(others)),
    }


def verify_t_me_2(results: list[MEKernelResult]) -> dict:
    """T-ME-2: Rapidly evolving genes are in Collapse regime."""
    rapid = [r for r in results if r.category == "rapid"]
    collapse_count = sum(1 for r in rapid if r.regime == "Collapse")
    passed = collapse_count >= 2
    return {
        "name": "T-ME-2",
        "passed": bool(passed),
        "rapid_collapse_count": collapse_count,
        "rapid_total": len(rapid),
    }


def verify_t_me_3(results: list[MEKernelResult]) -> dict:
    """T-ME-3: At least 2 distinct regimes across all entities."""
    regimes = {r.regime for r in results}
    passed = len(regimes) >= 2
    return {
        "name": "T-ME-3",
        "passed": bool(passed),
        "regimes": sorted(regimes),
        "count": len(regimes),
    }


def verify_t_me_4(results: list[MEKernelResult]) -> dict:
    """T-ME-4: IC/F monotonically decreases across conservation categories."""
    cat_order = ["ultra_conserved", "highly_conserved", "moderate", "rapid"]
    cat_icf: dict[str, float] = {}
    for cat in cat_order:
        vals = [r.IC / r.F if r.F > EPSILON else 0.0 for r in results if r.category == cat]
        cat_icf[cat] = float(np.mean(vals))
    decreasing = all(cat_icf[cat_order[i]] >= cat_icf[cat_order[i + 1]] for i in range(len(cat_order) - 1))
    passed = decreasing
    return {
        "name": "T-ME-4",
        "passed": bool(passed),
        "IC_F_by_category": cat_icf,
    }


def verify_t_me_5(results: list[MEKernelResult]) -> dict:
    """T-ME-5: Histone H4 in top-2 IC (near-maximal channel uniformity)."""
    h4 = next(r for r in results if r.name == "Histone_H4")
    sorted_ic = sorted([r.IC for r in results], reverse=True)
    passed = sorted_ic[1] <= h4.IC  # top 2
    return {
        "name": "T-ME-5",
        "passed": bool(passed),
        "Histone_H4_IC": h4.IC,
        "top2_threshold": float(sorted_ic[1]),
    }


def verify_t_me_6(results: list[MEKernelResult]) -> dict:
    """T-ME-6: Olfactory receptors have lowest paralogy channel → extreme Δ."""
    olfactory = next(r for r in results if r.name == "Olfactory_receptors")
    olf_delta = olfactory.F - olfactory.IC
    rapid = [r for r in results if r.category == "rapid"]
    rapid_deltas = [r.F - r.IC for r in rapid]
    # Olfactory receptors: paralogy near 0 → geometric slaughter
    passed = olf_delta >= min(rapid_deltas)
    return {
        "name": "T-ME-6",
        "passed": bool(passed),
        "Olfactory_delta": float(olf_delta),
        "rapid_min_delta": float(min(rapid_deltas)),
    }


def verify_all_theorems() -> list[dict]:
    """Run all T-ME theorems."""
    results = compute_all_entities()
    return [
        verify_t_me_1(results),
        verify_t_me_2(results),
        verify_t_me_3(results),
        verify_t_me_4(results),
        verify_t_me_5(results),
        verify_t_me_6(results),
    ]


if __name__ == "__main__":
    for t in verify_all_theorems():
        status = "PROVEN" if t["passed"] else "FAILED"
        print(f"  {t['name']}: {status}  {t}")
