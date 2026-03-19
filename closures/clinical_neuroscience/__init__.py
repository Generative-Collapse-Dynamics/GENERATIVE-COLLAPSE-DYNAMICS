"""Clinical Neuroscience closure domain — Tier-2 expansion."""

from closures.clinical_neuroscience.sleep_neurophysiology import (
    SN_ENTITIES,
)
from closures.clinical_neuroscience.sleep_neurophysiology import (
    compute_all_entities as compute_all_sn_entities,
)
from closures.clinical_neuroscience.sleep_neurophysiology import (
    verify_all_theorems as verify_all_sn_theorems,
)

__all__ = [
    "SN_ENTITIES",
    "compute_all_sn_entities",
    "verify_all_sn_theorems",
]
