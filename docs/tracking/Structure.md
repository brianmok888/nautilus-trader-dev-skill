# Structure — nautilus-trader-dev-skill

<!-- CHARTER -->
<!-- Role: Structural wiring — skill inventory, capability matrix, reference layers, tool/test surfaces, external authority hierarchy. -->
<!-- Read when: answering "how is X connected?", "what capability does Y have?", "where does code/skill content belong?". -->
<!-- Updated when: structural wiring changed (new skill, new reference dir, new tool, new test surface, boundary shift). -->
<!-- Does NOT contain: invariants, closure evidence, per-skill behavior detail, plans. -->
<!-- Write-target rule: only update this file if structural wiring changed. -->

Review date: 2026-07-30
Cutover implementation baseline: `c2f1a5f84980a9e8b554f2e7e4559cd17436d02a`
Current reconciliation: `docs/superpowers/reports/2026-07-30-nt-v2-rust-cutover-reconciliation.md`; exact ship SHA is external-attested.

## Repo shape

- **Stack:** AI Agent Skills (Claude Code, Gemini CLI, Codex) for NautilusTrader development
- **Languages:** Markdown (skill/reference content), Python (tools, tests), Rust (skill examples/contracts)
- **Package manager:** uv (Python); tests run via `uv run pytest`
- **Lint:** ruff (`ruff.toml`)
- **NT alignment:** GitHub `develop` developer-guide snapshot with version-sensitive migration notes
- **Cutover gate shape:** 18 skills with G0-G7 cards; 143 Pass, 1 Pending, 0 Blocked (`nt-implement` G2 awaits real `capnp` generation/round trip)
- **Validation surface:** `uv run pytest -q --ignore=tests/test_quality_gates.py` and `uv run pytest -q tests/test_quality_gates.py`

## Skill inventory

| Skill                            | Purpose                                                    | Rust-first | Notes |
| -------------------------------- | ---------------------------------------------------------- | ---------- | ----- |
| `nt`                               | Entry-point router for all NautilusTrader tasks            | —          | Classifies intent, dispatches to `nt-*` skills |
| `nt-architect`                     | Architecture decomposition (Actor/Indicator/Strategy)     | yes        | Start here for new projects |
| `nt-implement`                     | Strategy/Actor/Indicator implementation                    | yes        | Templates + conventions |
| `nt-strategy-builder-rust`         | **Flagship** — production Rust strategy + LiveNode wiring  | yes        | Default for production/live-node work |
| `nt-strategy-builder`              | Python strategy workflows                                  | no         | **Migration/reference-only** — not for new work |
| `nt-evomap-integration`            | EvoMap advisory sidecar integration                        | no         | **Sole active Python lane** — advisory only, never execution authority |
| `nt-adapters`                      | Adapter development (CEX/venue)                            | yes        | Spec exec testing contract |
| `nt-dex-adapter`                   | Custom DEX adapter development                             | yes        | Has rules/ + tests/ |
| `nt-live`                          | Live trading runtime                                       | yes        | LiveNode, execution, adapters |
| `nt-backtest`                      | Backtesting                                                | yes        | Has templates/ + references/ |
| `nt-data`                          | Data handling and serialization                            | yes        | |
| `nt-model`                         | Model definitions                                          | yes        | |
| `nt-signals`                       | Signal generation                                          | yes        | Has templates/ + references/ |
| `nt-trading`                       | Trading workflows                                          | yes        | Has templates/ + references/ |
| `nt-testing`                       | Testing policies                                           | yes        | |
| `nt-review`                        | Pre-deployment code review                                 | yes        | |
| `nt-dev`                           | Development environment setup                              | yes        | |
| `nt-learn`                         | Learning curriculum                                        | yes        | Has curriculum/ |
| `brainstorming_evomap`             | EvoMap brainstorming prototypes                            | no         | Has tests/ |

## Reference layers

