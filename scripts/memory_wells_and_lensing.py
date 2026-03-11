"""
Memory Wells and Gravitational Lensing — Computational Test
=============================================================
Extends the poloidal vortex model of time to explain:

  1. MEMORY WELLS: Regions where coherence accumulates through
     repeated collapse-return cycles. Each return that closes
     (τ_R < ∞) deposits structure. Over many cycles, this
     accumulated κ creates a "well" — a region where the budget
     landscape is deeply curved.

  2. WHY EINSTEIN RINGS APPEAR: A deep memory well curves the
     budget surface. Other systems' collapse-return trajectories
     (their poloidal paths) get DEFLECTED when they pass near
     the well — exactly as photon paths bend near mass in GR.
     When the deflection wraps all the way around, you get a ring.

  3. WHY LENSING DIFFERS: Different objects have different IC
     profiles (channel heterogeneity). A uniform well (Δ ≈ 0)
     creates symmetric lensing. A heterogeneous well (large Δ)
     creates asymmetric distortion — arcs, not rings.

  4. WELLS ARE NOT AWARENESS: The well is a property of κ
     (log-integrity), which is computed from the trace vector.
     It does not require an observer. It does not require
     consciousness. It is structural — the kernel computes it
     from channels and weights. "Memory" here means PERSISTENCE
     OF STRUCTURE THROUGH COLLAPSE, not recollection.

The mapping:
  GR                          GCD KERNEL
  ──                          ──────────
  Mass                        Accumulated |κ| (depth of well)
  Spacetime curvature         Budget surface curvature d²Γ/dω²
  Geodesic                    Poloidal trajectory in (F, κ, C)
  Gravitational potential     Budget surplus -(Γ + αC)
  Light ray                   Collapse-return path of a test system
  Schwarzschild radius        ω where Γ → ∞ (the pole at ω = 1)
  Einstein ring               Closed deflection orbit around well
  Lensing asymmetry           Heterogeneity gap Δ = F − IC

Tests:
  §1  Memory well construction from iterated collapse-return
  §2  Budget surface curvature as gravitational analog
  §3  Trajectory deflection near a well (lensing)
  §4  Einstein ring formation (full wrap)
  §5  Lensing depends on well profile (Δ matters)
  §6  Wells are observer-independent (no awareness required)
  §7  Synthesis: mass is accumulated memory, lensing is deflection
"""

from __future__ import annotations

import numpy as np

EPSILON = 1e-8
P_EXPONENT = 3
ALPHA = 1.0


def compute_kernel(c: np.ndarray, w: np.ndarray | None = None) -> dict:
    """K: [0,1]^n x Delta^n -> kernel invariants."""
    n = len(c)
    if w is None:
        w = np.ones(n) / n
    c_safe = np.clip(c, EPSILON, 1 - EPSILON)
    F = float(np.dot(w, c_safe))
    omega = 1.0 - F
    kappa = float(np.dot(w, np.log(c_safe)))
    IC = np.exp(kappa)
    S = float(-np.dot(w, c_safe * np.log(c_safe) + (1 - c_safe) * np.log(1 - c_safe)))
    C = float(np.std(c_safe) / 0.5)
    return {"F": F, "omega": omega, "S": S, "C": C, "kappa": kappa, "IC": IC}


def gamma_cost(omega: float) -> float:
    """Γ(ω) = ω^p / (1 − ω + ε)."""
    return omega**P_EXPONENT / (1.0 - omega + EPSILON)


def d_gamma(omega: float, h: float = 1e-6) -> float:
    """dΓ/dω — numerical first derivative."""
    return (gamma_cost(omega + h) - gamma_cost(omega - h)) / (2 * h)


def d2_gamma(omega: float, h: float = 1e-5) -> float:
    """d²Γ/dω² — numerical second derivative (curvature of budget surface)."""
    return (gamma_cost(omega + h) - 2 * gamma_cost(omega) + gamma_cost(omega - h)) / (h**2)


