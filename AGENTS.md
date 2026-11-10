# PROJECT KNOWLEDGE BASE

**Generated:** 2026-11-09 (root update from reducer digests)
**Commit:** 329f5b3 (inherited root evidence baseline; current HEAD not inspected)
**Branch:** main (inherited root metadata; current branch not inspected)

## OVERVIEW
Reusable AI-agent skills for NautilusTrader development only: Rust V2, PyO3, and `LiveNode`, supported by Python validators and Markdown references. `docs/prompts/master-prompt.md` defines the maintenance mission and scope.

## STRUCTURE
```text
nautilus-trader-dev-skill/
|-- skills/       # Instruction packs; enter through nt/SKILL.md
|-- references/   # Upstream snapshots, local contracts, G2 evidence
|-- tools/        # Upstream pin, synchronization, quality and evidence gates
|-- tests/        # Host-Python repository gates; distinct from pinned runtime tests
`-- docs/         # Workflows, behavior specifications, tracking and receipts
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Route an NT request | `skills/nt/SKILL.md` | Load the smallest relevant skill set. |
| Architecture to review | `skills/nt-architect/`, `skills/nt-implement/`, `skills/nt-review/` | Workflow spine; Rust strategy work uses `skills/nt-strategy-builder-rust/`. |
| Venue adapters | `skills/nt-adapters/`, `skills/nt-dex-adapter/` | CeFi and DEX instruction boundaries. |
| Signals, data, backtests, operation | `skills/nt-signals/`, `skills/nt-data/`, `skills/nt-backtest/`, `skills/nt-live/` | Follow the router for narrower model/trading skills. |
| Trading examples and analysis snapshots | `skills/nt-trading/AGENTS.md`, `skills/nt-signals/AGENTS.md` | Domain guidance routes their own reference and migration trees. |
| Strategy-to-live workflow | `docs/end_to_end_guide.md` | Source-versioned Rust workflow; preserve its develop boundary. |
| Reproducible upstream baseline | `tools/upstream_baseline.py` | Pin authority, not the current-develop overlay. |
| Reviewed develop changes | `references/upstream-delta-review.json` | Version-scoped overlay only. |
| Canonical local contracts | `references/developer_guide/contracts/` | Distinct from upstream-derived snapshots. |
| Maintenance and test detail | `tools/AGENTS.md`, `tests/AGENTS.md` | Subtree commands and gate ownership. |
| Reference provenance | `references/AGENTS.md`, `references/README.md` | Shared content and current workflow routing. |
| Behavior-spec deltas | `docs/specs/README.md` | Implementation manifests declare deterministic `spec-deltas`, including `[]`. |
| Findings and closure | `docs/tracking/Findings.md` | Evidence-backed findings and closure. |
| Invariants, wiring, skill readiness | `docs/tracking/Handguard.md`, `Structure.md`, `Components.md` | Separate charters; do not duplicate closure content. |
| Governance evidence | `docs/tracking/receipts/` | Versioned, secret-safe JSON; priority and evidence state are independent. |

## CODE MAP
Digest-reported symbols and consumers; imported-binding counts are not LSP symbol reference counts.

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `CHECKS` | Check registry | `tools/check_static_quality.py` | `tests/test_quality_gates.py` | Deterministic checks, then G2 card checks; governance receipts run separately. |
| `CUTOVER_SKILL_NAMES` | Inventory constant | `tools/cutover_inventory.py` | `validate_cutover_inventory` consumer | Pins the skill inventory. |
| `UPSTREAM_COMMIT` | Pin constant | `tools/upstream_baseline.py` | Snapshot validator alias `EXPECTED_UPSTREAM_COMMIT` | Source pin authority; checkout state is separate. |

## CONVENTIONS
- Source authority: pinned upstream commit, reviewed develop overlay, local canonical contracts, then skill guidance/templates. Label version boundaries when they disagree.
- New production guidance uses Rust V2, PyO3, and `LiveNode`; Python-era guidance is migration/reference-only.
- Approved specifications describe stable behavior; executable skills, validators, and tests remain primary local truth.
- Upstream is read-only ground truth. Maintenance implementation belongs in this skill repository, not upstream or a downstream trading project.
- Reading `docs/prompts/master-prompt.md` does not launch its separate maintenance mission or authorize changes.
- Regenerate durable G2 evidence when the pin or owned skill/test/tool content changes; evidence JSON comes from the harness, never manual edits.
- Existing skill guidance is evidence-pinned; do not trim it for a documentation reformat. New skill-local files also change owned-content hashes.

