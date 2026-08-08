# PROJECT KNOWLEDGE BASE

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material in this file is migration/reference-only; prefer Rust V2/PyO3 and `LiveNode` for current work.

## Mission

This repository contains reusable AI-agent skills for **NautilusTrader development only**. It guides architecture, implementation, testing, integration, operation, and review of NautilusTrader components. `docs/prompts/master-prompt.md` is the maintenance mission and scope authority.

Upstream NautilusTrader is read-only ground truth. Inspect its source, developer guides, examples, tests, schemas, and toolchain standards to improve this repository, but never implement or prepare upstream changes while executing the master prompt. AI, advisory, evolution-system, and downstream application work belong in separate repositories.

## Repository shape

```
nautilus-trader-dev-skill/
├── skills/                       # 17 NT development skills
│   ├── nt/                       # Entry-point router
│   ├── nt-architect/             # Architecture decomposition
│   ├── nt-implement/             # Rust-first component implementation
│   ├── nt-strategy-builder-rust/ # Production Rust strategy and LiveNode path
│   ├── nt-strategy-builder/      # Migration/reference-only Python workflows
│   ├── nt-dex-adapter/           # Custom DEX adapter development
│   └── nt-review/                # Pre-deployment review
├── references/                   # Upstream-derived NT references and contracts
├── tests/                        # Repository behavior and evidence gates
├── tools/                        # Sync, freshness, classification, and G2 validators
└── docs/                         # Current guides, prompt, and tracking charters
```

## Routing

Start with `skills/nt/SKILL.md`. It classifies the request and loads the smallest relevant skill set.

| Work | Primary skill |
| --- | --- |
| Architecture and decomposition | `nt-architect` |
| Component implementation | `nt-implement` |
| Production Rust strategies | `nt-strategy-builder-rust` |
| Backtests | `nt-backtest` |
| Live operation | `nt-live` |
| Market data and catalogs | `nt-data` |
| Orders, positions, and execution | `nt-trading`, `nt-model` |
| CeFi adapters | `nt-adapters` |
| DEX adapters | `nt-dex-adapter` |
| Signals and indicators | `nt-signals` |
| Core contribution guidance | `nt-dev`, `nt-testing` |
| Review | `nt-review` |
| Learning | `nt-learn` |

## Source authority

1. Pinned upstream commit from `tools/upstream_baseline.py` for reproducible G2 validation.
2. Reviewed current-develop delta in `references/upstream-delta-review.json` for version-scoped overlays.
3. Local canonical contracts in `references/developer_guide/contracts/`.
4. Skill guidance and templates.

When sources disagree, label the version boundary explicitly. Do not invent APIs or treat a current-develop feature as available at the pin.

## Development rules

NT v2 compatibility note: legacy Cython/v1 and Python `TradingNode` material below is migration/reference-only; use Rust V2/PyO3 and `LiveNode` for current work.

- Default new guidance to Rust V2, PyO3, and `LiveNode`.
- Label Cython/v1 and Python `TradingNode` material migration/reference-only.
- Preserve user and concurrent-agent changes; do not revert unrelated work.
- Use test-first development for behavioral changes.
- Keep files focused and avoid speculative abstractions.
- Update G2 owned-content hashes when owned skill/test/tool content changes.
- Do not modify AI or downstream-project artifacts; they are outside this repository and should not exist here.

## Validation

Run the relevant focused tests while editing, then complete:

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

A validator result is evidence only when its command exited successfully in the current work session.

## Tracking charters

- `docs/tracking/Handguard.md`: non-negotiable invariants.
- `docs/tracking/Structure.md`: current repository wiring and inventory.
- `docs/tracking/Components.md`: per-skill behavior and readiness.
- `docs/tracking/Findings.md`: current findings and closure evidence.

Do not store session handoffs, completed implementation plans, external attestations, or generated agent state in the repository.
