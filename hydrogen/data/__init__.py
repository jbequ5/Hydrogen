"""Data loading infrastructure for Hydrogen.

Supports both synthetic and benchmark datasets (primarily PDEBench).
The goal is to score miners against high-quality reference solutions.
"""

from .pdebench_loader import PDEBenchLoader
from .synthetic_loader import SyntheticLoader

__all__ = ["PDEBenchLoader", "SyntheticLoader", "get_data_loader"]

def get_data_loader(use_benchmark: bool = True, pde_name: str = None):
    if use_benchmark and pde_name:
        return PDEBenchLoader(pde_name=pde_name)
    return SyntheticLoader()
