# Data Strategy for Hydrogen

## Goal
Score miners against the highest quality reference solutions possible.
This ensures emissions reward *actually useful* improvements in physics-informed neural operators.

## Recommended Sources (Priority Order)

### 1. PDEBench (Primary Recommendation)
- Best public benchmark for PINO/FNO-style work.
- High-quality numerical data for:
  - Darcy (excellent match)
  - Navier-Stokes 2D incompressible (`ns_incom`)
  - Burgers
  - Various diffusion problems
- Use this wherever available.

### 2. The Well (Secondary)
- Very large and diverse (15TB).
- Good for long-term breadth.

### 3. Synthetic / Custom Generation
- Use when no good benchmark exists (e.g. Elasticity, pure Poisson).
- Improve quality over time (higher-order solvers, better IC/BC).

## Implementation Plan

1. Create unified data loading layer (`hydrogen/data/`)
2. Prioritize PDEBench integration for Darcy + Navier-Stokes
3. Make `load_challenge(use_benchmark=True)` the default path when data is available
4. Keep synthetic generators as fallback

## Current Status
- Infrastructure created
- PDEBench loader scaffold in place
- Darcy and NS challenges can be switched to benchmark mode

## Next Actions
- Implement full HDF5 parsing for key PDEBench datasets
- Add download automation
- Wire benchmark data into validator training loop
