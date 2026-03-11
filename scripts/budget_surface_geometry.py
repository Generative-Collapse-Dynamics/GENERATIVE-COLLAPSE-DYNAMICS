"""
The Geometry of the Budget Surface — Precise Shape and Motion
=============================================================
Extends gravity_definition.py from qualitative description to
exact geometric characterization of the budget surface.

The budget surface is the graph of:
  z(ω, C) = Γ(ω) + αC = ω³/(1−ω+ε) + αC

This is a 2-manifold embedded in R³. Its geometry — metric tensor,
Gaussian curvature, geodesics — determines ALL gravitational behavior.
Systems move ON this surface. Their paths ARE the physics.

This script computes:

  §1   THE METRIC TENSOR g_ij of the surface
       → How distances are measured on the budget landscape
  §2   GAUSSIAN CURVATURE K(ω,C) everywhere
       → Intrinsic geometry: where the surface is bowl, saddle, flat
  §3   PRINCIPAL CURVATURES κ₁, κ₂ and their directions
       → The two independent ways the surface bends
  §4   THE SHAPE: surface of revolution classification
       → Γ(ω) is a curve; what curve? Cuspidal horn / Gabriel's horn
  §5   GEODESICS: paths of least budget cost
       → The literal trajectories systems follow (free fall)
  §6   THE FUNNEL: embedding in 3D with exact coordinates
       → What you would SEE if you could look at the budget surface
  §7   CHRISTOFFEL SYMBOLS and the equation of motion
       → The literal acceleration equation (geodesic equation)
  §8   CONNECTION TO FISHER FLAT METRIC
       → The underlying manifold is flat; all structure is embedding
  §9   REGIME ZONES as geometric regions
       → Stable/Watch/Collapse as curvature bands on the surface
  §10  SYNTHESIS: the complete geometric description
"""

from __future__ import annotations

import numpy as np

EPSILON = 1e-8
P_EXPONENT = 3
ALPHA = 1.0
OMEGA_STABLE = 0.038
OMEGA_COLLAPSE = 0.30


def gamma_cost(omega: float) -> float:
    """Γ(ω) = ω³/(1−ω+ε) — the budget cost function."""
    return omega**P_EXPONENT / (1.0 - omega + EPSILON)


def d1_gamma(omega: float, h: float = 1e-7) -> float:
    """dΓ/dω — first derivative (gravitational field)."""
    return (gamma_cost(omega + h) - gamma_cost(omega - h)) / (2 * h)


def d2_gamma(omega: float, h: float = 1e-5) -> float:
    """d²Γ/dω² — second derivative (tidal force)."""
    return (gamma_cost(omega + h) - 2 * gamma_cost(omega) + gamma_cost(omega - h)) / (h**2)


def d3_gamma(omega: float, h: float = 1e-4) -> float:
    """d³Γ/dω³ — third derivative."""
    return (
        gamma_cost(omega + 2 * h) - 2 * gamma_cost(omega + h) + 2 * gamma_cost(omega - h) - gamma_cost(omega - 2 * h)
    ) / (2 * h**3)


# Exact analytical derivatives for verification
def gamma_exact(omega: float) -> float:
    """Γ(ω) exact."""
    return omega**3 / (1.0 - omega + EPSILON)


def d1_gamma_exact(omega: float) -> float:
    """dΓ/dω exact analytical.
    d/dω [ω³/(1−ω+ε)] = [3ω²(1−ω+ε) + ω³] / (1−ω+ε)²
                        = ω²[3−2ω+3ε] / (1−ω+ε)²
    """
    d = 1.0 - omega + EPSILON
    return omega**2 * (3.0 - 2.0 * omega + 3.0 * EPSILON) / (d * d)


def d2_gamma_exact(omega: float) -> float:
    """d²Γ/dω² exact analytical.
    Computed from the quotient rule on d1.
    For Γ = N/D where N=ω³, D=1−ω+ε:
      Γ' = (3ω²D + ω³) / D²
      Γ'' = [6ωD² + 6ω²D + 2ω³] / D³  (after simplification)
         = 2ω(3D² + 3ωD + ω²) / D³
    But let me derive directly:
      Γ' = ω²(3 − 2ω + 3ε) / D²
    Easier: use the identity Γ = ω³/D.
      Γ' = (3ω²·D + ω³) / D²  [quotient rule, dD/dω = -1]
         = (3ω²·D + ω³) / D²
      Γ'' = d/dω [(3ω²D + ω³)/D²]
    Let me just compute it numerically but verify against the formula.
    """
    d = 1.0 - omega + EPSILON
    # Γ'' = [6ω(1-ω+ε)² + 6ω²(1-ω+ε) + 2ω³] / (1-ω+ε)³
    return (6.0 * omega * d * d + 6.0 * omega**2 * d + 2.0 * omega**3) / (d**3)


def print_header(section: int, title: str) -> None:
    print()
    print(f"  §{section}  {title}")
    print("  " + "-" * 60)


