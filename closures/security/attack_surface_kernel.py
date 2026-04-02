"""Attack Surface Kernel Closure — Security Domain.

Tier-2 closure mapping 12 canonical attack surfaces through the GCD
kernel.  Each surface is characterized by 8 channels measuring its
defensive posture.

Channels (8, equal weights w_i = 1/8):
  0  exposure_area       — size of exposed interface (low = well-shielded → 1.0)
  1  access_complexity   — attack complexity required (high → 1.0)
  2  auth_requirement    — authentication needed (strong → 1.0)
  3  patch_status        — currency of defenses [0,1]
  4  monitoring_depth    — depth of observation [0,1]
  5  redundancy          — backup / failover protection [0,1]
  6  isolation           — network segmentation level [0,1]
  7  logging_coverage    — audit trail quality [0,1]

12 entities across 4 categories:
  Web      (3): Public_API, Web_Portal, CDN_Edge
  Network  (3): Open_Ports, VPN_Gateway, DNS_Server
  Human    (3): Email_Endpoint, Admin_Console, Help_Desk
  Physical (3): Server_Room, USB_Ports, Wireless_AP

6 theorems (T-ATK-1 through T-ATK-6).
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

ATK_CHANNELS = [
    "exposure_area",
    "access_complexity",
    "auth_requirement",
    "patch_status",
    "monitoring_depth",
    "redundancy",
    "isolation",
    "logging_coverage",
]
N_ATK_CHANNELS = len(ATK_CHANNELS)


@dataclass(frozen=True, slots=True)
class AttackSurfaceEntity:
    """An attack surface with 8 measurable channels."""

    name: str
    category: str
    exposure_area: float
    access_complexity: float
    auth_requirement: float
    patch_status: float
    monitoring_depth: float
    redundancy: float
    isolation: float
    logging_coverage: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.exposure_area,
                self.access_complexity,
                self.auth_requirement,
                self.patch_status,
                self.monitoring_depth,
                self.redundancy,
                self.isolation,
                self.logging_coverage,
            ]
        )


ATK_ENTITIES: tuple[AttackSurfaceEntity, ...] = (
    # ── Web ──────────────────────────────────────────────────────
    # Moderate exposure, decent protection, good monitoring
    AttackSurfaceEntity("Public_API", "web", 0.30, 0.40, 0.75, 0.80, 0.85, 0.70, 0.55, 0.90),
    AttackSurfaceEntity("Web_Portal", "web", 0.35, 0.50, 0.80, 0.75, 0.80, 0.65, 0.50, 0.85),
    AttackSurfaceEntity("CDN_Edge", "web", 0.20, 0.35, 0.60, 0.85, 0.90, 0.95, 0.70, 0.75),
    # ── Network ──────────────────────────────────────────────────
    # Highly variable — VPN_Gateway well-protected, Open_Ports not
    AttackSurfaceEntity("Open_Ports", "network", 0.15, 0.30, 0.45, 0.65, 0.70, 0.50, 0.40, 0.60),
    AttackSurfaceEntity("VPN_Gateway", "network", 0.70, 0.80, 0.90, 0.82, 0.75, 0.60, 0.65, 0.80),
    AttackSurfaceEntity("DNS_Server", "network", 0.25, 0.35, 0.30, 0.70, 0.85, 0.80, 0.55, 0.75),
    # ── Human ────────────────────────────────────────────────────
    # Admin_Console is well-defended; Help_Desk/Email are weak
    AttackSurfaceEntity("Email_Endpoint", "human", 0.25, 0.20, 0.55, 0.60, 0.65, 0.40, 0.30, 0.70),
    AttackSurfaceEntity("Admin_Console", "human", 0.80, 0.85, 0.95, 0.90, 0.92, 0.75, 0.70, 0.95),
    AttackSurfaceEntity("Help_Desk", "human", 0.30, 0.25, 0.40, 0.50, 0.55, 0.35, 0.25, 0.50),
    # ── Physical ─────────────────────────────────────────────────
    # Server_Room is fortress; USB_Ports are dangerously exposed
    AttackSurfaceEntity("Server_Room", "physical", 0.90, 0.88, 0.92, 0.95, 0.95, 0.85, 0.90, 0.92),
    AttackSurfaceEntity("USB_Ports", "physical", 0.20, 0.15, 0.25, 0.40, 0.30, 0.20, 0.35, 0.25),
    AttackSurfaceEntity("Wireless_AP", "physical", 0.45, 0.55, 0.65, 0.60, 0.50, 0.40, 0.45, 0.55),
)


@dataclass(frozen=True, slots=True)
class ATKKernelResult:
    """Kernel output for an attack-surface entity."""

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


def compute_atk_kernel(entity: AttackSurfaceEntity) -> ATKKernelResult:
    """Compute kernel invariants for an attack-surface entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_ATK_CHANNELS) / N_ATK_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return ATKKernelResult(
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


def compute_all_entities() -> list[ATKKernelResult]:
    """Compute kernel for all attack-surface entities."""
    return [compute_atk_kernel(e) for e in ATK_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-ATK-1 through T-ATK-6
# ---------------------------------------------------------------------------


def verify_t_atk_1(results: list[ATKKernelResult]) -> dict:
    """T-ATK-1: Server_Room has the highest F among all entities.

    The physical server room has the strongest overall posture — every
    channel is ≥ 0.85, yielding the highest arithmetic mean fidelity.
    """
    best = max(results, key=lambda r: r.F)
    passed = best.name == "Server_Room"
    return {
        "name": "T-ATK-1",
        "passed": bool(passed),
        "best_name": best.name,
        "best_F": float(best.F),
    }


def verify_t_atk_2(results: list[ATKKernelResult]) -> dict:
    """T-ATK-2: USB_Ports has the lowest IC among all entities.

    Every channel of USB_Ports is in the range [0.15, 0.40] — uniformly
    poor defense means the geometric mean yields the lowest IC.
    """
    worst = min(results, key=lambda r: r.IC)
    passed = worst.name == "USB_Ports"
    return {
        "name": "T-ATK-2",
        "passed": bool(passed),
        "worst_name": worst.name,
        "worst_IC": float(worst.IC),
    }


def verify_t_atk_3(results: list[ATKKernelResult]) -> dict:
    """T-ATK-3: Physical surfaces span the widest F range.

    The physical category contains both the best-defended surface
    (Server_Room, F ≈ 0.91) and one of the worst (USB_Ports,
    F ≈ 0.26), producing the widest intra-category spread.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    ranges = {k: max(v) - min(v) for k, v in cats.items()}
    passed = ranges["physical"] > max(v for k, v in ranges.items() if k != "physical")
    return {
        "name": "T-ATK-3",
        "passed": bool(passed),
        "physical_range": float(ranges["physical"]),
        "other_max_range": float(max(v for k, v in ranges.items() if k != "physical")),
    }


def verify_t_atk_4(results: list[ATKKernelResult]) -> dict:
    """T-ATK-4: Web surfaces have smallest F variance.

    All three web surfaces (Public_API, Web_Portal, CDN_Edge) have
    similar channel profiles, yielding the tightest F clustering.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    variances = {k: float(np.var(v)) for k, v in cats.items()}
    passed = variances["web"] < min(v for k, v in variances.items() if k != "web")
    return {
        "name": "T-ATK-4",
        "passed": bool(passed),
        "web_variance": variances["web"],
        "other_min_variance": float(min(v for k, v in variances.items() if k != "web")),
    }


def verify_t_atk_5(results: list[ATKKernelResult]) -> dict:
    """T-ATK-5: No entity achieves Stable regime.

    Attack surfaces are inherently specialized — no surface
    simultaneously satisfies all four Stable gates.
    """
    regimes = {r.regime for r in results}
    passed = "Stable" not in regimes
    return {
        "name": "T-ATK-5",
        "passed": bool(passed),
        "regimes_present": sorted(regimes),
    }


def verify_t_atk_6(results: list[ATKKernelResult]) -> dict:
    """T-ATK-6: USB_Ports has the highest ω (deepest in Collapse).

    USB_Ports has the lowest F (≈ 0.26), so ω = 1 − F ≈ 0.74 is the
    highest drift among all attack-surface entities.
    """
    worst = max(results, key=lambda r: r.omega)
    passed = worst.name == "USB_Ports"
    return {
        "name": "T-ATK-6",
        "passed": bool(passed),
        "worst_name": worst.name,
        "worst_omega": float(worst.omega),
    }


def verify_all_theorems() -> list[dict]:
    """Run all 6 attack-surface theorems and return results."""
    results = compute_all_entities()
    return [
        verify_t_atk_1(results),
        verify_t_atk_2(results),
        verify_t_atk_3(results),
        verify_t_atk_4(results),
        verify_t_atk_5(results),
        verify_t_atk_6(results),
    ]


if __name__ == "__main__":
    print("Attack Surface Kernel — 12 entities × 8 channels")
    print("=" * 60)
    for t in verify_all_theorems():
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  {t['name']}: {status}")
