# NT V2 Rust Cutover Reconciliation

## Scope and baseline

This report repeats the Phase 1 audit against the post-fix tree. NautilusTrader
latest/nightly documentation and upstream source remain authoritative. Reproducible
G2 evidence is pinned to upstream commit
`6e59fd74eaacacbb7410936f1766bd89fcce6f59` (Python V2 `2.0.0rc2`, Rust
workspace `0.61.0`, Rust toolchain `1.97.1`). Moving upstream refs are reported
separately and do not silently replace that baseline.

## Reconciled findings

### Rust conversion gaps

| Finding | Severity | Status | Post-fix evidence | Residual fix proposal |
| --- | --- | --- | --- | --- |
| New strategy, backtest, live, and production requests could route to the Python builder instead of Rust. | P0 | Closed | `skills/nt/SKILL.md:29`, `skills/nt/SKILL.md:65`, `skills/nt/SKILL.md:67`, and `README.md:77` route non-AI work to `nt-strategy-builder-rust`; `skills/nt/SKILL.md:68` preserves only the AI/advisory Python lane. | — |
| The Rust strategy guidance lacked a self-contained, compile-checked V2 path. | P0 | Closed | `skills/nt-strategy-builder-rust/SKILL.md:68` documents the current `Strategy`/`DataActor` contract; `tests/test_rust_first_end_to_end.py:130` extracts and Cargo-checks the named example against the pinned upstream. | — |
| Component registration examples used stale or nonexistent native/builtin APIs. | P1 | Closed | `skills/nt-live/references/concepts/rust.md:234` uses `add_strategy`/`add_actor`; `skills/nt-live/references/concepts/rust.md:244` limits `add_builtin_*` to bundled examples; `tests/test_v2_guidance_hardening.py:234` locks both boundaries. | — |
| Active examples contained stale crate pins, removed order subscriptions, obsolete visualization, or incomplete instrument inventory. | P1 | Closed | `tests/test_v2_guidance_hardening.py:453` rejects removed subscriptions and line 463 rejects the old `0.57` pin; `docs/visualization.md:30` uses `TearsheetConfig`/`create_tearsheet`; `skills/nt-model/SKILL.md:137` lists all 18 `InstrumentAny` variants. | — |
| DEX production guidance and retained Python migration clients could be mistaken for a production-ready adapter path. | P0 | Closed | `skills/nt-dex-adapter/SKILL.md:86` requires Rust core infrastructure, line 118 requires Rust factories through `LiveNodeBuilder`, and `skills/nt-dex-adapter/rules/compliance_checklist.md:27` bars Python-only adapters from `APPROVED FOR USE`. | — |
| Retained DEX migration templates could silently fabricate success, invalid precision, or authoritative reconciliation. | P1 | Closed | `skills/nt-dex-adapter/migration_reference/python/templates/legacy_migration/dex_exec_client.py:158` and subsequent unsupported paths fail closed; `skills/nt-dex-adapter/migration_reference/python/templates/legacy_migration/dex_data_client.py:322` rejects non-finite/non-positive and quantized-zero values; executable regressions begin at `skills/nt-dex-adapter/tests/test_legacy_migration_fail_closed.py:97`. | — |

### V2 compliance violations

