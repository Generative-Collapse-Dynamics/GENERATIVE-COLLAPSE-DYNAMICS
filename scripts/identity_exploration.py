"""
Identity Exploration Script — Probing for New Structural Identities

This script searches for mathematical relationships in the GCD kernel
that may constitute new structural identities beyond the current 28.

Each candidate is verified numerically across large sample sets. Only
relationships that hold to machine precision (or with quantified,
diminishing error) are reported.

Axiom-0 derivation: Every candidate traces back to the kernel
K: [0,1]^n x Delta^n -> (F, omega, S, C, kappa, IC).
"""

from __future__ import annotations

import numpy as np

from umcp.frozen_contract import ALPHA, C_STAR, EPSILON, OMEGA_TRAP, P_EXPONENT

# =============================================================================
# Utility: Kernel computation
# =============================================================================


def kernel(c: np.ndarray, w: np.ndarray | None = None, eps: float = EPSILON):
    """Compute full kernel outputs for trace vector c with weights w."""
    c = np.asarray(c, dtype=np.float64)
    n = len(c)
    if w is None:
        w = np.full(n, 1.0 / n)
    w = np.asarray(w, dtype=np.float64)

    c_clip = np.clip(c, eps, 1.0 - eps)

    F = float(np.dot(w, c_clip))
    omega = 1.0 - F
    kappa = float(np.dot(w, np.log(c_clip)))
    IC = float(np.exp(kappa))
    S = float(-np.dot(w, c_clip * np.log(c_clip) + (1 - c_clip) * np.log(1 - c_clip)))
    C = float(np.sqrt(np.dot(w, (c_clip - F) ** 2)) / 0.5)
    Delta = F - IC

    return {
        "F": F,
        "omega": omega,
        "S": S,
        "C": C,
        "kappa": kappa,
        "IC": IC,
        "Delta": Delta,
        "c_clip": c_clip,
        "w": w,
        "n": n,
    }


def fisher_angle(c: np.ndarray, eps: float = EPSILON):
    """Convert channel coordinates to Fisher angles theta = arcsin(sqrt(c))."""
    c_clip = np.clip(c, eps, 1.0 - eps)
    return np.arcsin(np.sqrt(c_clip))


# =============================================================================
# CANDIDATE 1: Entropy-Curvature Product Identity
# At c = 1/2 (equator), S * C should have a specific value for uniform traces
# More broadly: explore S * C as a function of F
# =============================================================================


def explore_entropy_curvature_product():
    print("=" * 72)
    print("  CANDIDATE 1: Entropy-Curvature Coupling")
    print("  Explore: S·C and S/C as functions across the manifold")
    print("=" * 72)

    # For homogeneous traces (all c_i = c), C = 0 and S·C = 0
    # The interesting case is heterogeneous traces
    # Hypothesis: For rank-2 systems, S·C has a constrained relationship to F

    np.random.seed(42)
    n_trials = 50000
    n_channels = 8

    results = []
    for _ in range(n_trials):
        c = np.random.uniform(0.01, 0.99, n_channels)
        k = kernel(c)
        results.append(k)

    F_vals = np.array([r["F"] for r in results])
    S_vals = np.array([r["S"] for r in results])
    C_vals = np.array([r["C"] for r in results])
    IC_vals = np.array([r["IC"] for r in results])
    kappa_vals = np.array([r["kappa"] for r in results])
    Delta_vals = np.array([r["Delta"] for r in results])

    # Check correlation between S*C and other kernel outputs
    SC_product = S_vals * C_vals
    corr_SC_F = np.corrcoef(SC_product, F_vals)[0, 1]
    corr_SC_Delta = np.corrcoef(SC_product, Delta_vals)[0, 1]
    corr_SC_kappa = np.corrcoef(SC_product, kappa_vals)[0, 1]

    print(f"\n  corr(S·C, F)     = {corr_SC_F:.6f}")
    print(f"  corr(S·C, Δ)     = {corr_SC_Delta:.6f}")
    print(f"  corr(S·C, κ)     = {corr_SC_kappa:.6f}")

    # More interesting: S + κ relationship across heterogeneous traces
    Sk_sum = S_vals + kappa_vals
    corr_Sk_F = np.corrcoef(Sk_sum, F_vals)[0, 1]
    corr_Sk_C = np.corrcoef(Sk_sum, C_vals)[0, 1]
    corr_Sk_FC = np.corrcoef(Sk_sum, F_vals * C_vals)[0, 1]

    print(f"\n  S + κ statistics (n={n_channels} channels, {n_trials} traces):")
    print(f"  corr(S+κ, F)     = {corr_Sk_F:.6f}")
    print(f"  corr(S+κ, C)     = {corr_Sk_C:.6f}")
    print(f"  corr(S+κ, F·C)   = {corr_Sk_FC:.6f}")
    print(f"  mean(S+κ)        = {np.mean(Sk_sum):.6f}")
    print(f"  std(S+κ)         = {np.std(Sk_sum):.6f}")
    print(f"  max(S+κ)         = {np.max(Sk_sum):.6f}")
    print(f"  min(S+κ)         = {np.min(Sk_sum):.6f}")

    return F_vals, S_vals, C_vals, IC_vals, kappa_vals, Delta_vals


