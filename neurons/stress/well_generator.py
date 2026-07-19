# neurons/stress/well_generator.py

"""
Well-based Stress Generator - Now fully deterministic.
"""

import random
from typing import List

from neurons.utils.determinism import get_sub_seeds
from .base_generator import BaseStressGenerator, stress_registry
from .stress_models import StressVariant, StressSource


class WellStressGenerator(BaseStressGenerator):
    WELL_DATASET_MAP = {
        "hyperbolic": ["turbulence", "viscoelastic"],
        "elliptic": ["active_matter"],
        "parabolic": ["acoustic_scattering"],
        "multi_physics": ["active_matter", "viscoelastic"],
    }

    def generate(self, challenge_id: str, physics_class: str, seed: int, difficulty: float = 0.5):
        sub_seeds = get_sub_seeds(seed)
        rng = random.Random(sub_seeds["stress_generation"])

        variants = []
        datasets = self.WELL_DATASET_MAP.get(physics_class, [])
        if not datasets:
            return variants

        num_variants = max(2, int(3 + difficulty * 4))

        for i in range(num_variants):
            dataset = rng.choice(datasets)
            slice_id = f"{dataset}_slice_{rng.randint(0, 999)}"

            variant = StressVariant(
                variant_id=f"well_{physics_class}_{i}",
                source=StressSource.WELL,
                parameters={"well_dataset": dataset, "slice_id": slice_id},
                well_dataset=dataset,
                difficulty=difficulty,
                metadata={
                    "physics_justification": f"Sampled from The Well ({dataset}) for generalization."
                },
            )
            variants.append(variant)

        return variants


for physics_class in WellStressGenerator.WELL_DATASET_MAP.keys():
    stress_registry.register(physics_class, WellStressGenerator())