## ANTI-PATTERNS

NT v2 compatibility note: the Cython/v1, .pyx, and TradingNode tokens below
are migration/reference-only audit targets; use Rust V2/PyO3 and LiveNode.
- No invented APIs, unlabelled version mixing, or current-develop functionality represented as available at the pin.
- No Cython, v1, .pyx, or `TradingNode` references without an adjacent migration/reference-only label accepted by `check_legacy_labelling.py`.
- No upstream implementation or upstream-change preparation while executing the maintenance mission.
- Do not treat host-Python static gates as pinned-v2 runtime evidence; these are separate test populations.
- Do not infer runtime readiness or published-release APIs from source snapshots, support tables, stored receipts, or develop review records.
- Do not claim a validator passed without inspecting successful output from the current session.

## UNIQUE STYLES
- Skills are instruction packs with YAML-frontmatter `SKILL.md` entry points, not importable runtime modules.
- The architecture, implementation, and review skills share the root reference tree by symlink; edits have cross-skill consumers.
- Adapter, signal, and trading skills carry their own reference trees; do not assume all skill references are symlinks. The copied analysis crate is read-only reference material.
- Python templates carry machine-checked `# TEMPLATE_CLASSIFICATION:` headers.

## COMMANDS
Before artifact-producing validation or G2 runs, apply
`references/developer_guide/contracts/environment_tooling.md` bounded-build
policy. Repository static Python checks do not require an upstream Rust build.

Run relevant focused checks, then the documented repository validation gates:

```bash
python3 -m pytest -q
python3 tools/check_dev_guide_sync.py
python3 tools/check_dev_guide_snapshot_sync.py
python3 tools/check_rust_trading_reference_sync.py
python3 tools/check_legacy_labelling.py
python3 tools/check_upstream_freshness.py --format json
python3 tools/check_skill_g2_harnesses.py --check-cards
python3 tools/check_governance_receipts.py
git diff --check
```

## NOTES
- Full-suite gates need the pinned checkout via `NT_UPSTREAM_ROOT` or `~/.cache/nautilus-trader-dev-skill/nautilus_trader-pinned`; source pin and checkout state are separate claims.
- Reducers report source pin and reviewed overlay header `77d785c69205c4326e6aadb46d03fb45357a78f2`, reviewed 2026-11-09. The earlier root pin `2ceb2a9a624e174a5160c10f8188afbdd57ecb99` is historical; resolve pin authority through `tools/upstream_baseline.py`.
- Published `v2.0.0rc8` at `d53849b216e20f2c122ca01b4dd0da377638b186` differs from the reported unreleased rc9 develop baseline. Preserve individual snapshot and venue-overlay commits and dates.
- The reviewed overlay has empty current `deltas` and retained historical `reviewed_transitions`; an empty current list does not erase historical evidence or prove freshness.
- `tools/run_pinned_v2_pytest.py` requires the expected clean upstream; only `skills/nt-dex-adapter/tests/test_dex_compliance.py` is host-allowlisted. Other selected runtime paths use upstream `python/.venv/bin/python`; the runner clears repository pytest options with `-o addopts=`.
- Host tests include real-binding example execution. Host-suite success, G2 card checks, stored G2 results, pinned runtime tests, adapter conformance, venue and operational evidence remain separate claims.
- `pytest.ini` intentionally contains only `[pytest]`; do not describe repository pytest options as existing.
- Legacy Python strategy material under `skills/nt-strategy-builder/` is migration/reference-only, not the production lane.
- Do not store session handoffs, completed implementation plans, external attestations, or generated agent state in the repository.
- This root update uses only the existing root and reducer digests. Metadata identifies evidence sources, not a newly inspected checkout state; no repository validator or runtime result is claimed by this guidance update.
