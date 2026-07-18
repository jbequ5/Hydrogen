"""SOTA Agentic Miner interface for Hydrogen.

Designed for autonomous agents (LLMs, evolutionary strategies, RL, etc.)
to participate in the subnet with minimal friction.

Key features:
- Easy access to symbolically/causally recommended priors
- Fast local self-testing before submission
- Clean hooks for strategy proposal/mutation
- Feedback loop for learning over time
- Async-friendly design
"""

from typing import Dict, Any, Optional, List

import asyncio

from hydrogen.miner.strategy_generator import generate_strategy


class AgenticMiner:
    """
    High-level interface for agentic mining.

    This class is intentionally lightweight and extensible.
    Advanced agents can subclass it or inject custom proposers.
    """

    def __init__(self, client):
        """
        client: An instance of HydrogenClient (or compatible SDK).
        """
        self.client = client
        self.history: List[Dict[str, Any]] = []  # Simple in-memory trajectory

    async def get_challenges(self) -> List[str]:
        """Return list of currently active challenges."""
        return await self.client.get_active_challenges()

    async def get_priors(self, challenge_id: str) -> Dict[str, Any]:
        """
        Get symbolically and causally recommended priors for a challenge.
        These come from the Landscape Agent's analysis.
        """
        return await self.client.get_priors(challenge_id)

    async def propose_strategy(
        self,
        challenge_id: str,
        base_strategy: Optional[Dict[str, Any]] = None,
        mutation_strength: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Propose a new strategy for a challenge.

        Default behavior:
        - Start from Landscape priors if no base_strategy is given
        - Apply light mutation for exploration

        Advanced agents can override this method entirely.
        """
        if base_strategy is None:
            priors = await self.get_priors(challenge_id)
            base_strategy = generate_strategy(
                challenge_id=challenge_id,
                backbone=priors.get("recommended_backbone", "fno"),
            )
            # Merge suggested loss weights from priors
            if "loss_vector" in priors:
                base_strategy.setdefault("pino", {})["loss_vector"] = priors["loss_vector"]

        # Light mutation for exploration (can be replaced by smarter agents)
        strategy = self._light_mutate(base_strategy, mutation_strength)
        return strategy

    def _light_mutate(self, strategy: dict, strength: float = 0.15) -> dict:
        """Simple mutation for exploration. Sophisticated agents should override this."""
        import copy
        import random

        mutated = copy.deepcopy(strategy)

        # Mutate loss weights slightly
        if "pino" in mutated and "loss_vector" in mutated["pino"]:
            for key in mutated["pino"]["loss_vector"]:
                val = mutated["pino"]["loss_vector"][key]
                mutated["pino"]["loss_vector"][key] = max(
                    0.1, val * (1 + random.uniform(-strength, strength))
                )

        # Occasionally tweak learning rate
        if random.random() < 0.3:
            lr = mutated.get("learning_rate", 0.001)
            mutated["learning_rate"] = max(1e-5, lr * random.uniform(0.7, 1.4))

        return mutated

    async def validate_locally(
        self,
        strategy: dict,
        challenge_id: str,
        quick: bool = True,
    ) -> Dict[str, Any]:
        """
        Fast local validation of a strategy.

        Returns estimated score, physics gate results, and other diagnostics.
        Use this before paying the submission fee.
        """
        result = await self.client.validate_locally(
            strategy=strategy,
            challenge_id=challenge_id,
            quick=quick,
        )
        return result

    async def submit(self, strategy: dict, challenge_id: str) -> Dict[str, Any]:
        """Submit a strategy to the network."""
        result = await self.client.submit(challenge_id=challenge_id, strategy=strategy)

        # Record in local history for learning
        self.history.append({
            "challenge_id": challenge_id,
            "strategy": strategy,
            "result": result,
            "timestamp": asyncio.get_event_loop().time(),
        })

        return result

    async def get_recent_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent submission results for this agent."""
        return self.history[-limit:]

    async def run_iteration(self, challenge_id: str, iterations: int = 5):
        """
        High-level helper: Run multiple propose -> validate -> (maybe submit) iterations.

        Sophisticated agents can replace this with their own loop.
        """
        best_score = -float("inf")
        best_strategy = None

        for i in range(iterations):
            strategy = await self.propose_strategy(challenge_id)
            validation = await self.validate_locally(strategy, challenge_id, quick=True)

            estimated_score = validation.get("estimated_score", 0.0)

            print(f"Iteration {i+1}: estimated_score = {estimated_score:.4f}")

            if estimated_score > best_score:
                best_score = estimated_score
                best_strategy = strategy

            # Simple policy: submit if estimated score looks good
            if estimated_score > 0.08:  # Tunable threshold
                print("Submitting promising strategy...")
                result = await self.submit(best_strategy, challenge_id)
                return result

        # Fallback: submit best found
        if best_strategy:
            return await self.submit(best_strategy, challenge_id)

        return None


# Example usage for an LLM-based or evolutionary agent
async def example_agent_loop():
    from hydrogen_miner import HydrogenClient

    client = HydrogenClient(hotkey="5F...")
    miner = AgenticMiner(client)

    challenges = await miner.get_challenges()

    for challenge_id in challenges:
        result = await miner.run_iteration(challenge_id, iterations=6)
        if result:
            print(f"Submitted to {challenge_id} with result: {result}")
