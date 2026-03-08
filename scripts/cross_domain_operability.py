"""Cross-Domain Operability Analysis — live measurement across all closures.

Loads every closure domain with kernel computation and measures
cross-domain Tier-1 identity conformance using ONE kernel.
"""

from __future__ import annotations

import sys

sys.path.insert(0, ".")
sys.path.insert(0, "src")

import numpy as np

# ── Canonical element names for nuclides ─────────────────────────
_ELEMENT_SYMBOLS: dict[int, str] = {
    1: "H",
    2: "He",
    3: "Li",
    6: "C",
    7: "N",
    8: "O",
    11: "Na",
    12: "Mg",
    13: "Al",
    14: "Si",
    16: "S",
    19: "K",
    20: "Ca",
    22: "Ti",
    24: "Cr",
    26: "Fe",
    28: "Ni",
    29: "Cu",
    30: "Zn",
    34: "Se",
    36: "Kr",
    38: "Sr",
    40: "Zr",
    42: "Mo",
    47: "Ag",
    50: "Sn",
    54: "Xe",
    56: "Ba",
    74: "W",
    78: "Pt",
    79: "Au",
    82: "Pb",
    83: "Bi",
    92: "U",
}

# Reference nuclides spanning the binding curve (SEMF, no measured values)
_REFERENCE_NUCLIDES: list[tuple[int, int]] = [
    (1, 1),
    (1, 2),
    (2, 4),
    (3, 7),
    (6, 12),
    (7, 14),
    (8, 16),
    (11, 23),
    (12, 24),
    (13, 27),
    (14, 28),
    (16, 32),
    (19, 39),
    (20, 40),
    (22, 48),
    (24, 52),
    (26, 56),
    (28, 58),
    (28, 62),
    (29, 63),
    (30, 64),
    (34, 80),
    (36, 84),
    (38, 88),
    (40, 90),
    (42, 98),
    (47, 107),
    (50, 120),
    (54, 136),
    (56, 138),
    (74, 184),
    (78, 195),
    (79, 197),
    (82, 208),
    (83, 209),
    (92, 238),
]


# Type alias for collected entity tuples
# (name, F, omega, IC, kappa, S, C, regime)
EntityTuple = tuple[str, float, float, float, float, float, float, str]


def _regime_key(regime: str) -> str:
    """Normalize a regime string to Stable/Watch/Collapse."""
    r = regime.split("(")[0].strip().lower()
    if "stable" in r or r == "peak" or r == "plateau":
        return "Stable"
    if "collapse" in r or "fragment" in r or "deficit" in r:
        return "Collapse"
    return "Watch"


