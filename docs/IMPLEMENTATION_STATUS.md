# Implementation Status (Updated July 17, 2026)

**Docs cleanup** ✓
**Scaffolding + integration** ✓
**Step 1 (challenge loader)** ✓
**Step 2 (validator core)** ✓

**This update (Real PhysicsNeMo training)**:
- New module: `hydrogen/training/physicsnemo_trainer.py`
  - `train_physics_neural_operator()` — actual small FNO training using PhysicsNeMo
  - Uses loss weights directly from miner strategy
  - Includes simple physics residual term + boundary loss
  - Graceful fallback to dummy if `physicsnemo` not installed
- Updated `neurons/validator.py` to call the real trainer by default
- `main()` now supports `--real` flag to force PhysicsNeMo path

**How to run with real training** (inside Docker image or after `pip install physicsnemo`):
```bash
python neurons/validator.py --challenge poisson_2d_v1 --real
```

**Note**: Training is deliberately short (6 epochs) for fast iteration in MVP.
In production validator, increase epochs + use proper PhysicsNeMo PDE losses.

**Current state**: We have a working end-to-end prototype with real model training + physics gates.

**Next logical steps**:
- Simple Landscape agent (fragment storage + baseline proposer)
- Better UQ and soft penalties in scoring
- Expand to Darcy + Burgers challenges
- Miner CLI with local dry-run

Old duplicated files can be removed now.