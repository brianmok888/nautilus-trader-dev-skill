# PROJECT KNOWLEDGE BASE

NT v2 compatibility note: legacy/v1 removal-history items in this file are migration/release-history reference-only; prefer current Rust v2/PyO3 guidance for new work.

**Generated:** 2026-06-08
**Commit:** 618653c
**Branch:** main
**Stack:** AI Agent Skills (Claude Code, Gemini CLI, Codex) for NautilusTrader development
**NautilusTrader Alignment:** GitHub `develop` developer-guide snapshot with version-sensitive migration notes

## OVERVIEW

AI agent skills repository for building production-grade trading systems with NautilusTrader. Contains specialized skills covering architecture → implementation → integration → execution → review workflow, plus reference documentation and templates.

Current developer-guide sync status is verified by `tools/check_dev_guide_sync.py`.
Local references summarize official pages and include source metadata; skills use
canonical contracts under `references/developer_guide/contracts/` for
agent-actionable rules.

## STRUCTURE

```
nautilus-trader-dev-skill/
├── skills/                 # Specialized skills
│   ├── nt/                # Entry-point router for NautilusTrader tasks
│   ├── nt-architect/      # Architecture decomposition (Actor/Indicator/Strategy)
│   ├── nt-implement/      # Strategy/Actor/Indicator implementation
│   ├── nt-evomap-integration/ # EvoMap advisory sidecar integration
│   ├── nt-strategy-builder-rust/ # Default production strategy and LiveNode wiring
│   ├── nt-strategy-builder/ # Migration/reference-only Python strategy workflows
│   ├── nt-dex-adapter/    # Custom DEX adapter development
│   └── nt-review/         # Pre-deployment code review
├── references/            # NautilusTrader API reference docs
│   ├── api_reference/     # API documentation
│   ├── concepts/          # Conceptual guides
│   ├── developer_guide/   # Development guides
│   └── integrations/      # Integration examples
└── docs/                  # Usage guides (uv, serialization, visualization)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Start a NautilusTrader task | `skills/nt/` | Classifies intent and routes to relevant `nt-*` skills |
| Design component architecture | `skills/nt-architect/` | Start here for new projects |
| Implement Strategy/Actor | `skills/nt-implement/` | Templates + conventions |
| Production strategy or live-node work | `skills/nt-strategy-builder-rust/` | Rust strategy, backtest, and `LiveNode` paths |
| Explicit Python strategy request | `skills/nt-strategy-builder-rust/` | Repository cutover stays Rust; Python builder is migration/reference-only |
| AI/advisory work | `skills/nt-evomap-integration/` | Sole active Python lane; never execution authority |
| Build DEX adapter | `skills/nt-dex-adapter/` | 7-phase implementation |
| Review before deployment | `skills/nt-review/` | FFI/Rust/Performance checklist |
| Find API docs | `references/api_reference/` | Per-module API reference |
| Understand concepts | `references/concepts/` | backtesting, live, orders, cache |
| Adapter dev guide | `references/developer_guide/adapters.md` | Rust-first pattern |
| End-to-End Workflow | `docs/end_to_end_guide.md` | **NEW** Full walkthrough |

## SKILL WORKFLOW

```
nt (entry/router)
        │
        ▼
nt-architect → nt-implement → nt-strategy-builder-rust → nt-review
                    ↓                ↓
     nt-evomap-integration (if EvoMap)  nt-dex-adapter (if DEX)
```

**Sequence:**
1. **nt** — Start here when the task needs classification or multiple Nautilus skills
2. **nt-architect** — Decompose system into Actor/Indicator/Strategy components
3. **nt-implement** — Write individual components with templates
4. **nt-evomap-integration** — (Optional) Add governed EvoMap advisory workflow
5. **nt-strategy-builder-rust** — Default ambiguous, production, backtest, and Rust/v2 `LiveNode` strategy path
6. **nt-strategy-builder** — Use only for explicitly labelled Python migration/reference work
7. **nt-dex-adapter** — (Optional) Build custom DEX adapter
8. **nt-review** — Review before live deployment

## CONVENTIONS (PROJECT-SPECIFIC)

### Python
- Ruff linting, 100 char lines
- PEP 604 union syntax: `X | None` (not `Optional[X]`)
- NumPy docstrings, imperative mood
- Type hints required everywhere

### Rust
- `AHashMap` for hot paths
- `get_runtime().spawn()` (NEVER `tokio::spawn()` from Python threads)
- `anyhow::bail!` for errors
- `#![deny(unsafe_op_in_unsafe_fn)]`
- No box-style banner comments

