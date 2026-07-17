"""Landscape Agent module (initial skeleton).

Will eventually handle collection, storage, and distribution of
symbolic priors, evolved loss weights, and learned scoring expressions.
"""

from .storage import save_symbolic_artifact, load_symbolic_artifacts

__all__ = ["save_symbolic_artifact", "load_symbolic_artifacts"]
