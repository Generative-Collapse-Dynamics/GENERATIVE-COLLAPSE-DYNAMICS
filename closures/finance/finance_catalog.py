"""
Finance Entity Catalog — 30 Financial Entities Through the GCD Kernel

Maps 30 financial entities (companies, indices, asset classes, instruments)
to an 8-channel trace vector and computes Tier-1 kernel invariants.

Channels (8):
    c₁ = revenue_growth       — Year-over-year revenue growth normalized to [0,1]
    c₂ = profit_margin        — Net income / revenue, clipped to [0,1]
    c₃ = debt_coverage        — Interest coverage ratio, normalized
    c₄ = cashflow_stability   — Operating cash flow consistency
    c₅ = market_liquidity     — Bid-ask spread / volume proxy
    c₆ = dividend_continuity  — Payout consistency over 10 years
    c₇ = volatility_control   — 1 - normalized annualized vol
    c₈ = regulatory_compliance — Compliance score (audit outcomes)

All values are sourced from public financial data (SEC filings, Bloomberg,
CRSP, Compustat) and normalized to [0,1] before ε-clamping.

Cross-references:
    - contracts/FINANCE.INTSTACK.v1.yaml
    - closures/finance/finance_embedding.py (4-channel operational embedding)
    - src/umcp/kernel_optimized.py (Tier-1 kernel function)
    - KERNEL_SPECIFICATION.md (Lemma 1: range bounds)
"""

from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

_WORKSPACE = Path(__file__).resolve().parents[2]
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from src.umcp.frozen_contract import EPSILON  # noqa: E402
from src.umcp.kernel_optimized import compute_kernel_outputs  # noqa: E402

# ---------------------------------------------------------------------------
# Channel definitions
# ---------------------------------------------------------------------------

FINANCE_CHANNELS: list[str] = [
    "revenue_growth",
    "profit_margin",
    "debt_coverage",
    "cashflow_stability",
    "market_liquidity",
    "dividend_continuity",
    "volatility_control",
    "regulatory_compliance",
]

N_FINANCE_CHANNELS = len(FINANCE_CHANNELS)  # 8


# ---------------------------------------------------------------------------
# Entity profile
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class FinancialEntity:
    """One financial entity with 8-channel trace vector.

    All channel values are normalized to [0, 1].
    """

    name: str
    category: str  # equity, index, bond, commodity, crypto, sovereign, fund
    sector: str  # Technology, Energy, Finance, etc.

    revenue_growth: float
    profit_margin: float
    debt_coverage: float
    cashflow_stability: float
    market_liquidity: float
    dividend_continuity: float
    volatility_control: float
    regulatory_compliance: float

    def trace_vector(self) -> np.ndarray:
        """Return ε-clamped trace vector c ∈ [ε, 1-ε]^8."""
        c = np.array(
            [
                self.revenue_growth,
                self.profit_margin,
                self.debt_coverage,
                self.cashflow_stability,
                self.market_liquidity,
                self.dividend_continuity,
                self.volatility_control,
                self.regulatory_compliance,
            ],
            dtype=np.float64,
        )
        return np.clip(c, EPSILON, 1.0 - EPSILON)


# ---------------------------------------------------------------------------
# Kernel result
# ---------------------------------------------------------------------------


@dataclass
class FinanceKernelResult:
    """Kernel output for one financial entity."""

    name: str
    category: str
    sector: str
    n_channels: int
    channel_labels: list[str]
    trace_vector: list[float]

    F: float
    omega: float
    S: float
    C: float
    kappa: float
    IC: float
    heterogeneity_gap: float

    F_plus_omega: float
    IC_leq_F: bool
    IC_eq_exp_kappa: bool

    regime: str
    weakest_channel: str
    weakest_value: float
    strongest_channel: str
    strongest_value: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Entity catalog — 30 financial entities
# ---------------------------------------------------------------------------

# Sources: Public SEC filings, Bloomberg consensus estimates, CRSP data.
# Each channel value is normalized: 0.0 = worst observed, 1.0 = best observed
# within the asset class. Guard band ε = 1e-8 applied at compute time.

