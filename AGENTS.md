# PROJECT KNOWLEDGE BASE

**Generated:** 2026-10-15
**Commit:** 329f5b3 (skills digest baseline; not independently rechecked)
**Branch:** main (working tree carries local knowledge-base updates; metadata records HEAD 329f5b3)

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
Digest-reported symbols and consumers; no LSP reference counts were supplied.

| Symbol | Type | Location | Refs | Role |
|--------|------|----------|------|------|
| `CHECKS` | Check registry | `tools/check_static_quality.py` | `tests/test_quality_gates.py` | Quality-gate inventory coupling. |
| `CUTOVER_SKILL_NAMES` | Inventory constant | `tools/cutover_inventory.py` | `validate_cutover_inventory` consumer | Pins the skill inventory. |

## CONVENTIONS
- Source authority: pinned upstream commit, reviewed develop overlay, local canonical contracts, then skill guidance/templates. Label version boundaries when they disagree.
- New production guidance uses Rust V2, PyO3, and `LiveNode`; Python-era guidance is migration/reference-only.
- Approved specifications describe stable behavior; executable skills, validators, and tests remain primary local truth.
- Upstream is read-only ground truth. Maintenance implementation belongs in this skill repository, not upstream or a downstream trading project.
- Regenerate durable G2 evidence when the pin or owned skill/test/tool content changes; evidence JSON comes from the harness, never manual edits.
- Existing skill guidance is evidence-pinned; do not trim it for a documentation reformat. New skill-local files also change owned-content hashes.

## ANTI-PATTERNS
- No invented APIs, unlabelled version mixing, or current-develop functionality represented as available at the pin.
- No Cython, v1, .pyx, or `TradingNode` references without an adjacent migration/reference-only label accepted by `check_legacy_labelling.py`.
- No upstream implementation or upstream-change preparation while executing the maintenance mission.
- Do not treat host-Python static gates as pinned-v2 runtime evidence; these are separate test populations.
- Do not claim a validator passed without inspecting successful output from the current session.

## UNIQUE STYLES
- Skills are instruction packs with YAML-frontmatter `SKILL.md` entry points, not importable runtime modules.
- The architecture, implementation, and review skills share the root reference tree by symlink; edits have cross-skill consumers.
- Adapter and signal skills carry their own reference trees; do not assume all skill references are symlinks.
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
- Full-suite gates need the pinned checkout via `NT_UPSTREAM_ROOT` or `~/.cache/nautilus-trader-dev-skill/nautilus_trader-pinned`; the digest records pin `2ceb2a9a624e174a5160c10f8188afbdd57ecb99`.
- Pinned-v2 runtime tests under `skills/nt-dex-adapter/tests/` use `tools/run_pinned_v2_pytest.py` with the upstream virtualenv Python, not the host static-suite interpreter.
- `pytest.ini` intentionally contains only `[pytest]`; do not describe repository pytest options as existing.
- Legacy Python strategy material under `skills/nt-strategy-builder/` is migration/reference-only, not the production lane.
- Do not store session handoffs, completed implementation plans, external attestations, or generated agent state in the repository.
- This root update uses only the existing root and reducer digests. Generated metadata identifies the supplied baseline, not a newly inspected checkout state.
