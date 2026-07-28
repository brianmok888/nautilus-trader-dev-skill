---
source_url: https://nautilustrader.io/docs/nightly/developer_guide/
source_repo: nautechsystems/nautilus_trader/docs/developer_guide/index.md
source_commit: f20f8af36e0f488779d3f543a217b2d19ea2db81
sync_date: 2026-07-28
target: NautilusTrader develop developer guide source snapshot
confidence: high
legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only
---

# Developer Guide

Guidance on developing and extending NautilusTrader, or contributing back to the project.

NautilusTrader uses a **Rust core with Python bindings** architecture:

- **Rust** handles networking, data parsing, order matching, and other performance-critical operations.
- **Python** provides the user-facing API for strategy development, configuration, and system integration.
- **PyO3** bridges the two, exposing Rust functionality to Python with minimal overhead.

This approach combines Python's simplicity and ecosystem with Rust's performance and memory safety.

## Contents

- [Environment Setup](environment_setup.md)
- [Design Principles](design_principles.md)
- [Coding Standards](coding_standards.md)
- [Rust](rust.md)
- [Python](python.md)
- [Testing](testing.md)
- [Test Datasets](test_datasets.md)
- [Docs Style](docs.md)
- [Markdown Style](markdown_style.md)
- [Release Notes](releases.md)
- [Release Security Architecture](release_security.md)
- [Adapters](adapters.md)
- [Data Testing Spec](spec_data_testing.md)
- [Execution Testing Spec](spec_exec_testing.md)
- [Benchmarking](benchmarking.md)
- [FFI Memory Contract](ffi.md)
- [Plugins](plugins.md)
