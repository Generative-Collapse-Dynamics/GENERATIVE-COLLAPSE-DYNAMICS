"""Security Kernel Closure — Security Domain.

Tier-2 closure mapping 12 canonical security defense systems through
the GCD kernel.  Each system is characterized by 8 channels drawn from
operational security metrics.

Channels (8, equal weights w_i = 1/8):
  0  access_control      — effectiveness of access restriction [0,1]
  1  encryption_strength  — cryptographic protection level [0,1]
  2  monitoring_coverage  — breadth of observation/detection [0,1]
  3  patch_currency       — update / patch freshness [0,1]
  4  auth_depth           — authentication layer depth [0,1]
  5  incident_response    — response capability [0,1]
  6  compliance           — regulatory conformance score [0,1]
  7  threat_detect        — threat detection accuracy [0,1]

12 entities across 4 categories:
  Network  (3): Firewall, IDS_IPS, VPN
  Endpoint (3): Antivirus, EDR, DLP
  Identity (3): MFA, SSO, PAM
  Cloud    (3): WAF, CASB, SIEM

6 theorems (T-SK-1 through T-SK-6).
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

SK_CHANNELS = [
    "access_control",
    "encryption_strength",
    "monitoring_coverage",
    "patch_currency",
    "auth_depth",
    "incident_response",
    "compliance",
    "threat_detect",
]
N_SK_CHANNELS = len(SK_CHANNELS)


@dataclass(frozen=True, slots=True)
class SecurityEntity:
    """A security defense system with 8 measurable channels."""

    name: str
    category: str
    access_control: float
    encryption_strength: float
    monitoring_coverage: float
    patch_currency: float
    auth_depth: float
    incident_response: float
    compliance: float
    threat_detect: float

    def trace_vector(self) -> np.ndarray:
        return np.array(
            [
                self.access_control,
                self.encryption_strength,
                self.monitoring_coverage,
                self.patch_currency,
                self.auth_depth,
                self.incident_response,
                self.compliance,
                self.threat_detect,
            ]
        )


SK_ENTITIES: tuple[SecurityEntity, ...] = (
    # ── Network ──────────────────────────────────────────────────
    # Good monitoring/detection/access; variable auth depth
    SecurityEntity("Firewall", "network", 0.95, 0.70, 0.90, 0.80, 0.30, 0.85, 0.88, 0.92),
    SecurityEntity("IDS_IPS", "network", 0.50, 0.20, 0.95, 0.75, 0.15, 0.92, 0.70, 0.98),
    SecurityEntity("VPN", "network", 0.85, 0.98, 0.60, 0.82, 0.80, 0.65, 0.90, 0.40),
    # ── Endpoint ─────────────────────────────────────────────────
    # Solid local protection; often poor monitoring / auth
    SecurityEntity("Antivirus", "endpoint", 0.60, 0.40, 0.75, 0.55, 0.10, 0.70, 0.80, 0.95),
    SecurityEntity("EDR", "endpoint", 0.75, 0.50, 0.95, 0.80, 0.20, 0.95, 0.85, 0.97),
    SecurityEntity("DLP", "endpoint", 0.92, 0.88, 0.85, 0.60, 0.40, 0.65, 0.95, 0.80),
    # ── Identity ─────────────────────────────────────────────────
    # Excellent auth; more balanced channels overall
    SecurityEntity("MFA", "identity", 0.88, 0.82, 0.65, 0.78, 0.98, 0.60, 0.88, 0.55),
    SecurityEntity("SSO", "identity", 0.80, 0.78, 0.55, 0.72, 0.95, 0.45, 0.85, 0.35),
    SecurityEntity("PAM", "identity", 0.95, 0.80, 0.75, 0.75, 0.97, 0.80, 0.92, 0.60),
    # ── Cloud ────────────────────────────────────────────────────
    # Broad coverage but variable depth
    SecurityEntity("WAF", "cloud", 0.85, 0.65, 0.80, 0.60, 0.50, 0.78, 0.82, 0.88),
    SecurityEntity("CASB", "cloud", 0.70, 0.80, 0.90, 0.55, 0.70, 0.65, 0.78, 0.85),
    SecurityEntity("SIEM", "cloud", 0.55, 0.30, 0.98, 0.70, 0.25, 0.95, 0.75, 0.97),
)


@dataclass(frozen=True, slots=True)
class SKKernelResult:
    """Kernel output for a security entity."""

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


def compute_sk_kernel(entity: SecurityEntity) -> SKKernelResult:
    """Compute kernel invariants for a security entity."""
    c = np.clip(entity.trace_vector(), EPSILON, 1 - EPSILON)
    w = np.ones(N_SK_CHANNELS) / N_SK_CHANNELS
    result = compute_kernel_outputs(c, w)
    F = float(result["F"])
    omega = float(result["omega"])
    S = float(result["S"])
    C = float(result["C"])
    kappa = float(result["kappa"])
    IC = float(result["IC"])
    regime = _classify_regime(omega, F, S, C)
    return SKKernelResult(
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


def compute_all_entities() -> list[SKKernelResult]:
    """Compute kernel for all security entities."""
    return [compute_sk_kernel(e) for e in SK_ENTITIES]


# ---------------------------------------------------------------------------
# Theorems T-SK-1 through T-SK-6
# ---------------------------------------------------------------------------


def verify_t_sk_1(results: list[SKKernelResult]) -> dict:
    """T-SK-1: Identity systems have highest mean F.

    Identity systems (MFA, SSO, PAM) have the most balanced channel
    profiles — high auth_depth compensates for moderate monitoring —
    yielding the highest category mean fidelity.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F)
    id_f = np.mean(cats["identity"])
    other_f = [np.mean(v) for k, v in cats.items() if k != "identity"]
    passed = id_f > max(other_f)
    return {
        "name": "T-SK-1",
        "passed": bool(passed),
        "identity_mean_F": float(id_f),
        "other_max_F": float(max(other_f)),
    }