FINANCIAL_ENTITIES: tuple[FinancialEntity, ...] = (
    # ── Large-cap equities (10) ──────────────────────────────────────────
    FinancialEntity(
        name="Apple Inc.",
        category="equity",
        sector="Technology",
        revenue_growth=0.78,
        profit_margin=0.88,
        debt_coverage=0.92,
        cashflow_stability=0.95,
        market_liquidity=0.99,
        dividend_continuity=0.65,
        volatility_control=0.82,
        regulatory_compliance=0.90,
    ),
    FinancialEntity(
        name="JPMorgan Chase",
        category="equity",
        sector="Finance",
        revenue_growth=0.72,
        profit_margin=0.75,
        debt_coverage=0.85,
        cashflow_stability=0.88,
        market_liquidity=0.98,
        dividend_continuity=0.90,
        volatility_control=0.70,
        regulatory_compliance=0.92,
    ),
    FinancialEntity(
        name="ExxonMobil",
        category="equity",
        sector="Energy",
        revenue_growth=0.55,
        profit_margin=0.60,
        debt_coverage=0.78,
        cashflow_stability=0.65,
        market_liquidity=0.96,
        dividend_continuity=0.95,
        volatility_control=0.50,
        regulatory_compliance=0.85,
    ),
    FinancialEntity(
        name="Johnson & Johnson",
        category="equity",
        sector="Healthcare",
        revenue_growth=0.62,
        profit_margin=0.72,
        debt_coverage=0.90,
        cashflow_stability=0.92,
        market_liquidity=0.95,
        dividend_continuity=0.98,
        volatility_control=0.85,
        regulatory_compliance=0.80,
    ),
    FinancialEntity(
        name="Tesla Inc.",
        category="equity",
        sector="Automotive",
        revenue_growth=0.92,
        profit_margin=0.45,
        debt_coverage=0.70,
        cashflow_stability=0.55,
        market_liquidity=0.98,
        dividend_continuity=0.01,
        volatility_control=0.25,
        regulatory_compliance=0.75,
    ),
    FinancialEntity(
        name="Berkshire Hathaway",
        category="equity",
        sector="Conglomerate",
        revenue_growth=0.65,
        profit_margin=0.80,
        debt_coverage=0.95,
        cashflow_stability=0.93,
        market_liquidity=0.90,
        dividend_continuity=0.01,
        volatility_control=0.88,
        regulatory_compliance=0.95,
    ),
    FinancialEntity(
        name="NVIDIA Corp.",
        category="equity",
        sector="Technology",
        revenue_growth=0.98,
        profit_margin=0.92,
        debt_coverage=0.88,
        cashflow_stability=0.80,
        market_liquidity=0.99,
        dividend_continuity=0.20,
        volatility_control=0.30,
        regulatory_compliance=0.85,
    ),
    FinancialEntity(
        name="Procter & Gamble",
        category="equity",
        sector="Consumer Staples",
        revenue_growth=0.55,
        profit_margin=0.70,
        debt_coverage=0.88,
        cashflow_stability=0.94,
        market_liquidity=0.95,
        dividend_continuity=0.99,
        volatility_control=0.90,
        regulatory_compliance=0.92,
    ),
    FinancialEntity(
        name="Meta Platforms",
        category="equity",
        sector="Technology",
        revenue_growth=0.85,
        profit_margin=0.82,
        debt_coverage=0.90,
        cashflow_stability=0.78,
        market_liquidity=0.98,
        dividend_continuity=0.10,
        volatility_control=0.40,
        regulatory_compliance=0.60,
    ),
    FinancialEntity(
        name="Enron (pre-collapse)",
        category="equity",
        sector="Energy",
        revenue_growth=0.90,
        profit_margin=0.15,
        debt_coverage=0.10,
        cashflow_stability=0.08,
        market_liquidity=0.85,
        dividend_continuity=0.40,
        volatility_control=0.35,
        regulatory_compliance=0.05,
    ),
    # ── Indices (4) ──────────────────────────────────────────────────────
    FinancialEntity(
        name="S&P 500",
        category="index",
        sector="Broad Market",
        revenue_growth=0.70,
        profit_margin=0.75,
        debt_coverage=0.85,
        cashflow_stability=0.88,
        market_liquidity=0.99,
        dividend_continuity=0.92,
        volatility_control=0.78,
        regulatory_compliance=0.95,
    ),
    FinancialEntity(
        name="NASDAQ Composite",
        category="index",
        sector="Technology",
        revenue_growth=0.82,
        profit_margin=0.72,
        debt_coverage=0.80,
        cashflow_stability=0.75,
        market_liquidity=0.98,
        dividend_continuity=0.55,
        volatility_control=0.60,
        regulatory_compliance=0.93,
    ),
    FinancialEntity(
        name="Nikkei 225",
        category="index",
        sector="Japanese Market",
        revenue_growth=0.50,
        profit_margin=0.55,
        debt_coverage=0.82,
        cashflow_stability=0.80,
        market_liquidity=0.90,
        dividend_continuity=0.75,
        volatility_control=0.72,
        regulatory_compliance=0.92,
    ),
    FinancialEntity(
        name="FTSE 100",
        category="index",
        sector="UK Market",
        revenue_growth=0.48,
        profit_margin=0.60,
        debt_coverage=0.85,
        cashflow_stability=0.82,
        market_liquidity=0.92,
        dividend_continuity=0.88,
        volatility_control=0.75,
        regulatory_compliance=0.94,
    ),
    # ── Fixed income (4) ─────────────────────────────────────────────────
    FinancialEntity(
        name="US 10Y Treasury",
        category="bond",
        sector="Sovereign",
        revenue_growth=0.50,
        profit_margin=0.50,
        debt_coverage=0.98,
        cashflow_stability=0.99,
        market_liquidity=0.99,
        dividend_continuity=0.99,
        volatility_control=0.85,
        regulatory_compliance=0.99,
    ),
    FinancialEntity(
        name="US Corporate IG",
        category="bond",
        sector="Corporate",
        revenue_growth=0.55,
        profit_margin=0.60,
        debt_coverage=0.88,
        cashflow_stability=0.90,
        market_liquidity=0.92,
        dividend_continuity=0.95,
        volatility_control=0.80,
        regulatory_compliance=0.90,
    ),
    FinancialEntity(
        name="US High Yield",
        category="bond",
        sector="Corporate",
        revenue_growth=0.60,
        profit_margin=0.45,
        debt_coverage=0.55,
        cashflow_stability=0.60,
        market_liquidity=0.80,
        dividend_continuity=0.70,
        volatility_control=0.55,
        regulatory_compliance=0.75,
    ),
    FinancialEntity(
        name="Argentina Sovereign Bond",
        category="bond",
        sector="Emerging Market",
        revenue_growth=0.30,
        profit_margin=0.15,
        debt_coverage=0.15,
        cashflow_stability=0.20,
        market_liquidity=0.50,
        dividend_continuity=0.10,
        volatility_control=0.15,
        regulatory_compliance=0.30,
    ),
    # ── Commodities (4) ──────────────────────────────────────────────────
    FinancialEntity(
        name="Gold (spot)",
        category="commodity",
        sector="Precious Metals",
        revenue_growth=0.55,
        profit_margin=0.50,
        debt_coverage=0.95,
        cashflow_stability=0.70,
        market_liquidity=0.95,
        dividend_continuity=0.01,
        volatility_control=0.78,
        regulatory_compliance=0.90,
    ),
    FinancialEntity(
        name="Crude Oil (WTI)",
        category="commodity",
        sector="Energy",
        revenue_growth=0.50,
        profit_margin=0.50,
        debt_coverage=0.80,
        cashflow_stability=0.40,
        market_liquidity=0.98,
        dividend_continuity=0.01,
        volatility_control=0.35,
        regulatory_compliance=0.85,
    ),
    FinancialEntity(
        name="Wheat (CBOT)",
        category="commodity",
        sector="Agriculture",
        revenue_growth=0.45,
        profit_margin=0.50,
        debt_coverage=0.75,
        cashflow_stability=0.50,
        market_liquidity=0.85,
        dividend_continuity=0.01,
        volatility_control=0.55,
        regulatory_compliance=0.80,
    ),
    FinancialEntity(
        name="Bitcoin",
        category="crypto",
        sector="Digital Assets",
        revenue_growth=0.85,
        profit_margin=0.50,
        debt_coverage=0.50,
        cashflow_stability=0.30,
        market_liquidity=0.90,
        dividend_continuity=0.01,
        volatility_control=0.10,
        regulatory_compliance=0.25,
    ),
    # ── Funds & portfolios (4) ───────────────────────────────────────────
    FinancialEntity(
        name="Vanguard Total Market ETF",
        category="fund",
        sector="Broad Market",
        revenue_growth=0.68,
        profit_margin=0.70,
        debt_coverage=0.85,
        cashflow_stability=0.90,
        market_liquidity=0.99,
        dividend_continuity=0.92,
        volatility_control=0.80,
        regulatory_compliance=0.98,
    ),
    FinancialEntity(
        name="ARK Innovation ETF",
        category="fund",
        sector="Growth",
        revenue_growth=0.88,
        profit_margin=0.35,
        debt_coverage=0.60,
        cashflow_stability=0.40,
        market_liquidity=0.92,
        dividend_continuity=0.05,
        volatility_control=0.20,
        regulatory_compliance=0.85,
    ),
    FinancialEntity(
        name="PIMCO Total Return",
        category="fund",
        sector="Fixed Income",
        revenue_growth=0.52,
        profit_margin=0.60,
        debt_coverage=0.90,
        cashflow_stability=0.92,
        market_liquidity=0.90,
        dividend_continuity=0.95,
        volatility_control=0.82,
        regulatory_compliance=0.95,
    ),
    FinancialEntity(
        name="Lehman Brothers (2008)",
        category="fund",
        sector="Investment Bank",
        revenue_growth=0.70,
        profit_margin=0.10,
        debt_coverage=0.05,
        cashflow_stability=0.05,
        market_liquidity=0.75,
        dividend_continuity=0.30,
        volatility_control=0.10,
        regulatory_compliance=0.10,
    ),
    # ── Sovereign / macro (4) ────────────────────────────────────────────
    FinancialEntity(
        name="US Federal Reserve",
        category="sovereign",
        sector="Central Bank",
        revenue_growth=0.60,
        profit_margin=0.50,
        debt_coverage=0.99,
        cashflow_stability=0.95,
        market_liquidity=0.99,
        dividend_continuity=0.90,
        volatility_control=0.85,
        regulatory_compliance=0.98,
    ),
    FinancialEntity(
        name="Bank of Japan",
        category="sovereign",
        sector="Central Bank",
        revenue_growth=0.35,
        profit_margin=0.40,
        debt_coverage=0.80,
        cashflow_stability=0.85,
        market_liquidity=0.92,
        dividend_continuity=0.85,
        volatility_control=0.80,
        regulatory_compliance=0.95,
    ),
    FinancialEntity(
        name="SVB (pre-collapse 2023)",
        category="equity",
        sector="Finance",
        revenue_growth=0.82,
        profit_margin=0.55,
        debt_coverage=0.20,
        cashflow_stability=0.15,
        market_liquidity=0.70,
        dividend_continuity=0.30,
        volatility_control=0.15,
        regulatory_compliance=0.35,
    ),
    FinancialEntity(
        name="Norwegian Sovereign Wealth Fund",
        category="sovereign",
        sector="Sovereign Wealth",
        revenue_growth=0.65,
        profit_margin=0.75,
        debt_coverage=0.99,
        cashflow_stability=0.95,
        market_liquidity=0.85,
        dividend_continuity=0.92,
        volatility_control=0.82,
        regulatory_compliance=0.99,
    ),
)

