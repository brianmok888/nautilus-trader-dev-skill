---
name: nt-dev
description: "Use when setting up NautilusTrader development environment, writing code that follows project conventions, running tests, benchmarks, managing releases, or understanding FFI memory contracts."
---

NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# nt-dev

## NT V2 Rust readiness gates

This repository cutover card records the current state of this skill. For future work, re-run the cited evidence and change a row to `Pending` or `Blocked` whenever that work lacks proof; `Pass` requires an explicit command, file, or official URL.

NT v2 compatibility note: readiness-table mentions of legacy Cython/v1 and Python live TradingNode are migration/reference-only; prefer Rust v2/PyO3 and LiveNode for new work.

| Gate | Description | Status | Evidence |
| --- | --- | --- | --- |
| G0 Upstream baseline | Confirm the upstream snapshot, official docs, release tag, and local reference baseline before copying APIs. | Pass | Snapshot recorded in `tools/check_dev_guide_sync.py` as f20f8af36e0f488779d3f543a217b2d19ea2db81. |
| G1 Lane classification | Classify the work as Rust execution-critical/performance, supported Python V2 strategy/config, Python AI/advisory, or legacy. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the 34-template lane inventory and Python/Rust V2 strategy boundary tests. |
| G2 Legacy label | Label legacy Cython/v1 and Python live TradingNode guidance as migration/reference-only. | Pass | Compatibility note in this file names legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |
| G3 Rust ownership | Rust owns runtime, adapter networking/parsing, normalization, risk/execution state, and performance-sensitive paths; Python and Rust strategies remain supported V2 surfaces. | Pass | `uv run pytest -q tests/test_template_classification.py tests/test_v2_guidance_hardening.py` passed the ownership-boundary regression tests; `references/developer_guide/python.md:12-14` records upstream Python strategy support. |
| G4 NT V2 API shape | Use current NT V2/PyO3 API shapes and crate/module boundaries instead of retired APIs. | Pass | `uv run python tools/check_dev_guide_snapshot_sync.py` byte-compared all 18 guide bodies to pinned upstream f20f8af; `uv run pytest -q tests/test_v2_guidance_hardening.py` passed current API-shape regressions. |
| G5 Test evidence | Collect readiness-focused checker, targeted test, lint, or build evidence before marking implementation complete. | Pass | 2026-07-28: `uv run pytest -q --ignore=tests/test_quality_gates.py` passed 253 tests; `uv run python tools/check_dev_guide_sync.py` passed. |
| G6 Safety/compliance | Enforce fail-closed risk, deterministic ordering, fixed-point precision/overflow, secrets, async runtime, FFI, and audit boundaries. | Pass | `uv run pytest -q tests/test_dev_guide_sync.py tests/test_v2_guidance_hardening.py` passed 106 safety, runtime, FFI, legacy, and V2 boundary regressions. |
| G7 Completion report | Report changed paths, validation commands, evidence, and any Pending or Blocked readiness gates. | Pending | Final Phase 4 reconciliation, logical commit SHAs, and push evidence are recorded only after the working tree is committed and pushed. |

AI/advisory lane remains Python and off execution-critical paths; it stays asynchronous, approval gate protected, and non-authoritative for Rust production paths. Rust production paths must not depend on it for order placement, risk checks, adapter state, or live-node liveness.

Development gates: the minimum Rust compliance evidence for changed production code is `cargo fmt --check`, `cargo nextest`, `cargo clippy`, `cargo deny`, and relevant PyO3/stub regeneration checks; add Python lint/tests only for Python research/config or AI/advisory lane changes.

## What This Skill Covers

NautilusTrader **developer workflow** — environment setup, coding standards, testing, benchmarking, FFI memory contracts, documentation style, and release process.

**Scope**: Cross-cutting concerns that apply to all NautilusTrader development, regardless of domain.

## When To Use