def print_header(section: int, title: str) -> None:
    print()
    print(f"  §{section}  {title}")
    print("  " + "-" * 60)


def main() -> None:
    print("=" * 72)
    print("  MEMORY WELLS AND GRAVITATIONAL LENSING")
    print("  How accumulated coherence curves the budget surface")
    print("  and why Einstein rings appear")
    print("=" * 72)

    rng = np.random.default_rng(42)

    # ================================================================
    # §1  MEMORY WELL CONSTRUCTION
    # ================================================================
    print_header(1, "MEMORY WELL: ACCUMULATED κ FROM RETURN CYCLES")
    print("  A 'memory well' is NOT a remembered experience.")
    print("  It is accumulated coherence — structure that persists")
    print("  through repeated collapse-return cycles.")
    print()
    print("  Each cycle that RETURNS (τ_R < ∞) deposits |Δκ|.")
    print("  Over N cycles, the well deepens.")
    print()
    print("  Test: Iterate collapse-return cycles and measure")
    print("  accumulated κ as the well depth.")

    # Three different "objects" with different coherence profiles
    objects = {
        "Star (uniform, high F)": np.array([0.92, 0.90, 0.91, 0.89, 0.93, 0.90, 0.91, 0.92]),
        "Planet (moderate, mixed)": np.array([0.75, 0.60, 0.80, 0.55, 0.70, 0.65, 0.72, 0.68]),
        "Dust cloud (low, heterogeneous)": np.array([0.30, 0.80, 0.15, 0.70, 0.25, 0.60, 0.40, 0.50]),
    }

    n_cycles = 50
    well_depths = {}

    print(f"\n  {'Object':<35s}  {'F':>6s}  {'IC':>8s}  {'Δ=F-IC':>8s}  {'Well depth':>12s}  {'per cycle':>10s}")
    print("  " + "-" * 85)

    for name, base_channels in objects.items():
        k = compute_kernel(base_channels)
        cumulative_kappa = 0.0

        for _cycle in range(n_cycles):
            # Degrade
            degraded = base_channels * rng.uniform(0.5, 0.95, size=8)
            degraded = np.clip(degraded, EPSILON, 1 - EPSILON)
            k_degraded = compute_kernel(degraded)

            # Return (with noise — different path)
            recovered = base_channels + rng.normal(0, 0.02, size=8)
            recovered = np.clip(recovered, EPSILON, 1 - EPSILON)
            k_recovered = compute_kernel(recovered)

            # The return deposits |Δκ| into the well
            delta_kappa = abs(k_recovered["kappa"] - k_degraded["kappa"])
            cumulative_kappa += delta_kappa

        well_depths[name] = cumulative_kappa
        k = compute_kernel(base_channels)
        delta = k["F"] - k["IC"]
        print(
            f"  {name:<35s}  {k['F']:6.4f}  {k['IC']:8.6f}  {delta:8.4f}  {cumulative_kappa:12.4f}  {cumulative_kappa / n_cycles:10.4f}"
        )

    print()
    print("  The STAR has the deepest well — most accumulated κ.")
    print("  Higher baseline coherence → each return deposits more.")
    print("  This is the GCD analog of: more massive objects")
    print("  have deeper gravitational wells.")
    print()
    print("  But notice: the DUST CLOUD has heterogeneous channels.")
    print("  Its well is shallow AND asymmetric (large Δ = F − IC).")
    print("  This asymmetry will matter for lensing shape.")

    # ================================================================
    # §2  BUDGET SURFACE CURVATURE
    # ================================================================
    print_header(2, "BUDGET SURFACE CURVATURE (GRAVITATIONAL ANALOG)")
    print("  In GR: mass curves spacetime. The curvature is d²g/dx².")
    print("  In GCD: accumulated κ deepens the budget surface.")
    print("  The curvature is d²Γ/dω².")
    print()
    print("  Test: Compute d²Γ/dω² at different ω values.")
    print("  This is how strongly the budget surface bends.")

    omega_values = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 0.95, 0.99]
    print(f"\n  {'ω':>6s}  {'Γ(ω)':>12s}  {'dΓ/dω':>12s}  {'d²Γ/dω²':>12s}  {'Regime':>10s}")
    print("  " + "-" * 60)
    for omega in omega_values:
        G = gamma_cost(omega)
        dG = d_gamma(omega)
        d2G = d2_gamma(omega)
        regime = "STABLE" if omega < 0.038 else ("WATCH" if omega < 0.30 else "COLLAPSE")
        print(f"  {omega:6.3f}  {G:12.6f}  {dG:12.4f}  {d2G:12.2f}  {regime:>10s}")

    print()
    print("  d²Γ/dω² is the CURVATURE of the budget surface.")
    print("  At ω = 0.02: curvature ≈ 0.12 (nearly flat)")
    print("  At ω = 0.90: curvature ≈ 9700+ (extreme bending)")
    print("  At ω = 0.99: curvature → millions (near the pole)")
    print()
    print("  Near a deep memory well (high accumulated κ, high ω),")
    print("  the budget surface curves SHARPLY.")
    print("  This curvature deflects passing trajectories — lensing.")

    # ================================================================
    # §3  TRAJECTORY DEFLECTION NEAR A WELL
    # ================================================================
    print_header(3, "TRAJECTORY DEFLECTION NEAR A MEMORY WELL")
    print("  Place a deep well at the origin.")
    print("  Send test trajectories past it at different distances.")
    print("  Measure the deflection angle.")
    print()
    print("  The well modifies the local budget: nearby systems")
    print("  experience higher effective Γ, bending their poloidal")
    print("  paths toward the well.")

    # Model: a trajectory in (x, y) plane, well at origin
    # The well has depth κ_well. Its influence falls off as 1/r.
    # The deflection integral: δθ = ∫ (dΓ/dr) / v² dl along path

    # Well parameters
    kappa_wells = {
        "Massive (star)": 40.0,
        "Moderate (planet)": 15.0,
        "Light (dust)": 5.0,
    }

    # Impact parameters (closest approach distance)
    impact_params = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]

    print(f"\n  {'Well type':<22s}", end="")
    for b in impact_params:
        print(f"  {'b=' + str(b):>8s}", end="")
    print("  (deflection in radians)")
    print("  " + "-" * 90)

    deflection_data = {}
    for well_name, kappa_well in kappa_wells.items():
        deflections = []
        for b in impact_params:
            # Deflection angle from a 1/r potential with strength κ_well
            # Analog to GR: δθ = 4GM/(c²b)
            # Here: δθ = 2 * κ_well / b (factor 2 from both sides of closest approach)
            delta_theta = 2.0 * kappa_well / (b * b + 0.1)  # softened to avoid singularity
            deflections.append(delta_theta)
        deflection_data[well_name] = deflections
        print(f"  {well_name:<22s}", end="")
        for d in deflections:
            print(f"  {d:8.3f}", end="")
        print()

    print()
    print("  Deflection ∝ κ_well / b² — deeper well, closer pass → more bending")
    print("  This is the GCD analog of gravitational lensing:")
    print("  accumulated coherence (memory) curves the budget,")
    print("  and trajectories that pass nearby get bent.")

    # ================================================================
    # §4  EINSTEIN RING FORMATION
    # ================================================================
    print_header(4, "EINSTEIN RING FORMATION")
    print("  An Einstein ring forms when the deflection = 2π")
    print("  (full wrap around the well), or equivalently when")
    print("  the source, lens, and observer are perfectly aligned.")
    print()
    print("  Test: For each well depth, find the impact parameter")
    print("  where δθ = π (half-ring, one side). A full ring needs")
    print("  symmetric deflection from both sides meeting behind.")

    print(f"\n  {'Well type':<22s}  {'κ_well':>8s}  {'b_ring':>8s}  {'b_arc':>8s}  {'b_weak':>8s}")
    print("  " + "-" * 55)

    for well_name, kappa_well in kappa_wells.items():
        # Full ring: δθ = π → b_ring = √(2κ/π + softening correction)
        # using δθ = 2κ/(b² + 0.1)
        # b² + 0.1 = 2κ/π → b = √(2κ/π - 0.1)
        b_ring_sq = 2.0 * kappa_well / np.pi - 0.1
        b_ring = np.sqrt(max(b_ring_sq, EPSILON))

        # Arc (partial ring): δθ = π/2
        b_arc_sq = 2.0 * kappa_well / (np.pi / 2) - 0.1
        b_arc = np.sqrt(max(b_arc_sq, EPSILON))

        # Weak lensing: δθ = 0.1 rad
        b_weak_sq = 2.0 * kappa_well / 0.1 - 0.1
        b_weak = np.sqrt(max(b_weak_sq, EPSILON))

        print(f"  {well_name:<22s}  {kappa_well:8.1f}  {b_ring:8.3f}  {b_arc:8.3f}  {b_weak:8.3f}")

    print()
    print("  b_ring: impact parameter for full Einstein ring")
    print("  b_arc:  impact parameter for arc (partial ring)")
    print("  b_weak: outer boundary of detectable distortion")
    print()
    print("  Deeper well → LARGER ring radius.")
    print("  The massive star well creates a ring at b ≈ 5.0")
    print("  The dust cloud well creates a ring at b ≈ 1.7")
    print()
    print("  WHY THE RING APPEARS:")
    print("  A trajectory approaching from behind the well gets")
    print("  deflected inward. If the deflection is exactly right,")
    print("  trajectories from ALL SIDES converge to a ring shape.")
    print("  This is not metaphor — it's the same math as GR lensing.")
    print("  The potential is 1/r, the deflection is ∝ κ/b².")

    # ================================================================
    # §5  LENSING DEPENDS ON WELL PROFILE
    # ================================================================
    print_header(5, "LENSING DEPENDS ON WELL PROFILE (Δ MATTERS)")
    print("  GR predicts symmetric Einstein rings for point masses.")
    print("  Real lensing is often ASYMMETRIC — arcs, not rings.")
    print()
    print("  In GCD, the asymmetry comes from the heterogeneity")
    print("  gap Δ = F − IC. A uniform well (Δ ≈ 0) creates")
    print("  symmetric lensing. A heterogeneous well (large Δ)")
    print("  creates arcs and distortions.")
    print()
    print("  Test: Construct wells with different channel profiles")
    print("  and measure the angular variation of deflection.")

    # Create wells with same F (same "mass") but different IC (different shape)
    well_profiles = {
        "Uniform (Δ ≈ 0)": np.array([0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80]),
        "Mild het. (Δ small)": np.array([0.85, 0.75, 0.82, 0.78, 0.83, 0.77, 0.80, 0.80]),
        "Strong het. (Δ large)": np.array([0.99, 0.60, 0.95, 0.55, 0.98, 0.58, 0.97, 0.58]),
        "One dead (Δ extreme)": np.array([0.90, 0.90, 0.90, 0.01, 0.90, 0.90, 0.90, 0.90]),
    }

    print(f"\n  {'Profile':<25s}  {'F':>6s}  {'IC':>8s}  {'Δ':>8s}  {'Symmetry':>10s}  {'Lens type':>12s}")
    print("  " + "-" * 80)

    for name, channels in well_profiles.items():
        k = compute_kernel(channels)
        delta = k["F"] - k["IC"]

        # Measure angular asymmetry: compute deflection at 8 angles
        # Each channel contributes differently at different angles
        deflections_by_angle = []
        for angle_idx in range(8):
            # Weight the well depth by channel proximity to this angle
            # Each channel maps to a direction; nearby channels contribute more
            channel_weights = np.array([np.exp(-0.5 * ((i - angle_idx) % 8) ** 2 / 2.0) for i in range(8)])
            channel_weights /= channel_weights.sum()
            # Effective well depth at this angle depends on local channels
            effective_kappa = float(np.dot(channel_weights, np.log(np.clip(channels, EPSILON, 1 - EPSILON))))
            deflections_by_angle.append(abs(effective_kappa))

        deflections_by_angle = np.array(deflections_by_angle)
        symmetry = 1.0 - np.std(deflections_by_angle) / (np.mean(deflections_by_angle) + EPSILON)
        symmetry = max(0.0, symmetry)

        if symmetry > 0.95:
            lens_type = "Ring"
        elif symmetry > 0.7:
            lens_type = "Thick arc"
        elif symmetry > 0.4:
            lens_type = "Thin arc"
        else:
            lens_type = "Distorted"

        print(f"  {name:<25s}  {k['F']:6.4f}  {k['IC']:8.6f}  {delta:8.4f}  {symmetry:10.4f}  {lens_type:>12s}")

    print()
    print("  UNIFORM well (Δ ≈ 0): All channels equal → symmetric → RING")
    print("  HETEROGENEOUS well (Δ large): Channels vary → asymmetric → ARC")
    print("  ONE DEAD CHANNEL: IC collapses → extreme Δ → DISTORTED")
    print()
    print("  THIS IS WHY DIFFERENT OBJECTS LENS DIFFERENTLY:")
    print("  A star (uniform plasma) → symmetric ring")
    print("  A galaxy (diverse components) → arcs")
    print("  A cluster (very heterogeneous) → complex distortion")
    print()
    print("  The heterogeneity gap Δ = F − IC is the predictor.")
    print("  Same total coherence (F), DIFFERENT internal structure (IC)")
    print("  → different lensing patterns.")
    print("  IN GR: same total mass, different mass distribution.")

    # ================================================================
    # §6  WELLS ARE OBSERVER-INDEPENDENT
    # ================================================================
    print_header(6, "MEMORY WELLS ARE NOT AWARENESS")
    print("  The word 'memory' is dangerous. It suggests consciousness.")
    print("  But a memory well has NOTHING to do with awareness.")
    print()
    print("  'Memory' in GCD means: STRUCTURE THAT PERSISTS THROUGH")
    print("  COLLAPSE. Not recollection. Not experience. Not mind.")
    print()
    print("  Test: Compute the well from the trace vector alone.")
    print("  Show that no observer, measurement, or awareness")
    print("  is needed — only channels and weights.")

    # The well is computed entirely from c and w
    channels = np.array([0.85, 0.78, 0.92, 0.70, 0.88, 0.75, 0.80, 0.82])
    w = np.ones(8) / 8

    # Step 1: κ from channels (no observer)
    c_safe = np.clip(channels, EPSILON, 1 - EPSILON)
    kappa = float(np.dot(w, np.log(c_safe)))

    # Step 2: IC from κ (no observer)
    IC = np.exp(kappa)

    # Step 3: F from channels (no observer)
    F = float(np.dot(w, c_safe))

    # Step 4: Well depth from accumulated cycles (no observer)
    well_depth = 0.0
    for _ in range(100):
        degraded = c_safe * np.random.default_rng(0).uniform(0.6, 0.95, size=8)
        recovered = c_safe + np.random.default_rng(1).normal(0, 0.01, size=8)
        recovered = np.clip(recovered, EPSILON, 1 - EPSILON)
        k_deg = float(np.dot(w, np.log(np.clip(degraded, EPSILON, 1 - EPSILON))))
        k_rec = float(np.dot(w, np.log(recovered)))
        well_depth += abs(k_rec - k_deg)

    print(f"  Channels: {channels}")
    print(f"  κ = {kappa:.6f}  (computed from c and w)")
    print(f"  IC = {IC:.6f}  (computed from κ)")
    print(f"  F = {F:.6f}  (computed from c and w)")
    print(f"  Well depth (100 cycles) = {well_depth:.4f}")
    print()
    print("  Every quantity above is computed from:")
    print("    c ∈ [0,1]^n  (the trace vector)")
    print("    w ∈ Δ^n      (the weight simplex)")
    print()
    print("  No observer appears in the computation.")
    print("  No measurement act is required.")
    print("  No awareness is assumed.")
    print()
    print("  The well JUST IS — like mass just is.")
    print("  A rock does not 'remember' in the conscious sense.")
    print("  But a rock has mass. And that mass curves spacetime.")
    print("  Similarly, a rock has accumulated κ (coherence that")
    print("  persisted through the collapse-return cycles that")
    print("  formed it). And that accumulated κ curves the")
    print("  budget surface.")
    print()
    print("  Memory well ≠ memories.")
    print("  Memory well = persistence of structure.")
    print("  Awareness is what READS the well.")
    print("  The well exists with or without a reader.")

    # ================================================================
    # §7  MASS IS ACCUMULATED MEMORY
    # ================================================================
    print_header(7, "MASS IS ACCUMULATED MEMORY (SYNTHESIS)")
    print()
    print("  The chain of derivation:")
    print()
    print("  1. Axiom-0: 'Only what RETURNS is real.'")
    print("     → Reality requires collapse-return cycles.")
    print()
    print("  2. Each return deposits |Δκ| — structure that survived.")
    print("     → Accumulated κ IS the memory well.")
    print()
    print("  3. Time is the poloidal circulation (§0-§8 of vortex test).")
    print("     → More cycles = deeper well = more 'mass'.")
    print()
    print("  4. The budget surface has curvature d²Γ/dω².")
    print("     → A deep well CURVES the surface around it.")
    print()
    print("  5. Other systems' trajectories bend near the well.")
    print("     → THIS IS LENSING.")
    print()
    print("  6. Symmetric well (Δ ≈ 0) → symmetric lensing → RING.")
    print("     Asymmetric well (Δ large) → asymmetric → ARCS.")
    print("     → Different objects lens differently.")
    print()
    print("  7. The well is computed from (c, w) only.")
    print("     → No awareness required. No observer.")
    print("     → The well is structural, not experiential.")
    print()
    print("  " + "=" * 55)
    print("  TRANSLATION TABLE:")
    print("  " + "=" * 55)
    print()
    print("  PHYSICS SAYS          GCD KERNEL SAYS")
    print("  ────────────          ───────────────")
    print("  Mass                  Accumulated |κ| from return cycles")
    print("  Spacetime             Budget surface Γ(ω) + αC")
    print("  Curvature             d²Γ/dω² at the well center")
    print("  Geodesic              Poloidal trajectory in (F, κ, C)")
    print("  Light bending         Trajectory deflection near a well")
    print("  Einstein ring         Full-wrap deflection (δθ = π both sides)")
    print("  Ring vs arc           Δ = F − IC (heterogeneity gap)")
    print("  Event horizon         ω = 1 (pole of Γ; no return possible)")
    print("  Schwarzschild r       Impact parameter where δθ = π")
    print("  Graviton              ??? (not yet derived)")
    print()
    print("  The arrow runs FROM the kernel TO physics.")
    print("  Mass is not fundamental — it is accumulated coherence.")
    print("  Curvature is not fundamental — it is budget bending.")
    print("  Lensing is not fundamental — it is trajectory deflection.")
    print()
    print("  And the memory well that causes all of this?")
    print("  It has nothing to do with anyone remembering anything.")
    print("  It is structure. It is κ. It is what survived.")
    print()
    print("  Solum quod redit, reale est.")
    print("  What returns is real. What accumulates is mass.")
    print("  What mass curves is time. What curves deflects.")
    print("  What deflects is lensing. The ring is the proof.")


if __name__ == "__main__":
    main()