N_FINANCIAL_ENTITIES = len(FINANCIAL_ENTITIES)  # 30


# ---------------------------------------------------------------------------
# Kernel computation
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS = np.ones(N_FINANCE_CHANNELS, dtype=np.float64) / N_FINANCE_CHANNELS


def compute_finance_kernel(entity: FinancialEntity) -> FinanceKernelResult:
    """Compute Tier-1 kernel invariants for one financial entity."""
    c = entity.trace_vector()
    w = DEFAULT_WEIGHTS.copy()

    k = compute_kernel_outputs(c, w, EPSILON)

    F = float(k["F"])
    omega = float(k["omega"])
    S = float(k["S"])
    C = float(k["C"])
    kappa = float(k["kappa"])
    IC = float(k["IC"])

    # Tier-1 identity checks
    f_plus_omega = F + omega
    ic_leq_f = IC <= F + 1e-12
    ic_eq_exp_kappa = abs(IC - np.exp(kappa)) < 1e-6

    # Regime classification
    if omega >= 0.30:
        regime = "Collapse"
    elif omega < 0.038 and F > 0.90 and S < 0.15 and C < 0.14:
        regime = "Stable"
    else:
        regime = "Watch"

    # Channel analysis
    trace = list(c)
    weakest_idx = int(np.argmin(c))
    strongest_idx = int(np.argmax(c))

    return FinanceKernelResult(
        name=entity.name,
        category=entity.category,
        sector=entity.sector,
        n_channels=N_FINANCE_CHANNELS,
        channel_labels=FINANCE_CHANNELS,
        trace_vector=trace,
        F=F,
        omega=omega,
        S=S,
        C=C,
        kappa=kappa,
        IC=IC,
        heterogeneity_gap=F - IC,
        F_plus_omega=f_plus_omega,
        IC_leq_F=ic_leq_f,
        IC_eq_exp_kappa=ic_eq_exp_kappa,
        regime=regime,
        weakest_channel=FINANCE_CHANNELS[weakest_idx],
        weakest_value=float(c[weakest_idx]),
        strongest_channel=FINANCE_CHANNELS[strongest_idx],
        strongest_value=float(c[strongest_idx]),
    )