# =============================================================================
# CANDIDATE 2: The S ≈ f(F, C) Statistical Constraint — Find the Function
# The documentation says S is "asymptotically determined" by F and C but
# never writes down what f is. Let's find it.
# =============================================================================


def explore_S_constraint():
    print("\n" + "=" * 72)
    print("  CANDIDATE 2: The Statistical Constraint S ≈ f(F, C)")
    print("  Goal: Find the explicit functional form")
    print("=" * 72)

    np.random.seed(123)

    for n_ch in [4, 8, 16, 32, 64, 128]:
        n_trials = 20000
        results = []
        for _ in range(n_trials):
            c = np.random.uniform(0.01, 0.99, n_ch)
            k = kernel(c)
            results.append(k)

        F_vals = np.array([r["F"] for r in results])
        S_vals = np.array([r["S"] for r in results])
        C_vals = np.array([r["C"] for r in results])

        corr_SC = np.corrcoef(S_vals, C_vals)[0, 1]
        corr_SF = np.corrcoef(S_vals, F_vals)[0, 1]

        # Try: S ≈ a*h(F) + b*C + c where h is binary entropy
        h_F = -(F_vals * np.log(F_vals) + (1 - F_vals) * np.log(1 - F_vals))
        # Linear regression: S = α₀ + α₁·h(F) + α₂·C
        A = np.column_stack([np.ones(n_trials), h_F, C_vals])
        coeffs, _residuals, _, _ = np.linalg.lstsq(A, S_vals, rcond=None)
        S_pred = A @ coeffs
        r2 = 1 - np.sum((S_vals - S_pred) ** 2) / np.sum((S_vals - np.mean(S_vals)) ** 2)

        # Also try: S ≈ h(F) - β·C² (subtract curvature correction)
        A2 = np.column_stack([np.ones(n_trials), h_F, C_vals, C_vals**2])
        coeffs2, _, _, _ = np.linalg.lstsq(A2, S_vals, rcond=None)
        S_pred2 = A2 @ coeffs2
        r2_quad = 1 - np.sum((S_vals - S_pred2) ** 2) / np.sum((S_vals - np.mean(S_vals)) ** 2)

        # Try pure relationship: S ≈ h(F) exactly when C → 0
        # So the correction should vanish with C
        # Try: S = h(F) · (1 - γ·C²)
        mask_low_C = C_vals < 0.05
        if np.sum(mask_low_C) > 10:
            ratio_low_C = np.mean(S_vals[mask_low_C] / h_F[mask_low_C])
        else:
            ratio_low_C = float("nan")

        print(f"\n  n = {n_ch:3d} channels:")
        print(f"    corr(S, C) = {corr_SC:+.6f}   corr(S, F) = {corr_SF:+.6f}")
        print(f"    Linear  S = {coeffs[0]:.4f} + {coeffs[1]:.4f}·h(F) + {coeffs[2]:.4f}·C   R² = {r2:.8f}")
        print(f"    Quadratic R² = {r2_quad:.8f}")
        print(f"    S/h(F) when C<0.05: {ratio_low_C:.6f}")


# =============================================================================
# CANDIDATE 3: Heterogeneity Gap Taylor Expansion
# Δ = F - IC. For small heterogeneity, can we get exact series?
# =============================================================================