- Setting up a development environment (uv, Rust toolchain, Cap'n Proto, IDE configs)
- Writing code that follows project conventions (formatting, naming, comments)
- Running tests (unit, integration, property-based, fuzzing, memory leak)
- Writing or running benchmarks (Criterion, iai, flamegraph)
- Understanding or modifying FFI/memory boundaries between Rust and Python
- Curating test datasets
- Writing or reviewing documentation
- Managing releases (develop/nightly/master branch model)

## When NOT To Use

- **Strategy or trading logic** → use `nt-trading`
- **Backtest configuration** → use `nt-backtest`
- **Adapter integration** → use `nt-adapters`
- **Domain model types** → use `nt-model`

## Development Environment

### Prerequisites

| Tool | Purpose | Install |
|------|---------|---------|
| **uv** | Python venv & dependency management | [docs.astral.sh/uv](https://docs.astral.sh/uv) |
| **Rust** | Core platform implementation | [rust-lang.org/tools/install](https://www.rust-lang.org/tools/install) |
| **Cap'n Proto** | Serialization schema compilation | Version pinned in `tools.toml`; install with `./scripts/install-capnp.sh` |
| **prek** | Automated formatting/linting at commit | `make install-tools`, then `prek install` |

### Initial Setup

```bash
# 1. Install all dependencies (dev + test)
uv sync --active --all-groups --all-extras
# Or: make install

# 2. Debug build (faster iteration)
make install-debug

# 3. Set up hooks with current official tooling
make install-tools
prek install
```

### Environment setup contract

Follow `references/developer_guide/contracts/environment_tooling.md` before
changing setup instructions.

For current NautilusTrader core development:

```bash
uv sync --active --all-groups --all-extras
make install-tools
prek install
```

Use `prek install` for hook installation. Keep official make target names that
still include `pre-commit`, but do not present `pre-commit install` as the
current default unless the target repository explicitly remains on legacy
pre-commit tooling.

### Environment Variables (Linux/macOS)

Required for Rust/PyO3 when using Python installed via `uv`:

```bash
# PyO3 Python interpreter path (reduces recompilation)
export PYO3_PYTHON="$PWD/.venv/bin/python"

# Linux only: uv-managed Python runtime library path
PYTHON_LIB_DIR="$("$PYO3_PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
export LD_LIBRARY_PATH="$PYTHON_LIB_DIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# Python home for Rust tests
export PYTHONHOME="$("$PYO3_PYTHON" -c 'import sys; print(sys.base_prefix)')"
```

Verify: `python -c "import sys; print(sys.executable)"` and check `$PYO3_PYTHON` / `$PYTHONHOME`.

### Cap'n Proto Installation

```bash
# Script (recommended; reads pinned version from tools.toml)
./scripts/install-capnp.sh

# Inspect pinned version used by repo tooling
bash scripts/tool-version.sh capnp

# macOS
brew install capnp
```

### Builds & Rebuilds

```bash
make build          # Release build
make build-debug    # Debug build (significantly faster)
make format         # Auto-format all code
make pre-commit     # Run full pre-commit suite
```

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new Rust-backed work.

After any changes to `.rs`, `.pyx`, or `.pxd` files, rebuild with `make build` or `make build-debug`.

### IDE Configuration

**VS Code (rust-analyzer)**: Set `VIRTUAL_ENV`, `CC=clang`, `CXX=clang++` in `rust-analyzer.cargo.extraEnv`, `check.extraEnv`, and `runnables.extraEnv`. Enable `features = "all"` and `testExplorer = true`.

**Faster builds (optional)**: Use cranelift backend on nightly toolchain. See `references/developer_guide/environment_setup.md` for the Cargo.toml patch. **Do not commit** the cranelift patch.

### Dependency Management

- Treat GitHub `develop` manifests as the authoritative baseline for package,
  crate, MSRV, and Python version ranges when this repo tracks source snapshots.
- Do not copy current version numbers into docs, runner images, or scripts when
  the manifest can be read instead. Treat `rust-toolchain.toml`, `Cargo.toml`,
  `pyproject.toml`, lockfiles, and `tools.toml` as the version sources.
- `pyproject.toml` pins uv through `required-version` and enforces the
  `exclude-newer = "3 days"` cooldown; read the actual pin with
  `scripts/uv-version.sh` instead of duplicating it in guidance.
- `[tool.uv].no-build-package` pins third-party packages to wheels; update it with `scripts/check-no-build-packages.sh` when `uv.lock` or `pyproject.toml` changes.
- Bypass cooldown only for justified urgent updates: `uv lock --exclude-newer "0 seconds"`.
- Workspace deps: use `serde = { workspace = true }` for shared deps.

## Coding Conventions

### Universal Rules (All Source Files)

- **Spaces only**, never hard tabs
- Lines **< 100 characters**; wrap thoughtfully
- **American English** spelling (`color`, `serialize`, `behavior`)

### Comment Conventions

1. One blank line above every comment block/docstring
2. **Sentence case** — capitalize first letter, rest lowercase (except proper nouns)
3. No double spaces after periods
4. Single-line comments: no trailing period (unless URL/link)
5. Multi-line comments: commas between sentences, period on final line
6. Keep comments concise — *less is more*
7. No emoji

### Formatting

- Align at next logical indent (not hanging vanity alignment)
- Closing parenthesis on new line at logical indent
- Trailing comma on multi-line parameter/argument lists

### Error Messages & Naming

- Avoid "got" — use "was", "received", "found"
- Use `e` (not `err` or `error`) for caught errors: `Err(e)`, `except SomeError as e:`
- Internal fields: abbreviations OK (`_price_prec`)
- Public API: full descriptive names (`price_precision`)
- User-facing: never abbreviate

### Rust Doc Mood → **Indicative**: "Returns a cached client."
### Python Doc Mood → **Imperative**: "Return a cached client."

### Shell Portability

- Shebang: `#!/usr/bin/env bash`
- Avoid bash 4+ features in user-facing scripts (macOS ships bash 3.2)
- Use portable alternatives: `sed -i.bak` instead of `sed -i`, `-E` instead of `-E`, etc.

### Commit Messages

- Subject ≤ 60 chars, capitalized, no trailing period
- Imperative voice ("Add feature" not "Added feature")
- Optional body under 100 char width

### Python Conventions

- **PEP-8** generally; one departure: use `is None`/`is not None` (not truthiness) for None checks
- Use truthiness for **empty collections**: `if not my_list:`
- **Type hints required** on all function/method signatures
- **PEP 604** union syntax: `Instrument | None` (not `Optional[Instrument]`)
- **NumPy docstrings** for public API
- **No docstrings** on private methods (`_prefix`) — use inline `#` comments instead
- Test naming: descriptive scenario names `test_currency_with_negative_precision_raises_overflow_error`

### Rust Conventions

- Copyright header required on all files (automated enforcement via pre-commit)
- **Cargo manifest layout**: internal crates first (alphabetical), blank line, external deps (alphabetical), blank line, optional deps
- Feature flags: `default = []`, additive, documented at crate level
- **Imports**: auto-formatted by rustfmt (std → external → local)
- **One blank line** between functions and above doc comments
- **Inline format strings**: `anyhow::bail!("Failed: {n}")` not positional
- **Fully qualify**: `anyhow::*`, `log::*`, `tokio::*` — but not Nautilus domain types
- **Error handling**: `anyhow::Result<T>` primary; `thiserror` for domain errors; `?` for propagation
- **Logging**: `log::info!`, `log::warn!` etc. — always fully qualified
- **Async**: `get_runtime().spawn()` in adapters (not `tokio::spawn()`); `#[tokio::test]` OK in tests

### NT v2 transition baseline (v1.230.0 release)

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- NautilusTrader v1.230.0 is the latest release baseline as of 2026-07-28.
  Preserve legacy Cython/v1 guidance where explicitly labelled, but target
  Rust v2 / PyO3 for new Rust-backed work only when the required engine,
  adapter, and test coverage exist.
- Upstream `develop` source label is 1.231.0 and `python/pyproject.toml` is
  `2.0.0rc2`; upstream release notes identify 2.0.0rc1 as the first public
  candidate and describe the rolling `2.0.0rcN` line before final 2.0.0.
- Rust-oriented v2.0 readiness is the default: Rust core first, PyO3 bindings
  second, Python only for user strategy/configuration and AI/advisory lanes.
- Treat v2 status as readiness-scoped rather than complete v1-equivalent
  coverage. Do not claim v2 production readiness from method presence,
  generated stubs, or partial adapter wiring alone.
- Treat `rust-toolchain.toml` as the Rust baseline. Current source alignment
  uses Rust 1.97.1; public docs may still mention 1.96.x while they catch up.
- Python v2 controller subclassing and importable controller configs are
  supported for backtest/live orchestration.
- Python v2 subclassable execution algorithms are supported for routed orders.
- Python v2 `FeeModel` and `FillModel` subclass support enables custom
  backtest models without falling back to legacy Cython extension patterns.

### Current Rust/PyO3 Deltas

NT v2 compatibility note: legacy Cython/v1 reference-only; prefer Rust v2/PyO3 for new work.

- PyO3 properties: use `#[getter]` only for cheap, side-effect-free,
  attribute-like values. Use methods for actions, mutations, I/O, arguments,
  non-trivial work, or collection clones.
- Python stubs: annotate Python-exposed Rust APIs with `pyo3-stub-gen`
  (`gen_stub_pyclass`, `gen_stub_pyclass_enum`, `gen_stub_pymethods`,
  `gen_stub_pyfunction`) and regenerate with `make py-stubs-v2`.
- PyO3 enums: do not combine the `hash` pyclass attribute with `eq_int`;
  implement manual `__hash__` returning the discriminant.
- DST-observable iteration: use `IndexMap` / `IndexSet` when iteration order
  feeds observable behavior. Use `AHashMap` / `AHashSet` for lookup-only hot
  paths, immutable `Arc<AHashMap<...>>` for read-only sharing, and `DashMap`
  for concurrent reads/writes.
- Async functions: document cancellation safety for control-plane futures.
  Use `get_runtime().block_on()` only for sync-to-async bridges outside an
  ambient Tokio runtime, such as PyO3 methods, binary entry points, dedicated
  background threads, or tests. Never use `get_runtime().block_on()` inside live `DataClient` or
  `ExecutionClient` trait method implementations; spawn work with
  `get_runtime().spawn()` and return immediately. Python-thread-sensitive tasks
  should also use `get_runtime().spawn()`.
- Generated FFI bindings and precision mode: when compiling `nautilus-model`
  with `ffi` outside the aligned feature set, include `high-precision` or set
  `HIGH_PRECISION=true`; verify generated `model.h` / `model.pxd` did not drift
  before committing FFI-related work.
- Python v2 live callback routing: Tokio worker threads must not run Python
  code during live trading. Route unavoidable Python callbacks through live
  runner event channels; do not call `Python::attach` from Tokio worker tasks.
- Fuzz targets require nightly at runtime: `rustup toolchain install nightly`.

## Testing & Benchmarking

### Rust quality gates

For Rust or PyO3 changes, keep local checks aligned with upstream developer-guide
expectations:

```bash
cargo nextest run --workspace --features "arrow,ffi,python,high-precision,streaming,defi" --cargo-profile nextest --lib --tests
cargo clippy --workspace --all-targets --features "arrow,ffi,python,high-precision,streaming,defi" -- -D warnings
cargo deny check
```

Use `rstest` fixtures for repeated Rust setup and table-style test cases; keep
fixture helpers close to the crate/module under test.


### Generated Python artifacts

After changing Python-exposed Rust surfaces (`#[pyclass]`, `#[pymethods]`,
`#[pyfunction]`, stub annotations, wrapped Rust docs, or adapter feature wiring),
run `make py-stubs-v2` and commit every generated `.pyi` file and wrapper doc
comment. The v2 stub target checks the uv version pinned by `required-version`
in `python/pyproject.toml`; follow the printed `uv self update --version ...`
hint before rerunning if local uv differs.

### Test Categories

| Category | Tool | Purpose |
|----------|------|---------|
| Unit tests | pytest / cargo nextest | Individual component correctness |
| Integration tests | pytest / cargo nextest | Cross-component interaction |
| Acceptance tests | DataTester | Live adapter data validation |
| Property-based | proptest (Rust) | Invariant verification for all valid inputs |
| Fuzzing | Custom | Malformed input resilience |
| Memory leak | Custom | FFI allocation tracking |
| Performance | pytest-benchmark / codspeed | Hot-path timing |

### Running Tests

```bash
# v1 legacy Python tests (tests/)
make pytest

# v2 Python tests (python/tests/) — uses debug Rust extension
make pytest-v2

# Rust tests
make cargo-test
# With optional features:
make cargo-test EXTRA_FEATURES="capnp hypersync"

# Performance tests
make test-performance
```

### Test Style

- **Python** (`python/tests/`): pytest-style free functions, no test classes. Use `@pytest.fixture`, `@pytest.mark.parametrize`.
- **Rust**: Use `unwrap`/`expect` freely in tests. Do not capture log output to assert on messages.
- **Waiting for async**: Use `await eventually(...)` and `wait_until_async(...)` instead of arbitrary sleeps.
- **Mocks**: Prefer hand-written stubs over `MagicMock`. Never mock the object under test.

### Property-Based Testing (proptest)

Use for: core domain types, accounting engines, matching engines, state machines.

Example invariants:
- Round-trip: `parse(to_string(value)) == value`
- Inverse: `(A + B) - B == A`
- Transitivity: `A < B and B < C → A < C`

### Benchmarking

Two frameworks:

| Framework | Measures | When to use |
|-----------|----------|-------------|
| **Criterion** | Wall-clock time with confidence intervals | End-to-end, >100ns scenarios, visual comparisons |
| **iai** | CPU instruction counts (deterministic) | Ultra-fast functions, CI regression gating |

**Directory layout**: `crates/<crate>/benches/` with `foo_criterion.rs` and `foo_iai.rs`.

```bash
cargo bench -p nautilus-core                          # Single crate
cargo bench -p nautilus-core --bench time             # Single benchmark
make cargo-ci-benches                                  # CI benches
```

**Flamegraph**: `cargo flamegraph --bench <name> -p <crate> --profile bench`

### Data Type Testing

New data types need tests at all layers: DataEngine, DataActor (Rust), PyO3 dispatch, Python Actor, Backtest client, Adapter spec. See `references/developer_guide/testing.md` and `references/developer_guide/contracts/testing_policy.md` for the full test layer matrix.

## FFI & Memory

### Core Rules

1. **Rust panics must never unwind across FFI** — wrap every `extern "C"` function in `abort_on_panic(|| { ... })`
2. **CVec lifecycle**: Rust builds `Vec<T>` → converts with `into()` (leaks allocation) → foreign code uses data → foreign code calls **type-specific drop helper** exactly once
3. **Never call drop helper twice** (double-free) and **never forget it** (memory leak)
4. **No generic `cvec_drop`** — always use type-specific helpers (`vec_drop_book_levels`, etc.)
5. **PyCapsule with destructor**: Always use `PyCapsule::new_with_destructor`, never `PyCapsule::new(..., None)`
6. **Box-backed `*_API` wrappers**: Every `*_new` must have a matching `*_drop`. Validate params before allocation.
7. **Typed CVec wrappers and Send**: never mark raw `CVec` as `Send`; wrap the
   concrete payload (for example a transparent `DataFfiCVec`) and document the
   invariant before an unsafe `Send` impl.
8. **Rust-owned CVec capsules with explicit drop**: use only type-specific
   named capsules and type-specific drop functions, validate `len <= cap`, and
   reset metadata before `Vec::from_raw_parts`.

### CVec Lifecycle

| Step | Owner | Action |
|------|-------|--------|
| 1 | Rust | Build `Vec<T>`, convert with `into()` — leaks and transfers ownership |
| 2 | Foreign | Use data while `CVec` is in scope. **Do not modify ptr/len/cap** |
| 3 | Foreign | Call type-specific drop helper **exactly once** |

### PyCapsule Pattern (Rust → Python)

```rust
let my_data = Box::new(MyStruct::new());
let ptr = Box::into_raw(my_data);
let capsule = PyCapsule::new_with_destructor(py, ptr, None, |ptr, _| {
    let _ = unsafe { Box::from_raw(ptr) };
}).expect("capsule creation failed");
```

## Test Datasets

### Categories

| Category | Size | Storage | Availability |
|----------|------|---------|-------------|
| **Small** | < 1 MB | Checked into `tests/test_data/<source>/` | Always |
| **Large** | > 1 MB | R2 bucket as Parquet | Downloaded on first use |
| **User-fetched** | Any | Local only | Manual download with user's credentials |

### Required Metadata (`metadata.json`)

| Field | Description |
|-------|-------------|
| `file` | Filename |
| `sha256` | SHA-256 hash |
| `size_bytes` | File size |
| `original_url` | Source download URL |
| `licence` | License terms |
| `added_at` | ISO 8601 timestamp |

### Storage Format

New datasets → **Nautilus Parquet** (ZSTD level 3, 1M row groups). Not raw vendor formats.

### Naming Convention

```
<source>_<instrument>_<date>_<datatype>.parquet
```

### Curation

```bash
scripts/curate-dataset.sh <slug> <filename> <download-url> <licence>
```

User-fetched datasets: commit manifest + metadata only. Tests skip cleanly when data absent.

## Release Process

### Three-Branch Model

| Branch | Purpose | Publishes |
|--------|---------|-----------|
| **`develop`** | Active development | Dev wheels to R2 |
| **`nightly`** | Pre-release testing | Alpha wheels + CLI binaries |
| **`master`** | Stable releases | PyPI, Docker, docs |

### Versioning

- Python package version in `pyproject.toml` (e.g., `1.223.0`) — drives release tag
- Rust workspace version in `Cargo.toml` (e.g., `0.53.0`) — independent

### Release Checklist

**Pre-release (on `develop`)**:
- [ ] Finalize `RELEASES.md`
- [ ] Verify versions in `pyproject.toml` and `Cargo.toml`
- [ ] All CI passes

**Release**:
- [ ] Merge `develop` → `nightly` → verify CI
- [ ] Merge `nightly` → `master`
- [ ] Verify build workflow (wheels, tag, PyPI)
- [ ] Verify docker workflow
- [ ] Verify docs rebuild

**Post-release (on `develop`)**:
- [ ] Update release date in `RELEASES.md`
- [ ] Add `---` separator
- [ ] Add next version template
- [ ] Bump `pyproject.toml` version

### Release Notes Sections

Order: Enhancements → Breaking Changes → Security → Fixes → Internal Improvements → Documentation Updates → Deprecations

Start items with: "Added", "Removed", "Renamed", "Changed", "Fixed", "Implemented", "Improved", "Upgraded"

### Docs Style

- **Admonitions**: `:::note`, `:::info`, `:::tip`, `:::warning`, `:::danger` (use sparingly)
- **Headings**: Title case for `#`, sentence case for `##` and below
- **Lists**: Hyphens (`-`), not `*` or `+`
- **Tables**: `✓` for supported, `-` for unsupported
- **Code**: backticks for inline, code blocks for multi-line
- **NumPy docstrings** for Python API docs

## References

- `references/developer_guide/environment_setup.md` — Full environment setup guide
- `references/developer_guide/coding_standards.md` — Formatting, comments, commit messages
- `references/developer_guide/rust.md` — Rust conventions summary (Cargo, features, async, attrs)
- `references/developer_guide/python.md` — Python style, type hints, docstrings
- `references/developer_guide/testing.md` — Test categories, running, style, data type test matrix
- `references/developer_guide/benchmarking.md` — Criterion, iai, flamegraph, directory layout
- `references/developer_guide/ffi.md` — CVec lifecycle, PyCapsule, abort_on_panic, ownership
- `references/developer_guide/test_datasets.md` — Dataset categories, metadata, curation workflow
- `references/developer_guide/releases.md` — Branch model, versioning, checklist, release notes
- `references/developer_guide/docs.md` — Docs types, admonitions, MDX components, style guide
- `references/developer_guide/contracts/environment_tooling.md` — Current tooling contract
