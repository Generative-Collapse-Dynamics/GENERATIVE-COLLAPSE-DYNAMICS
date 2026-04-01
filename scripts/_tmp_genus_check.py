"""Temp script to verify genus series kernel outputs."""

from __future__ import annotations

import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from closures.continuity_theory.topological_persistence import (
    compute_all_entities,
    verify_all_theorems,
)

results = compute_all_entities()
print(f"Entities: {len(results)}")
print(f"{'Name':<30} {'Cat':<14} {'F':>6} {'w':>6} {'IC':>6} {'D':>6} {'IC/F':>6} {'Regime':<10}")
print("-" * 90)
for r in results:
    d = r.F - r.IC
    icf = r.IC / r.F if r.F > 1e-8 else 0
    print(f"{r.name:<30} {r.category:<14} {r.F:6.3f} {r.omega:6.3f} {r.IC:6.3f} {d:6.3f} {icf:6.3f} {r.regime:<10}")

print()
print("=== GENUS SERIES (g=0 to g=10) ===")
genus_names = [
    "sphere",
    "torus",
    "genus_2_surface",
    "genus_3_surface",
    "genus_4_surface",
    "genus_5_surface",
    "genus_7_surface",
    "genus_10_surface",
]
for name in genus_names:
    r = next(x for x in results if x.name == name)
    d = r.F - r.IC
    icf = r.IC / r.F if r.F > 1e-8 else 0
    print(f"  {name:<25} F={r.F:.4f}  IC={r.IC:.4f}  D={d:.4f}  IC/F={icf:.4f}  S={r.S:.4f}  C={r.C:.4f}  {r.regime}")

print()
print("=== THEOREMS ===")
for t in verify_all_theorems():
    print(f"  {t['name']}: {'PASS' if t['passed'] else 'FAIL'}  {t}")