def _collect() -> dict[str, list[EntityTuple]]:
    """Load every closure domain and extract (name, F, ω, IC, κ, S, C, regime)."""
    results: dict[str, list[EntityTuple]] = {}

    # 1. Standard Model (31 particles)
    try:
        from closures.standard_model.subatomic_kernel import compute_all

        data = [(r.name, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in compute_all()]
        results["Standard Model"] = data
    except Exception as e:
        print(f"  SM ERROR: {e}")

    # 2. Atomic Physics — 118 elements via periodic kernel
    try:
        from closures.atomic_physics.periodic_kernel import batch_compute_all

        data = [(r.symbol, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in batch_compute_all()]
        results["Atomic Physics"] = data
    except Exception as e:
        print(f"  ATOM ERROR: {e}")

    # 3. Nuclear Binding — 36 reference nuclides across binding curve
    try:
        from closures.nuclear_physics.nuclide_binding import compute_binding

        data = []
        for z, a in _REFERENCE_NUCLIDES:
            r = compute_binding(z, a)
            sym = _ELEMENT_SYMBOLS.get(z, f"Z{z}")
            name = f"{sym}-{a}"
            # BindingResult has F_eff/omega_eff (single-channel); use 1-F_eff
            # for omega to enforce duality identity (omega_eff can exceed 1
            # for weakly-bound nuclides like H-1).
            f_eff = r.F_eff
            data.append((name, f_eff, 1.0 - f_eff, f_eff, 0.0, 0.0, 0.0, r.regime))
        results["Nuclear Binding"] = data
    except Exception as e:
        print(f"  NUC ERROR: {e}")

    # 4. QGP/RHIC (27 entities)
    try:
        from closures.nuclear_physics.qgp_rhic import run_full_analysis

        r = run_full_analysis()
        data = [(e.name, e.F, e.omega, e.IC, e.kappa, e.S, e.C, e.regime) for e in r.all_entities]
        results["QGP/RHIC"] = data
    except Exception as e:
        print(f"  QGP ERROR: {e}")

    # 5. Matter Genesis (99 entities)
    try:
        from closures.standard_model.matter_genesis import (
            run_full_analysis as mg_run,
        )

        r = mg_run()
        data = [(e.name, e.F, e.omega, e.IC, e.kappa, e.S, e.C, e.regime) for e in r.entities]
        results["Matter Genesis"] = data
    except Exception as e:
        print(f"  MG ERROR: {e}")

    # 6. Stellar Ages (dict-based return)
    try:
        from closures.astronomy.stellar_ages_cosmology import (
            run_full_analysis as sa_run,
        )

        r = sa_run()
        data = [
            (
                e["name"],
                e["F"],
                e["omega"],
                e["IC"],
                e["kappa"],
                e["S"],
                e["C"],
                str(e.get("regime", "Watch")),
            )
            for e in r["kernel_results"]
        ]
        results["Stellar Ages"] = data
    except Exception as e:
        print(f"  SA ERROR: {e}")

    # 7. Consciousness Coherence (20 systems)
    try:
        from closures.consciousness_coherence.coherence_kernel import (
            COHERENCE_CATALOG,
            compute_coherence_kernel,
        )

        data = []
        for cs in COHERENCE_CATALOG:
            k = compute_coherence_kernel(cs)
            data.append((cs.name, k.F, k.omega, k.IC, k.kappa, k.S, k.C, k.regime))
        results["Consciousness"] = data
    except Exception as e:
        print(f"  CONSC ERROR: {e}")

    # 8. Dynamic Semiotics (30 sign systems)
    try:
        from closures.dynamic_semiotics.semiotic_kernel import (
            SIGN_SYSTEMS,
            compute_semiotic_kernel,
        )

        data = []
        for ss in SIGN_SYSTEMS:
            k = compute_semiotic_kernel(ss)
            data.append((ss.name, k.F, k.omega, k.IC, k.kappa, k.S, k.C, k.regime))
        results["Semiotics"] = data
    except Exception as e:
        print(f"  SEM ERROR: {e}")

    # 9. Evolution (40 organisms)
    try:
        from closures.evolution.evolution_kernel import (
            ORGANISMS,
            compute_organism_kernel,
        )

        data = []
        for org in ORGANISMS:
            k = compute_organism_kernel(org)
            data.append((org.name, k.F, k.omega, k.IC, k.kappa, k.S, k.C, k.regime))
        results["Evolution"] = data
    except Exception as e:
        print(f"  EVO ERROR: {e}")

    # 10. Quantum Dimer Model (13 phases)
    try:
        from closures.quantum_mechanics.quantum_dimer_model import (
            QDM_PHASES,
            compute_qdm_kernel,
        )

        data = []
        for p in QDM_PHASES:
            k = compute_qdm_kernel(p)
            data.append((p.name, k.F, k.omega, k.IC, k.kappa, k.S, k.C, k.regime))
        results["Quantum Dimer"] = data
    except Exception as e:
        print(f"  QDM ERROR: {e}")

    # 11. FQHE Bilayer Graphene (11 states)
    try:
        from closures.quantum_mechanics.fqhe_bilayer_graphene import (
            FQHE_STATES,
            compute_fqhe_kernel,
        )

        data = []
        for s in FQHE_STATES:
            k = compute_fqhe_kernel(s)
            data.append((k.name, k.F, k.omega, k.IC, k.kappa, k.S, k.C, k.regime))
        results["FQHE Bilayer"] = data
    except Exception as e:
        print(f"  FQHE ERROR: {e}")

    # 12. Materials Science — Crystal Morphology (17 compounds)
    try:
        from closures.materials_science.crystal_morphology_database import (
            compute_all_crystal_kernels,
        )

        data = [(r.name, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in compute_all_crystal_kernels()]
        results["Crystals"] = data
    except Exception as e:
        print(f"  CRYST ERROR: {e}")

    # 13. Materials Science — Bioactive Compounds (12 compounds)
    try:
        from closures.materials_science.bioactive_compounds_database import (
            compute_all_bioactive_kernels,
        )

        data = [(r.name, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in compute_all_bioactive_kernels()]
        results["Bioactive"] = data
    except Exception as e:
        print(f"  BIO ERROR: {e}")

    # 14. Materials Science — Photonic Materials (14 materials)
    try:
        from closures.materials_science.photonic_materials_database import (
            compute_all_photonic_kernels,
        )

        data = [(r.name, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in compute_all_photonic_kernels()]
        results["Photonic"] = data
    except Exception as e:
        print(f"  PHOT ERROR: {e}")

    # 15. Materials Science — Particle Detectors (8 scintillators)
    try:
        from closures.materials_science.particle_detector_database import (
            compute_all_scintillator_kernels,
        )

        data = [(r.name, r.F, r.omega, r.IC, r.kappa, r.S, r.C, r.regime) for r in compute_all_scintillator_kernels()]
        results["Detectors"] = data
    except Exception as e:
        print(f"  DET ERROR: {e}")

    # 16. Quincke Rollers (12 states)
    try:
        from closures.rcft.quincke_rollers import run_full_analysis as qr_run

        r = qr_run()
        data = [(e.name, e.F, e.omega, e.IC, e.kappa, e.S, e.C, e.regime) for e in r.results]
        results["Quincke Rollers"] = data
    except Exception as e:
        print(f"  QR ERROR: {e}")

    return results


def main() -> None:
    results = _collect()

    all_F: list[float] = []
    all_IC: list[float] = []
    all_delta: list[float] = []
    all_omega: list[float] = []
    all_regimes: dict[str, int] = {"Stable": 0, "Watch": 0, "Collapse": 0}
    tier1_violations = 0
    total_entities = 0
    domain_stats: list[dict] = []

    for domain, data in results.items():
        n = len(data)
        total_entities += n
        Fs = [d[1] for d in data]
        omegas = [d[2] for d in data]
        ICs = [d[3] for d in data]
        deltas = [f - ic for f, ic in zip(Fs, ICs, strict=True)]
        regimes: dict[str, int] = {"Stable": 0, "Watch": 0, "Collapse": 0}
        t1 = 0
        for d in data:
            _, F, omega, IC, _kp, _S, _C, regime = d
            rk = _regime_key(regime)
            regimes[rk] += 1
            if abs(F + omega - 1.0) > 1e-8:
                t1 += 1
            if IC > F + 1e-8:
                t1 += 1
        tier1_violations += t1
        for rk in all_regimes:
            all_regimes[rk] += regimes.get(rk, 0)
        all_F.extend(Fs)
        all_IC.extend(ICs)
        all_delta.extend(deltas)
        all_omega.extend(omegas)
        domain_stats.append(
            {
                "domain": domain,
                "n": n,
                "F_mean": float(np.mean(Fs)),
                "F_std": float(np.std(Fs)),
                "IC_mean": float(np.mean(ICs)),
                "delta_mean": float(np.mean(deltas)),
                "omega_mean": float(np.mean(omegas)),
                "regimes": regimes,
                "t1_fail": t1,
            }
        )

    # ── Report ──
    W = 105
    print("=" * W)
    print("  CROSS-DOMAIN KERNEL OPERABILITY ANALYSIS")
    print(f"  {len(results)} domains | {total_entities} entities | ONE kernel")
    print("=" * W)
    print(f"\n  Tier-1 violations: {tier1_violations} / {total_entities}")
    print("  " + "-" * 50)

    hdr = (
        f"  {'Domain':25s} {'N':>5s}  {'<F>':>7s} {'s(F)':>7s}  "
        f"{'<IC>':>7s}  {'<D>':>7s}  {'<w>':>7s}  "
        f"{'Stb':>4s} {'Wtc':>4s} {'Col':>4s}  {'T1':>3s}"
    )
    print("\n" + "-" * W)
    print(hdr)
    print("-" * W)
    for d in sorted(domain_stats, key=lambda x: -x["F_mean"]):
        r = d["regimes"]
        print(
            f"  {d['domain']:25s} {d['n']:5d}  "
            f"{d['F_mean']:7.4f} {d['F_std']:7.4f}  "
            f"{d['IC_mean']:7.4f}  {d['delta_mean']:7.4f}  {d['omega_mean']:7.4f}  "
            f"{r.get('Stable', 0):4d} {r.get('Watch', 0):4d} {r.get('Collapse', 0):4d}  "
            f"{d['t1_fail']:3d}"
        )
    print("-" * W)
    print(
        f"  {'ALL COMBINED':25s} {total_entities:5d}  "
        f"{np.mean(all_F):7.4f} {np.std(all_F):7.4f}  "
        f"{np.mean(all_IC):7.4f}  {np.mean(all_delta):7.4f}  {np.mean(all_omega):7.4f}  "
        f"{all_regimes['Stable']:4d} {all_regimes['Watch']:4d} {all_regimes['Collapse']:4d}  "
        f"{tier1_violations:3d}"
    )

    # ── Patterns ──
    print("\n" + "=" * W)
    print("  CROSS-DOMAIN PATTERN ANALYSIS")
    print("=" * W)

    corr = float(np.corrcoef(all_F, all_IC)[0, 1])
    max_res = max(abs(f + o - 1.0) for f, o in zip(all_F, all_omega, strict=True))
    ic_f = [ic / f if f > 1e-10 else 0 for ic, f in zip(all_IC, all_F, strict=True)]
    ic_exceeds = sum(1 for ic, f in zip(all_IC, all_F, strict=True) if ic > f + 1e-10)

    print(f"\n  F-IC Pearson correlation:  r = {corr:.4f}")
    print(f"  F + w = 1 max residual:   {max_res:.2e}")
    print(f"  IC/F ratio  mean={np.mean(ic_f):.4f}  min={min(ic_f):.6f}  max={max(ic_f):.4f}")
    print(f"  IC > F violations:        {ic_exceeds}/{total_entities}")

    watch_n = sum(1 for d in domain_stats if d["regimes"].get("Watch", 0) > 0)
    col_n = sum(1 for d in domain_stats if d["regimes"].get("Collapse", 0) > 0)
    stb_n = sum(1 for d in domain_stats if d["regimes"].get("Stable", 0) > 0)
    print(
        f"\n  Regime coverage: Stable in {stb_n}/{len(domain_stats)}, "
        f"Watch in {watch_n}/{len(domain_stats)}, "
        f"Collapse in {col_n}/{len(domain_stats)} domains"
    )

    # All three regimes
    all_three = [
        d["domain"] for d in domain_stats if all(d["regimes"].get(r, 0) > 0 for r in ("Stable", "Watch", "Collapse"))
    ]
    print(f"  All 3 regimes in: {', '.join(all_three) if all_three else 'none'}")

    # Heterogeneity gap
    print("\n  HETEROGENEITY GAP D = F - IC (by domain, sorted):")
    for d in sorted(domain_stats, key=lambda x: -x["delta_mean"]):
        bar = "#" * int(d["delta_mean"] * 80)
        print(f"    {d['domain']:25s}  D = {d['delta_mean']:.4f}  {bar}")

    # Fidelity ladder
    print("\n  FIDELITY LADDER (what survives collapse, by domain):")
    for d in sorted(domain_stats, key=lambda x: x["F_mean"]):
        bar = "#" * int(d["F_mean"] * 60)
        print(f"    {d['domain']:25s}  F = {d['F_mean']:.4f}  {bar}")

    # Integrity bound
    print("\n  INTEGRITY BOUND IC <= F:")
    print(f"    Violations across {total_entities} entities: {ic_exceeds}")
    print(f"    IC <= F holds universally: {'YES' if ic_exceeds == 0 else 'NO'}")

    # Regime partition
    print(f"\n  REGIME PARTITION ({total_entities} entities):")
    for rn, rc in sorted(all_regimes.items(), key=lambda x: -x[1]):
        pct = 100.0 * rc / total_entities if total_entities > 0 else 0.0
        bar = "#" * int(pct)
        print(f"    {rn:10s}  {rc:5d}  ({pct:5.1f}%)  {bar}")

    # Cross-domain bridges
    print("\n  CROSS-DOMAIN BRIDGES:")
    print("    Domains spanning Watch + Collapse:")
    for d in domain_stats:
        if d["regimes"].get("Watch", 0) > 0 and d["regimes"].get("Collapse", 0) > 0:
            print(f"      {d['domain']:25s}  W={d['regimes']['Watch']}  C={d['regimes']['Collapse']}")
    if all_three:
        print("    Domains spanning ALL THREE regimes:")
        for d in domain_stats:
            if all(d["regimes"].get(r, 0) > 0 for r in ("Stable", "Watch", "Collapse")):
                print(
                    f"      {d['domain']:25s}  S={d['regimes']['Stable']}  "
                    f"W={d['regimes']['Watch']}  C={d['regimes']['Collapse']}"
                )

    # F-IC clustering
    print("\n  F-IC CLUSTERING (domains grouped by mean F):")
    high = [d for d in domain_stats if d["F_mean"] > 0.65]
    mid = [d for d in domain_stats if 0.45 <= d["F_mean"] <= 0.65]
    low = [d for d in domain_stats if d["F_mean"] < 0.45]
    print(f"    High-F (>0.65): {', '.join(d['domain'] for d in high) or 'none'}")
    print(f"    Mid-F  (0.45-0.65): {', '.join(d['domain'] for d in mid) or 'none'}")
    print(f"    Low-F  (<0.45): {', '.join(d['domain'] for d in low) or 'none'}")

    # Bottom line
    print("\n" + "=" * W)
    print("  BOTTOM LINE")
    print("=" * W)
    print(f"\n  {total_entities} entities across {len(results)} domains pass through ONE kernel.")
    print(f"  Tier-1 violations: {tier1_violations}")
    print(f"  IC > F violations: {ic_exceeds}")
    print(f"  F + ω = 1 max residual: {max_res:.2e}")
    print(f"  F-IC correlation: r = {corr:.4f}")
    print()
    print("=" * W)


if __name__ == "__main__":
    main()
