"""Cross-domain kernel harvest — computes kernel outputs from all closure domains."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

domains: dict[str, list[dict]] = {}


def harvest(domain_name: str, module_path: str, func_name: str, cat_attr: str = "category") -> None:
    try:
        mod = importlib.import_module(module_path)
        fn = getattr(mod, func_name)
        results = fn()
        entries = []
        for r in results:
            cat = getattr(r, cat_attr, "unknown") if cat_attr else "all"
            entries.append(
                {
                    "name": getattr(r, "name", getattr(r, "symbol", str(r))),
                    "category": cat,
                    "F": float(r.F),
                    "omega": float(r.omega),
                    "IC": float(r.IC),
                    "S": float(r.S),
                    "C": float(r.C),
                    "kappa": float(r.kappa),
                    "regime": str(r.regime),
                }
            )
        domains[domain_name] = entries
        print(f"  OK {domain_name}: {len(entries)} entities")
    except Exception as e:
        print(f"  FAIL {domain_name}: {e}")


STD_CLOSURES = [
    ("spliceosome_dynamics", "closures.quantum_mechanics.spliceosome_dynamics"),
    ("photonic_confinement", "closures.quantum_mechanics.photonic_confinement"),
    ("topological_bands", "closures.quantum_mechanics.topological_band_structures"),
    ("neural_correlates", "closures.consciousness_coherence.neural_correlates"),
    ("altered_states", "closures.consciousness_coherence.altered_states"),
    ("neurotransmitter", "closures.clinical_neuroscience.neurotransmitter_systems"),
    ("developmental_neuro", "closures.clinical_neuroscience.developmental_neuroscience"),
    ("sleep_neuro", "closures.clinical_neuroscience.sleep_neurophysiology"),
    ("temporal_topology", "closures.spacetime_memory.temporal_topology"),
    ("cosmological_memory", "closures.spacetime_memory.cosmological_memory"),
    ("grav_wave_memory", "closures.spacetime_memory.gravitational_wave_memory"),
    ("grav_phenomena", "closures.spacetime_memory.gravitational_phenomena"),
    ("binary_stars", "closures.astronomy.binary_star_systems"),
    ("electroweak", "closures.standard_model.electroweak_precision"),
    ("market_microstructure", "closures.finance.market_microstructure"),
    ("volatility_surface", "closures.finance.volatility_surface"),
    ("molecular_evolution", "closures.evolution.molecular_evolution"),
    ("computational_semiotics", "closures.dynamic_semiotics.computational_semiotics"),
    ("media_coherence", "closures.dynamic_semiotics.media_coherence"),
    ("topological_persist", "closures.continuity_theory.topological_persistence"),
    ("organizational_resil", "closures.continuity_theory.organizational_resilience"),
    ("budget_geometry", "closures.continuity_theory.budget_geometry"),
    ("attention_mechanisms", "closures.awareness_cognition.attention_mechanisms"),
    ("defect_physics", "closures.materials_science.defect_physics"),
    ("acoustics", "closures.everyday_physics.acoustics"),
    ("fluid_dynamics", "closures.everyday_physics.fluid_dynamics"),
    ("reaction_channels", "closures.nuclear_physics.reaction_channels"),
    ("rigid_body", "closures.kinematics.rigid_body_dynamics"),
]

SPECIAL_CLOSURES = [
    ("subatomic_particles", "closures.standard_model.subatomic_kernel", "compute_all"),
    ("semiotic_kernel", "closures.dynamic_semiotics.semiotic_kernel", "compute_all_sign_systems"),
    ("long_period_transients", "closures.astronomy.long_period_radio_transients", "compute_all_lpt_kernels"),
    ("evolution_kernel", "closures.evolution.evolution_kernel", "compute_all_organisms"),
    ("coherence_kernel", "closures.consciousness_coherence.coherence_kernel", "compute_all_coherence_systems"),
    ("spacetime_kernel", "closures.spacetime_memory.spacetime_kernel", "compute_all_spacetime"),
    ("finance_catalog", "closures.finance.finance_catalog", "compute_all_financial_entities"),
]


def main() -> None:
    print("=" * 80)
    print("  CROSS-DOMAIN KERNEL HARVEST")
    print("=" * 80)

    print("\n=== HARVESTING STANDARD CLOSURES ===")
    for name, mod_path in STD_CLOSURES:
        harvest(name, mod_path, "compute_all_entities")

    print("\n=== HARVESTING SPECIAL CLOSURES ===")
    for name, mod_path, fn in SPECIAL_CLOSURES:
        harvest(name, mod_path, fn)

    # Additional special closures
    EXTRA_SPECIAL = [
        ("brain_kernel", "closures.evolution.brain_kernel", "compute_all_brains"),
        ("awareness_kernel", "closures.awareness_cognition.awareness_kernel", "compute_all_organisms"),
        ("neurocognitive_kernel", "closures.clinical_neuroscience.neurocognitive_kernel", "compute_all_states"),
        ("qgp_rhic", "closures.nuclear_physics.qgp_rhic", "build_all_entities"),
        ("trinity_blast_wave", "closures.nuclear_physics.trinity_blast_wave", "build_all_entities"),
    ]
    print("\n=== HARVESTING EXTRA CLOSURES ===")
    for name, mod_path, fn in EXTRA_SPECIAL:
        harvest(name, mod_path, fn)

    # Periodic kernel (118 elements) — uses batch_compute_all
    try:
        from closures.atomic_physics.periodic_kernel import batch_compute_all

        results = batch_compute_all()
        entries = []
        for r in results:
            entries.append(
                {
                    "name": getattr(r, "symbol", getattr(r, "name", str(r))),
                    "category": "element",
                    "F": float(r.F),
                    "omega": float(r.omega),
                    "IC": float(r.IC),
                    "S": float(r.S),
                    "C": float(r.C),
                    "kappa": float(r.kappa),
                    "regime": str(r.regime),
                }
            )
        domains["periodic_kernel"] = entries
        print(f"  OK periodic_kernel: {len(entries)} entities")
    except Exception as e:
        print(f"  FAIL periodic_kernel: {e}")

    total_entities = sum(len(v) for v in domains.values())
    print(f"\n{'=' * 80}")
    print(f"  TOTAL: {len(domains)} domains, {total_entities} entities")
    print(f"{'=' * 80}")

    # Cross-domain statistics table
    print(
        f"\n{'Domain':<28} {'N':>4} {'<F>':>7} {'<IC>':>7} {'<Δ>':>7} {'<IC/F>':>7} {'<ω>':>7} {'<S>':>7} {'<C>':>7} {'Stb':>4} {'Wtc':>4} {'Col':>4}"
    )
    print("-" * 110)

    all_F, all_IC, all_gap, all_omega = [], [], [], []
    domain_stats = []

    for dname in sorted(domains.keys()):
        entities = domains[dname]
        n = len(entities)
        Fs = [e["F"] for e in entities]
        ICs = [e["IC"] for e in entities]
        gaps = [e["F"] - e["IC"] for e in entities]
        omegas = [e["omega"] for e in entities]
        Ss = [e["S"] for e in entities]
        Cs = [e["C"] for e in entities]
        icfs = [e["IC"] / e["F"] if e["F"] > 0 else 0 for e in entities]
        stable = sum(1 for e in entities if e["regime"] == "Stable")
        watch = sum(1 for e in entities if e["regime"] == "Watch")
        collapse = sum(1 for e in entities if e["regime"] == "Collapse")

        all_F.extend(Fs)
        all_IC.extend(ICs)
        all_gap.extend(gaps)
        all_omega.extend(omegas)

        domain_stats.append(
            {
                "name": dname,
                "n": n,
                "F": np.mean(Fs),
                "IC": np.mean(ICs),
                "gap": np.mean(gaps),
                "icf": np.mean(icfs),
                "omega": np.mean(omegas),
                "S": np.mean(Ss),
                "C": np.mean(Cs),
                "stable": stable,
                "watch": watch,
                "collapse": collapse,
                "max_gap": max(gaps),
                "min_F": min(Fs),
                "max_F": max(Fs),
                "min_IC": min(ICs),
                "max_IC": max(ICs),
            }
        )

        print(
            f"{dname:<28} {n:>4} {np.mean(Fs):>7.4f} {np.mean(ICs):>7.4f} {np.mean(gaps):>7.4f} {np.mean(icfs):>7.4f} {np.mean(omegas):>7.4f} {np.mean(Ss):>7.4f} {np.mean(Cs):>7.4f} {stable:>4} {watch:>4} {collapse:>4}"
        )

    print("-" * 110)
    N = len(all_F)
    print(
        f"{'GLOBAL':<28} {N:>4} {np.mean(all_F):>7.4f} {np.mean(all_IC):>7.4f} {np.mean(all_gap):>7.4f} {np.mean([ic / f if f > 0 else 0 for ic, f in zip(all_IC, all_F, strict=True)]):>7.4f} {np.mean(all_omega):>7.4f}"
    )

    # Rankings
    print("\n=== DOMAIN RANKING BY MEAN HETEROGENEITY GAP ===")
    for d in sorted(domain_stats, key=lambda x: x["gap"], reverse=True):
        print(f"  {d['name']:<28} <Δ>={d['gap']:.4f}  max={d['max_gap']:.4f}  <IC/F>={d['icf']:.4f}")

    print("\n=== HIGHEST STABLE FRACTION ===")
    for d in sorted(domain_stats, key=lambda x: x["stable"] / max(x["n"], 1), reverse=True)[:10]:
        pct = d["stable"] / d["n"] * 100
        print(f"  {d['name']:<28} {d['stable']}/{d['n']} = {pct:.1f}%  <F>={d['F']:.4f}")

    print("\n=== HIGHEST COLLAPSE FRACTION ===")
    for d in sorted(domain_stats, key=lambda x: x["collapse"] / max(x["n"], 1), reverse=True)[:10]:
        pct = d["collapse"] / d["n"] * 100
        print(f"  {d['name']:<28} {d['collapse']}/{d['n']} = {pct:.1f}%  <F>={d['F']:.4f}")

    # Flatten for cross-domain extremes
    flat = []
    for dname, entities in domains.items():
        for e in entities:
            e2 = dict(e)
            e2["domain"] = dname
            e2["gap"] = e["F"] - e["IC"]
            e2["icf"] = e["IC"] / e["F"] if e["F"] > 0 else 0
            flat.append(e2)

    print("\n=== CROSS-DOMAIN EXTREMES ===")
    print("  HIGHEST F:")
    for e in sorted(flat, key=lambda x: x["F"], reverse=True)[:8]:
        print(f"    {e['domain']:25s} {e['name']:30s} F={e['F']:.4f} IC={e['IC']:.4f} {e['regime']}")

    print("  LOWEST F:")
    for e in sorted(flat, key=lambda x: x["F"])[:8]:
        print(f"    {e['domain']:25s} {e['name']:30s} F={e['F']:.4f} ω={e['omega']:.4f} {e['regime']}")

    print("  LARGEST HETEROGENEITY GAP (Δ = F − IC):")
    for e in sorted(flat, key=lambda x: x["gap"], reverse=True)[:15]:
        print(
            f"    {e['domain']:25s} {e['name']:30s} Δ={e['gap']:.4f} F={e['F']:.4f} IC={e['IC']:.4f} IC/F={e['icf']:.4f}"
        )

    print("  LOWEST IC/F (most crushed coherence):")
    for e in sorted(flat, key=lambda x: x["icf"])[:15]:
        print(f"    {e['domain']:25s} {e['name']:30s} IC/F={e['icf']:.4f} Δ={e['gap']:.4f} F={e['F']:.4f}")

    print("  HIGHEST IC/F (most uniform channels):")
    for e in sorted(flat, key=lambda x: x["icf"], reverse=True)[:8]:
        print(f"    {e['domain']:25s} {e['name']:30s} IC/F={e['icf']:.4f} F={e['F']:.4f}")

    print("  HIGHEST CURVATURE C:")
    for e in sorted(flat, key=lambda x: x["C"], reverse=True)[:8]:
        print(f"    {e['domain']:25s} {e['name']:30s} C={e['C']:.4f} F={e['F']:.4f} Δ={e['gap']:.4f}")

    # Global regime distribution
    total = len(flat)
    s = sum(1 for e in flat if e["regime"] == "Stable")
    w = sum(1 for e in flat if e["regime"] == "Watch")
    c = sum(1 for e in flat if e["regime"] == "Collapse")
    print(f"\n=== GLOBAL REGIME DISTRIBUTION ({total} entities across {len(domains)} domains) ===")
    print(f"  Stable:   {s:>4} ({s / total * 100:.1f}%)")
    print(f"  Watch:    {w:>4} ({w / total * 100:.1f}%)")
    print(f"  Collapse: {c:>4} ({c / total * 100:.1f}%)")
    print("  Theory:   Stable 12.5% / Watch 24.4% / Collapse 63.1%")

    # Cross-domain gap signature patterns
    print("\n=== GAP SIGNATURE ANALYSIS ===")
    print("  Domains where max_gap > 0.10 (severe geometric slaughter present):")
    for d in sorted(domain_stats, key=lambda x: x["max_gap"], reverse=True):
        if d["max_gap"] > 0.10:
            worst = max(
                [e for e in flat if e["domain"] == d["name"]],
                key=lambda x: x["gap"],
            )
            print(f"    {d['name']:<28} max_Δ={d['max_gap']:.4f}  entity={worst['name']}")

    print("\n  Domains with near-zero mean gap (homogeneous channels):")
    for d in sorted(domain_stats, key=lambda x: x["gap"]):
        if d["gap"] < 0.010:
            print(f"    {d['name']:<28} <Δ>={d['gap']:.4f}  <IC/F>={d['icf']:.4f}")

    print(f"\n{'=' * 80}")
    print("  CROSS-DOMAIN HARVEST COMPLETE")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
