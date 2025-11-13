"""
RAIA Utility Functions

Helper functions for advanced RAG evaluation including drift detection algorithms.
"""

from .drift_detection import (
    kl_divergence,
    js_divergence,
    wasserstein_distance,
    cosine_similarity,
    compute_embedding_drift,
    detect_drift_comprehensive,
)
from .comparison import RAIAComparator

__all__ = [
    "kl_divergence",
    "js_divergence",
    "wasserstein_distance",
    "cosine_similarity",
    "compute_embedding_drift",
    "detect_drift_comprehensive",
    "RAIAComparator",
]