def explore_gap_expansion():
    print("\n" + "=" * 72)
    print("  CANDIDATE 3: Heterogeneity Gap Taylor Series")
    print("  Δ = F - IC in terms of channel variance and higher moments")
    print("=" * 72)

    np.random.seed(42)
    n_ch = 8

    # For channels c_i = c̄ + δ_i where δ_i is small perturbation:
    # F = c̄ (by construction with uniform weights)
    # κ = (1/n)Σ ln(c̄ + δ_i) ≈ ln(c̄) + (1/n)Σ[δ_i/c̄ - δ_i²/(2c̄²) + ...]
    # Since Σδ_i = 0: κ ≈ ln(c̄) - Var(c)/(2c̄²) + ...
    # IC = exp(κ) ≈ c̄ · exp(-Var(c)/(2c̄²))
    # Δ = F - IC ≈ c̄ · (1 - exp(-Var(c)/(2c̄²))) ≈ Var(c)/(2c̄)

    c_bar_values = [0.3, 0.5, 0.7, 0.9]
    sigma_values = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]

    print("\n  Testing Δ ≈ Var(c)/(2c̄) and Δ ≈ c̄·(1 - exp(-Var(c)/(2c̄²)))")
    print(f"  {'c̄':>6s} {'σ':>6s} {'Δ_exact':>12s} {'Δ_approx1':>12s} {'err1%':>8s} {'Δ_approx2':>12s} {'err2%':>8s}")

    for c_bar in c_bar_values:
        for sigma in sigma_values:
            if c_bar - 3 * sigma < 0.01 or c_bar + 3 * sigma > 0.99:
                continue
            # Generate traces with specific mean and variance
            n_trials = 5000
            errors1 = []
            errors2 = []
            for _ in range(n_trials):
                c = np.random.normal(c_bar, sigma, n_ch)
                c = np.clip(c, 0.01, 0.99)
                k = kernel(c)
                var_c = np.var(c)
                actual_mean = k["F"]

                approx1 = var_c / (2 * actual_mean)  # First order
                approx2 = actual_mean * (1 - np.exp(-var_c / (2 * actual_mean**2)))  # Exponential

                errors1.append((k["Delta"] - approx1) / max(k["Delta"], 1e-15))
                errors2.append((k["Delta"] - approx2) / max(k["Delta"], 1e-15))

            mean_err1 = np.mean(np.abs(errors1)) * 100
            mean_err2 = np.mean(np.abs(errors2)) * 100
            mean_delta = np.mean(
                [kernel(np.random.normal(c_bar, sigma, n_ch).clip(0.01, 0.99))["Delta"] for _ in range(500)]
            )

            print(
                f"  {c_bar:6.2f} {sigma:6.3f} {mean_delta:12.6f} "
                f"{sigma**2 / (2 * c_bar):12.6f} {mean_err1:8.2f}% "
                f"{c_bar * (1 - np.exp(-(sigma**2) / (2 * c_bar**2))):12.6f} {mean_err2:8.2f}%"
            )

    # Higher-order: include skewness and kurtosis
    print("\n  HIGHER-ORDER EXPANSION:")
    print("  Δ ≈ Var(c)/(2c̄) + Var(c)²/(4c̄³)·(excess_kurtosis/4 - 1/2)")
    print("  Testing with skewed distributions...")

    for c_bar in [0.5, 0.7]:
        c = np.random.beta(2, 2, (10000, n_ch)) * 0.6 + (c_bar - 0.3)
        c = np.clip(c, 0.01, 0.99)
        deltas = []
        approxes_1 = []
        approxes_2 = []
        approxes_3 = []
        for i in range(len(c)):
            k = kernel(c[i])
            var_c = np.var(c[i])
            mu3 = np.mean((c[i] - np.mean(c[i])) ** 3)
            F = k["F"]

            a1 = var_c / (2 * F)
            a2 = F * (1 - np.exp(-var_c / (2 * F**2)))
            # Third order with skewness
            a3 = var_c / (2 * F) + var_c**2 / (8 * F**3) - mu3 / (3 * F**2)

            deltas.append(k["Delta"])
            approxes_1.append(a1)
            approxes_2.append(a2)
            approxes_3.append(a3)

        deltas = np.array(deltas)
        err1 = np.mean(np.abs(np.array(approxes_1) - deltas) / deltas) * 100
        err2 = np.mean(np.abs(np.array(approxes_2) - deltas) / deltas) * 100
        err3 = np.mean(np.abs(np.array(approxes_3) - deltas) / deltas) * 100

        print(f"  c̄ ≈ {c_bar}: err_linear={err1:.2f}%  err_exp={err2:.2f}%  err_3rd={err3:.2f}%")


# =============================================================================
# CANDIDATE 4: Entropy Derivative Identity
# dS/dF at fixed C — does this have a clean closed form?
# =============================================================================


