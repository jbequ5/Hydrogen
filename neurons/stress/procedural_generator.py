# neurons/stress/procedural_generator.py

"""
Procedural Stress Generator for Hydrogen - Full Phase 0 Coverage.

Supports all current problem types:
- Elliptic (Poisson, Darcy)
- Hyperbolic (Burgers)
- Parabolic (Heat)
- Incompressible Flow (Navier-Stokes laminar)
- Elasticity
- Thermo-elasticity (Multi-physics)

Follows docs/STRESS_TEST_DESIGN.md
"""

import random
from typing import List, Dict, Any

from .base_generator import BaseStressGenerator, stress_registry
from .stress_models import StressVariant, StressSource


class ProceduralStressGenerator(BaseStressGenerator):
    """
    Generates procedural stress variants based on physics class.
    Deep implementations for all Phase 0 problem types.
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

        if physics_class in ["elliptic", "poisson", "darcy"]:
            variants.extend(self._generate_elliptic_stress(rng, difficulty))

        elif physics_class == "hyperbolic":
            variants.extend(self._generate_burgers_stress(rng, difficulty))

        elif physics_class == "parabolic":
            variants.extend(self._generate_heat_stress(rng, difficulty))

        elif physics_class in ["incompressible", "navier_stokes"]:
            variants.extend(self._generate_ns_stress(rng, difficulty))

        elif physics_class == "elasticity":
            variants.extend(self._generate_elasticity_stress(rng, difficulty))

        elif physics_class in ["multi_physics", "thermo_elasticity"]:
            variants.extend(self._generate_thermo_elasticity_stress(rng, difficulty))

        return variants

    # ============================================================
    # Elliptic (Poisson / Darcy)
    # ============================================================

    def _generate_elliptic_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(4 + difficulty * 5))

        for i in range(num):
            source_amplitude = 1.0 + difficulty * rng.uniform(0.5, 4.0)
            boundary_variation = difficulty * rng.uniform(0.05, 0.4)
            coeff_variation = difficulty * rng.uniform(0.1, 0.8)

            parameters = {
                "source_amplitude": round(source_amplitude, 3),
                "boundary_variation": round(boundary_variation, 3),
                "coeff_variation": round(coeff_variation, 3),
            }

            variant = StressVariant(
                variant_id=f"elliptic_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying source strength, boundary conditions, and "
                        "coefficient fields to stress conservation and maximum principle."
                    )
                },
            )
            variants.append(variant)

        return variants

    # ============================================================
    # Burgers (Hyperbolic) - Deep
    # ============================================================

    def _generate_burgers_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(5 + difficulty * 6))

        for i in range(num):
            shock_strength = 1.0 + difficulty * rng.uniform(0.5, 3.0)
            hf_amplitude = difficulty * rng.uniform(0.01, 0.15)
            rollout_steps = int(50 + difficulty * rng.uniform(50, 200))
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
                        "Varying shock strength, high-frequency content, and "
                        "rollout length to stress conservation, shock capturing, "
                        "and long-term stability."
                    )
                },
            )
            variants.append(variant)

        return variants

    # ============================================================
    # Heat (Parabolic)
    # ============================================================

    def _generate_heat_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(4 + difficulty * 5))

        for i in range(num):
            forcing_amplitude = difficulty * rng.uniform(0.5, 3.0)
            conductivity_variation = difficulty * rng.uniform(0.1, 0.7)
            rollout_steps = int(40 + difficulty * rng.uniform(30, 150))

            parameters = {
                "forcing_amplitude": round(forcing_amplitude, 3),
                "conductivity_variation": round(conductivity_variation, 3),
                "rollout_steps": rollout_steps,
            }

            variant = StressVariant(
                variant_id=f"heat_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying time-dependent forcing and conductivity to stress "
                        "energy conservation and long-term decay."
                    )
                },
            )
            variants.append(variant)

        return variants

    # ============================================================
    # Navier-Stokes (Incompressible Flow)
    # ============================================================

    def _generate_ns_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(5 + difficulty * 5))

        for i in range(num):
            reynolds = 50 + difficulty * rng.uniform(20, 80)  # Laminar range
            geometry_scale = 1.0 + difficulty * rng.uniform(-0.2, 0.4)
            boundary_perturbation = difficulty * rng.uniform(0.02, 0.15)

            parameters = {
                "reynolds": round(reynolds, 1),
                "geometry_scale": round(geometry_scale, 3),
                "boundary_perturbation": round(boundary_perturbation, 3),
            }

            variant = StressVariant(
                variant_id=f"ns_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying Reynolds number and geometry within laminar regime "
                        "to stress divergence-free condition and energy stability."
                    )
                },
            )
            variants.append(variant)

        return variants

    # ============================================================
    # Elasticity
    # ============================================================

    def _generate_elasticity_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(4 + difficulty * 5))

        for i in range(num):
            young_modulus_variation = difficulty * rng.uniform(0.1, 0.6)
            poisson_ratio = 0.25 + difficulty * rng.uniform(-0.05, 0.1)
            boundary_displacement = difficulty * rng.uniform(0.05, 0.3)

            parameters = {
                "young_modulus_variation": round(young_modulus_variation, 3),
                "poisson_ratio": round(poisson_ratio, 3),
                "boundary_displacement": round(boundary_displacement, 3),
            }

            variant = StressVariant(
                variant_id=f"elasticity_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying material properties and boundary displacement "
                        "to stress equilibrium and boundary satisfaction."
                    )
                },
            )
            variants.append(variant)

        return variants

    # ============================================================
    # Thermo-Elasticity (Multi-physics)
    # ============================================================

    def _generate_thermo_elasticity_stress(
        self, rng: random.Random, difficulty: float
    ) -> List[StressVariant]:
        variants = []
        num = max(3, int(5 + difficulty * 5))

        for i in range(num):
            thermal_expansion = 1e-5 * (1 + difficulty * rng.uniform(0.2, 1.5))
            coupling_strength = difficulty * rng.uniform(0.3, 1.2)
            temperature_variation = difficulty * rng.uniform(10, 80)

            parameters = {
                "thermal_expansion": round(thermal_expansion, 8),
                "coupling_strength": round(coupling_strength, 3),
                "temperature_variation": round(temperature_variation, 1),
            }

            variant = StressVariant(
                variant_id=f"thermo_elasticity_proc_{i}",
                source=StressSource.PROCEDURAL,
                parameters=parameters,
                difficulty=difficulty,
                metadata={
                    "physics_justification": (
                        "Varying thermal expansion and coupling strength to stress "
                        "thermo-mechanical interaction and conservation in coupled system."
                    )
                },
            )
            variants.append(variant)

        return variants


# ============================================================
# Register generator for all supported physics classes
# ============================================================
for pc in ["elliptic", "poisson", "darcy", "hyperbolic", "parabolic",
           "incompressible", "navier_stokes", "elasticity",
           "multi_physics", "thermo_elasticity"]:
    stress_registry.register(pc, ProceduralStressGenerator())
