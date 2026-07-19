# neurons/challenge/generator.py

"""
Challenge Generation Function - Now includes symbolic metadata.

Follows docs/CHALLENGE_GENERATION_DESIGN.md
"""

from typing import Optional, Dict, Any

from neurons.symbolic.extractor import SymbolicMetadataExtractor
from neurons.symbolic.symbolic_models import SymbolicMetadata


class Challenge:
    def __init__(self, challenge_id: str, physics_class: str, **kwargs):
        self.challenge_id = challenge_id
        self.physics_class = physics_class
        self.training_data = kwargs.get("training_data")
        self.holdout_data = kwargs.get("holdout_data")
        self.stress_config = kwargs.get("stress_config", {})
        self.symbolic_metadata: Optional[SymbolicMetadata] = kwargs.get("symbolic_metadata")
        self.difficulty = kwargs.get("difficulty", 0.5)
        self.metadata = kwargs.get("metadata", {})


def generate_challenge(
    challenge_id: str, config: Optional[Dict[str, Any]] = None
) -> Challenge:
    """
    Generate a Challenge object with symbolic metadata included.
    """
    config = config or {}
    physics_class = config.get("physics_class", "unknown")

    # Extract symbolic metadata
    extractor = SymbolicMetadataExtractor()
    symbolic_metadata = extractor.extract(challenge_id, config)

    return Challenge(
        challenge_id=challenge_id,
        physics_class=physics_class,
        training_data=config.get("training_data"),
        holdout_data=config.get("holdout_data"),
        stress_config=config.get("stress_config", {}),
        symbolic_metadata=symbolic_metadata,
        difficulty=config.get("difficulty", 0.5),
        metadata=config,
    )
