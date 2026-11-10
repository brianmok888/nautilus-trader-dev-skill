# tools

## OVERVIEW
Repository maintenance package: upstream pin resolution, sync/schema/governance
validators, and the pinned-v2 pytest runner. CLI-first, imported by tests/ as
a package.

Score 11: code ratio >70% (+2), `__init__.py` boundary (+2), >30 symbols (+2),
>10 imported exports (+2), >20 references to imported bindings (+3).
Distinct domain: maintenance validators and evidence orchestration. Symbol and
import counts use Python AST; LSP symbol reference centrality is unmeasured.

## WHERE TO LOOK

| Task | Module |
|---|---|
| Upstream pin | upstream_baseline.py (UPSTREAM_COMMIT, default_upstream_root, remote refs) |
| Run tests at the V2 pin | run_pinned_v2_pytest.py (upstream venv Python, `-o addopts=`, host-Python allowlist) |
| One-shot static gate | check_static_quality.py (CHECKS orchestration + G2 --check-cards) |
| Dev-guide policy | check_dev_guide_sync.py (policy, metadata and source authority) |
| Dev-guide snapshot parity | check_dev_guide_snapshot_sync.py (EXPECTED_UPSTREAM_COMMIT vs local guide) |
| Rust reference sync | check_rust_trading_reference_sync.py |
| Pin freshness | check_upstream_freshness.py (--format json delta report) |
| Legacy labelling | check_legacy_labelling.py |
| Findings ledger schema | check_findings_schema.py (validate_findings) |
| Receipt validation | check_governance_receipts.py (separate from CHECKS orchestration) |
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
  upstream venv with setup instructions, and routes only
  `skills/nt-dex-adapter/tests/test_dex_compliance.py` to host Python.
  It checks the upstream commit and clean state before selecting either interpreter.
- Run `python3 tools/check_static_quality.py` for CHECKS then G2 `--check-cards`;
  run `python3 tools/check_governance_receipts.py` separately.
- G2 `--check-cards` validates existing evidence; it does not execute fresh
  runtime steps. `write_evidence` records owned-content and upstream provenance.

## ANTI-PATTERNS

- Never recode the upstream commit locally: import from upstream_baseline;
  check_dev_guide_snapshot_sync's EXPECTED_UPSTREAM_COMMIT aliases that value.
- Keep deterministic gate coverage aligned with check_static_quality.CHECKS
  and test_quality_gates; governance receipts remain a separate explicit gate.
- Do not mutate the upstream checkout from any tool: upstream is read-only
  ground truth. Optional Rust reference compilation uses a temporary copy.
- Keep check and synchronization modes distinct; check mode must report drift
  without silently repairing it. Preserve explicit local sync/evidence writers.