def verify_t_sk_2(results: list[SKKernelResult]) -> dict:
    """T-SK-2: Endpoint systems have lowest mean IC.

    Endpoint tools typically sacrifice one channel heavily (auth_depth
    for Antivirus at 0.10, EDR at 0.20) — geometric slaughter drags
    IC down while F (arithmetic) stays moderate.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.IC)
    ep_ic = np.mean(cats["endpoint"])
    other_ic = [np.mean(v) for k, v in cats.items() if k != "endpoint"]
    passed = ep_ic < min(other_ic)
    return {
        "name": "T-SK-2",
        "passed": bool(passed),
        "endpoint_mean_IC": float(ep_ic),
        "other_min_IC": float(min(other_ic)),
    }


def verify_t_sk_3(results: list[SKKernelResult]) -> dict:
    """T-SK-3: No entity achieves Stable regime.

    Security systems require channel specialization — no entity
    simultaneously achieves ω < 0.038, F > 0.90, S < 0.15, and
    C < 0.14.  All entities are in Watch or Collapse.
    """
    regimes = {r.regime for r in results}
    passed = "Stable" not in regimes
    return {
        "name": "T-SK-3",
        "passed": bool(passed),
        "regimes_present": sorted(regimes),
    }


def verify_t_sk_4(results: list[SKKernelResult]) -> dict:
    """T-SK-4: PAM has highest IC among all entities.

    PAM has the best-balanced channel profile (minimum channel = 0.60),
    preventing geometric slaughter and producing the highest composite
    integrity.
    """
    best = max(results, key=lambda r: r.IC)
    passed = best.name == "PAM"
    return {
        "name": "T-SK-4",
        "passed": bool(passed),
        "best_name": best.name,
        "best_IC": float(best.IC),
    }


def verify_t_sk_5(results: list[SKKernelResult]) -> dict:
    """T-SK-5: Entities with auth_depth < 0.20 are in Collapse.

    When authentication depth is near ε, the resulting ω exceeds
    0.30, pushing the entity past the Collapse gate.
    """
    low_auth = [e for e in SK_ENTITIES if e.auth_depth < 0.20]
    low_auth_names = {e.name for e in low_auth}
    collapse_status = {}
    for r in results:
        if r.name in low_auth_names:
            collapse_status[r.name] = r.regime == "Collapse"
    passed = len(collapse_status) > 0 and all(collapse_status.values())
    return {
        "name": "T-SK-5",
        "passed": bool(passed),
        "low_auth_entities": sorted(collapse_status.keys()),
        "all_collapse": all(collapse_status.values()),
    }


def verify_t_sk_6(results: list[SKKernelResult]) -> dict:
    """T-SK-6: Identity systems have smallest mean heterogeneity gap.

    Because identity systems are the most balanced (highest min-channel),
    the gap Δ = F − IC is smallest for the identity category.
    """
    cats: dict[str, list[float]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r.F - r.IC)
    id_delta = np.mean(cats["identity"])
    other_delta = [np.mean(v) for k, v in cats.items() if k != "identity"]
    passed = id_delta < min(other_delta)
    return {
        "name": "T-SK-6",
        "passed": bool(passed),
        "identity_mean_delta": float(id_delta),
        "other_min_delta": float(min(other_delta)),
    }


def verify_all_theorems() -> list[dict]:
    """Run all 6 security-kernel theorems and return results."""
    results = compute_all_entities()
    return [
        verify_t_sk_1(results),
        verify_t_sk_2(results),
        verify_t_sk_3(results),
        verify_t_sk_4(results),
        verify_t_sk_5(results),
        verify_t_sk_6(results),
    ]


if __name__ == "__main__":
    print("Security Kernel — 12 entities × 8 channels")
    print("=" * 60)
    for t in verify_all_theorems():
        status = "PASS" if t["passed"] else "FAIL"
        print(f"  {t['name']}: {status}")
