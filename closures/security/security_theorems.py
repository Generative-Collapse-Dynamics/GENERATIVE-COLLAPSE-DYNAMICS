"""Security Theorems Closure — Security Domain.

Tier-2 closure proving 10 cross-cutting theorems about the security
kernel (``security_kernel.py``).  These theorems operate on the
computed kernel outputs for all 12 security entities and verify
structural properties that emerge from the channel data.

10 theorems (T-SEC-1 through T-SEC-10).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats  # type: ignore[import-untyped]

_WORKSPACE = Path(__file__).resolve().parents[2]
for _p in [str(_WORKSPACE / "src"), str(_WORKSPACE)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from closures.security.security_kernel import (  # noqa: E402
    SK_ENTITIES,
    SKKernelResult,
    compute_all_entities,
)

# ---------------------------------------------------------------------------
# Theorems T-SEC-1 through T-SEC-10
# ---------------------------------------------------------------------------


def verify_t_sec_1(results: list[SKKernelResult]) -> dict:
    """T-SEC-1: Duality identity F + ω = 1 holds exactly."""
    residuals = [abs(r.F + r.omega - 1.0) for r in results]
    passed = all(r < 1e-12 for r in residuals)
    return {
        "name": "T-SEC-1",
        "passed": bool(passed),
        "max_residual": float(max(residuals)),
    }


def verify_t_sec_2(results: list[SKKernelResult]) -> dict:
    """T-SEC-2: Integrity bound IC ≤ F holds for all entities."""
    violations = [(r.name, r.IC - r.F) for r in results if r.IC > r.F + 1e-12]
    passed = len(violations) == 0
    return {
        "name": "T-SEC-2",
        "passed": bool(passed),
        "violations": violations,
    }


def verify_t_sec_3(results: list[SKKernelResult]) -> dict:
    """T-SEC-3: Log-integrity relation IC = exp(κ) holds for all entities."""
    residuals = [abs(r.IC - np.exp(r.kappa)) for r in results]
    passed = all(r < 1e-10 for r in residuals)
    return {
        "name": "T-SEC-3",
        "passed": bool(passed),
        "max_residual": float(max(residuals)),
    }


def verify_t_sec_4(results: list[SKKernelResult]) -> dict:
    """T-SEC-4: Identity category has highest mean IC.

    The balanced channel profiles of identity systems produce the
    highest geometric-mean integrity across all categories.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.IC)
    id_ic = float(np.mean(cats["identity"]))
    other_ic = {k: float(np.mean(v)) for k, v in cats.items() if k != "identity"}
    passed = id_ic > max(other_ic.values())
    return {
        "name": "T-SEC-4",
        "passed": bool(passed),
        "identity_mean_IC": id_ic,
        "other_mean_IC": other_ic,
    }


def verify_t_sec_5(results: list[SKKernelResult]) -> dict:
    """T-SEC-5: Min-channel value positively correlates with IC (ρ > 0.5).

    Geometric slaughter ensures that the entity's weakest channel is
    the dominant predictor of composite integrity.
    """
    min_channels = [float(np.min(e.trace_vector())) for e in SK_ENTITIES]
    ic_values = [r.IC for r in results]
    result = sp_stats.spearmanr(min_channels, ic_values)
    rho = float(result.statistic)  # type: ignore[union-attr]
    passed = rho > 0.5
    return {
        "name": "T-SEC-5",
        "passed": bool(passed),
        "spearman_rho": rho,
    }


def verify_t_sec_6(results: list[SKKernelResult]) -> dict:
    """T-SEC-6: Heterogeneity gap Δ = F − IC is strictly positive for all."""
    gaps = [(r.name, r.F - r.IC) for r in results]
    passed = all(g > 0 for _, g in gaps)
    return {
        "name": "T-SEC-6",
        "passed": bool(passed),
        "min_gap": float(min(g for _, g in gaps)),
        "max_gap": float(max(g for _, g in gaps)),
    }


def verify_t_sec_7(results: list[SKKernelResult]) -> dict:
    """T-SEC-7: IDS_IPS has the highest curvature C.

    IDS/IPS has extremely heterogeneous channels — near-perfect
    detection (0.98) alongside near-ε auth (0.15) — producing the
    largest signal dispersion.
    """
    best = max(results, key=lambda r: r.C)
    passed = best.name == "IDS_IPS"
    return {
        "name": "T-SEC-7",
        "passed": bool(passed),
        "best_name": best.name,
        "best_C": float(best.C),
    }


def verify_t_sec_8(results: list[SKKernelResult]) -> dict:
    """T-SEC-8: Network and identity categories each have ≥1 entity with F > 0.75."""
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    net_ok = any(f > 0.75 for f in cats["network"])
    id_ok = any(f > 0.75 for f in cats["identity"])
    passed = net_ok and id_ok
    return {
        "name": "T-SEC-8",
        "passed": bool(passed),
        "network_max_F": float(max(cats["network"])),
        "identity_max_F": float(max(cats["identity"])),
    }


def verify_t_sec_9(results: list[SKKernelResult]) -> dict:
    """T-SEC-9: Cross-category IC ordering Identity > Cloud > Network > Endpoint."""
    cats: dict[str, float] = {}
    by_cat: dict[str, list[float]] = {}
    for r in results:
        by_cat.setdefault(r.category, []).append(r.IC)
    for k, v in by_cat.items():
        cats[k] = float(np.mean(v))
    ordering = cats["identity"] > cats["cloud"] > cats["network"] > cats["endpoint"]
    passed = bool(ordering)
    return {
        "name": "T-SEC-9",
        "passed": passed,
        "category_mean_IC": cats,
    }


def verify_t_sec_10(results: list[SKKernelResult]) -> dict:
    """T-SEC-10: All Collapse-regime entities have IC below the global mean.

    Collapse occurs when ω ≥ 0.30 (low F).  Those same entities have
    the most channel heterogeneity, dragging IC below the fleet average.
    """
    mean_ic = float(np.mean([r.IC for r in results]))
    collapse_ents = [r for r in results if r.regime == "Collapse"]
    all_below = all(mean_ic > r.IC for r in collapse_ents)
    passed = len(collapse_ents) > 0 and all_below
    return {
        "name": "T-SEC-10",
        "passed": bool(passed),
        "global_mean_IC": mean_ic,
        "collapse_count": len(collapse_ents),
        "all_below_mean": all_below,
    }


def verify_all_theorems() -> list[dict]:
    """Run all 10 security theorems and return results."""
    results = compute_all_entities()
    return [
        verify_t_sec_1(results),
        verify_t_sec_2(results),
        verify_t_sec_3(results),
        verify_t_sec_4(results),
        verify_t_sec_5(results),
        verify_t_sec_6(results),
        verify_t_sec_7(results),
        verify_t_sec_8(results),
        verify_t_sec_9(results),
        verify_t_sec_10(results),
    ]


if __name__ == "__main__":
    print("Security Theorems — 10 cross-cutting theorems")
    print("=" * 60)
    for t in verify_all_theorems():
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  {t['name']}: {status}  {t}")