### Lifecycle Rules (all components)
- `super().__init__(config)` must be first call in `__init__`
- `on_start`: load instrument from cache (null check), load models, `request_bars` then `subscribe_bars`
- `on_stop`: cancel orders, unsubscribe, cleanup state
- `on_reset`: clear buffers and state for reuse
- Never use `clock`/`logger`/`cache` in `__init__` (not yet available)

### Tooling
- `uv` for dependency management and test execution (not pip)
- `cargo nextest` for Rust tests (not cargo test)
- `msgspec.Struct` favored for high-throughput serialization
- Skills and references are markdown-first; keep guidance concise and executable

## ANTI-PATTERNS (CRITICAL)

NT v2 compatibility note: v1.x and removed-item entries in the table below are migration/release-history reference-only.
| Pattern | Consequence |
|---------|-------------|
| Panic across FFI | Undefined behavior |
| CVec double-free | Crash |
| `tokio::spawn()` from Python | Panic |
| `.clone()` in hot paths | Performance degradation |
| `.unwrap()` in production | Potential panic |
| Raw `float` for Price/Quantity | Precision loss |
| `time.sleep()` in handlers | Blocks event loop |
| Unbounded lists | Memory leak |
| `reconciliation=False` live | State drift |
| Redundant `Arc<Py<T>>` around Python callbacks | Usually unnecessary; analyze the ownership graph, use weakrefs for back-references, and release callback registrations explicitly |
| `prob_fill_on_stop` in FillModel | Deprecated — use `prob_slippage` |
| `from nautilus_trader.adapters.dydx_v4` | **Removed in v1.223.0** — use `nautilus_trader.adapters.dydx` |
| `listen_key_ping_max_failures` in Binance config | **Removed in v1.223.0** — Binance now uses WebSocket API auth |
| `subscribe_order_book_snapshots()` | **Removed in v1.223.0** — use `_subscribe_order_book_depth` |
| `Quantity - Quantity` expecting `Decimal` result | **v1.223.0**: returns `Quantity`; negative result raises `ValueError` |
| `trade_execution=True` in bar-only backtests | **v1.223.0**: default changed to `True`; set `False` explicitly for bar-only |
| `x += y` for `Price`/`Quantity`/`Money` in Rust | **v1.223.0**: `AddAssign`/`SubAssign` removed — use `x = x + y` |
| `fill_limit_at_touch` in FillModel | **v1.224.0**: Renamed to `fill_limit_inside_spread` |
| Coinbase International adapter (`COINBASE_INTX`) | **v1.224.0**: Entire package removed — use different venue |
| `InstrumentProvider.load_ids_async` override | **v1.224.0**: Now has default — only `load_all_async` required |
| Hyperliquid `builder_fee_refresh_mins` | **v1.224.0**: Config removed |
| legacy adapter environment flags | **v1.227.0**: Removed — use adapter `environment` enum; Binance/Kraken live naming is `Live` / `LIVE` |
| `time_bars_origins` | **v1.227.0**: Renamed to `time_bars_origin_offset` |
| `From<OrderInitialized>` | **v1.227.0**: Removed — use `TryFrom` / `try_into` and handle invariant errors |
| old Rust cache raw-reference assumptions | **v1.227.0**: cache accessors return scoped wrappers; use owned snapshot helpers for boundaries |

## COMMANDS

