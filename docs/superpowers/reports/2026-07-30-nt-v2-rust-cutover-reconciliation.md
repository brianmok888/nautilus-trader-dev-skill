# NT V2 Rust Cutover Reconciliation

## Scope and evidence boundary

This report re-runs the 2026-07-30 Phase 1 audit against the post-fix tree. The
Phase 1 baseline is repository commit
`c2f1a5f84980a9e8b554f2e7e4559cd17436d02a`. Reproducible G2 evidence uses
NautilusTrader commit `6e59fd74eaacacbb7410936f1766bd89fcce6f59`;
the reviewed current-develop overlay is
`45903fc8b925adae6323035fb0b4fb5b49b4f89b`. The exact final repository SHA and
independent review verdicts are external-attested after the final commit to
avoid self-referential evidence.

## Findings reconciliation

| Phase 1 finding | Severity | Status | Post-fix evidence |
| --- | --- | --- | --- |
| Active non-AI guidance authorized Python prototyping, labs, notebooks, or tests. | P0 | Closed | `tests/test_rust_lane_cutover.py:16`; `tests/test_markdown_lane_contract.py`; `skills/nt/SKILL.md:112` |
| Active learning/live references exposed copyable Python `TradingNode`. | P0 | Closed | `tests/test_rust_lane_cutover.py:40`; `skills/nt-learn/curriculum/07-live-trading.md`; `skills/nt-adapters/references/integrations/ib.md:1555` |
| G3 used a non-current PyO3 root projection for `ExecTesterConfig`. | P0 | Closed | `tests/test_rust_lane_cutover.py:91`; `skills/nt-testing/migration_reference/python/exec_tester_config.md:7` |
| Execution-spec freshness falsely claimed no develop drift. | P1 | Closed | `skills/nt-testing/SKILL.md:17`; `tests/test_exec_spec_current_overlay.py:33` |
| Adapter delivery used seven phases instead of the official ten. | P1 | Closed | `skills/nt-adapters/SKILL.md:188`; `tests/test_nt_v2_adapter_overlays.py:13` |
| Polymarket fee guidance used stale rates/model. | P1 | Closed | `references/integrations/polymarket.md:483`; `tests/test_nt_v2_adapter_overlays.py:51` |
| Lighter identity omitted 31-bit probing and restart recovery. | P1 | Closed | `references/integrations/lighter.md:226`; `tests/test_nt_v2_adapter_overlays.py:67` |
| Cap'n Proto trading values used `Float64` without schema validation. | P1 | Implementation closed; execution Pending | `skills/nt-implement/templates/capnp_schema.capnp:13`; structural fixed-point validation passes, but `tests/test_capnp_schema_precision.py` cannot compile/round-trip without `capnp`, so `nt-implement` G2 remains Pending. |
| G0-G7 evidence lacked an exact-SHA external ship attestation. | P1 | Implementation closed; ship validation Pending | `tools/check_cutover_attestation.py`; `tests/test_cutover_attestation.py`; the external ship attestation is generated and validated only after the final commit and exact-SHA reviews. |
| Standalone legacy-labelling gate and wrapper were absent. | P1 | Closed | `tools/check_legacy_labelling.py`; `tests/test_legacy_labelling.py` |
| Reference Python bypassed classification/Ruff. | P1 | Closed | `tools/template_classification.py:23`; `ruff.toml`; `tests/test_quality_gates.py:58` |
| Source-pinned guide bodies had a blanket legacy exemption. | P1 | Closed | `tools/check_dev_guide_sync.py:76`; `tests/test_dev_guide_sync.py:1562` |
| Upstream freshness could not prove every develop delta was dispositioned. | P2 | Closed | `tools/check_upstream_freshness.py:117`; `references/upstream-delta-review.json` maps all 40 develop delta commits. |
| Current PyO3 `CustomData` injection was absent. | P2 | Closed | `skills/nt-backtest/SKILL.md`; `tests/test_nt_v2_state_and_custom_data.py:15` |
| Rust actor/strategy state persistence was absent. | P2 | Closed | `skills/nt-live/SKILL.md`; `skills/nt-trading/SKILL.md`; `tests/test_nt_v2_state_and_custom_data.py:38` |
| Rust benchmark templates were not formatted or compiled. | P2 | Closed | `references/dev_templates/criterion_template.rs`; `references/dev_templates/iai_template.rs`; `tests/test_rust_benchmark_templates.py` |

### Closure totals

| Severity | Phase 1 | Closed | Residual |
| --- | ---: | ---: | ---: |
| P0 | 3 | 3 | 0 |
| P1 | 9 | 9 implemented | 2 validation gates Pending |
| P2 | 4 | 4 | 0 |
| **Total** | **16** | **16 implemented** | **2 validation gates Pending** |

## Progressive gate result

- Skills: **18**
- Gates per skill: **8** (`G0` through `G7`)
- Total gate rows: **144**
- Card-declared status: **143 Pass, 1 Pending, 0 Blocked**
- Pending: `nt-implement` G2. Structural fixed-point checks and owning Rust crate
  compilation passed, but this environment has no `capnp` executable, so actual
  schema generation and round-trip validation did not run.
- Card validator: `uv run python tools/check_skill_g2_harnesses.py --check-cards`
- G2 execution: `uv run python tools/check_skill_g2_harnesses.py --execute`
- Durable G2 evidence: `references/g2-evidence/*.json`

A G2 Cargo check proves compilation only. It does not prove adapter spec
conformance, controlled-venue/testnet behavior, resilience, fuzzing, or
operations readiness. Those remain mandatory change-specific delivery gates in
`skills/nt-adapters/SKILL.md`.

## Verification evidence

The final verification pass executes:

```bash
uv run pytest -q --ignore=tests/test_quality_gates.py
uv run pytest -q tests/test_quality_gates.py
uv run --with ruff ruff check .
uv run python tools/check_legacy_labelling.py
uv run python tools/check_dev_guide_sync.py
uv run python tools/check_dev_guide_snapshot_sync.py
uv run python tools/check_upstream_freshness.py
uv run python tools/check_skill_g2_harnesses.py --check-cards
python3 -m compileall -q tools tests skills/nt-evomap-integration/python_sidecar/brainstorming_evomap
```

All pass statuses in this report are contingent on the fresh outputs captured
before ship. Exact-current-SHA code-reviewer and architect verdicts are attached
externally after the final commit.

The readiness rows are bounded to the commands they cite. In particular, the
shared G3 command checks selected binding/ownership/callback policies, and the
shared G6 command checks selected repository policy boundaries; neither row is
a substitute for change-specific implementation, safety, or production
acceptance evidence.

## Follow-up TODO

1. **Pending environment gate:** install a compatible Cap'n Proto compiler,
   re-run `uv run pytest -q tests/test_capnp_schema_precision.py`, regenerate
   `nt-implement` G2 evidence, and change its card to Pass only after the real
   compile/round-trip path executes.
2. **Change-specific adapter acceptance:** when an adapter implementation
   changes, run official spec execution tests plus controlled-venue, resilience,
   fuzz, and operations gates. Do not infer those results from the repository's
   credentialless Cargo checks.
3. **Moving upstream:** re-run `tools/check_upstream_freshness.py` whenever
   `origin/develop` advances and disposition every new commit in
   `references/upstream-delta-review.json` before calling freshness reviewed.