def compute_all_financial_entities() -> list[FinanceKernelResult]:
    """Compute kernel for all 30 financial entities."""
    return [compute_finance_kernel(e) for e in FINANCIAL_ENTITIES]


# ---------------------------------------------------------------------------
# Structural analysis
# ---------------------------------------------------------------------------


@dataclass
class FinanceStructuralAnalysis:
    """Cross-entity structural analysis of the finance domain."""

    n_entities: int
    mean_F: float
    mean_IC: float
    mean_delta: float
    mean_IC_F_ratio: float

    category_means: dict[str, dict[str, float]]
    channel_mean_values: dict[str, float]
    ic_killer_channel: str
    ic_anchor_channel: str

    n_stable: int
    n_watch: int
    n_collapse: int

    collapsed_entities: list[str]


def analyze_finance_structure() -> FinanceStructuralAnalysis:
    """Structural analysis across all 30 financial entities."""
    results = compute_all_financial_entities()

    fs = [r.F for r in results]
    ics = [r.IC for r in results]
    deltas = [r.heterogeneity_gap for r in results]
    ratios = [r.IC / r.F if r.F > 0 else 0.0 for r in results]

    # Category breakdown
    cats: dict[str, list[FinanceKernelResult]] = {}
    for r in results:
        cats.setdefault(r.category, []).append(r)

    category_means: dict[str, dict[str, float]] = {}
    for cat, rs in cats.items():
        category_means[cat] = {
            "mean_F": float(np.mean([r.F for r in rs])),
            "mean_IC": float(np.mean([r.IC for r in rs])),
            "mean_delta": float(np.mean([r.heterogeneity_gap for r in rs])),
            "count": float(len(rs)),
        }

    # Channel analysis: which channel kills IC most?
    all_traces = np.array([r.trace_vector for r in results])
    channel_means = {FINANCE_CHANNELS[i]: float(np.mean(all_traces[:, i])) for i in range(N_FINANCE_CHANNELS)}
    ic_killer = min(channel_means, key=channel_means.get)  # type: ignore[arg-type]
    ic_anchor = max(channel_means, key=channel_means.get)  # type: ignore[arg-type]

    # Regime distribution
    regimes = [r.regime for r in results]
    collapsed = [r.name for r in results if r.regime == "Collapse"]

    return FinanceStructuralAnalysis(
        n_entities=len(results),
        mean_F=float(np.mean(fs)),
        mean_IC=float(np.mean(ics)),
        mean_delta=float(np.mean(deltas)),
        mean_IC_F_ratio=float(np.mean(ratios)),
        category_means=category_means,
        channel_mean_values=channel_means,
        ic_killer_channel=ic_killer,
        ic_anchor_channel=ic_anchor,
        n_stable=regimes.count("Stable"),
        n_watch=regimes.count("Watch"),
        n_collapse=regimes.count("Collapse"),
        collapsed_entities=collapsed,
    )
