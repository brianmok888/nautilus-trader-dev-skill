NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# REFERENCES

## OVERVIEW
Shared reference navigation; existing guidance retained at score 5 for snapshots, local contracts and harness evidence.

## STRUCTURE

```text
references/
|-- api_reference/     # Sphinx module pages; adapters/ and model/ navigation
|-- concepts/          # Architecture, services and trading lifecycle
|-- developer_guide/   # Upstream-derived development snapshots
|   `-- contracts/    # Canonical local contracts, not upstream snapshots
|-- g2-evidence/       # Harness-generated per-skill evidence
|-- integrations/      # Venue/provider guides with version-scoped overlays
|-- dev_templates/     # Criterion and iai Rust benchmark templates
`-- upstream-delta-review.json  # Reviewed develop changes and transition history
```

## WHERE TO LOOK

Read `concepts/overview.md`, `architecture.md`, `backtesting.md`, then `live.md` first.

| Topic | File |
|-------|------|
| BacktestEngine | `concepts/backtesting.md` |
| LiveNode | `concepts/live.md` |
| TradingNode (legacy v1 migration/reference-only routing) | `concepts/live.md` |
| Order types | `concepts/orders.md` |
| Data subscriptions | `concepts/data.md` |
| Actor system | `concepts/actors.md` |
| Cache | `concepts/cache.md` |
| Message bus | `concepts/message_bus.md` |
| Portfolio state and positions | `concepts/portfolio.md`, `concepts/positions.md` |
| Reporting | `concepts/reports.md` |
| Adapter development | `developer_guide/adapters.md` |
| Rust conventions | `developer_guide/rust.md` |
| FFI safety | `developer_guide/ffi.md` |
| Local behavior and build admission | `developer_guide/contracts/` |
| Backtest API | `api_reference/backtest.md` |
| Live API | `api_reference/live.md` |
| Model types | `api_reference/model/` |
| Venue/provider capability | `integrations/index.md`, then the venue guide |
| Current tooling workflows | `README.md` routes to `../docs/` |

## CONVENTIONS
- Shared references are symlinked into skill directories; resolve paths from the consuming skill folder.
- Examples: `references/concepts/backtesting.md`, `references/api_reference/live.md`.
- `README.md` records synchronization; `../tools/upstream_baseline.py` remains the pin authority.
- Current inspected pin: `77d785c69205c4326e6aadb46d03fb45357a78f2`; older cited commits remain historical boundaries.
- Published rc8 and unreleased rc9 develop are separate surfaces; inspect the cited source before borrowing APIs.
- Overlay top-level `deltas: []` coexists with historical `reviewed_transitions`; preserve each transition's provenance.
- Developer-guide snapshot headers identify source commits; `contracts/` holds separate local normative behavior.
- G2 records identify scope, content hash, upstream commit and command steps; interpret the recorded steps individually.
- Host checks, synchronization and documentation snapshots do not establish Rust/PyO3 runtime readiness.

## ANTI-PATTERNS
- Do not infer pinned module availability from Sphinx directives or Latest/Nightly labels; consult `api_reference/system.md` and `model/tick_scheme.md`.
- Do not use historical BitMEX pages as current adapter guidance; their headers record removal at `3adf5a8dc`.
- Do not flatten venue overlays into retained historical bodies; Polymarket explicitly marks incomplete synchronization.
- Do not mistake provider support tables, benchmark templates or recorded pass statuses for fresh runtime evidence.