| Finding | Severity | Status | Post-fix evidence | Residual fix proposal |
| --- | --- | --- | --- | --- |
| AI/EvoMap Python guidance did not mechanically exclude execution authority or synchronous hot-handler behavior. | P0 | Closed | `skills/nt-evomap-integration/SKILL.md:42` keeps Nautilus as the only execution authority and line 55 defines the non-blocking mailbox boundary; `tools/check_skill_g2_harnesses.py:775` rejects order-submission capabilities and line 848 requires authority, timeout, fallback, approval, and audit invariants. | — |
| Current V2 component, event, visualization, instrument, and crate APIs drifted from upstream. | P1 | Closed | `tests/test_v2_guidance_hardening.py:234`, `:255`, `:338`, `:453`, and `:463` enforce the corrected APIs and inventories. | — |
| The Python V2 boundary test was collected in the repository's default V1 environment. | P1 | Closed | `pytest.ini:1` isolates the pinned-only module; `tools/run_pinned_v2_pytest.py:1` clears inherited `addopts`; `tests/test_pytest_environment_split.py:1` locks both environments. | — |
| G2 FFI compiles could rewrite pinned high-precision generated bindings and invalidate provenance. | P0 | Closed | `tools/check_skill_g2_harnesses.py:204` and `:407` enable `python,ffi,high-precision`; `tests/test_skill_g2_harnesses.py:124` enforces the feature on every FFI step. | — |
| G2 readiness could pass with missing skills, empty ownership, mutable/self-referential provenance, stale commands, or dirty upstream state. | P0 | Closed | `tests/test_skill_g2_harnesses.py:15` defines exactly 18 skills; `tools/check_skill_g2_harnesses.py` rejects empty ownership and validates schema, pin, clean state, owned-content hash, and exact commands. | — |
| G2 ownership covered declared files but not the complete skill tree or in-repo symlink targets. | P0 | Closed | `tools/g2_owned_content.py:56` walks every owned tree entry, line 74 records symlink text and recursively includes in-repo targets, line 142 hashes logical paths/types/payloads, and line 159 rejects untracked owned sources; `tests/test_g2_owned_content.py` covers broken, escaping, cyclic, unsupported, and changed-content cases. | — |
| A rejected advisory decision could be approved later because audit append and decision finalization were not atomic. | P0 | Closed | `skills/nt-evomap-integration/templates/advisory_actor.py` accepts the immutable audit record before completing the request; `tests/test_ai_advisory_boundary.py` verifies rejection is terminal and a later request can proceed. | — |
| The advisory actor retained terminal request state, so the sole active Python lane accepted only one review until lifecycle reset. | P1 | Closed | `skills/nt-evomap-integration/templates/advisory_actor.py` releases request state only after an audited approval, operator rejection, late decision/result, or timeout; `tests/test_ai_advisory_boundary.py` covers sequential requests after each terminal outcome in the pinned V2 runtime. | — |
| DEX G2 ran ambient Python migration suites instead of the pinned V2 compliance contract. | P0 | Closed | `tests/test_dex_g2_harness.py:11` pins `test_dex_compliance.py` through `tools/run_pinned_v2_pytest.py` and retains Hyperliquid/blockchain Cargo checks; line 41 excludes legacy migration execution from production G2. | — |

### Legacy/unlabelled v1, Cython, or template content

| Finding | Severity | Status | Post-fix evidence | Residual fix proposal |
| --- | --- | --- | --- | --- |
| Shipped Python/Cython guidance files could appear without an exact lane classification. | P0 | Closed | `tests/test_template_classification.py:26` enumerates every shipped Python-family guidance file; `tools/template_classification.py:42` requires one exact header and line 67 requires the exact legacy classification for legacy executable signals. | — |
| Generic banners or directory placement could bless `TradingNode`, live-client/factory, Cython, or V1 executable content. | P0 | Closed | `tests/test_template_classification.py:36`, `:89`, `:128`, `:152`, and `:214` cover directory, alias, syntax-error, Cython, V1, and qualified-call bypasses; `tools/template_classification.py:65` requires the `legacy_migration` namespace. | — |
| Retained live/DEX/adapter Python executables remained in default template paths. | P1 | Closed | Retained files are quarantined under `skills/nt-adapters/templates/legacy_migration/`, `skills/nt-dex-adapter/migration_reference/python/templates/`, `skills/nt-implement/templates/legacy_migration/`, and `skills/nt-strategy-builder/templates/legacy_migration/`; `skills/nt-dex-adapter/migration_reference/python/templates/legacy_migration/dex_exec_client.py:1` shows the exact legacy header. | — |
| Markdown could contain unlabelled Cython/V1/`TradingNode` guidance or offer a legacy fallback for new production work. | P1 | Closed | `tools/check_dev_guide_sync.py:1051` scans unlabelled `TradingNode`, line 1076 scans unlabelled legacy/Cython/V1 guidance, and line 1120 rejects legacy fallbacks for new live/production work. | — |
| Ordinary non-AI Python examples and templates remained mixed into active Rust-oriented skill trees. | P0 | Closed | `skills/nt-{trading,backtest,signals,live,data,implement}/SKILL.md` expose ordered Rust, PyO3, migration, and source-pinned H2 lanes; ordinary Python is physically under each skill's `migration_reference/python/`; `tools/markdown_lane_contract.py` and `tools/template_classification.py` enforce the structure and quarantine. | — |
| Executable Python under `docs/prototypes` was outside skill-scoped lane discovery and the EvoMap network-capability boundary. | P0 | Closed | The prototype now lives under `skills/nt-evomap-integration/python_sidecar/brainstorming_evomap`; `tests/test_template_classification.py` scans repository Python outside excluded test/tool/reference surfaces, and `tools/check_skill_g2_harnesses.py` rejects network calls outside `python_sidecar`. | — |

### Improvement opportunities versus current nightly/develop