def explore_entropy_derivatives():
    print("\n" + "=" * 72)
    print("  CANDIDATE 4: Entropy-Fidelity Derivative Identity")
    print("  Explore: dS/dF|_C and d²S/dF²|_C")
    print("=" * 72)

    # For a homogeneous system (all c_i = c), S = h(c) and F = c
    # So dS/dF = dh/dc = ln((1-c)/c)
    # This means at F = 1/2: dS/dF = 0 (entropy maximum)
    # At F = c*: dS/dF = ln((1-c*)/c*) = -1/c* (from E3)

    # For heterogeneous systems, the relationship is more complex
    # Can we write S(F, C) explicitly for rank-2?

    # Rank-2: two channels c₁, c₂ with equal weights
    # F = (c₁ + c₂)/2, C = |c₁ - c₂|/(2·0.5) = |c₁ - c₂|
    # c₁ = F + C/2, c₂ = F - C/2
    # S = (1/2)[h(F+C/2) + h(F-C/2)]
    # κ = (1/2)[ln(F+C/2) + ln(F-C/2)] = (1/2)ln((F+C/2)(F-C/2)) = (1/2)ln(F²-C²/4)

    print("\n  Rank-2 exact formulas (n=2, equal weights):")
    print("  S(F,C) = [h(F+C/2) + h(F-C/2)] / 2")
    print("  κ(F,C) = ln(F² - C²/4) / 2")
    print("  IC(F,C) = √(F² - C²/4)")
    print("  Δ(F,C) = F - √(F² - C²/4)")
    print("  (where h(x) = -x·ln(x) - (1-x)·ln(1-x))")

    print("\n  Verification:")
    for F in [0.3, 0.5, 0.7, 0.9]:
        for C_half in [0.0, 0.05, 0.10, 0.15, 0.20]:
            c1 = F + C_half
            c2 = F - C_half
            if c1 > 0.99 or c2 < 0.01:
                continue
            k = kernel(np.array([c1, c2]))
            # Rank-2 formula
            IC_formula = np.sqrt(F**2 - C_half**2)
            kappa_formula = 0.5 * np.log(F**2 - C_half**2)
            S_formula = 0.5 * (
                -(c1 * np.log(c1) + (1 - c1) * np.log(1 - c1)) - (c2 * np.log(c2) + (1 - c2) * np.log(1 - c2))
            )

            delta_IC = abs(k["IC"] - IC_formula)
            delta_kappa = abs(k["kappa"] - kappa_formula)
            delta_S = abs(k["S"] - S_formula)

            if C_half == 0.0:
                print(
                    f"    F={F:.1f}, C/2={C_half:.2f}: IC err={delta_IC:.2e}, κ err={delta_kappa:.2e}, S err={delta_S:.2e}"
                )
            else:
                print(
                    f"    F={F:.1f}, C/2={C_half:.2f}: IC err={delta_IC:.2e}, κ err={delta_kappa:.2e}, S err={delta_S:.2e}"
                )

    # Now derive dS/dF at fixed C for rank-2:
    # dS/dF = (1/2)[h'(F+C/2) + h'(F-C/2)] = (1/2)[ln((1-F-C/2)/(F+C/2)) + ln((1-F+C/2)/(F-C/2))]
    # At C = 0: dS/dF = h'(F) = ln((1-F)/F) ← the homogeneous derivative

    print("\n  Rank-2 derivative identity:")
    print("  ∂S/∂F|_C = (1/2)[ln((1-c₁)/c₁) + ln((1-c₂)/c₂)]")
    print("  At C=0: reduces to ln((1-F)/F)")
    print("  At F=1/2, C=0: dS/dF = 0 (entropy maximum)")
    print("  At F=c*, C=0: dS/dF = -1/c* (from E3)")


# =============================================================================
# CANDIDATE 5: IC/F Ratio Bounds as Function of C
# IC/F ratio should be tightly constrained by curvature
# =============================================================================


def explore_IC_F_ratio():
    print("\n" + "=" * 72)
    print("  CANDIDATE 5: IC/F Ratio as Function of Curvature")
    print("  Hypothesis: IC/F = g(C) with tight bounds")
    print("=" * 72)

    np.random.seed(42)

    for n_ch in [2, 4, 8, 16, 32]:
        n_trials = 20000
        results = []
        for _ in range(n_trials):
            c = np.random.uniform(0.01, 0.99, n_ch)
            k = kernel(c)
            results.append(k)

        C_vals = np.array([r["C"] for r in results])
        IC_F_ratio = np.array([r["IC"] / r["F"] for r in results])
        corr = np.corrcoef(C_vals, IC_F_ratio)[0, 1]

        # For rank-2: IC/F = √(1 - (C/(2F))²)
        # More generally: IC/F = exp(κ - ln(F))
        # Can we bound IC/F by C alone?

        # Bin by C and find min/max IC/F
        bins = np.linspace(0, 1, 21)
        print(f"\n  n = {n_ch:2d} channels: corr(C, IC/F) = {corr:.4f}")
        print(f"    {'C range':>12s} {'min IC/F':>10s} {'mean IC/F':>10s} {'max IC/F':>10s} {'spread':>10s}")
        for i in range(len(bins) - 1):
            mask = (C_vals >= bins[i]) & (C_vals < bins[i + 1])
            if np.sum(mask) > 20:
                mn = np.min(IC_F_ratio[mask])
                mx = np.max(IC_F_ratio[mask])
                avg = np.mean(IC_F_ratio[mask])
                print(f"    [{bins[i]:.2f},{bins[i + 1]:.2f})  {mn:10.4f} {avg:10.4f} {mx:10.4f} {mx - mn:10.4f}")


