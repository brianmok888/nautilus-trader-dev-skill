# tests

Repository-behavior gates, not product unit tests: 42 flat pytest modules
(~8.5k lines, 406 test functions) pinning validator behavior, skill-repository
content, and the test-environment machinery itself.

Earned by scoring (9: 42 files, 100% code ratio, high symbol density, 406
test functions) and a domain no parent file covers: this suite is the
executable contract for the repository itself.

## WHERE TO LOOK

| Concern | Modules |
|---|---|
| Validator behavior (mirrors tools/) | test_dev_guide_sync (2,421 lines, largest), test_dev_guide_snapshot_sync, test_rust_trading_reference_sync, test_rust_analysis_reference_sync, test_upstream_freshness, test_findings_schema, test_governance_receipts, test_markdown_lane_contract, test_template_classification, test_legacy_labelling, test_quality_gates (pins tools/check_static_quality.CHECKS) |
| G2 harness and ownership | test_skill_g2_harnesses, test_g2_owned_content, test_dex_g2_harness, test_progressive_gate_cards |
| Upstream-pinned content assertions | test_current_* and test_v2_* / test_nt_v2_* modules, test_rust_first_end_to_end, test_rust_lane_cutover, test_rust_benchmark_templates, test_capnp_schema_precision, test_v2_inventory_pins_versions, test_exec_spec_current_overlay |
| Test-environment machinery | test_pytest_environment_split (pinned-v2 runner contract), test_command_portability (bans `uv run pytest` in SKILL.md) |
| Prompt/governance content | test_master_prompt_contract / _hardening / _governance, test_ascii_typography, test_repository_scope_cleanup, test_pressure_review_regressions, test_strategy_builder_v2_contract, test_v2_dex_template_policy |

## CONVENTIONS

- Import validators as a package: `from tools import check_dev_guide_sync`.
  Run pytest from the repository root; the suite relies on that import context.
- Two test populations exist. This directory runs on host Python and is fully
  static. Pinned-v2 runtime tests live in `skills/nt-dex-adapter/tests/` and
  run only through `tools/run_pinned_v2_pytest.py` (upstream venv Python,
  repository pytest options cleared); its host-Python allowlist covers exactly
  one static dex compliance module.
- Upstream-pinned tests resolve the checkout via
  `tools.upstream_baseline.default_upstream_root()` (env `NT_UPSTREAM_ROOT`,
  else XDG cache default) and scope expectations to `UPSTREAM_COMMIT`; they
  require the pinned checkout to be present locally.
- `pytest.ini` intentionally contains only `[pytest]`. Do not add repository
  pytest options; the pinned-v2 runner exists to keep them out of pinned runs
  (`-o addopts=`).
- No conftest.py: fixtures stay monkeypatch-local per module
  (pytest.MonkeyPatch), keeping modules independently runnable.

## ANTI-PATTERNS

- Never hardcode upstream commits or host paths in a test; import
  `UPSTREAM_COMMIT` / `default_upstream_root` from tools.upstream_baseline.
- Do not add `uv run pytest` or other module-unsafe invocations to skills
  content; test_command_portability fails on it.
- Do not add a tools/ validator without extending both
  `tools/check_static_quality.py` CHECKS and test_quality_gates in the same
  change.
- Do not loosen a pinned content assertion into unversioned "latest"
  expectations; version scoping to the pin is the point of the current/v2
  modules.
