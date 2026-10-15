NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-signals

Indicators, order books, bar aggregation, custom data types, portfolio
statistics, and tearsheets. Earned its file: score 13 (vendors a full Rust
crate as reference material); distinct analysis domain.

**Entry:** `SKILL.md` (271 lines; G0-G7 readiness gates with pinned evidence).

## WHERE TO LOOK

| Need | Location |
|------|----------|
| Statistics implementations (upstream Rust) | `references/rust/analysis/` — vendored analysis crate; `src/statistics/` (35 modules) with mirrored `python/statistics/` |
| Python analysis mirror (reference only) | `migration_reference/python/python/analysis/` (analyzer, tearsheet, config, themes) |
| API — portfolio, indicators, book, data, analysis | `references/api/` |
| Concepts — portfolio, data, visualization, reports | `references/concepts/` |
| Guides — indicators, custom-data patterns, serialization | `references/guides/` |
| Shared pinned developer guide (Rust production lane) | root `references/developer_guide/rust.md` |

## CONVENTIONS

- Production lane is Rust v2/PyO3; the Python `analysis` package is
  migration/reference-only.
- The vendored crate is a read-only reference snapshot: read it to port or
  verify statistics behavior; do not build it here, add it to a workspace, or
  edit it in place.

## ANTI-PATTERNS

- Treating `references/rust/analysis/` as repo code (cargo build/edit) — it is
  pinned upstream reference material.
- Presenting `migration_reference/python/python/analysis/` as current guidance.
- Introducing legacy indicator APIs in new guidance without a migration/reference-only label.