# =============================================================================
# CANDIDATE 6: Seam Budget Symmetry
# Is there a duality between D_ω and D_C in the budget?
# =============================================================================


def explore_budget_symmetry():
    print("\n" + "=" * 72)
    print("  CANDIDATE 6: Budget Component Relationships")
    print("  Explore: Γ(ω) vs D_C = α·C")
    print("=" * 72)

    np.random.seed(42)
    n_ch = 8
    n_trials = 30000

    results = []
    for _ in range(n_trials):
        c = np.random.uniform(0.01, 0.99, n_ch)
        k = kernel(c)
        omega = k["omega"]
        C = k["C"]
        gamma = omega**P_EXPONENT / (1 - omega + EPSILON)
        D_C = ALPHA * C
        results.append(
            {
                "omega": omega,
                "C": C,
                "gamma": gamma,
                "D_C": D_C,
                "total": gamma + D_C,
                "ratio": gamma / max(D_C, 1e-15),
                "F": k["F"],
                "IC": k["IC"],
                "Delta": k["Delta"],
            }
        )

    gammas = np.array([r["gamma"] for r in results])
    D_Cs = np.array([r["D_C"] for r in results])
    totals = gammas + D_Cs
    Deltas = np.array([r["Delta"] for r in results])

    # Does total debit relate to Delta?
    corr_total_Delta = np.corrcoef(totals, Deltas)[0, 1]
    # Does the ratio Γ/D_C have structure?
    print(f"\n  corr(Γ+D_C, Δ) = {corr_total_Delta:.6f}")
    print(f"  corr(Γ, D_C)   = {np.corrcoef(gammas, D_Cs)[0, 1]:.6f}")
    print(f"  mean(Γ/(Γ+D_C))= {np.mean(gammas / totals):.6f}")
    print(f"  std(Γ/(Γ+D_C)) = {np.std(gammas / totals):.6f}")

    # Cross-over point: where does Γ(ω) = D_C = α·C?
    # For typical traces, when does drift cost equal curvature cost?
    crossover_mask = np.abs(gammas - D_Cs) < 0.01
    if np.sum(crossover_mask) > 0:
        cross_omegas = np.array([r["omega"] for r in results])[crossover_mask]
        cross_Cs = np.array([r["C"] for r in results])[crossover_mask]
        print(f"\n  Crossover (Γ ≈ D_C): mean ω = {np.mean(cross_omegas):.4f}, mean C = {np.mean(cross_Cs):.4f}")


# =============================================================================
# CANDIDATE 7: Equator Convergence Identity (Unification)
# At c = 1/2 for homogeneous traces, four things converge simultaneously.
# Can we find MORE convergences? What about c* = 0.7822?
# =============================================================================