| Finding | Severity | Status | Post-fix evidence | Residual fix proposal |
| --- | --- | --- | --- | --- |
| Moving upstream changes were not distinguished from the reproducible G2 baseline. | P1 | Closed | `README.md:14` labels current-develop observations; `tools/check_upstream_freshness.py:101` reports each ref as current, drifted, or diverged without mutating the pin. | — |
| New develop-only cache, order-constructor, and backtest-result APIs were not covered or version-scoped. | P2 | Closed | `skills/nt-data/SKILL.md:107` scopes cache APIs to commit `aabb824cb`; `skills/nt-model/SKILL.md:12` scopes `OrderInitialized::new_checked`; `skills/nt-backtest/SKILL.md:56` scopes `BacktestResult.returns_series`. | — |
| Adapter execution-spec freshness versus develop was unknown. | P2 | Closed | `skills/nt-testing/SKILL.md:11` keeps `spec_exec_testing` as the measurable contract, and line 17 records that it is unchanged between the pin and current `origin/develop`. | — |
| Readiness claims were static rather than domain-scoped and content-bound. | P1 | Closed | Every `skills/nt*/SKILL.md` contains G0-G7; `tools/check_skill_g2_harnesses.py` validates targeted commands and schema-v2 evidence; `tools/g2_owned_content.py` binds evidence to complete skill trees; the artifacts live under `references/g2-evidence/`. | — |
| Gate cards embedded volatile dates and test counts that could become stale without a behavior change. | P2 | Closed | `tests/test_skill_g2_harnesses.py::test_readiness_cards_do_not_embed_volatile_test_counts` rejects dated/count-bound gate evidence; all 18 cards now cite stable commands and artifacts. | — |
| G0/G1/G3-G7 Pass rows could cite the card validator itself, circularly treating card shape and G2 provenance as proof of unrelated gates. | P0 | Closed | Every non-G2 row now cites a direct command or the reconciliation report; both `tools/check_dev_guide_sync.py` and `tools/check_skill_g2_harnesses.py` reject `--check-cards` as non-G2 Pass evidence. | — |

## Progressive gate result

- Skills: **18**
- Gates per skill: **8** (`G0` through `G7`)
- Total gate rows: **144**
- Status: **144 Pass, 0 Pending, 0 Blocked**
- Card validator: `uv run python tools/check_skill_g2_harnesses.py --check-cards`
- G2 execution: `uv run python tools/check_skill_g2_harnesses.py --execute`
- G2 durable evidence: `references/g2-evidence/*.json` (schema version 2,
  pinned upstream commit, clean-upstream flag including untracked files, exact
  successful commands, and owned content hash). G0/G1/G3-G7 rely on the direct
  command or report cited by each row rather than these G2 artifacts.

## Post-fix validation evidence

The reconciliation uses these measurable checks:

```bash
uv run pytest -q tests/test_dev_guide_sync.py -k 'legacy or cython or v1 or tradingnode'
uv run pytest -q tests/test_v2_guidance_hardening.py -k 'pyo3 or binding or rust or live_runner'
uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py -k 'lane or python or rust or current_develop'
uv run pytest -q tests/test_markdown_lane_contract.py tests/test_g2_owned_content.py tests/test_dex_g2_harness.py
uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py tests/test_rust_first_end_to_end.py -k 'safety or fail_closed or precision or overflow or secret or async or ffi or audit or legacy or cython or v1 or advisory'
uv run pytest -q --ignore=tests/test_quality_gates.py
uv run pytest -q tests/test_quality_gates.py
uv run python tools/check_dev_guide_sync.py
uv run python tools/check_dev_guide_snapshot_sync.py
uv run python tools/check_skill_g2_harnesses.py --execute
uv run python tools/check_skill_g2_harnesses.py --check-cards
```

## Residual follow-up TODO

No P0/P1 cutover implementation finding remains open. The following are
validation/maintenance follow-ups and do not change the 144 content-readiness
gate results:

1. **P2 — repository-wide static-analysis debt:** normal `uv run basedpyright`
   remains red on pre-existing dynamic/template and retained legacy integration
   surfaces. Do not claim repository-wide type-check cleanliness; reduce this
   debt in a separately scoped change rather than weakening diagnostics.
2. **P2 — moving-upstream drift:** `tools/check_upstream_freshness.py` is
   expected to return non-zero whenever a tracked ref moves beyond or diverges
   from the reproducible pin. Review the report periodically and deliberately
   choose a new baseline in a dedicated update.
3. **P2 — embedded-fence coverage:** G2 validates each skill's declared V2
   owner surface and content-binds the complete skill tree, but it does not
   independently compile every Rust fence or execute every optional prose
   command such as `nextest`, `clippy`, or `deny`. Treat such commands as
   additional project-level evidence until a future fence extractor can compile
   them without inventing missing crate context.
