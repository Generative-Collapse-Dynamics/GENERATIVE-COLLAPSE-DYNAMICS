#!/usr/bin/env python3
"""Structural Twin Finder — Cross-Domain Morphology Engine.

Collapsus generativus est; solum quod redit, reale est.

This script harvests entities from ALL domain closures, computes their
kernel outputs, and finds structural twins across completely different
fields. A neutron and a dying language can have the same IC/F signature
— not by metaphor, but by measured proximity in kernel space.

The kernel does not know what domain it is in. It measures structure.
Two entities are structural twins when they occupy the same region of
(IC/F, Δ/F, C) space regardless of whether one is a quark and the
other is a symphony orchestra.

Usage:
    python scripts/structural_twins.py              # Full analysis
    python scripts/structural_twins.py --twins 10   # Top 10 twin pairs
    python scripts/structural_twins.py --autopsy     # Channel death autopsy
    python scripts/structural_twins.py --boundaries  # Phase boundary scan
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Ensure project root is on path
_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))

from src.umcp.frozen_contract import EPSILON
from src.umcp.kernel_optimized import OptimizedKernelComputer

_kernel = OptimizedKernelComputer()


# ─── Entity representation ──────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class KernelEntity:
    """A single entity from any domain, with its kernel outputs."""

    name: str
    domain: str
    subdomain: str
    channels: tuple[float, ...]
    channel_names: tuple[str, ...]
    n_channels: int
    F: float
    omega: float
    S: float
    C: float
    kappa: float
    IC: float
    IC_over_F: float
    delta: float  # heterogeneity gap = F - IC
    delta_over_F: float  # normalized het gap
    regime: str


def _compute_entity(
    name: str,
    domain: str,
    subdomain: str,
    c: np.ndarray,
    w: np.ndarray,
    channel_names: list[str] | tuple[str, ...],
) -> KernelEntity | None:
    """Compute kernel outputs for a single entity."""
    if len(c) < 2:
        return None
    try:
        c_clean = np.clip(c, EPSILON, 1.0 - EPSILON).astype(np.float64)
        r = _kernel.compute(c_clean, w)
        ic_f = r.IC / r.F if r.F > EPSILON else 0.0
        delta = r.F - r.IC
        delta_f = delta / r.F if r.F > EPSILON else 0.0

        if r.omega >= 0.30:
            regime = "Collapse"
        elif r.omega < 0.038 and r.F > 0.90 and r.S < 0.15 and r.C < 0.14:
            regime = "Stable"
        else:
            regime = "Watch"

        return KernelEntity(
            name=name,
            domain=domain,
            subdomain=subdomain,
            channels=tuple(float(x) for x in c_clean),
            channel_names=tuple(channel_names),
            n_channels=len(c_clean),
            F=r.F,
            omega=r.omega,
            S=r.S,
            C=r.C,
            kappa=r.kappa,
            IC=r.IC,
            IC_over_F=ic_f,
            delta=delta,
            delta_over_F=delta_f,
            regime=regime,
        )
    except Exception:
        return None


# ─── Domain harvesters ───────────────────────────────────────────────


def _harvest_subatomic() -> list[KernelEntity]:
    """Harvest Standard Model particles (31 entities, 8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.standard_model.subatomic_kernel import (
            COMPOSITE_PARTICLES,
            FUNDAMENTAL_PARTICLES,
        )
    except ImportError:
        return entities

    channels = [
        "mass_log",
        "charge_abs",
        "spin_norm",
        "color_dof",
        "weak_T3",
        "hypercharge",
        "generation",
        "stability",
    ]

    def _normalize(p: object, is_composite: bool = False) -> np.ndarray | None:
        """Build 8-channel trace from particle attributes."""
        try:
            mass = getattr(p, "mass_GeV", 0.0) or 1e-30
            mass_log = np.clip((np.log10(max(mass, 1e-30)) + 30) / 60, EPSILON, 1.0 - EPSILON)
            charge = np.clip(abs(getattr(p, "charge_e", 0.0)) / 2.0, EPSILON, 1.0 - EPSILON)
            spin = np.clip(getattr(p, "spin", 0.0) / 2.0, EPSILON, 1.0 - EPSILON)
            color = np.clip(getattr(p, "color_dof", 1) / 8.0, EPSILON, 1.0 - EPSILON)
            weak = np.clip((getattr(p, "weak_T3", 0.0) + 1.0) / 2.0, EPSILON, 1.0 - EPSILON)
            hyper = np.clip((getattr(p, "hypercharge_Y", 0.0) + 2.0) / 4.0, EPSILON, 1.0 - EPSILON)
            gen = np.clip(getattr(p, "generation", 0) / 3.0, EPSILON, 1.0 - EPSILON)

            lt = getattr(p, "lifetime_s", None)
            if lt is None or lt <= 0:
                stab = EPSILON
            else:
                stab = np.clip(np.log10(max(lt, 1e-30)) / 30 + 1.0, EPSILON, 1.0 - EPSILON)

            return np.array([mass_log, charge, spin, color, weak, hyper, gen, stab])
        except Exception:
            return None

    for p in FUNDAMENTAL_PARTICLES:
        c = _normalize(p)
        if c is not None:
            w = np.ones(8) / 8
            e = _compute_entity(getattr(p, "name", str(p)), "Physics", "Fundamental", c, w, channels)
            if e:
                entities.append(e)

    for p in COMPOSITE_PARTICLES:
        c = _normalize(p, is_composite=True)
        if c is not None:
            w = np.ones(8) / 8
            e = _compute_entity(getattr(p, "name", str(p)), "Physics", "Composite", c, w, channels)
            if e:
                entities.append(e)

    return entities


def _harvest_atoms() -> list[KernelEntity]:
    """Harvest periodic table (118 elements, ≤8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.atomic_physics.periodic_kernel import _normalize_element
        from closures.materials_science.element_database import ELEMENTS
    except ImportError:
        return entities

    for el in ELEMENTS:
        try:
            c, w, labels = _normalize_element(el)
            if len(c) >= 2:
                e = _compute_entity(f"{el.symbol} ({el.name})", "Chemistry", "Element", c, w, labels)
                if e:
                    entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_brains() -> list[KernelEntity]:
    """Harvest brain kernel (species, 10 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.evolution.brain_kernel import BRAIN_CATALOG
    except ImportError:
        return entities

    channels = [
        "EQ",
        "cortical_neurons",
        "PFC_ratio",
        "synaptic_density",
        "connectivity",
        "metabolic",
        "plasticity",
        "language",
        "temporal_integ",
        "social_cognition",
    ]
    for brain in BRAIN_CATALOG:
        try:
            c = brain.trace_vector()
            w = np.ones(len(c)) / len(c)
            e = _compute_entity(
                getattr(brain, "species", str(brain)),
                "Biology",
                "Neuroscience",
                c,
                w,
                channels[: len(c)],
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_organisms() -> list[KernelEntity]:
    """Harvest awareness-cognition organisms (34 entities, 10 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.awareness_cognition.awareness_kernel import (
            ALL_CHANNELS,
            ORGANISM_CATALOG,
            WEIGHTS,
        )
    except ImportError:
        return entities

    for org in ORGANISM_CATALOG:
        try:
            c = org.trace
            e = _compute_entity(
                org.name,
                "Biology",
                "Awareness-Cognition",
                c,
                WEIGHTS,
                list(ALL_CHANNELS),
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_coherence() -> list[KernelEntity]:
    """Harvest consciousness coherence systems (20 entities, 8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.consciousness_coherence.coherence_kernel import COHERENCE_CATALOG
    except ImportError:
        return entities

    channels = [
        "harmonic_ratio",
        "recursive_depth",
        "return_fidelity",
        "spectral_coherence",
        "phase_stability",
        "information_density",
        "temporal_persistence",
        "cross_scale_coupling",
    ]
    for sys_obj in COHERENCE_CATALOG:
        try:
            c = sys_obj.trace_vector()
            w = np.ones(8) / 8
            e = _compute_entity(
                sys_obj.name,
                "Consciousness",
                getattr(sys_obj, "category", "System"),
                c,
                w,
                channels,
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_semiotics() -> list[KernelEntity]:
    """Harvest semiotic sign systems (30 entities, 8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.dynamic_semiotics.semiotic_kernel import SIGN_SYSTEMS
    except ImportError:
        return entities

    channels = [
        "sign_repertoire",
        "interpretant_depth",
        "ground_stability",
        "translation_fidelity",
        "semiotic_density",
        "indexical_coupling",
        "iconic_persistence",
        "symbolic_recursion",
    ]
    for ss in SIGN_SYSTEMS:
        try:
            c = ss.trace_vector()
            w = np.ones(8) / 8
            e = _compute_entity(
                ss.name,
                "Semiotics",
                getattr(ss, "category", "Sign System"),
                c,
                w,
                channels,
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_matter_genesis() -> list[KernelEntity]:
    """Harvest matter genesis entities (99 entities, variable channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.standard_model.matter_genesis import (
            build_act_i,
            build_act_ii,
            build_act_iii,
            build_act_iv,
            build_act_v,
            build_act_vi,
        )
    except ImportError:
        return entities

    all_genesis = []
    for builder in [build_act_i, build_act_ii, build_act_iii, build_act_iv, build_act_v, build_act_vi]:
        all_genesis.extend(builder())

    for ge in all_genesis:
        try:
            c = np.array(ge.trace, dtype=np.float64)
            if len(c) < 2:
                continue
            w = np.ones(len(c)) / len(c)
            ch_names = list(ge.channel_names) if hasattr(ge, "channel_names") else [f"ch{i}" for i in range(len(c))]
            e = _compute_entity(
                ge.name,
                "Genesis",
                f"Act-{ge.act}",
                c,
                w,
                ch_names,
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_stars() -> list[KernelEntity]:
    """Harvest stellar samples (23 stellar populations, 8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.astronomy.stellar_ages_cosmology import (
            _build_representative_stars,
        )
    except ImportError:
        return entities

    channels = [
        "teff",
        "logg",
        "metallicity",
        "alpha_fe",
        "mass",
        "age",
        "av",
        "n_stars",
    ]
    for star in _build_representative_stars():
        try:
            c = star.trace_vector()
            w = np.ones(len(c)) / len(c)
            e = _compute_entity(
                star.name,
                "Astronomy",
                getattr(star, "sample_type", "Star"),
                c,
                w,
                channels[: len(c)],
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


def _harvest_cosmology() -> list[KernelEntity]:
    """Harvest cosmological epochs (6 epochs, 8 channels)."""
    entities: list[KernelEntity] = []
    try:
        from closures.astronomy.cosmology import compute_all_cosmological_epochs
    except ImportError:
        return entities

    for epoch in compute_all_cosmological_epochs():
        try:
            c = np.array(epoch.trace, dtype=np.float64)
            w = np.ones(len(c)) / len(c)
            ch_names = [f"cosmo_ch{i}" for i in range(len(c))]
            e = _compute_entity(
                epoch.epoch,
                "Cosmology",
                f"z={epoch.redshift}",
                c,
                w,
                ch_names,
            )
            if e:
                entities.append(e)
        except Exception:
            continue
    return entities


# ─── Universal harvest ───────────────────────────────────────────────


def harvest_all() -> list[KernelEntity]:
    """Harvest entities from all available domain closures."""
    all_entities: list[KernelEntity] = []

    harvesters = [
        ("Subatomic particles", _harvest_subatomic),
        ("Periodic table", _harvest_atoms),
        ("Brain profiles", _harvest_brains),
        ("Organisms (awareness)", _harvest_organisms),
        ("Coherence systems", _harvest_coherence),
        ("Sign systems", _harvest_semiotics),
        ("Matter genesis", _harvest_matter_genesis),
        ("Stellar populations", _harvest_stars),
        ("Cosmological epochs", _harvest_cosmology),
    ]

    for label, fn in harvesters:
        result = fn()
        if result:
            print(f"  Harvested {len(result):>4d} entities from {label}")
        all_entities.extend(result)

    return all_entities


# ─── Analysis engines ────────────────────────────────────────────────


@dataclass
class TwinPair:
    """A pair of structural twins from different domains."""

    entity_a: KernelEntity
    entity_b: KernelEntity
    distance: float  # Euclidean in (IC/F, Δ/F, C) space
    shared_regime: bool


def find_structural_twins(entities: list[KernelEntity], top_n: int = 20) -> list[TwinPair]:
    """Find cross-domain structural twins by proximity in kernel space.

    Two entities are structural twins if they occupy the same region of
    (IC/F, Δ/F, C) space. Only cross-domain pairs are considered.
    """
    # Build coordinate matrix
    coords = np.array([[e.IC_over_F, e.delta_over_F, e.C] for e in entities], dtype=np.float64)

    pairs: list[TwinPair] = []

    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            # Only cross-domain pairs
            if entities[i].domain == entities[j].domain:
                continue

            dist = float(np.sqrt(np.sum((coords[i] - coords[j]) ** 2)))
            pairs.append(
                TwinPair(
                    entity_a=entities[i],
                    entity_b=entities[j],
                    distance=dist,
                    shared_regime=entities[i].regime == entities[j].regime,
                )
            )

    pairs.sort(key=lambda p: p.distance)
    return pairs[:top_n]


def channel_death_autopsy(entities: list[KernelEntity]) -> None:
    """For entities in Collapse regime, identify which channels killed IC."""
    collapsed = [e for e in entities if e.regime == "Collapse" and e.n_channels >= 3]
    collapsed.sort(key=lambda e: e.IC_over_F)

    print()
    print("=" * 80)
    print("  CHANNEL DEATH AUTOPSY — Which channels killed multiplicative coherence?")
    print("  *Unus canalis mortuus omnes necat* — one dead channel kills all.")
    print("=" * 80)

    for e in collapsed[:15]:
        print()
        print(f"  {e.name} ({e.domain}/{e.subdomain})")
        print(f"  F={e.F:.4f}  IC={e.IC:.6f}  IC/F={e.IC_over_F:.4f}  Δ={e.delta:.4f}  regime={e.regime}")
        print(f"  Channels ({e.n_channels}):")

        # Identify channel contributions to κ
        c_arr = np.array(e.channels)
        w_arr = np.ones(e.n_channels) / e.n_channels
        ln_contributions = w_arr * np.log(np.clip(c_arr, EPSILON, 1.0))

        # Sort by contribution (most negative = most damaging)
        order = np.argsort(ln_contributions)
        for idx in order:
            ch_name = e.channel_names[idx] if idx < len(e.channel_names) else f"ch{idx}"
            c_val = e.channels[idx]
            contrib = ln_contributions[idx]
            bar_len = int(min(abs(contrib) * 10, 40))
            bar = "█" * bar_len
            marker = " ← KILLER" if c_val < 0.05 else ""
            print(f"    {ch_name:>25s}: c={c_val:.4f}  κ_contrib={contrib:+.4f}  {bar}{marker}")


def phase_boundary_scan(entities: list[KernelEntity]) -> None:
    """Detect phase boundaries: where IC/F drops sharply within a domain."""
    print()
    print("=" * 80)
    print("  PHASE BOUNDARY SCANNER — Where does the universe break?")
    print("  *Praecipitium integritatis* — integrity cliffs across domains.")
    print("=" * 80)

    # Group by domain+subdomain, sort by IC/F
    from collections import defaultdict

    groups: dict[str, list[KernelEntity]] = defaultdict(list)
    for e in entities:
        groups[e.domain].append(e)

    for domain, group in sorted(groups.items()):
        group.sort(key=lambda e: -e.IC_over_F)

        # Find biggest drops
        drops: list[tuple[KernelEntity, KernelEntity, float]] = []
        for i in range(len(group) - 1):
            ratio = group[i + 1].IC_over_F / group[i].IC_over_F if group[i].IC_over_F > EPSILON else 0
            if ratio < 0.5 and group[i].IC_over_F > 0.1:  # >50% drop from a meaningful IC/F
                drops.append((group[i], group[i + 1], ratio))

        if drops:
            print(f"\n  ── {domain} ({len(group)} entities) ──")
            for above, below, _ratio in drops[:3]:
                factor = above.IC_over_F / below.IC_over_F if below.IC_over_F > EPSILON else float("inf")
                print(f"    CLIFF: {above.name} (IC/F={above.IC_over_F:.4f})")
                print(f"       →   {below.name} (IC/F={below.IC_over_F:.4f})")
                print(f"       Drop: {factor:.1f}× — {above.subdomain} → {below.subdomain}")


# ─── Main ────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description="Structural Twin Finder")
    parser.add_argument("--twins", type=int, default=20, help="Number of twin pairs")
    parser.add_argument("--autopsy", action="store_true", help="Channel death autopsy")
    parser.add_argument("--boundaries", action="store_true", help="Phase boundary scan")
    args = parser.parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   STRUCTURAL TWIN FINDER — Cross-Domain Morphology Engine  ║")
    print("║                                                            ║")
    print("║   The kernel does not know what domain it is in.           ║")
    print("║   It measures structure. Twins are measured, not asserted. ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("Harvesting entities from all domain closures...")
    print()

    entities = harvest_all()

    print(f"\n  TOTAL: {len(entities)} entities across {len({e.domain for e in entities})} domains")

    # Summary by domain
    domain_summary: dict[str, list[KernelEntity]] = {}
    for e in entities:
        domain_summary.setdefault(e.domain, []).append(e)

    print()
    print("  Domain Summary:")
    print(
        f"  {'Domain':<18s}  {'N':>5s}  {'⟨F⟩':>7s}  {'⟨IC⟩':>9s}  {'⟨IC/F⟩':>8s}  {'⟨Δ⟩':>7s}  {'Stable':>7s}  {'Watch':>6s}  {'Coll':>6s}"
    )
    print("  " + "-" * 78)
    for domain, group in sorted(domain_summary.items()):
        n = len(group)
        mean_F = np.mean([e.F for e in group])
        mean_IC = np.mean([e.IC for e in group])
        mean_icf = np.mean([e.IC_over_F for e in group])
        mean_delta = np.mean([e.delta for e in group])
        n_stable = sum(1 for e in group if e.regime == "Stable")
        n_watch = sum(1 for e in group if e.regime == "Watch")
        n_coll = sum(1 for e in group if e.regime == "Collapse")
        print(
            f"  {domain:<18s}  {n:>5d}  {mean_F:>7.4f}  {mean_IC:>9.6f}  "
            f"{mean_icf:>8.4f}  {mean_delta:>7.4f}  {n_stable:>7d}  {n_watch:>6d}  {n_coll:>6d}"
        )

    # ── Structural Twins ──
    print()
    print("=" * 80)
    print("  STRUCTURAL TWINS — Cross-domain entities in the same kernel region")
    print("  Matching coordinates: (IC/F, Δ/F, C) — domain-independent structure")
    print("=" * 80)

    twins = find_structural_twins(entities, top_n=args.twins)
    for i, pair in enumerate(twins):
        a, b = pair.entity_a, pair.entity_b
        print()
        print(f"  TWIN PAIR #{i + 1}  (distance = {pair.distance:.6f})")
        print(f"    A: {a.name:<35s}  [{a.domain}/{a.subdomain}]")
        print(f"       F={a.F:.4f}  IC={a.IC:.6f}  IC/F={a.IC_over_F:.4f}  Δ={a.delta:.4f}  C={a.C:.4f}  {a.regime}")
        print(f"    B: {b.name:<35s}  [{b.domain}/{b.subdomain}]")
        print(f"       F={b.F:.4f}  IC={b.IC:.6f}  IC/F={b.IC_over_F:.4f}  Δ={b.delta:.4f}  C={b.C:.4f}  {b.regime}")
        regime_match = "SAME REGIME" if pair.shared_regime else f"DIFFERENT ({a.regime} vs {b.regime})"
        print(f"    Regime: {regime_match}")

    # ── Optional analyses ──
    if args.autopsy or (not args.boundaries):
        channel_death_autopsy(entities)

    if args.boundaries or (not args.autopsy):
        phase_boundary_scan(entities)

    # ── The punchline ──
    print()
    print("=" * 80)
    print("  The kernel does not know whether it measured a quark or a language.")
    print("  The structural twins are real because the mechanism is real.")
    print("  *Solum quod redit, reale est.*")
    print("=" * 80)


if __name__ == "__main__":
    main()