| Directory                                    | Contents                                              | Authority |
| -------------------------------------------- | ----------------------------------------------------- | --------- |
| `references/developer_guide/`                  | Snapshot of NT official developer guide               | Source of truth for NT API/behavior |
| `references/developer_guide/contracts/`        | Agent-actionable rules extracted from dev guide       | **Canonical** — skills must follow these |
| `references/api_reference/adapters/`           | Adapter API docs                                      | Reference |
| `references/api_reference/model/`              | Model API docs                                        | Reference |
| `references/concepts/`                         | Conceptual guides                                     | Reference |
| `references/integrations/`                     | Integration examples                                  | Reference |
| `references/dev_templates/`                    | Development templates                                 | Reference |
| `references/g2-evidence/`                      | G2 evidence against the immutable pinned NT V2 baseline | Audit trail |

### Developer-guide contracts (canonical rules)

| Contract                       | Owns                                                |
| ------------------------------ | --------------------------------------------------- |
| `adapter_contract.md`            | Adapter development rules                           |
| `design_principles.md`           | Core design principles                              |
| `environment_tooling.md`         | Environment and tooling setup                       |
| `live_runtime_contract.md`       | Live runtime rules                                  |
| `testing_policy.md`              | Testing requirements                                |

## Tool surface

| Tool                                      | Purpose                                                 |
| ----------------------------------------- | ------------------------------------------------------- |
| `tools/check_dev_guide_sync.py`             | Verify local references match NT developer guide         |
| `tools/check_dev_guide_snapshot_sync.py`    | Verify developer guide snapshot is current               |
| `tools/check_rust_trading_reference_sync.py` | Verify Rust trading references are in sync              |
| `tools/check_skill_g2_harnesses.py`         | G2 evidence harness — skills validate against the immutable pinned NT V2 baseline |
| `tools/check_upstream_freshness.py`         | Check NT upstream for newer commits since last snapshot |
| `tools/upstream_baseline.py`                | Baseline config for upstream checks                     |
| `tools/cutover_inventory.py`                | Enumerate the 18 cutover skills and lane ownership      |
| `tools/g2_owned_content.py`                 | Bind G2 evidence to complete tracked skill trees        |
| `tools/markdown_lane_contract.py`           | Enforce Rust, PyO3, migration, and source-pinned lanes  |
| `tools/run_pinned_v2_pytest.py`             | Run V2-only Python contracts in the pinned upstream env |
| `tools/template_classification.py`          | Classify Python guidance as advisory or migration-only  |

## Test surface

- **Repository suites:** final exact-SHA counts are reported by the external cutover attestation; the committed tree must pass both `uv run pytest -q --ignore=tests/test_quality_gates.py` and `uv run pytest -q tests/test_quality_gates.py` without relying on stale inventory totals.
- **Core sync/gate tests:** `test_dev_guide_sync`, `test_dev_guide_snapshot_sync`, `test_quality_gates`, `test_rust_first_end_to_end`, `test_rust_trading_reference_sync`, `test_skill_g2_harnesses`, `test_upstream_freshness`.
- **Cutover boundary tests:** `test_ai_advisory_boundary`, `test_dex_g2_harness`, `test_g2_owned_content`, `test_markdown_lane_contract`, `test_pytest_environment_split`, `test_template_classification`, `test_v2_guidance_hardening`.
- **Lint:** `uv run --with ruff ruff check .` passes.

## External authority hierarchy

When sources disagree, prefer this order:

1. NautilusTrader source code (`nautilus_core` Rust, `nautilus_trader` Python on GitHub `develop`)
2. NT official docs (nautilustrader.io/docs/latest/developer_guide)
3. `references/developer_guide/contracts/` — extracted agent-actionable rules
4. Skill SKILL.md files
5. Other reference directories

## Where content belongs

| Type of work                          | Target                              |
| ------------------------------------- | ----------------------------------- |
| New skill                             | `skills/<skill-name>/SKILL.md`       |
| Skill templates/rules                 | `skills/<skill-name>/templates/` or `rules/` |
| NT dev guide contract                 | `references/developer_guide/contracts/` |
| Sync checker                          | `tools/check_*.py`                    |
| Tests                                 | `tests/` or `skills/<skill>/tests/`   |
| Plans                                 | `docs/plans/`                         |
| Session handoffs                      | `docs/handoffs/`                      |
