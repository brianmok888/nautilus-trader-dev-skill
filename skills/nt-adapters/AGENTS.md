NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-adapters

## OVERVIEW

CeFi venue-adapter specification hub with its own reference tree. Earned its
file: score 8 (file count 3, descendant directories 2, skill configuration 1,
symbol density 2); distinct adapter domain beyond the parent index.

**Entry:** `SKILL.md` (self-indexing; G0-G7 readiness gates with pinned evidence).

## WHERE TO LOOK

| Need | Location |
|------|----------|
| Per-venue wiring (Binance, Bybit, OKX, Deribit, dYdX, Hyperliquid, Kraken, Databento, Tardis, IB, Polymarket, ...) | `references/integrations/<venue>.md`; start at `references/integrations/index.md` |
| Source-versioned adapter contract (phases, method contracts, capability gates) | `references/guides/official_adapter_spec.md` |
| Execution-client acceptance matrix | `references/guides/spec_exec_testing.md` |
| Data-client acceptance matrix | `references/guides/spec_data_testing.md` |
| Rust adapter coding rules / FFI | `references/guides/rust.md`, `references/guides/coding_standards.md`, `references/guides/ffi.md` |
| Current Rust example adapters | `references/examples/rust_adapters/` |
| Python adapter examples (migration/reference-only) | `references/examples/legacy_migration/`, `migration_reference/python/` |
| API / concepts | `references/api/`, `references/concepts/` |
| Upstream delta review + gate evidence | shared root `references/upstream-delta-review.json` and `references/g2-evidence/` |

## VERSION AND EVIDENCE BOUNDARIES

- Resolve the active pin from root `tools/upstream_baseline.py` and the reviewed
  delta record before copying APIs. Guide frontmatter records source provenance;
  integration overlays may still cite older commits and supersede history only
  within their stated scope. Neither an overlay nor an API page proves runtime support.
- Rust examples carry package, target, and feature instructions. Confirm their
  source version and venue environment before use; some execution examples select
  Live/Mainnet, and historical commands are not current runtime evidence.

## CONVENTIONS

- Rust core (HTTP/WS clients, parsing, signing) under `crates/adapters/<venue>/`;
  Python/PyO3 exposes configuration, factories, and lifecycle controls, not execution
  authority. These paths describe upstream layout; maintenance stays in this repo.
- Preserve declared fixed-point precision at parser boundaries; do not route
  discrete price or quantity values through `f64`.
- Readiness is not proven by parser/unit tests alone: document the supported
  capability matrix per venue and run the DataTester/ExecTester acceptance specs.
- Gate `Pass` statuses cite explicit commands, files, or official URLs; re-run
  the cited evidence before flipping a row. `Pending` and `Blocked` remain non-pass.
- G2 compilation establishes build evidence only; live acceptance, resilience,
  fuzz, and operational checks require their own recorded evidence.

## ANTI-PATTERNS

- Presenting `legacy_migration/` or `migration_reference/` Python as current production guidance: that Python-era material is migration/reference-only; prefer the Rust v2 lane.
- Claiming adapter readiness from unit tests while skipping the acceptance specs.
- Assuming one venue's capabilities, recovery behavior, or environment defaults
  apply to another; use that venue's version-labelled guide and acceptance subset.
- Treating migration/reference-only templates or historical placeholder APIs as
  complete adapters or validated upstream interfaces.
- Editing the pinned upstream developer-guide snapshot as if it were repo-owned.
