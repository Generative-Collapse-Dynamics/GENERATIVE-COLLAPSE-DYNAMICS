"""
UMCP Security Domain

Applies UMCP architecture to security validation:
- Anti-virus/malware detection
- Anti-scam/phishing detection
- Identity verification
- Privacy protection

Core Axiom Translation:
    "What Returns Through Collapse Is Real" → "What Survives Validation Is Trusted"

Architecture:
    Tier-0: Frozen security policy (contracts, closures)
    Tier-1: Deterministic security invariants (T, θ, H, D, σ, TIC, τ_A)
    Tier-2: Diagnostic overlays (threat classification, reputation, etc.)
"""

# Attack Surface Kernel
# Tier-1 Kernel
from closures.security.anomaly_return import (
    TauAType,
    compute_anomaly_return,
    compute_anomaly_return_series,
    detect_anomaly_events,
)
from closures.security.attack_surface_kernel import (
    ATK_CHANNELS,
    ATK_ENTITIES,
    N_ATK_CHANNELS,
    ATKKernelResult,
    compute_atk_kernel,
)
from closures.security.attack_surface_kernel import (
    compute_all_entities as compute_all_atk_entities,
)
from closures.security.attack_surface_kernel import (
    verify_all_theorems as verify_all_atk_theorems,
)
from closures.security.behavior_profiler import (
    AnomalyLevel,
    BehaviorTrend,
    analyze_trend,
    compute_baseline_profile,
    compute_deviation,
    detect_behavior_anomalies,
    profile_behavior_series,
)
from closures.security.device_daemon import (
    DeviceCategory,
    DeviceDaemon,
    DeviceStatus,
    NetworkAction,
    NetworkDevice,
)
from closures.security.privacy_auditor import (
    PIISeverity,
    ViolationType,
    audit_data_privacy,
    detect_pii,
    generate_privacy_report,
)
from closures.security.reputation_analyzer import (
    ReputationResult,
    ReputationType,
    analyze_file_hash,
    analyze_ip_reputation,
    analyze_url_reputation,
)
from closures.security.response_engine import (
    ResponseAction,
    ResponseDecision,
    ResponseEngine,
)

# Daemon Components (Background Service)
from closures.security.security_daemon import (
    MonitoredEntity,
    SecurityDaemon,
    SecurityEvent,
)
from closures.security.security_entropy import compute_security_entropy, compute_signal_dispersion

# Security Kernel
from closures.security.security_kernel import (
    N_SK_CHANNELS,
    SK_CHANNELS,
    SK_ENTITIES,
    SKKernelResult,
    compute_sk_kernel,
)
from closures.security.security_kernel import (
    compute_all_entities as compute_all_sk_entities,
)
from closures.security.security_kernel import (
    verify_all_theorems as verify_all_sk_theorems,
)

# Security Theorems
from closures.security.security_theorems import (
    verify_all_theorems as verify_all_sec_theorems,
)

# Main Validator
from closures.security.security_validator import SecurityInvariants, SecurityValidator, ValidationResult

# Tier-2 Domain Expansion Closures
from closures.security.threat_classifier import (
    ThreatClassification,
    ThreatType,
    classify_threat,
    classify_threat_series,
    generate_threat_report,
)
from closures.security.trust_fidelity import (
    classify_trust_status,
    compute_trust_fidelity,
    compute_trust_fidelity_series,
)
from closures.security.trust_integrity import compute_seam_residual, compute_trust_integrity, compute_trust_seam

__all__ = [
    # Attack Surface Kernel
    "ATK_CHANNELS",
    "ATK_ENTITIES",
    "N_ATK_CHANNELS",
    "N_SK_CHANNELS",
    # Security Kernel
    "SK_CHANNELS",
    "SK_ENTITIES",
    "ATKKernelResult",
    "AnomalyLevel",
    "BehaviorTrend",
    "DeviceCategory",
    "DeviceDaemon",
    "DeviceStatus",
    "MonitoredEntity",
    "NetworkAction",
    "NetworkDevice",
    "PIISeverity",
    "ReputationResult",
    "ReputationType",
    "ResponseAction",
    "ResponseDecision",
    "ResponseEngine",
    "SKKernelResult",
    # Daemon Components (Background Service)
    "SecurityDaemon",
    "SecurityEvent",
    "SecurityInvariants",
    # Main Validator
    "SecurityValidator",
    "TauAType",
    "ThreatClassification",
    "ThreatType",
    "ValidationResult",
    "ViolationType",
    "analyze_file_hash",
    "analyze_ip_reputation",
    "analyze_trend",
    "analyze_url_reputation",
    "audit_data_privacy",
    # Tier-2 Domain Expansion Closures
    "classify_threat",
    "classify_threat_series",
    "classify_trust_status",
    "compute_all_atk_entities",
    "compute_all_sk_entities",
    "compute_anomaly_return",
    "compute_anomaly_return_series",
    "compute_atk_kernel",
    "compute_baseline_profile",
    "compute_deviation",
    "compute_seam_residual",
    "compute_security_entropy",
    "compute_signal_dispersion",
    # Tier-1 Kernel
    "compute_sk_kernel",
    "compute_trust_fidelity",
    "compute_trust_fidelity_series",
    "compute_trust_integrity",
    "compute_trust_seam",
    "detect_anomaly_events",
    "detect_behavior_anomalies",
    "detect_pii",
    "generate_privacy_report",
    "generate_threat_report",
    "profile_behavior_series",
    # Theorem verification
    "verify_all_atk_theorems",
    "verify_all_sec_theorems",
    "verify_all_sk_theorems",
]
