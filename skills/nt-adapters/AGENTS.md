NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-adapters

CeFi venue-adapter specification hub — the largest skill in the pack (134
files). Earned its file: score 10 (file count, subdirs, boundary, centrality);
distinct adapter domain with a reference tree the parent index does not map.

**Entry:** `SKILL.md` (665 lines, self-indexing; G0-G7 readiness gates with
pinned upstream evidence).

## WHERE TO LOOK

| Need | Location |
|------|----------|
| Per-venue wiring (Binance, Bybit, OKX, Deribit, dYdX, Hyperliquid, Kraken, Databento, Tardis, IB, Polymarket, ...) | `references/integrations/<venue>.md` (22 files; see `integrations/index.md`) |
| Authoritative adapter contract (phases, method contracts, capability gates) | `references/guides/official_adapter_spec.md` |
| Execution-client acceptance matrix | `references/guides/spec_exec_testing.md` |
| Data-client acceptance matrix | `references/guides/spec_data_testing.md` |
| Rust adapter coding rules / FFI | `references/guides/rust.md`, `references/guides/coding_standards.md`, `references/guides/ffi.md` |
| Current Rust example adapters | `references/examples/rust_adapters/` |
| Python adapter examples (migration/reference-only) | `references/examples/legacy_migration/`, `migration_reference/python/` |
| API / concepts | `references/api/`, `references/concepts/` |
| Upstream delta review + gate evidence | shared root `references/upstream-delta-review.json` and `references/g2-evidence/` |

## CONVENTIONS

- Rust core (HTTP/WS clients, parsing, signing) under `crates/adapters/<venue>/`;
  Python is the integration layer only.
- Readiness is not proven by parser/unit tests alone: document the supported
  capability matrix per venue and run the DataTester/ExecTester acceptance specs.
- Gate `Pass` statuses cite explicit commands, files, or official URLs; re-run
  the cited evidence before flipping a row.

## ANTI-PATTERNS

- Presenting `legacy_migration/` or `migration_reference/` Python as current production guidance: that Python-era material is migration/reference-only; prefer the Rust v2 lane.
- Claiming adapter readiness from unit tests while skipping the acceptance specs.
- Editing the pinned upstream developer-guide snapshot as if it were repo-owned.
