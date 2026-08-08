# Master-Prompt Alignment Cleanup Plan

## Objective

Make the repository's tracked surface match `docs/prompts/master-prompt.md`: reusable NautilusTrader-development skills and their current evidence only, with no AI/EvoMap lane or obsolete session/cutover artifacts.

## Tasks

1. Add boundary regressions proving the main router, skill inventory, and repository tree exclude AI/EvoMap and obsolete process artifacts; run them red.
2. Remove the AI/EvoMap skill, evidence, tests, plans, sidecar template, and all historical plan/report/handoff/session-state artifacts approved under cleanup scope B.
3. Remove obsolete cutover-attestation and historical inventory tooling/tests/scaffolding when no current validator depends on them.
4. Rewrite the main router and repository-facing documentation to list only NT-development skills and to state the upstream read-only and AI-out-of-scope boundaries.
5. Update the G2 harness registry, ownership hashes, tracking charters, and any retained legacy-lane tests to reflect the reduced skill inventory without weakening NT behavior checks.
6. Run focused tests green, then the full repository suite, sync/freshness validators, G2 card/evidence validation, diagnostics, diff checks, and manual router QA.

## Expected file classes

- Delete: `skills/nt-evomap-integration/**`, its evidence/tests/plans, historical docs/session artifacts, optional EvoMap migration pattern, obsolete attestation files.
- Modify: `skills/nt/SKILL.md`, repository indexes/guides, tracking docs, G2 registry/tests, Rust-lane boundary tests.
- Add temporarily/currently: `docs/cleanup-design.md`, this plan, and repository-boundary regression coverage.

## Verification commands

```bash
python3 -m pytest -q
python3 tools/check_dev_guide_sync.py
python3 tools/check_dev_guide_snapshot_sync.py
python3 tools/check_rust_trading_reference_sync.py
python3 tools/check_legacy_labelling.py
python3 tools/check_upstream_freshness.py --format json
python3 tools/check_skill_g2_harnesses.py --check-cards
git diff --check
```
