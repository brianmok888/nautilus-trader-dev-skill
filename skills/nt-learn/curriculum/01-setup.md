# Stage 01: Rust-first setup and installation

## Goal

Prepare a NautilusTrader `develop` checkout for Rust V2 development, then prove
that the Rust workspace and representative Rust examples build.

## Prerequisites

- Git
- Rust stable and nightly toolchains
- Clang/LLVM for binding generation
- `uv`, because the upstream build uses an embedded Python runtime for PyO3

The Python runtime is a build dependency at the PyO3 boundary. It is not a
strategy, adapter, backtest, or live-execution lane.

## Clone the current development source

```bash
git clone --branch develop https://github.com/nautechsystems/nautilus_trader
cd nautilus_trader
```

Do not copy examples from an unrelated release into this checkout. The skill's
reproducible G2 harness compiles against its pinned upstream commit; the
freshness checker separately reviews changes on current `origin/develop` and
proves that reviewed `origin/develop` contains `origin/nightly`.

## Install toolchains

Install Rust with `rustup`, then enable formatting and linting components:

```bash
rustup toolchain install stable --component clippy,rustfmt
rustup toolchain install nightly --component clippy,rustfmt
rustc --version
cargo --version
```

Install Clang/LLVM using the official package for your operating system and
verify it:

```bash
clang --version
```

## Prepare the PyO3 build boundary

The upstream workspace uses an `uv`-managed environment for binding and mixed
workspace builds:

```bash
uv sync --all-extras
export PYO3_PYTHON="$PWD/.venv/bin/python"
```

On Linux, point the linker and embedded runtime at that environment:

```bash
PYTHON_LIB_DIR="$("$PYO3_PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("LIBDIR"))')"
export LD_LIBRARY_PATH="$PYTHON_LIB_DIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PYTHONHOME="$("$PYO3_PYTHON" -c 'import sys; print(sys.base_prefix)')"
```

These variables support compilation and PyO3 boundary tests. They do not move
execution authority out of Rust.

## Build the Rust workspace

Start with focused crates, then expand to workspace checks:

```bash
cargo check -p nautilus-core -p nautilus-model --features high-precision
cargo check -p nautilus-trading --features examples,high-precision --lib
cargo check -p nautilus-backtest --example engine-ema-cross --features examples
```

For a broader source-development gate:

```bash
make cargo-test
```

High precision is the expected Linux/macOS development path. When targeting a
platform without 128-bit support, verify the upstream platform policy rather
than silently changing numeric assumptions.

## Checkpoint

Continue to Stage 02 when:

- [ ] `rustc`, `cargo`, and `clang` are available
- [ ] the `uv` environment exists for PyO3 compilation
- [ ] the focused Rust crate checks pass
- [ ] the Rust EMA-cross backtest example compiles
- [ ] you can explain why Python is only a PyO3 build boundary here

For historical package-install and Python API onboarding, use the explicitly
labelled migration snapshot under
`skills/nt-learn/migration_reference/python/curriculum/01-setup.md`.
