/**
 * Frozen Parameters — TypeScript mirror of frozen_contract.py
 *
 * Trans suturam congelatum — frozen across the seam.
 * These values are seam-derived, not prescribed.
 */

/* ─── Frozen Parameters ─────────────────────────────────────────── */

/** Guard band: pole at ω=1 does not affect measurements to machine precision. */
export const EPSILON = 1e-8;

/** Unique integer where ω_trap is a Cardano root of x³+x−1=0. */
export const P_EXPONENT = 3;

/** Curvature cost coefficient (unit coupling). */
export const ALPHA = 1.0;

/** Auxiliary coefficient. */
export const LAMBDA = 0.2;

/** Seam residual tolerance: |s| ≤ tol for PASS. */
export const TOL_SEAM = 0.005;

/** Normalization domain bounds. */
export const DOMAIN_MIN = 0.0;
export const DOMAIN_MAX = 1.0;

/** Logistic self-dual fixed point. */
export const C_STAR = 0.7822;

/** Drift trapping threshold (Cardano root). */
export const OMEGA_TRAP = 0.6823;

/** Channel-space trap. */
export const C_TRAP = 0.3177;

/* ─── Regime Thresholds ─────────────────────────────────────────── */

export const REGIME_THRESHOLDS = {
  omega_stable_max: 0.038,
  F_stable_min: 0.90,
  S_stable_max: 0.15,
  C_stable_max: 0.14,
  omega_watch_min: 0.038,
  omega_watch_max: 0.30,
  omega_collapse_min: 0.30,
  IC_critical_max: 0.30,
} as const;

/* ─── Regime Colors ─────────────────────────────────────────────── */

export const REGIME_COLORS = {
  STABLE: { bg: '#065f46', text: '#6ee7b7', border: '#059669', label: 'Stable' },
  WATCH: { bg: '#78350f', text: '#fcd34d', border: '#d97706', label: 'Watch' },
  COLLAPSE: { bg: '#7f1d1d', text: '#fca5a5', border: '#dc2626', label: 'Collapse' },
  CRITICAL: { bg: '#581c87', text: '#d8b4fe', border: '#9333ea', label: 'Critical' },
} as const;

/* ─── Kernel Symbols ────────────────────────────────────────────── */

export const KERNEL_SYMBOLS = {
  F: { symbol: 'F', name: 'Fidelity', latin: 'Fidelitas', formula: 'F = Σ wᵢcᵢ', range: '[0,1]', unit: '' },
  omega: { symbol: 'ω', name: 'Drift', latin: 'Derivatio', formula: 'ω = 1 − F', range: '[0,1]', unit: '' },
  S: { symbol: 'S', name: 'Entropy', latin: 'Entropia', formula: 'S = −Σ wᵢ[cᵢ ln cᵢ + (1−cᵢ) ln(1−cᵢ)]', range: '≥0', unit: 'nats' },
  C: { symbol: 'C', name: 'Curvature', latin: 'Curvatura', formula: 'C = σ(c) / 0.5', range: '[0,1]', unit: '' },
  kappa: { symbol: 'κ', name: 'Log-integrity', latin: 'Log-Integritas', formula: 'κ = Σ wᵢ ln(cᵢ)', range: '≤0', unit: '' },
  IC: { symbol: 'IC', name: 'Integrity', latin: 'Integritas Composita', formula: 'IC = exp(κ)', range: '(0,1]', unit: '' },
} as const;

/* ─── Rosetta Lenses ────────────────────────────────────────────── */

export interface RosettaLens {
  name: string;
  drift: string;
  fidelity: string;
  roughness: string;
  return_: string;
  integrity: string;
}

export const ROSETTA_LENSES: RosettaLens[] = [
  {
    name: 'Epistemology',
    drift: 'Change in belief/evidence',
    fidelity: 'Retained warrant',
    roughness: 'Inference friction',
    return_: 'Justified re-entry',
    integrity: 'Epistemic coherence',
  },
  {
    name: 'Ontology',
    drift: 'State transition',
    fidelity: 'Conserved properties',
    roughness: 'Heterogeneity / interface seams',
    return_: 'Restored coherence',
    integrity: 'Structural wholeness',
  },
  {
    name: 'Phenomenology',
    drift: 'Perceived shift',
    fidelity: 'Stable features',
    roughness: 'Distress / bias / effort',
    return_: 'Coping / repair that holds',
    integrity: 'Experiential continuity',
  },
  {
    name: 'History',
    drift: 'Periodization (what shifted)',
    fidelity: 'Continuity (what endures)',
    roughness: 'Rupture / confound',
    return_: 'Restitution / reconciliation',
    integrity: 'Historical coherence',
  },
  {
    name: 'Policy',
    drift: 'Regime shift',
    fidelity: 'Compliance / mandate persistence',
    roughness: 'Friction / cost / externality',
    return_: 'Reinstatement / acceptance',
    integrity: 'Governance continuity',
  },
  {
    name: 'Physics',
    drift: 'Phase transition',
    fidelity: 'Conservation law',
    roughness: 'Dissipation / coupling',
    return_: 'Equilibrium restoration',
    integrity: 'Physical coherence',
  },
  {
    name: 'Finance',
    drift: 'Market regime shift',
    fidelity: 'Portfolio persistence',
    roughness: 'Volatility / liquidity friction',
    return_: 'Recovery / mean reversion',
    integrity: 'Portfolio coherence',
  },
  {
    name: 'Security',
    drift: 'Threat surface change',
    fidelity: 'Control persistence',
    roughness: 'Attack friction / noise',
    return_: 'Remediation / hardening',
    integrity: 'Security posture',
  },
  {
    name: 'Semiotics',
    drift: 'Sign drift — departure from referent',
    fidelity: 'Ground persistence — convention that survived',
    roughness: 'Translation friction — meaning loss',
    return_: 'Interpretant closure — sign chain returns',
    integrity: 'Semiotic coherence',
  },
];

/* ─── Five-Word Vocabulary ──────────────────────────────────────── */

export const FIVE_WORDS = [
  { word: 'Drift', latin: 'derivatio', symbol: 'ω', role: 'Debit D_ω', description: 'What moved — the salient change relative to the Contract' },
  { word: 'Fidelity', latin: 'fidelitas', symbol: 'F', role: '—', description: 'What persisted — structure, warrant, or signal that survived' },
  { word: 'Roughness', latin: 'curvatura', symbol: 'C', role: 'Debit D_C', description: 'Where/why it was bumpy — friction, confound, or seam' },
  { word: 'Return', latin: 'reditus', symbol: 'τ_R', role: 'Credit R·τ_R', description: 'Credible re-entry — how the claim returns to legitimacy' },
  { word: 'Integrity', latin: 'integritas', symbol: 'IC', role: 'Verdict', description: 'Does it hang together — read from reconciled ledger' },
] as const;
