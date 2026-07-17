# Documentation Cleanup Notes (July 17, 2026)

**Performed by Grok on user request**:

- Standardized filenames: Created clean `README.md` and `SPEC.md`. Deprecated/removed `ReadMe.md` and `Sepc.md` (typos).
- Deduplicated `SPEC.md`: Removed repeated SciML dependency sections (multiple near-identical 1.3 blocks), duplicated Phase 1 descriptions, and section numbering artifacts (e.g., repeated 7.5.3). Consolidated into single coherent document focused on Phase 0 MVP + clear later-phase references.
- Aligned inconsistencies: Emission mechanics, Phase 0 PDE count (now explicitly 3 for MVP realism), symbolic layer approach (pre-computed metadata for Phase 0).
- Updated `roadmap.md` to reflect gated scope and reference the new consolidated SPEC.
- Created this `docs/CLEANUP_NOTES.md` for transparency.
- `Launch_Spec.md` retained as historical/legacy Phase 0 elaboration (will be referenced or merged further if needed).
- All Appendices/ retained unchanged.

**Rationale**: The original specs were visionary and technically deep but had accumulated copy-paste duplication and minor inconsistencies during iterative editing. This cleanup makes the docs maintainable as the single source of truth while preserving full history in git.

**Next**: Code scaffolding (Python package structure, miner/validator skeletons, Dockerfile, basic physics gates) is being added immediately after this commit.

Previous full content available via git history or original files before this commit.