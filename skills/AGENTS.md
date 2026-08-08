# SKILLS OVERVIEW

17 skills for NautilusTrader development. Use workflow skills for
architecture, implementation, wiring, and review; use domain skills for focused
NautilusTrader concepts; use developer-guide skills for setup and testing.

## WORKFLOW

Start with `nt` for task classification and routing.

```
nt-architect → nt-implement → nt-strategy-builder-rust → nt-review
                    ↓                    ↓
              domain skills       nt-dex-adapter (if DEX)
```

## SKILL INDEX

| Skill | Purpose | Entry Point |
|-------|---------|-------------|
| **nt** | Entry-point router for NautilusTrader tasks | `nt/SKILL.md` |
| **nt-architect** | Decompose systems into Actor/Indicator/Strategy architecture | `nt-architect/SKILL.md` |
| **nt-implement** | Implement components with Rust-first defaults and migration-labelled Python templates | `nt-implement/SKILL.md` |
| **nt-review** | Review code before deployment | `nt-review/SKILL.md` |
| **nt-strategy-builder** | Migration/reference-only Python backtest, paper, and live examples | `nt-strategy-builder/SKILL.md` |
| **nt-strategy-builder-rust** | Default production strategy, Rust backtest, and LiveNode path | `nt-strategy-builder-rust/SKILL.md` |
| **nt-dex-adapter** | Build custom DEX adapters | `nt-dex-adapter/SKILL.md` |
| **nt-trading** | Orders, events, positions, and portfolio concepts | `nt-trading/SKILL.md` |
| **nt-signals** | Indicators, order books, and signal analysis | `nt-signals/SKILL.md` |
| **nt-data** | Market data types, subscriptions, and catalogs | `nt-data/SKILL.md` |
| **nt-backtest** | Backtest engine, venues, actors, and fill models | `nt-backtest/SKILL.md` |
| **nt-live** | Live trading, runtime selection, adapters, reconciliation | `nt-live/SKILL.md` |
| **nt-adapters** | CeFi adapter specification and production patterns | `nt-adapters/SKILL.md` |
| **nt-model** | Instruments, identifiers, and value objects | `nt-model/SKILL.md` |
| **nt-dev** | Developer guide alignment, setup, FFI, benchmarking | `nt-dev/SKILL.md` |
| **nt-testing** | Testing policy, DataTester, ExecTester, datasets | `nt-testing/SKILL.md` |
| **nt-learn** | Structured NautilusTrader learning curriculum | `nt-learn/SKILL.md` |

## COMMON PATTERNS

### All Skills Share
- `SKILL.md` — Skill definition (description, when to use, workflow)
- `templates/` — Classified Python templates; each `.py` file must declare `# TEMPLATE_CLASSIFICATION: ...` in its header
- `references/` — API reference docs (symlinked from root `references/`)
- `rules/` — DO/DON'T rulesets (some skills)

### Template Pattern
Upstream NT V2 supports Python strategies, but this repository's stricter cutover policy classifies Python strategy templates as migration/reference-only. New strategy, config, backtest, paper, and live work routes to Rust. AI and advisory work are outside this repository.

## ANTI-PATTERNS

| Pattern | Why Bad |
|---------|---------|
| Skipping nt-architect | Unstructured codebase |
| Ignoring nt-review | Bugs in production |
| Copy-paste without understanding | Maintenance nightmare |

## WHERE TO LOOK

| I need to... | Go to |
|--------------|-------|
| Start a NautilusTrader task and choose skills | `nt/` |
| Design architecture | `nt-architect/` |
| Write a strategy | `nt-implement/` |
| Research/config backtest | Rust path via `nt-strategy-builder-rust` + `nt-backtest`; Python template is migration/reference-only |
| Production/perf live | Rust `LiveNode` path via `nt-strategy-builder-rust` + `nt-live`; Python `live_node.py` is migration/reference-only |
| Add DEX support | `nt-dex-adapter/` |
| Review before deploy | `nt-review/` |
| Check setup/tooling | `nt-dev/` |
| Check test policy | `nt-testing/` |
