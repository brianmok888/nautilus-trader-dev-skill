NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` references in this file are retained for migration/reference-only context. Prefer Rust v2/PyO3 guidance and `LiveNode` for new Rust-backed live work.

# Environment Tooling Contract

## Bounded builds and storage

This is local development policy, not an upstream NautilusTrader default.
Apply it before Cargo builds, tests, Clippy, benchmarks, native Python fixture
preparation, or G2 harnesses that compile upstream code. Read-only upstream
evidence caches stay read-only; compile only in an authorized writable checkout.

- Default to `CARGO_BUILD_JOBS=2`. Serialize artifact-producing commands with
  one host/workspace shared lock across agents and checkouts; separate target
  directories do not make competing builds safe. Do not increase concurrency
  incidentally. Honor a consuming project's stricter host/lock policy.
- Inventory actual allocated target bytes, Cargo home, report/source growth,
  available memory and free bytes on every affected filesystem. Keep at least
  20 GiB free in addition to an explicit workload growth allowance and safety
  margin. Bind the budget to source/locks, toolchain, profile, features, target
  and compiler overrides. Unknown or insufficient budgets refuse compilation;
  a free-space check alone is not a budget. Provision capacity rather than
  lowering the allowance to force admission.
- Use the consuming workspace's maintained admission/monitoring guard when
  present. Monitor reserve and owned process groups during the command, stop
  before the reserve is consumed, await child exit before releasing the lock,
  and retain raw output/exit status. Without a suitable guard or quota, report
  the enforcement gap rather than starting an unbounded build. A lock and
  monitor do not protect against every unrelated host writer.
- Reuse an identified compatible target and freshly built native fixtures.
  Prepare binaries and test harnesses under the same guard before Python
  tests; use their documented executable-path overrides to avoid hidden Cargo
  builds. Distinguish a normal binary from a test harness using actual artifact
  metadata or its listed tests. A boolean is not an executable path.
- For routine verification, prefer a measured `debug = "line-tables-only"`
  workspace-root profile with explicit full-debug opt-in when local variables
  are needed. Do not edit read-only upstream manifests, force a downstream
  profile, or disable incremental compilation without an independent measured
  comparison. Preserve CPU compatibility, panic behavior and optimized
  profiling evidence. Record environment overrides and their effect.
- Retain at most two explicitly owned verification generations, with an
  allocated-byte ceiling and source/profile identity. Inventory unknown/shared
  artifacts; never evict them automatically. If the ceiling would be exceeded,
  stop and propose an exact retirement manifest. Check active compilers, running
  executables, service references and deployment symlinks under the shared lock.
  Deletion requires current authorization for those exact paths; never delete
  deployed release binaries, shared environments, operator data or shared caches
  to make a build fit. Clean only owned disposable artifacts after preserving
  evidence and confirming no active use.

These instructions do not install a build guard or change Cargo settings by
themselves. Record source/lock identity, command, effective profile/features,
jobs, lock, capacity allowance, minimum sampled free space and result before
claiming a resource-bounded verification run. Pressure or a deadline is not a
reason to skip admission, coverage, or cleanup authorization.

Sources:

- `references/developer_guide/environment_setup.md`
- Official developer guide environment setup page

## Required guidance

- Use `uv` for Python environment and command execution in this skill repo.
- For NautilusTrader core setup, prefer the official latest setup path:
  `make install-tools`, pinned tools from `tools.toml`, and `prek install`.
- Do not copy current version numbers into docs, runner images, or scripts when
  a manifest-backed source can be read (`rust-toolchain.toml`, `Cargo.toml`,
  `pyproject.toml`, lockfiles, or `tools.toml`).
- Preserve command names that are still official make targets, even when they
  include the phrase `pre-commit`.
- Fuzzing requires a Rust nightly runtime (`rustup toolchain install nightly`).

## Review rule

Unqualified setup instructions that say only `pre-commit install` are stale. Use
`prek install` or explain that a legacy repository still requires pre-commit.