def explore_special_points():
    print("\n" + "=" * 72)
    print("  CANDIDATE 7: Special Point Properties")
    print("  Catalog ALL unique properties at c = 1/2 and c = c*")
    print("=" * 72)

    c_half = 0.5
    c_star = C_STAR
    c_trap = 1.0 - OMEGA_TRAP
    eps = EPSILON

    for c_val, name in [
        (c_half, "EQUATOR c=1/2"),
        (c_star, f"COUPLING MAX c*={c_star:.6f}"),
        (c_trap, f"FIRST WELD c_trap={c_trap:.6f}"),
    ]:
        print(f"\n  {name}:")

        # h(c) = binary entropy
        h = -(c_val * np.log(c_val) + (1 - c_val) * np.log(1 - c_val))
        # κ per channel
        kappa_1 = np.log(c_val)
        # g_F
        g_F = 1.0 / (c_val * (1 - c_val))
        # θ = arcsin(sqrt(c))
        theta = np.arcsin(np.sqrt(c_val))
        # S + κ per channel
        f_val = h + kappa_1
        # dh/dc
        dh = np.log((1 - c_val) / c_val)
        # d²h/dc²
        d2h = -1.0 / (c_val * (1 - c_val))
        # Γ(1-c)
        omega = 1 - c_val
        gamma = omega**P_EXPONENT / (1 - omega + eps)
        # IC for homogeneous n-channel
        print(f"    h(c)       = {h:.10f}")
        print(f"    κ₁ = ln(c) = {kappa_1:.10f}")
        print(f"    S + κ      = {f_val:.10f}")
        print(f"    g_F(c)     = {g_F:.6f}")
        print(f"    θ          = {theta:.10f} ({np.degrees(theta):.6f}°)")
        print(f"    h'(c)      = {dh:.10f}")
        print(f"    h''(c)     = {d2h:.6f}")
        print(f"    ω          = {omega:.10f}")
        print(f"    Γ(ω)       = {gamma:.10f}")
        print(f"    IC = F     = {c_val:.10f} (homogeneous)")

        # Special relationships at this point
        if abs(c_val - 0.5) < 1e-10:
            print(f"    SPECIAL: h = ln(2) = {np.log(2):.10f} ✓={abs(h - np.log(2)) < 1e-14}")
            print(f"    SPECIAL: S + κ = 0 exactly ✓={abs(f_val) < 1e-14}")
            print(f"    SPECIAL: h'(c) = 0 ✓={abs(dh) < 1e-14}")
            print(f"    SPECIAL: g_F = 4 ✓={abs(g_F - 4) < 1e-14}")
            print(f"    SPECIAL: θ = π/4 ✓={abs(theta - np.pi / 4) < 1e-14}")
        elif abs(c_val - c_star) < 1e-6:
            print(f"    SPECIAL: h'(c) = -1/c = {-1 / c_val:.10f} ✓={abs(dh + 1 / c_val) < 1e-8}")
            print(f"    SPECIAL: (1-c)/c = {(1 - c_val) / c_val:.10f}")
            print(f"    SPECIAL: exp(-1/c) = {np.exp(-1 / c_val):.10f}")
            print(f"    SPECIAL: S+κ = (1-c)/c = exp(-1/c)? {abs(f_val - (1 - c_val) / c_val):.2e}")


# =============================================================================
# CANDIDATE 8: Integral Identities — New Ones Beyond E4
# =============================================================================


