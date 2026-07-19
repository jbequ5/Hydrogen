# neurons/stress/procedural_generator.py

"""
Procedural Stress Generator for Hydrogen.

Deep implementation starting with Burgers (hyperbolic) as the first physics class.
Follows docs/STRESS_TEST_DESIGN.md
"""

import random
from typing import List, Dict, Any

from .base_generator import BaseStressGenerator, stress_registry
from .stress_models import StressVariant, StressSource


class ProceduralStressGenerator(BaseStressGenerator):
    """
    Generates procedural stress variants based on physics class.

    Currently has deep support for Burgers (hyperbolic).
    Other physics classes can be added following the same pattern.
    """

    def generate(
        self,
        challenge_id: str,
        physics_class: str,
        seed: int,
        difficulty: float = 0.5
    ) -> List[StressVariant]:

        rng = random.Random(seed)
        variants = []

        if physics_class == "hyperbolic":
            # Burgers-specific procedural stress
            variants.extend(self._generate_burgers_stress(rng, difficulty))

        elif physics_class == "elliptic":
            variants.extend(self._generate_elliptic_stress(rng, difficulty))

        # Add more physics classes here as needed

        return variants

    # ============================================================
    # Burgers (Hyperbolic) Stress Generation - Deep Implementation
    # ============================================================

    def _generate_burgers_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        """
        Generate stress variants for Burgers equation.

        Stress dimensions:
        - Shock strength (initial condition steepness)
        - High-frequency perturbations
        - Long-horizon rollout length
        - Viscosity variation (within laminar-ish regime)
        """
        variants = []

        # Base number of variants scales with difficulty
        num_variants = max(3, int(5 + difficulty * 6))

        for i in range(num_variants):
            variant_seed = rng.randint(0, 2**31)

            # Shock strength: higher difficulty → steeper initial conditions
            shock_strength = 1.0 + difficulty * rng.uniform(0.5, 3.0)

            # High-frequency perturbation amplitude
            hf_amplitude = difficulty * rng.uniform(0.01, 0.15)

            # Rollout length (longer = harder stability test)
            rollout_steps = int(50 + difficulty * rng.uniform(50, 200))

            # Viscosity (small variations around typical Burgers value)
            viscosity = max(0.001, 0.01 * (1 + rng.uniform(-0.3, 0.3)))

            parameters = {
                "shock_strength": round(shock_strength, 3),
                "hf_amplitude": round(hf_amplitude, 4),
                "rollout_steps": rollout_steps,
                "viscosity": round(viscosity, 5),
            }

            variant = StressVariant(
                variant_id=f"burgers_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying shock strength, high-frequency content, "
                        "and rollout length to stress conservation, shock capturing, "
                        "and long-term stability."
                    ),
                    "variant_seed": variant_seed,
                },
            )
            variants.append(variant)

        return variants

    def _generate_elliptic_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        """
        Placeholder for elliptic physics class (Poisson, Darcy).
        Can be expanded later with source term, boundary, and coefficient stress.
        """
        return []


# Register the generator for relevant physics classes
stress_registry.register("hyperbolic", ProceduralStressGenerator())
stress_registry.register("elliptic", ProceduralStressGenerator())