```bash
# Install dependencies
uv sync --active --all-groups --all-extras

# Build nautilus-trader
uv run --no-sync python build.py

# Python tests
make pytest
make pytest-v2

# Rust tests
make cargo-test
cargo nextest run --workspace --features 'python,ffi,high-precision,defi' --cargo-profile nextest

# Skill-specific tests
uv run pytest skills/nt-strategy-builder/tests/ -v
uv run pytest skills/nt-dex-adapter/tests/ -v
```

## NOTES

- This is a **skills repo**, not the nautilus-trader source code
- Skills are consumed by AI agents (Claude Code, Gemini CLI, Codex, etc.) via SKILL.md files
- Templates use `asyncio.run(main())` pattern (no CLI framework)
- Copyright headers: 2015-2026

## DOCUMENTATION CHARTERS AND WRITE-TARGET ROUTING

Tracker files in `docs/tracking/` are scoped to non-overlapping charters. Each file's charter is declared in an HTML comment header at the top of the file. **Never duplicate content across multiple tracking files.** Each change routes to exactly one write-target.

| File                          | Charter (owns ONLY)                                              |
| ----------------------------- | ---------------------------------------------------------------- |
| `docs/tracking/Handguard.md`  | Non-negotiable invariants ("must never" / "must always").        |
| `docs/tracking/Structure.md`  | Structural wiring: skill inventory, reference layers, tools/tests, authority hierarchy. |
| `docs/tracking/Components.md` | Per-skill detail: behavior, readiness, Rust and migration-reference signals, known gaps.  |
| `docs/tracking/Findings.md`   | Issues with IDs, closure evidence, and the append-only delta log. |

**Write-target routing rule:**

- `docs/tracking/Findings.md`: ALWAYS updated on closure (one-line delta entry under `## Delta log`).
- `docs/tracking/Handguard.md`: ONLY IF a new invariant is introduced or an existing one changes.
- `docs/tracking/Structure.md`: ONLY IF structural wiring changed (new skill, new reference dir, new tool, boundary shift).
- `docs/tracking/Components.md`: ONLY IF a skill changed (new skill, readiness shift, review update).

If a change touches more than one charter, generate one todo per write-target. Do NOT paste the same closure text into multiple files.

### Workflow tiers

Classify every task before starting. Pick the lowest tier that fits; when unsure, pick the higher tier.

- **Tier A — Trivial:** single-file fix, typo, obvious bug. Skip research/validation/todos. Edit -> verify -> one-line delta in `docs/tracking/Findings.md`.
- **Tier B — Standard:** known change, 2-3 files, clear scope, no new skills. Todos -> code -> verify -> `docs/tracking/Findings.md` delta.
- **Tier C — Uncertain:** unfamiliar skill, multi-skill change, new integration. Todos -> code -> verify -> `docs/tracking/Findings.md` delta + at most ONE scoped update to `docs/tracking/Structure.md` OR `docs/tracking/Components.md` if scope changed.
- **Tier D — Architectural:** new skill, boundary change, capability shift, anything touching `docs/tracking/Handguard.md` invariants. Full pipeline: research -> validate -> todos -> code -> verify -> all relevant files per charter.

### Plan files

- New plans live in `docs/plans/`. Filename format: `YYYY-MM-DD-kebab-case-name.md`.
- Each plan starts with YAML frontmatter: `date`, `status: draft|approved|implemented|superseded|closed`, `tier: A|B|C|D`, `write-targets` (list).
- Lifecycle: `draft` -> `approved` -> `implemented` -> `closed`. Supersession: an `implemented` or `closed` plan may be marked `superseded` by a newer plan that references it.
- When a plan closes: move it to `docs/plans/archive/`, append a delta entry to `docs/tracking/Findings.md`, and update other charter files ONLY IF their scope changed.
- Do not promote historical plans to current runtime truth.

### Handoff files

- New session handoffs live in `docs/handoffs/`. Filename format: `YYYY-MM-DD-<topic>-handoff.md`.
- One handoff per work session or work segment. Content: what was done, what's in progress, what's next, blockers, repo state.
- Handoffs are historical once superseded. Do not edit historical handoffs to look current; do not promote them to current runtime truth.