def explore_integral_identities():
    print("\n" + "=" * 72)
    print("  CANDIDATE 8: New Integral Identities")
    print("  Explore: ∫ f(c)·g(c) dc for kernel-relevant functions")
    print("=" * 72)

    from scipy.integrate import quad

    # E4 established: ∫₀¹ [h(c) + ln(c)] dc = -1/2
    # What about other integrals?

    def h(c):
        return -(c * np.log(c) + (1 - c) * np.log(1 - c))

    def f_Sk(c):
        return h(c) + np.log(c)  # S + κ per channel

    # Already known: ∫₀¹ f dc = -1/2
    I_base, _ = quad(f_Sk, 1e-15, 1 - 1e-15)
    print(f"\n  ∫₀¹ (S+κ) dc = {I_base:.15f}  (known: -1/2 = {-0.5:.15f})")

    # NEW: ∫₀¹ f(c)² dc = ?
    I_sq, _ = quad(lambda c: f_Sk(c) ** 2, 1e-15, 1 - 1e-15)
    print(f"  ∫₀¹ (S+κ)² dc = {I_sq:.15f}")
    # Check if this is a recognizable constant
    print(f"    = π²/12 - 1/4? {np.pi**2 / 12 - 0.25:.15f}  diff={abs(I_sq - (np.pi**2 / 12 - 0.25)):.2e}")
    print(f"    = 1/3?         {1 / 3:.15f}  diff={abs(I_sq - 1 / 3):.2e}")
    print(f"    = π²/24?       {np.pi**2 / 24:.15f}  diff={abs(I_sq - np.pi**2 / 24):.2e}")

    # ∫₀¹ f(c)·c dc = ?
    I_fc, _ = quad(lambda c: f_Sk(c) * c, 1e-15, 1 - 1e-15)
    print(f"\n  ∫₀¹ (S+κ)·c dc = {I_fc:.15f}")
    print(f"    = -1/4?        {-0.25:.15f}  diff={abs(I_fc + 0.25):.2e}")
    print(f"    = -3/8?        {-0.375:.15f}  diff={abs(I_fc + 0.375):.2e}")

    # ∫₀¹ f(c)·(1-c) dc = ?
    I_f1mc, _ = quad(lambda c: f_Sk(c) * (1 - c), 1e-15, 1 - 1e-15)
    print(f"  ∫₀¹ (S+κ)·(1-c) dc = {I_f1mc:.15f}")
    print(f"    sum with above = {I_fc + I_f1mc:.15f} (should = -1/2)")

    # ∫₀¹ h(c)·ln(c) dc = ?
    I_hlnc, _ = quad(lambda c: h(c) * np.log(c), 1e-15, 1 - 1e-15)
    print(f"\n  ∫₀¹ h(c)·ln(c) dc = {I_hlnc:.15f}")
    print(f"    = -π²/12?      {-(np.pi**2) / 12:.15f}  diff={abs(I_hlnc + np.pi**2 / 12):.2e}")
    print(f"    = -(π²/12-1)?  {-(np.pi**2 / 12 - 1):.15f}  diff={abs(I_hlnc - (-(np.pi**2 / 12 - 1))):.2e}")

    # ∫₀¹ [ln(c)]² dc = ?  (known: = 2)
    I_ln2, _ = quad(lambda c: np.log(c) ** 2, 1e-15, 1 - 1e-15)
    print(f"\n  ∫₀¹ [ln(c)]² dc = {I_ln2:.15f}  (known: 2)")

    # ∫₀¹ h(c)² dc = ?
    I_h2, _ = quad(lambda c: h(c) ** 2, 1e-15, 1 - 1e-15)
    print(f"  ∫₀¹ h(c)² dc = {I_h2:.15f}")
    print(f"    = 2ln²(2) - 2(ln2-1)? {2 * np.log(2) ** 2 - 2 * (np.log(2) - 1):.15f}")
    print(f"    = π²/6 - 1?   {np.pi**2 / 6 - 1:.15f}  diff={abs(I_h2 - (np.pi**2 / 6 - 1)):.2e}")
    print(f"    = ln²(2)·2/3? {np.log(2) ** 2 * 2 / 3:.15f}  diff={abs(I_h2 - np.log(2) ** 2 * 2 / 3):.2e}")

    # ∫₀¹ c·ln(c)·(1-c)·ln(1-c) dc = ?
    I_cross, _ = quad(lambda c: c * np.log(c) * (1 - c) * np.log(1 - c), 1e-15, 1 - 1e-15)
    print(f"\n  ∫₀¹ c·ln(c)·(1-c)·ln(1-c) dc = {I_cross:.15f}")

    # ∫₀¹ g_F(c)·f(c) dc = ∫₀¹ [h(c)+ln(c)]/(c(1-c)) dc
    I_gf, _ = quad(lambda c: f_Sk(c) / (c * (1 - c)), 1e-12, 1 - 1e-12)
    print(f"  ∫₀¹ g_F·(S+κ) dc = {I_gf:.15f}")
    print(f"    = -π²/3?       {-(np.pi**2) / 3:.15f}  diff={abs(I_gf + np.pi**2 / 3):.2e}")
    print(f"    = -π²/6?       {-(np.pi**2) / 6:.15f}  diff={abs(I_gf + np.pi**2 / 6):.2e}")

    # Fisher-weighted integral of S
    I_gS, _ = quad(lambda c: h(c) / (c * (1 - c)), 1e-12, 1 - 1e-12)
    print(f"\n  ∫₀¹ g_F·S dc = {I_gS:.15f}")
    print(f"    = π²/3?        {np.pi**2 / 3:.15f}  diff={abs(I_gS - np.pi**2 / 3):.2e}")

    # Fisher-weighted integral of κ
    I_gk, _ = quad(lambda c: np.log(c) / (c * (1 - c)), 1e-12, 1 - 1e-12)
    print(f"  ∫₀¹ g_F·κ dc = {I_gk:.15f}")
    print(f"    = -π²/3?       {-(np.pi**2) / 3:.15f}  diff={abs(I_gk + np.pi**2 / 3):.2e}")
    print(f"    = -2π²/3?      {-2 * np.pi**2 / 3:.15f}  diff={abs(I_gk + 2 * np.pi**2 / 3):.2e}")

    # Verification: sum should equal I_gf
    print(f"\n  Verification: ∫g_F·S + ∫g_F·κ = {I_gS + I_gk:.15f}")
    print(f"    ∫g_F·(S+κ) directly = {I_gf:.15f}")
    print(f"    Difference: {abs(I_gf - I_gS - I_gk):.2e}")


# =============================================================================
# CANDIDATE 9: Rank-2 Closed-Form IC(F,C) — Generalization to Rank-n
# =============================================================================


