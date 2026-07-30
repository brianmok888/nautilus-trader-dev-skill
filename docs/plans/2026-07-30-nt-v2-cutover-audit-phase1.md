---
date: 2026-07-30
status: draft
tier: C
write-targets: [docs/tracking/Findings.md, docs/tracking/Components.md]
---

# NT V2 Rust Cutover Audit: Phase 1 Findings

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode`
references in this whole file are retained for migration/reference-only audit
evidence. Prefer Rust v2/PyO3 and `LiveNode` for new Rust-backed work.

## Review basis

NT v2 compatibility note: the Cython/v1 counts and classifications in this
block are migration/reference-only audit evidence; prefer Rust/PyO3 for new
work.

- Repository SHA: `c2f1a5f84980a9e8b554f2e7e4559cd17436d02a`.
- Pinned NautilusTrader baseline: `6e59fd74eaacacbb7410936f1766bd89fcce6f59`.
- Current upstream reviewed: `develop` at
  `45903fc8b925adae6323035fb0b4fb5b49b4f89b` and `nightly` at
  `22e802bc2366181393919ad43393bdb18b000c1d`.
- Scope: 18 NT `SKILL.md` files, 124 root references, 34 skill templates, and
  their enforcement tools and tests.
- Independent review: code-reviewer `REQUEST CHANGES`; architect `BLOCK`.
- Confirmed findings: **P0 3, P1 9, P2 4**. No confirmed unlabelled
  Cython/v1 occurrence was found by the current scanner; the enforcement
  gaps below can still allow future or source-snapshot violations to pass.

## Rust conversion gaps

[P0] Rust conversion gap: active non-AI guidance still authorizes Python prototyping, notebooks, labs, and tests instead of routing all new work to Rust.
  file: `skills/nt-signals/SKILL.md:29`; `skills/nt-backtest/SKILL.md:29`; `skills/nt-dev/SKILL.md:29`; `skills/nt-testing/SKILL.md:57`; `skills/nt-learn/SKILL.md:27`; `skills/nt-strategy-builder-rust/SKILL.md:27`
  fix: Remove active non-AI Python lane permissions, route new work to Rust, and make retained Python material explicitly migration/reference-only.

[P0] Rust conversion gap: the active learning and live-reference surface provides copyable Python `TradingNode` deployment outside physical migration quarantine.
  NT v2 compatibility note: Python live `TradingNode` is migration/reference-only; use Rust `LiveNode` for active work.
  file: `skills/nt-learn/curriculum/07-live-trading.md:9`; `skills/nt-learn/curriculum/07-live-trading.md:41`; `skills/nt-learn/curriculum/07-live-trading.md:243`; `references/concepts/live.md:67`; `references/integrations/okx.md:946`; `skills/nt-adapters/references/integrations/ib.md:1606`
  fix: Replace the active curriculum with Rust `LiveNode` guidance, move copyable Python live examples under `migration_reference/`, and leave pointer-only migration notes in active files.

[P0] Rust conversion gap: the documented G3 PyO3 import uses a compatibility projection absent from the normal current V2 feature set.
  file: `skills/nt-testing/SKILL.md:75`
  fix: Replace `nautilus_trader.core.nautilus_pyo3` root lookup with the current public `nautilus_trader.testkit.ExecTesterConfig` projection and execute the documented import in the G3 harness.

## V2 compliance violations

[P1] V2 compliance violation: execution-spec freshness is reported as unchanged although upstream added residual-close precision semantics.
  file: `skills/nt-testing/SKILL.md:17`; `references/developer_guide/spec_exec_testing.md:369`; `references/developer_guide/spec_exec_testing.md:1877`; `references/developer_guide/spec_exec_testing.md:2208`
  fix: Keep the immutable pinned snapshot labelled as such, add a current-upstream overlay for `close_positions_qty_precision`, exact sub-precision residuals, and the no-open-orders invariant, and regression-test the wording.

[P1] V2 compliance violation: adapter skills teach a seven-phase workflow while the pinned and current official guide defines ten dependency phases and distinct conformance, robustness, and operations exits.
  file: `skills/nt-adapters/SKILL.md:188`; `skills/nt-implement/SKILL.md:80`; `skills/nt-review/AGENTS.md:48`; `references/developer_guide/adapters.md:135`
  fix: Adopt the official ten-phase sequence and make G2 compilation evidence explicitly insufficient for adapter acceptance until spec, controlled-venue, resilience, fuzz, and operations evidence passes.

[P1] V2 compliance violation: Polymarket guidance hard-codes stale category rates and recommends the removed adapter-specific fee model.
  file: `references/integrations/polymarket.md:483`; `references/integrations/polymarket.md:510`
  fix: Source fee parameters from `instrument.fee_schedule`, document current rate/exponent values, and use `ProbabilityPriceFeeModel` without claiming unsupported future exponent or rebate behavior.

[P1] V2 compliance violation: Lighter order identity guidance omits 31-bit collision probing and restart recovery constraints.
  file: `references/integrations/lighter.md:223`
  fix: Document collision-probed client indexes, cached `VenueOrderId` mapping recovery, and the prohibition on reconstructing `ClientOrderId` from a numeric index alone.

[P1] V2 compliance violation: active Cap'n Proto trading-value fields use unvalidated `Float64` values and receive no schema or round-trip test.
  file: `skills/nt-implement/templates/capnp_schema.capnp:3`; `skills/nt-implement/templates/capnp_schema.capnp:18`; `tools/check_skill_g2_harnesses.py:299`
  fix: Encode trading values as raw fixed-point integers plus precision metadata and add schema-generation and round-trip validation to the owned G2 evidence.

[P1] V2 compliance violation: G0-G7 evidence can claim 144 Pass without binding all shared gate inputs and independent review to the exact repository SHA.
  file: `tools/check_skill_g2_harnesses.py:870`; `tests/test_skill_g2_harnesses.py:532`; `docs/superpowers/reports/2026-07-29-nt-v2-rust-cutover-reconciliation.md:65`
  fix: Add an exact-SHA external review/CI attestation and a manifest covering every file and command used by G0-G7; do not require a committed artifact to self-reference its eventual commit.

## Migration/reference-only legacy audit findings

NT v2 compatibility note: legacy Cython/v1 terms in this section are
migration/reference-only detector evidence; prefer Rust/PyO3 for new work.

[P1] Legacy enforcement gap: the mandatory standalone legacy-labelling gate and focused pytest wrapper do not exist.
  file: `tools/check_dev_guide_sync.py:906`; `tests/test_dev_guide_sync.py:1`
  fix: Add `tools/check_legacy_labelling.py` as a thin entry point over the canonical scanner and `tests/test_legacy_labelling.py` with clean-tree and unlabelled-fixture red/green coverage.

[P1] Legacy enforcement gap: Python source under `references/` bypasses template classification and the configured Ruff quality gate.
  NT v2 compatibility note: this legacy audit finding is migration/reference-only; it does not authorize Python production paths.
  file: `tests/test_template_classification.py:250`; `ruff.toml:1`; `tests/test_quality_gates.py:12`; `references/api_reference/conf.py:1`
  fix: Classify reference Python explicitly and lint/compile it with `--no-force-exclude` so source-snapshot and migration/reference code cannot bypass enforcement.

[P1] Legacy enforcement gap: source-pinned developer-guide files skip block-level Cython/v1 checking under a blanket snapshot exemption.
  NT v2 compatibility note: legacy Cython/v1 terms here are migration/reference-only audit evidence.
  file: `tools/check_dev_guide_sync.py:954`; `tools/check_dev_guide_sync.py:1040`; `references/developer_guide/environment_setup.md:8`
  fix: Preserve immutable snapshot bodies while requiring an explicit file-level source-snapshot policy or adjacent migration label for active-looking legacy blocks.

## Improvement opportunities

[P2] Improvement opportunity: the freshness gate reports only SHA/count drift and cannot prove that every relevant nightly/develop commit was dispositioned.
  file: `tools/check_upstream_freshness.py:101`; `tools/check_upstream_freshness.py:144`; `tests/test_v2_guidance_hardening.py:468`
  fix: Emit changed commits and paths and validate a reviewed delta manifest mapping relevant upstream changes to skills, references, tests, or an explicit no-impact decision.

[P2] Improvement opportunity: current PyO3 backtests can inject `CustomData`, but the backtest skill does not expose the current path.
  file: `skills/nt-backtest/SKILL.md:70`
  fix: Add a source-linked, bounded PyO3 `CustomData` injection note based on upstream commit `998005124e298e9b0c2f6c60be21e581f3426da1` and keep matching/execution ownership in Rust.

[P2] Improvement opportunity: actor and strategy state persistence across live and backtest is absent from the skill set.
  file: `skills/nt-live/SKILL.md:1`; `skills/nt-trading/SKILL.md:1`
  fix: Document Rust `on_load`/`on_save`, cache state loaders, and kernel save/finalize hooks from upstream commit `9a9e5fe7b762410229b380d5af92d32c13169c3a` with lifecycle tests.

[P2] Improvement opportunity: benchmark templates are neither rustfmt- nor compile-gated and retain prohibited banner comments.
  file: `references/dev_templates/criterion_template.rs:12`; `references/dev_templates/iai_template.rs:8`
  fix: Rustfmt the templates, replace banner separators with ordinary comments, and compile them in temporary benchmark crates.

## Approved implementation order

1. Close the active Python/Rust boundary and executable PyO3 import blockers.
2. Ship the mandatory legacy-labelling gate and close enforcement bypasses.
3. Reconcile execution-spec, adapter, Polymarket, Lighter, and precision drift.
4. Add bounded nightly/develop improvements and strengthen evidence provenance.
5. Regenerate cards only from fresh commands, reconcile this report, and obtain
   exact-current-SHA independent code-reviewer and architect verdicts.
