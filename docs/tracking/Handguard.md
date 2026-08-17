# Handguard — nautilus-trader-dev-skill

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

<!-- CHARTER -->
<!-- Role: Non-negotiable repository and skill invariants. -->
<!-- Does NOT contain: closures, plans, historical attestations, or per-skill detail. -->

Review date: 2026-08-10

## Scope authority

1. **This repository MUST contain NautilusTrader development guidance only.** Skills may architect, implement, test, integrate, operate, or review NT components.
2. **Upstream NautilusTrader MUST remain read-only while executing the master prompt.** Upstream source is evidence, never the implementation target.

## Rust-first authority

NT v2 compatibility note: Cython/v1 and legacy Python live terms below are migration/reference-only; prefer Rust V2/PyO3 and `LiveNode`.

3. **All new production guidance MUST default to Rust V2, PyO3, and `LiveNode`.**
4. **Python strategy and live material MUST be migration/reference-only unless it documents a current upstream binding contract.**
5. **Cython, v1, and legacy APIs MUST be explicitly labelled and paired with a current alternative.**

## Evidence integrity

6. **Version-sensitive claims MUST cite inspected upstream source or official documentation.** No fabricated identifiers, paths, or behavior claims.
7. **Pinned and current-develop APIs MUST not be conflated.** Post-pin behavior requires a version-scoped overlay.
8. **G2 Pass requires executable evidence and a matching owned-content hash.** Missing prerequisites yield Pending or Blocked, never an invented Pass.
9. **Tests MUST fail closed when their required pinned runtime is unavailable.** Static repository checks may use host Python only through an explicit allowlist.

## Repository hygiene

10. **Current repository docs MUST describe current behavior.** Completed plans, session handoffs, generated agent state, and external attestations do not belong in the tracked tree.
11. **Changes MUST preserve unrelated user work and MUST pass the complete validation matrix before completion is claimed.**
