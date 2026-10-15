# tools

Repository maintenance package: upstream pin resolution, sync/schema/governance
validators, and the pinned-v2 pytest runner. CLI-first, imported by tests/ as
a package.

Earned by scoring (11: `__init__.py` module boundary, 100% code ratio, high
symbol density, >10 cross-module exports, 20+ test modules importing tools.*)
and a distinct domain the parent does not cover: the machinery that keeps the
skill repository honest.

## WHERE TO LOOK

| Task | Module |
|---|---|
| Upstream pin | upstream_baseline.py (UPSTREAM_COMMIT, default_upstream_root, remote refs) |
| Run tests at the V2 pin | run_pinned_v2_pytest.py (upstream venv Python, `-o addopts=`, host-Python allowlist) |
| One-shot static gate | check_static_quality.py (CHECKS orchestration + G2 --check-cards) |
| Dev-guide policy | check_dev_guide_sync.py (1,640 lines, largest module) |
| Dev-guide snapshot parity | check_dev_guide_snapshot_sync.py (EXPECTED_UPSTREAM_COMMIT vs local guide) |
| Rust reference sync | check_rust_trading_reference_sync.py |
| Pin freshness | check_upstream_freshness.py (--format json delta report) |
| Legacy labelling | check_legacy_labelling.py |
| Findings ledger schema | check_findings_schema.py (validate_findings) |
| Receipt validation | check_governance_receipts.py |
| G2 harness and ownership | check_skill_g2_harnesses.py (assert_expected_upstream, --check-cards), g2_owned_content.py |
| Markdown lane contract | markdown_lane_contract.py (lane order, Python-call ban in Rust lanes) |
| Template/skill inventory | template_classification.py + cutover_inventory.py (17-skill list, Python fence rule) |

## CONVENTIONS

- Dual execution mode is part of the API: modules are importable as
  `tools.x` and runnable as `python3 tools/x.py` (sys.path bootstrap when
  `__package__` is empty). Preserve both paths when editing.
- Entry shape: `main(argv) -> int` returning a process exit code, raised via
  `SystemExit(main())`; module top level stays side-effect free because tests
  import modules directly.
- Style: `from __future__ import annotations`, pathlib.Path, typed
  signatures, `@dataclass(frozen=True, slots=True)` result records,
  `typing.Final` tuples for constants.
- Consumers are in-repo only: tests/ imports these modules; CLI/stdout is the
  human-facing surface. No external API stability is promised.
- The pinned-v2 runner requires at least one pytest path, refuses a missing
  upstream venv with instructions (`make sync && make build-debug` in the
  pinned upstream checkout), and routes the one static dex test to host
  Python.

## ANTI-PATTERNS

- Never recode the upstream commit locally: import from upstream_baseline;
  check_dev_guide_snapshot_sync's EXPECTED_UPSTREAM_COMMIT must be bumped
  together with the pin.
- Do not add a validator outside check_static_quality.CHECKS; test_quality_gates
  pins the tuple, so wire both in the same change.
- Do not mutate the upstream checkout from any tool: upstream is read-only
  ground truth; validators only read it.
- Checkers validate and report (check_* naming); do not add repair/mutation
  behavior to them - fixes belong in the content being validated.