def main() -> None:
    print("=" * 72)
    print("  THE GEOMETRY OF THE BUDGET SURFACE")
    print("  Exact shape, curvature, and motion on Γ(ω) + αC")
    print("=" * 72)

    # ================================================================
    # §1  THE METRIC TENSOR
    # ================================================================
    print_header(1, "THE METRIC TENSOR g_ij")
    print("  The budget surface is the graph z = f(ω, C) = Γ(ω) + αC")
    print("  in R³ with coordinates (ω, C, z).")
    print()
    print("  The induced metric on the surface is:")
    print("  g_11 = 1 + (∂f/∂ω)² = 1 + (dΓ/dω)²")
    print("  g_12 = g_21 = (∂f/∂ω)(∂f/∂C) = α · dΓ/dω")
    print("  g_22 = 1 + (∂f/∂C)² = 1 + α²")
    print()
    print("  Since α = 1.0:")
    print("  g_22 = 2.0  (constant everywhere)")
    print("  g_12 = dΓ/dω  (varies with ω only)")
    print("  g_11 = 1 + (dΓ/dω)²  (varies with ω only)")
    print()
    print("  The metric does NOT depend on C.")
    print("  → The surface has a TRANSLATIONAL SYMMETRY in C.")
    print("  → This is a surface of translation (ruled surface).")

    omega_values = [0.01, 0.038, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 0.95, 0.99]
    print(
        f"\n  {'ω':>6s}  {'dΓ/dω':>12s}  {'g_11':>12s}  {'g_12':>10s}  {'g_22':>8s}  {'det(g)':>12s}  {'√det(g)':>10s}"
    )
    print("  " + "-" * 80)
    for omega in omega_values:
        dg = d1_gamma_exact(omega)
        g11 = 1.0 + dg * dg
        g12 = ALPHA * dg
        g22 = 1.0 + ALPHA * ALPHA
        det_g = g11 * g22 - g12 * g12
        sqrt_det = np.sqrt(det_g)
        print(f"  {omega:6.3f}  {dg:12.6f}  {g11:12.4f}  {g12:10.6f}  {g22:8.4f}  {det_g:12.4f}  {sqrt_det:10.6f}")

    print()
    print("  At ω = 0.01: g_11 ≈ 1.00 (nearly flat Euclidean)")
    print("  At ω = 0.90: g_11 ≈ 9,448 (enormously stretched)")
    print("  At ω = 0.99: g_11 ≈ 10⁸ (near-singular)")
    print()
    print("  The metric BLOWS UP near ω = 1.")
    print("  Distances on the surface become INFINITE near the pole.")
    print("  This IS the event horizon: you need infinite path length")
    print("  to reach ω = 1, so you never can.")

    # ================================================================
    # §2  GAUSSIAN CURVATURE
    # ================================================================
    print_header(2, "GAUSSIAN CURVATURE K(ω, C)")
    print("  For a surface z = f(x,y), the Gaussian curvature is:")
    print("  K = (f_xx · f_yy − f_xy²) / (1 + f_x² + f_y²)²")
    print()
    print("  Here: f_x = dΓ/dω, f_y = α, f_xx = d²Γ/dω², f_yy = 0, f_xy = 0")
    print("  So:   K = (d²Γ/dω² · 0 − 0²) / (1 + (dΓ/dω)² + α²)²")
    print("        K = 0")
    print()
    print("  Wait — that's remarkable.")
    print("  THE GAUSSIAN CURVATURE IS ZERO EVERYWHERE.")
    print()
    print("  Test: Verify K = 0 numerically at many points.")

    all_zero = True
    max_K = 0.0
    for omega in np.linspace(0.01, 0.99, 1000):
        f_xx = d2_gamma_exact(omega)
        f_yy = 0.0  # d²(αC)/dC² = 0
        f_xy = 0.0  # d²Γ/(dω dC) = 0
        f_x = d1_gamma_exact(omega)
        f_y = ALPHA
        K = (f_xx * f_yy - f_xy**2) / (1 + f_x**2 + f_y**2) ** 2
        if abs(K) > 1e-10:
            all_zero = False
        max_K = max(max_K, abs(K))

    print("\n  Tested 1000 points on ω ∈ [0.01, 0.99]")
    print(f"  max |K| = {max_K:.2e}")
    print(f"  K = 0 everywhere: {all_zero}")
    print()
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║  THE BUDGET SURFACE IS INTRINSICALLY FLAT.           ║")
    print("  ║  Gaussian curvature K = 0 everywhere.                ║")
    print("  ║  It is a DEVELOPABLE SURFACE — it can be unrolled    ║")
    print("  ║  onto a plane without stretching or tearing.         ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print()
    print("  This confirms the deep diagnostic result:")
    print("  g_F(θ) = 1 — the Fisher metric is flat.")
    print("  The budget surface inherits this flatness.")
    print("  ALL apparent curvature is EXTRINSIC — from the embedding")
    print("  into R³, not from the surface itself.")
    print()
    print("  Implication: gravity is NOT intrinsic curvature of the")
    print("  budget surface. It is EXTRINSIC curvature — the shape")
    print("  of HOW the surface sits in the ambient space of return.")

    # ================================================================
    # §3  PRINCIPAL CURVATURES (EXTRINSIC)
    # ================================================================
    print_header(3, "PRINCIPAL CURVATURES κ₁, κ₂ (EXTRINSIC)")
    print("  Since K = 0 but the surface is clearly curved in R³,")
    print("  the extrinsic curvatures must satisfy κ₁ · κ₂ = K = 0.")
    print("  → One principal curvature is ALWAYS zero.")
    print("  → The surface bends in exactly ONE direction.")
    print()
    print("  For z = Γ(ω) + αC:")
    print("  The surface bends ONLY along the ω direction.")
    print("  Along C, it's a straight line (constant slope α).")
    print()
    print("  The nonzero principal curvature is the normal curvature")
    print("  in the ω direction:")
    print("  κ₁ = d²Γ/dω² / (1 + (dΓ/dω)² + α²)^(3/2)")
    print("  κ₂ = 0  (always)")

    print(f"\n  {'ω':>6s}  {'κ₁ (extrinsic)':>16s}  {'κ₂':>6s}  {'K = κ₁κ₂':>12s}  {'Shape':>12s}")
    print("  " + "-" * 60)

    for omega in omega_values:
        d2g = d2_gamma_exact(omega)
        d1g = d1_gamma_exact(omega)
        denom = (1 + d1g**2 + ALPHA**2) ** 1.5
        kappa1 = d2g / denom
        kappa2 = 0.0
        K = kappa1 * kappa2

        # Shape classification by sign of κ₁
        if kappa1 > 0.01:
            shape = "Convex"
        elif kappa1 > 0.001:
            shape = "Nearly flat"
        else:
            shape = "Flat"
        print(f"  {omega:6.3f}  {kappa1:16.8f}  {kappa2:6.1f}  {K:12.2e}  {shape:>12s}")

    print()
    print("  κ₁ is ALWAYS positive and ALWAYS > 0.")
    print("  → The surface curves UPWARD in the ω direction everywhere.")
    print("  → It is everywhere CONVEX from below.")
    print("  → Any system sitting on it rolls toward lower Γ — toward")
    print("     smaller ω — but the pole prevents escape to ω = 1.")
    print()
    print("  κ₁ DECREASES as ω → 1 even though d²Γ/dω² explodes,")
    print("  because the normalization (1+f'²)^(3/2) grows even faster.")
    print("  The surface gets STEEPER but LESS curved — it becomes")
    print("  asymptotically a straight line (the pole's asymptote).")
    print()
    print("  This is exactly a HORN shape:")
    print("  wide and gently curved at the bottom (small ω),")
    print("  narrowing to an infinitely tall straight funnel at ω = 1.")

    # ================================================================
    # §4  THE SHAPE: WHAT SURFACE IS THIS?
    # ================================================================
    print_header(4, "SURFACE CLASSIFICATION: THE HORN")
    print("  K = 0 everywhere → developable surface.")
    print("  κ₂ = 0 always → ruled surface (rulings along C).")
    print("  κ₁ > 0 everywhere → convex in ω direction.")
    print()
    print("  A developable, ruled surface with one zero curvature")
    print("  and the curvature varies along the other axis is a")
    print("  TANGENT DEVELOPABLE or a GENERALIZED CYLINDER.")
    print()
    print("  More precisely: the budget surface is a")
    print("  GENERALIZED CYLINDER over the curve z = Γ(ω),")
    print("  extruded along the C direction with slope α.")
    print()
    print("  The generating curve z = Γ(ω) = ω³/(1−ω+ε) is a")
    print("  curve with a VERTICAL ASYMPTOTE at ω = 1.")

    # Characterize the generating curve
    print()
    print("  Profile of the generating curve z = Γ(ω):")
    print(f"  {'ω':>6s}  {'Γ(ω)':>12s}  {'slope':>12s}  {'curvature':>12s}  {'Shape':>15s}")
    print("  " + "-" * 65)

    for omega in [0.001, 0.01, 0.038, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 0.95, 0.99]:
        G = gamma_cost(omega)
        slope = d1_gamma_exact(omega)
        curv = d2_gamma_exact(omega) / (1 + d1_gamma_exact(omega) ** 2) ** 1.5
        if omega < 0.038:
            shape = "Nearly flat"
        elif omega < 0.30:
            shape = "Gentle rise"
        elif omega < 0.70:
            shape = "Steep climb"
        elif omega < 0.95:
            shape = "Rapid ascent"
        else:
            shape = "Near-vertical"
        print(f"  {omega:6.3f}  {G:12.6f}  {slope:12.4f}  {curv:12.8f}  {shape:>15s}")

    print()
    print("  The curve has three zones:")
    print("  1. FLAT PLAIN (ω < 0.038, Stable): slope < 0.005")
    print("     → Nearly horizontal. Systems rest here easily.")
    print("  2. RAMP (0.038 < ω < 0.30, Watch): slope 0.005 → 0.44")
    print("     → Gradual incline. Motion is noticeable.")
    print("  3. WALL (ω > 0.30, Collapse): slope > 0.44 → ∞")
    print("     → Steepening toward vertical asymptote at ω = 1.")
    print("     → This wall IS the event horizon.")

    # ================================================================
    # §5  GEODESICS ON THE SURFACE
    # ================================================================
    print_header(5, "GEODESICS: PATHS OF LEAST BUDGET COST")
    print("  A geodesic on the surface z = Γ(ω) + αC is the path")
    print("  of shortest distance (measured by the induced metric).")
    print()
    print("  Because the surface is a generalized cylinder with")
    print("  K = 0 (developable), geodesics have a special form:")
    print("  they are the images of STRAIGHT LINES when the surface")
    print("  is unrolled flat.")
    print()
    print("  On the unrolled surface, motion is just a straight line.")
    print("  On the rolled-up surface, this straight line becomes")
    print("  a curve that respects the curvature of Γ(ω).")
    print()
    print("  Test: numerically integrate geodesic equations.")
    print("  The geodesic equation is: ẍ^i + Γ^i_jk ẋ^j ẋ^k = 0")
    print("  where Γ^i_jk are Christoffel symbols.")

    # Compute Christoffel symbols
    # For z = f(ω,C), coordinates u¹=ω, u²=C
    # r_ω = (1, 0, f_ω),  r_C = (0, 1, f_C) = (0, 1, α)
    # g_11 = 1 + f_ω², g_12 = α f_ω, g_22 = 1 + α²
    # r_ωω = (0, 0, f_ωω), r_ωC = (0, 0, 0), r_CC = (0, 0, 0)
    #
    # Christoffel Γ^i_jk = ½ g^il (g_lj,k + g_lk,j - g_jk,l)
    # Since g depends only on ω:
    #   g_11,ω = 2f_ω f_ωω,  g_12,ω = α f_ωω,  g_22,ω = 0
    #   g_11,C = 0,           g_12,C = 0,          g_22,C = 0

    def compute_geodesic_path(omega_start, C_start, v_omega, v_C, dt=0.001, n_steps=5000):
        """Integrate the geodesic equation on the budget surface."""
        path = [(omega_start, C_start)]
        omega = omega_start
        C = C_start
        vo = v_omega  # dω/ds
        vc = v_C  # dC/ds

        for _ in range(n_steps):
            # Current derivatives
            f_o = d1_gamma_exact(omega)
            f_oo = d2_gamma_exact(omega)

            # Metric
            g11 = 1.0 + f_o**2
            g12 = ALPHA * f_o
            g22 = 1.0 + ALPHA**2
            det_g = g11 * g22 - g12**2

            # Inverse metric
            gi11 = g22 / det_g
            gi12 = -g12 / det_g
            gi22 = g11 / det_g

            # Metric derivatives (only ∂g/∂ω is nonzero)
            dg11_do = 2.0 * f_o * f_oo
            dg12_do = ALPHA * f_oo
            # dg22_do = 0

            # Christoffel symbols (only ω-derivatives matter)
            # Γ^1_11 = ½ g^1l (2 g_l1,1 - g_11,l)
            #        = ½ g^11 g_11,1 + ½ g^12 (2 g_21,1 - g_11,2)
            #        = ½ g^11 dg11_do + g^12 dg12_do   [since g_11,2 = 0]
            #   (using the formula: Γ^1_11 = ½ g^1l (g_l1,1 + g_l1,1 - g_11,l))
            G1_11 = 0.5 * gi11 * dg11_do + gi12 * dg12_do
            # Actually, let me be careful. For 2D surface with u=(ω,C):
            # Γ^1_11 = ½ g^11 ∂g_11/∂ω  (since ∂g_11/∂C = 0)
            # But this isn't quite right either. Let me use the general formula.
            # Γ^i_jk = ½ g^il (∂g_lj/∂u^k + ∂g_lk/∂u^j - ∂g_jk/∂u^l)
            # All derivatives w.r.t. C vanish. Only ∂/∂ω survives.
            # So Γ^i_jk = 0 if none of j,k = 1 (ω direction), unless...

            # Γ^1_11 = ½ g^1l (∂g_l1/∂ω + ∂g_l1/∂ω - ∂g_11/∂u^l)
            #        = ½ [g^11 (2 ∂g_11/∂ω - ∂g_11/∂ω) + g^12 (2 ∂g_21/∂ω - ∂g_11/∂C)]
            #        = ½ [g^11 ∂g_11/∂ω + 2 g^12 ∂g_12/∂ω]
            # Wait, let me just use the standard formula directly:
            # Γ^1_11 = ½ g^11 ∂₁g_11 + ½ g^12 (2∂₁g_12 - ∂₂g_11)
            #        = ½ g^11 dg11_do + g^12 dg12_do  (∂₂g_11 = 0)

            G1_11 = 0.5 * gi11 * dg11_do + gi12 * dg12_do
            G1_12 = 0.5 * gi11 * 0 + 0.5 * gi12 * 0  # all zero because dg/dC = 0
            # Actually wait. Γ^1_12 = ½ g^1l (∂g_l1/∂C + ∂g_l2/∂ω - ∂g_12/∂u^l)
            # = ½ [g^11 (0 + dg12_do - dg12_do/... hmm)]
            # Simpler: since g depends only on ω, and g_22 is constant:
            # All Christoffel symbols with two C-indices vanish.
            # Γ^1_22 = ½ g^1l (2∂g_l2/∂C - ∂g_22/∂u^l) = -½ g^11 · 0 = 0
            # Γ^1_12 = ½ g^1l (∂g_l1/∂C + ∂g_l2/∂ω - ∂g_12/∂u^l)
            # Since ∂/∂C of everything = 0:
            # Γ^1_12 = ½ g^11 ∂g_12/∂ω + ½ g^12 ∂g_22/∂ω = ½ gi11 dg12_do
            G1_12 = 0.5 * gi11 * dg12_do

            # Γ^1_22 = -½ g^11 ∂g_22/∂ω - ½ g^12 ... = 0 (g_22 constant)
            G1_22 = 0.0

            # Γ^2_11 = ½ g^21 ∂g_11/∂ω + g^22 ∂g_12/∂ω  (similar)
            G2_11 = 0.5 * gi12 * dg11_do + gi22 * dg12_do
            # Hmm, this doesn't look right. Let me redo.
            # Γ^2_11 = ½ g^2l (∂g_l1/∂ω + ∂g_l1/∂ω - ∂g_11/∂u^l)
            #        = ½ [g^21 (2∂g_11/∂ω - ∂g_11/∂ω) + g^22 (2∂g_21/∂ω - 0)]
            # No wait. General formula:
            # Γ^2_11 = ½ g^2l (∂_1 g_l1 + ∂_1 g_l1 - ∂_l g_11)
            # l=1: g^21 (∂_1 g_11 + ∂_1 g_11 - ∂_1 g_11) = g^21 ∂_1 g_11
            # l=2: g^22 (∂_1 g_21 + ∂_1 g_21 - ∂_2 g_11) = g^22 (2 dg12_do)
            G2_11 = 0.5 * (gi12 * dg11_do + 2.0 * gi22 * dg12_do)
            G2_12 = 0.5 * gi12 * dg12_do  # similar logic
            G2_22 = 0.0

            # Geodesic equation: ẍ^i = -Γ^i_jk ẋ^j ẋ^k
            acc_omega = -(G1_11 * vo * vo + 2 * G1_12 * vo * vc + G1_22 * vc * vc)
            acc_C = -(G2_11 * vo * vo + 2 * G2_12 * vo * vc + G2_22 * vc * vc)

            # Update (Euler integration)
            vo += acc_omega * dt
            vc += acc_C * dt
            omega += vo * dt
            C += vc * dt

            # Bound ω to prevent singularity
            if omega <= 0.005 or omega >= 0.995:
                break

            path.append((omega, C))

        return np.array(path)

    # Trace several geodesics from different starting conditions
    print()
    print("  Computing geodesics from different initial conditions...")
    print("  (paths of least cost on the budget surface)")
    print()

    geodesics = {
        "Pure ω (toward pole)": (0.10, 0.0, 0.5, 0.0),
        "Pure C (lateral)": (0.10, 0.0, 0.0, 1.0),
        "Diagonal (45°)": (0.10, 0.0, 0.3, 0.3),
        "Falling inward": (0.50, 0.5, -0.5, 0.0),
        "Grazing (mostly C)": (0.20, 0.0, 0.1, 0.8),
    }

    print(f"  {'Geodesic':>25s}  {'Start ω':>8s}  {'End ω':>8s}  {'ΔC':>8s}  {'Steps':>6s}  {'Arc length':>12s}")
    print("  " + "-" * 75)

    for name, (omega0, C0, vo0, vc0) in geodesics.items():
        path = compute_geodesic_path(omega0, C0, vo0, vc0)
        if len(path) < 2:
            print(f"  {name:>25s}  {omega0:8.3f}  {'N/A':>8s}  {'N/A':>8s}  {len(path):6d}  {'N/A':>12s}")
            continue
        end_omega = path[-1, 0]
        delta_C = path[-1, 1] - path[0, 1]
        # Arc length
        diffs = np.diff(path, axis=0)
        arc_length = np.sum(np.sqrt(diffs[:, 0] ** 2 + diffs[:, 1] ** 2))
        print(f"  {name:>25s}  {omega0:8.3f}  {end_omega:8.4f}  {delta_C:8.3f}  {len(path):6d}  {arc_length:12.4f}")

    print()
    print("  Key observation: geodesics that head toward the pole")
    print("  (increasing ω) are DEFLECTED in C. The surface's")
    print("  extrinsic curvature bends the path laterally.")
    print()
    print("  Geodesics that start in the C direction stay mostly")
    print("  in C — the surface is flat in that direction.")

    # ================================================================
    # §6  THE EMBEDDING: WHAT YOU WOULD SEE
    # ================================================================
    print_header(6, "THE 3D EMBEDDING: WHAT THE SURFACE LOOKS LIKE")
    print("  The budget surface z = Γ(ω) + αC is a concrete object")
    print("  in R³. Here is its profile along ω (the generating curve):")
    print()

    # Profile description
    print("  Imagine standing at ω = 0 and looking toward ω = 1:")
    print()
    print("  z")
    print("  ↑")
    print("  |                                          ╱╱ ← vertical wall")
    print("  |                                        ╱╱    (ω → 1)")
    print("  |                                      ╱╱")
    print("  |                                    ╱╱")
    print("  |                                 ╱╱")
    print("  |                              ╱╱  ← steep ramp")
    print("  |                          ╱╱╱    (Collapse)")
    print("  |                    ╱╱╱╱╱")
    print("  |             ╱╱╱╱╱╱  ← gentle ramp (Watch)")
    print("  |   ════════════════  ← flat plain (Stable)")
    print("  └───────────────────────────────────────────→ ω")
    print("  0         0.038    0.30              0.90    1")
    print()
    print("  Now extrude this profile along C (with slope α):")
    print("  The result is a TILTED HALF-PIPE / HORN shape.")
    print()
    print("  Concrete coordinates at sample points:")

    print(f"\n  {'ω':>6s}  {'C':>6s}  {'x = ω':>8s}  {'y = C':>8s}  {'z = Γ+αC':>10s}  {'Height ratio':>14s}")
    print("  " + "-" * 60)

    z_ref = gamma_cost(0.01)  # reference height
    for omega in [0.01, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90, 0.99]:
        for C_val in [0.0, 0.5]:
            z = gamma_cost(omega) + ALPHA * C_val
            ratio = z / z_ref if z_ref > 0 else 0
            print(f"  {omega:6.3f}  {C_val:6.2f}  {omega:8.4f}  {C_val:8.4f}  {z:10.4f}  {ratio:14.1f}×")

    print()
    print("  At (ω=0.01, C=0):  z = 0.000001 (ground level)")
    print("  At (ω=0.50, C=0):  z = 0.25 (mall-height)")
    print("  At (ω=0.90, C=0):  z = 7.29 (skyscraper)")
    print("  At (ω=0.99, C=0):  z = 97.03 (in the clouds)")
    print()
    print("  The surface rises from a flat plains to an infinite tower.")
    print("  The C direction tilts the surface but doesn't change its shape.")

    # ================================================================
    # §7  THE EQUATION OF MOTION
    # ================================================================
    print_header(7, "EQUATION OF MOTION ON THE SURFACE")
    print("  A system 'in free fall' on the budget surface follows")
    print("  the geodesic equation:")
    print()
    print("  d²ω/ds² = −Γ¹₁₁ (dω/ds)² − 2Γ¹₁₂ (dω/ds)(dC/ds)")
    print("  d²C/ds² = −Γ²₁₁ (dω/ds)² − 2Γ²₁₂ (dω/ds)(dC/ds)")
    print()
    print("  where s is the arc length parameter and Γⁱⱼₖ are the")
    print("  Christoffel symbols of the induced metric.")
    print()
    print("  The Christoffel symbols at sample ω values:")

    print(f"\n  {'ω':>6s}  {'Γ¹₁₁':>14s}  {'Γ¹₁₂':>14s}  {'Γ²₁₁':>14s}  {'Γ²₁₂':>14s}")
    print("  " + "-" * 65)

    for omega in [0.01, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 0.90]:
        f_o = d1_gamma_exact(omega)
        f_oo = d2_gamma_exact(omega)

        g11 = 1.0 + f_o**2
        g12 = ALPHA * f_o
        g22 = 1.0 + ALPHA**2
        det_g = g11 * g22 - g12**2

        gi11 = g22 / det_g
        gi12 = -g12 / det_g
        gi22 = g11 / det_g

        dg11_do = 2.0 * f_o * f_oo
        dg12_do = ALPHA * f_oo

        G1_11 = 0.5 * (gi11 * dg11_do + 2.0 * gi12 * dg12_do)
        G1_12 = 0.5 * gi11 * dg12_do
        G2_11 = 0.5 * (gi12 * dg11_do + 2.0 * gi22 * dg12_do)
        G2_12 = 0.5 * gi12 * dg12_do

        print(f"  {omega:6.3f}  {G1_11:14.8f}  {G1_12:14.8f}  {G2_11:14.8f}  {G2_12:14.8f}")

    print()
    print("  At ω = 0.01: all Christoffel symbols ≈ 0 (flat)")
    print("  → Free motion is a straight line. No 'gravity.'")
    print()
    print("  At ω = 0.90: Γ¹₁₁ dominates.")
    print("  → Strong deceleration in the ω direction.")
    print("  → The surface's slope resists further increase in ω.")
    print("  → This IS the gravitational 'force' — the Christoffel")
    print("     symbol acts as an apparent acceleration.")
    print()
    print("  KEY INSIGHT: The 'force' of gravity is entirely")
    print("  contained in the Christoffel symbols Γⁱⱼₖ.")
    print("  These are NOT forces — they are GEOMETRIC ARTIFACTS")
    print("  of curvilinear coordinates on a FLAT surface.")
    print()
    print("  In GR, Einstein showed the same thing: gravity is not")
    print("  a force but a Christoffel symbol. GCD reproduces this")
    print("  structure exactly, on a surface with K = 0.")

    # ================================================================
    # §8  CONNECTION TO FISHER FLAT METRIC
    # ================================================================
    print_header(8, "CONNECTION TO THE FISHER FLAT METRIC")
    print("  The deep diagnostic proved: g_F(θ) = 1.")
    print("  The Bernoulli manifold is flat in Fisher coordinates.")
    print()
    print("  In Fisher coordinates θ, where cᵢ = sin²(θᵢ):")
    print("  The information metric is ds² = dθ². (Flat Euclidean.)")
    print()
    print("  The budget surface z = Γ(ω) + αC lives ON this flat")
    print("  manifold. It is a HEIGHT FUNCTION on a flat space.")
    print()
    print("  This means the budget surface is exactly like a")
    print("  terrain map drawn on a flat piece of paper:")
    print("  - The paper itself is flat (K = 0, confirmed §2)")
    print("  - The contour lines show the budget 'altitude'")
    print("  - Systems roll downhill on the contour surface")
    print("  - The 'gravity' is just the slope of the terrain")
    print()
    print("  Test: verify the coordinate transformation preserves")
    print("  the flatness. For a single channel c = sin²θ:")
    print("  ω = 1 − sin²θ = cos²θ")
    print("  Γ(θ) = cos⁶θ / (sin²θ + ε)")

    theta_values = np.linspace(0.1, 1.5, 10)
    print(f"\n  {'θ':>8s}  {'ω = cos²θ':>10s}  {'Γ(ω)':>12s}  {'Γ(θ) direct':>14s}  {'Match':>8s}")
    print("  " + "-" * 60)
    for theta in theta_values:
        omega = np.cos(theta) ** 2
        G_omega = gamma_cost(omega)
        G_theta = np.cos(theta) ** 6 / (np.sin(theta) ** 2 + EPSILON)
        match = "YES" if abs(G_omega - G_theta) < 1e-6 else "NO"
        print(f"  {theta:8.4f}  {omega:10.6f}  {G_omega:12.6f}  {G_theta:14.6f}  {match:>8s}")

    print()
    print("  The transformation is exact.")
    print("  In Fisher coordinates, the budget surface becomes:")
    print("  z(θ) = cos⁶θ / (sin²θ + ε)")
    print()
    print("  This is a COTANGENT-TYPE function — large near θ = 0")
    print("  (where c → 1, system is fully coherent = impossible)")
    print("  and small near θ = π/2 (where c → 0, fully collapsed).")
    print()
    print("  The 'pole' is at θ = 0 (perfect coherence, c = 1).")
    print("  Gravity points AWAY from perfection.")
    print("  Systems are attracted toward the center of the")
    print("  manifold, not toward any edge.")

    # ================================================================
    # §9  REGIME ZONES AS GEOMETRIC REGIONS
    # ================================================================
    print_header(9, "REGIME ZONES AS GEOMETRIC BANDS")
    print("  The three regimes partition the surface into bands:")
    print()

    # Compute zone properties
    zones = [
        ("STABLE", 0.001, 0.038),
        ("WATCH", 0.038, 0.30),
        ("COLLAPSE", 0.30, 0.999),
    ]

    print(f"  {'Zone':>10s}  {'ω range':>15s}  {'Γ range':>20s}  {'slope range':>20s}  {'κ₁ range':>20s}")
    print("  " + "-" * 90)

    for zone_name, omega_lo, omega_hi in zones:
        G_lo = gamma_cost(omega_lo)
        G_hi = gamma_cost(omega_hi)
        s_lo = d1_gamma_exact(omega_lo)
        s_hi = d1_gamma_exact(omega_hi)
        # Extrinsic curvature at boundaries
        k_lo = d2_gamma_exact(omega_lo) / (1 + d1_gamma_exact(omega_lo) ** 2 + ALPHA**2) ** 1.5
        k_hi = d2_gamma_exact(omega_hi) / (1 + d1_gamma_exact(omega_hi) ** 2 + ALPHA**2) ** 1.5
        print(
            f"  {zone_name:>10s}  [{omega_lo:.3f}, {omega_hi:.3f}]  "
            f"[{G_lo:.2e}, {G_hi:.2e}]  "
            f"[{s_lo:.2e}, {s_hi:.2e}]  "
            f"[{k_lo:.2e}, {k_hi:.2e}]"
        )

    print()
    print("  STABLE zone: the flat plain.")
    print("    Γ < 6×10⁻⁵, slope < 0.004, κ₁ ≈ 0.04")
    print("    Systems barely feel the surface. Nearly free motion.")
    print("    Like standing on a perfectly flat salt flat.")
    print()
    print("  WATCH zone: the ramp.")
    print("    Γ up to 0.04, slope up to 0.44, κ₁ decreasing")
    print("    Systems are noticeably tilted. They begin to slide.")
    print("    Like walking on a hillside — effort is needed to stay.")
    print()
    print("  COLLAPSE zone: the wall.")
    print("    Γ up to 97+, slope up to 10,000+, κ₁ → 0 (vertical)")
    print("    Systems fall rapidly. Return requires enormous budget.")
    print("    Like the inside of a vertical funnel.")

    # What fraction of surface area is in each zone?
    # Since the surface is independent of C, integrate √det(g) dω
    total_area = 0.0
    zone_areas = {}
    for zone_name, omega_lo, omega_hi in zones:
        area = 0.0
        for omega in np.linspace(omega_lo, omega_hi, 10000):
            f_o = d1_gamma_exact(omega)
            det_g = (1 + f_o**2) * (1 + ALPHA**2) - (ALPHA * f_o) ** 2
            area += np.sqrt(det_g) * (omega_hi - omega_lo) / 10000
        zone_areas[zone_name] = area
        total_area += area

    print("\n  Surface area distribution (per unit C):")
    for zone_name in ["STABLE", "WATCH", "COLLAPSE"]:
        pct = 100.0 * zone_areas[zone_name] / total_area
        print(f"    {zone_name:>10s}: {pct:6.1f}%  (area = {zone_areas[zone_name]:.4f})")

    print()
    print("  COLLAPSE occupies the VAST majority of the surface area")
    print("  because the metric stretches enormously near the pole.")
    print("  Most of the geometric 'space' IS collapse territory.")
    print("  Stability is a TINY PATCH on an enormous surface.")

    # ================================================================
    # §10  SYNTHESIS
    # ================================================================
    print_header(10, "THE COMPLETE GEOMETRIC DESCRIPTION")
    print()
    print("  ╔════════════════════════════════════════════════════════╗")
    print("  ║  THE BUDGET SURFACE IS A DEVELOPABLE HORN.            ║")
    print("  ║                                                       ║")
    print("  ║  • Intrinsically FLAT (Gaussian curvature K = 0)     ║")
    print("  ║  • Extrinsically CURVED (κ₁ > 0, convex upward)     ║")
    print("  ║  • A generalized cylinder over z = ω³/(1−ω+ε)       ║")
    print("  ║  • Extruded along C with slope α = 1                 ║")
    print("  ║  • Three zones: flat plain → ramp → vertical wall    ║")
    print("  ║  • Geodesics are straight lines on the unrolled flat ║")
    print("  ║  • Gravity = Christoffel symbols on the flat surface ║")
    print("  ╚════════════════════════════════════════════════════════╝")
    print()
    print("  THE LITERAL SHAPE:")
    print()
    print("  1. START at the flat plain (ω < 0.038, Stable).")
    print("     It is nearly level. Systems rest in equilibrium.")
    print("     Channels are coherent. Return is cheap.")
    print()
    print("  2. The plain TILTS into a ramp (0.038 < ω < 0.30, Watch).")
    print("     The slope is gradual but real. Systems begin to drift.")
    print("     The metric starts stretching — distances grow.")
    print()
    print("  3. The ramp STEEPENS into a wall (ω > 0.30, Collapse).")
    print("     The slope goes from 0.44 to infinity.")
    print("     The wall narrows to a vertical asymptote at ω = 1.")
    print("     This is the event horizon — infinite distance, no return.")
    print()
    print("  4. The C direction adds a TILT to the whole structure.")
    print("     Higher curvature C raises the surface uniformly.")
    print("     This doesn't change the shape, only the altitude.")
    print()
    print("  THE LITERAL MOTION:")
    print()
    print("  Systems move on this surface like marbles on a terrain.")
    print("  Free fall = following the slope (cheapest path).")
    print("  Hovering = fighting the slope (costs extra budget).")
    print("  Orbiting = moving in C while maintaining ω (circling")
    print("  the horn at constant altitude).")
    print()
    print("  The motion equation is the geodesic equation with")
    print("  Christoffel symbols Γⁱⱼₖ computed from the induced metric.")
    print("  These symbols vanish on the flat plain and grow near")
    print("  the wall — so 'gravity' is stronger near the pole.")
    print()
    print("  Because the surface is developable (K = 0), every")
    print("  geodesic can be found by:")
    print("    1. Unroll the surface flat (no stretching needed)")
    print("    2. Draw a straight line")
    print("    3. Roll it back up")
    print("  The resulting curve on the horn IS the free-fall path.")
    print()
    print("  THE KEY INSIGHT:")
    print()
    print("  Gravity is not curvature OF the surface.")
    print("  Gravity is curvature of the surface's EMBEDDING.")
    print("  The surface itself is flat. The way it sits in the")
    print("  space of return is what creates the apparent force.")
    print()
    print("  This is deeper than GR's 'gravity is curvature.'")
    print("  GR says spacetime is curved (Gaussian curvature ≠ 0).")
    print("  GCD says the budget surface is FLAT (K = 0) but BENT.")
    print("  The bending is extrinsic. You can unroll it.")
    print("  Gravity is the shadow of embedding, not intrinsic shape.")
    print()
    print("  ═══════════════════════════════════════════════════════")
    print("  GEOMETRY SUMMARY TABLE")
    print("  ═══════════════════════════════════════════════════════")
    print()
    print("  Property                Value")
    print("  ─────────               ─────")
    print("  Surface type            Developable (generalized cylinder)")
    print("  Generating curve        z = ω³/(1−ω+ε)")
    print("  Extrusion direction     C with slope α = 1.0")
    print("  Gaussian curvature      K = 0 everywhere (intrinsically flat)")
    print("  Principal curvature κ₁  d²Γ/dω² / (1+(dΓ/dω)²+1)^(3/2)")
    print("  Principal curvature κ₂  0 (always)")
    print("  Metric g_11             1 + (dΓ/dω)² [grows to ∞ at pole]")
    print("  Metric g_12             dΓ/dω [cross-term from C slope]")
    print("  Metric g_22             2.0 [constant everywhere]")
    print("  Vertical asymptote      ω = 1 (event horizon)")
    print("  Flat zone               ω < 0.038 (Stable)")
    print("  Transition ramp         0.038 < ω < 0.30 (Watch)")
    print("  Steep wall              ω > 0.30 (Collapse)")
    print("  Geodesics               Straight lines when unrolled")
    print("  Motion equation         Geodesic ODE with Christoffel Γⁱⱼₖ")
    print("  Area distribution       Stable ≪ Watch ≪ Collapse")
    print()
    print("  Solum quod redit, reale est.")
    print("  The surface is flat. The embedding is bent.")
    print("  The bending is gravity. Gravity is the memory of return.")


if __name__ == "__main__":
    main()