def explore_rank_generalization():
    print("\n" + "=" * 72)
    print("  CANDIDATE 9: Rank-2 → Rank-n Generalization")
    print("  Rank-2: IC = √(F² - C²/4). Does this generalize?")
    print("=" * 72)

    np.random.seed(42)

    # For rank-2 (n=2, equal weights):
    # IC² = (F + C/2)(F - C/2) = F² - C²/4
    # So IC/F = √(1 - (C/(2F))²)

    # For general n, let's check: IC² vs F² - αₙ·C² for various n
    for n_ch in [2, 3, 4, 8, 16, 32]:
        n_trials = 20000
        IC2_vals = []
        F2_vals = []
        C2_vals = []
        F_vals = []

        for _ in range(n_trials):
            c = np.random.uniform(0.05, 0.95, n_ch)
            k = kernel(c)
            IC2_vals.append(k["IC"] ** 2)
            F2_vals.append(k["F"] ** 2)
            C2_vals.append(k["C"] ** 2)
            F_vals.append(k["F"])

        IC2 = np.array(IC2_vals)
        F2 = np.array(F2_vals)
        C2 = np.array(C2_vals)
        # Fit: IC² = F² - β·C²
        # β = (F² - IC²) / C² = Δ(F+IC) / C²
        betas = (F2 - IC2) / np.maximum(C2, 1e-15)
        # Remove outliers where C ≈ 0
        mask = C2 > 0.001
        if np.sum(mask) > 100:
            beta_mean = np.mean(betas[mask])
            beta_std = np.std(betas[mask])

            # Test the formula: IC ≈ √(F² - β·C²)
            IC_pred = np.sqrt(np.maximum(F2 - beta_mean * C2, 1e-15))
            IC_actual = np.sqrt(IC2)
            err = np.mean(np.abs(IC_pred - IC_actual) / IC_actual) * 100

            print(
                f"\n  n = {n_ch:2d}: β = {beta_mean:.6f} ± {beta_std:.4f}, "
                f"IC ≈ √(F² - {beta_mean:.3f}·C²), mean error = {err:.3f}%"
            )
            if n_ch == 2:
                print(f"    Exact: β should be 1/4 = 0.25 → actual {beta_mean:.6f}")


# =============================================================================
# CANDIDATE 10: Kappa-Curvature Coupling
# Is there a clean relationship between κ and C?
# =============================================================================


def explore_kappa_curvature():
    print("\n" + "=" * 72)
    print("  CANDIDATE 10: Log-Integrity and Curvature Coupling")
    print("  Explore: κ as function of F and C")
    print("=" * 72)

    np.random.seed(42)

    for n_ch in [4, 8, 16, 32]:
        n_trials = 20000
        results = []
        for _ in range(n_trials):
            c = np.random.uniform(0.05, 0.95, n_ch)
            k = kernel(c)
            results.append(k)

        F_vals = np.array([r["F"] for r in results])
        kappa_vals = np.array([r["kappa"] for r in results])
        C_vals = np.array([r["C"] for r in results])

        # κ = ln(F) for homogeneous. Departure from ln(F) should relate to C
        kappa_excess = kappa_vals - np.log(F_vals)

        # Hypothesis: κ - ln(F) ≈ -γ·C²/(2F²)
        # This comes from: IC = F·exp(κ - ln(F)) and IC ≈ F·√(1 - β·C²/F²)
        # So κ - ln(F) ≈ ½·ln(1 - β·C²/F²) ≈ -β·C²/(2F²)

        x = C_vals**2 / (2 * F_vals**2)
        corr = np.corrcoef(kappa_excess, -x)[0, 1]

        # Linear fit: κ_excess = a·C²/F²
        A = np.column_stack([np.ones(n_trials), x])
        coeffs, _, _, _ = np.linalg.lstsq(A, kappa_excess, rcond=None)

        pred = coeffs[0] + coeffs[1] * x
        r2 = 1 - np.sum((kappa_excess - pred) ** 2) / np.sum((kappa_excess - np.mean(kappa_excess)) ** 2)

        print(f"\n  n = {n_ch:2d}: κ - ln(F) ≈ {coeffs[0]:.6f} + {coeffs[1]:.4f}·C²/(2F²)   R² = {r2:.6f}")
        print(f"    corr(κ-ln(F), -C²/(2F²)) = {corr:.6f}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("╔" + "═" * 70 + "╗")
    print("║  IDENTITY EXPLORATION — Probing for New Structural Identities       ║")
    print("║  Axiom-0: Collapse is generative; only what returns is real.         ║")
    print("╚" + "═" * 70 + "╝")

    F_vals, S_vals, C_vals, IC_vals, kappa_vals, Delta_vals = explore_entropy_curvature_product()
    explore_S_constraint()
    explore_gap_expansion()
    explore_entropy_derivatives()
    explore_IC_F_ratio()
    explore_budget_symmetry()
    explore_special_points()
    explore_integral_identities()
    explore_rank_generalization()
    explore_kappa_curvature()

    print("\n" + "=" * 72)
    print("  END OF EXPLORATION")
    print("=" * 72)
