# neurons/stress/stress_evaluator.py

"""
StressEvaluator - Determinism-aware evaluation of models on hidden stress sets.
"""

from typing import Dict, Any, Optional

from .stress_models import StressTestSet
from neurons.utils.determinism import get_sub_seeds, setup_determinism_for_component


class StressEvaluator:
    def __init__(self, scorer):
        self.scorer = scorer

    def evaluate(
        self,
        model: Any,
        stress_set: StressTestSet,
        master_seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        if master_seed is not None:
            sub_seeds = get_sub_seeds(master_seed)
            setup_determinism_for_component("scoring", master_seed, sub_seeds)

        results = {
            "hard_gate_failures": [],
            "soft_gate_penalties": {},
            "detailed_metrics": {},
            "stress_score_contribution": 0.0,
        }

        hard_fail = False

        for variant in stress_set.variants:
            metrics = self._simulate_metrics(variant)

            hard_violations = self.scorer.check_hard_gates(metrics)
            if hard_violations:
                hard_fail = True
                results["hard_gate_failures"].extend(hard_violations)

            soft_penalties = self.scorer.apply_soft_gates(metrics)
            for gate, penalty in soft_penalties.items():
                results["soft_gate_penalties"][gate] = (
                    results["soft_gate_penalties"].get(gate, 0) + penalty
                )

            results["detailed_metrics"][variant.variant_id] = metrics

        if hard_fail:
            results["stress_score_contribution"] = 0.0
        else:
            base = 1.0 - sum(results["soft_gate_penalties"].values()) / max(
                len(results["soft_gate_penalties"]), 1
            )
            results["stress_score_contribution"] = max(0.0, base)

        return results

    def _simulate_metrics(self, variant):
        """Temporary simulation. Replace with real model inference."""
        return {
            "mass_conservation_error": 1e-4,
            "energy_dissipation_rate": 1e-5,
            "boundary_error": 5e-4,
            "rollout_stability": 0.98,
        }
