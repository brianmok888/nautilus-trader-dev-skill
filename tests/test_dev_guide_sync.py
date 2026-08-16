import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_dev_guide_sync as sync
from tools.check_dev_guide_sync import (
    CURRENT_DEV_GUIDE_FILES,
    CURRENT_SYNC_COMMIT,
    CURRENT_SYNC_DATE,
    CURRENT_TARGET,
    ENTRY_SKILL_ROUTING_TARGETS,
    PINNED_SNAPSHOT_LEGACY_POLICY,
    CheckResult,
    run_checks,
)


def current_metadata(name: str = "design_principles.md") -> str:
    slug = "" if name == "index.md" else name.removesuffix(".md") + "/"
    return (
        "---\n"
        f"source_url: https://nautilustrader.io/docs/latest/developer_guide/{slug}\n"
        f"source_repo: nautechsystems/nautilus_trader/docs/developer_guide/{name}\n"
        f"source_commit: {CURRENT_SYNC_COMMIT}\n"
        f"sync_date: {CURRENT_SYNC_DATE}\n"
        f"target: {CURRENT_TARGET}\n"
        "confidence: high\n"
        f"legacy_policy: {PINNED_SNAPSHOT_LEGACY_POLICY}\n"
        "---\n"
    )


def test_current_developer_guide_inventory_matches_pinned_upstream() -> None:
    assert CURRENT_DEV_GUIDE_FILES == [
        "adapters.md",
        "benchmarking.md",
        "coding_standards.md",
        "design_principles.md",
        "docs.md",
        "environment_setup.md",
        "ffi.md",
        "index.md",
        "markdown_style.md",
        "plugins.md",
        "python.md",
        "release_security.md",
        "releases.md",
        "rust.md",
        "spec_data_testing.md",
        "spec_exec_testing.md",
        "test_datasets.md",
        "testing.md",
    ]


def write_entry_skill(root: Path) -> None:
    routes = "\n".join(
        f"- `{skill_name}`" for skill_name in ENTRY_SKILL_ROUTING_TARGETS
    )
    write(
        root / "skills/nt/SKILL.md",
        "---\n"
        "name: nt\n"
        "description: Entry-point/router skill for NautilusTrader tasks.\n"
        "---\n"
        "# Entry-point/router skill\n"
        "## Source of truth\n"
        "Use nautechsystems/nautilus_trader as source.\n"
        "## Rust-oriented v2.0 readiness\n"
        "Default new work is Rust-first/PyO3/LiveNode oriented. "
        "AI/advisory lane remains Python and off execution-critical paths.\n"
        "Strategy routing is language-gated: no cross-contamination between the Python and Rust strategy builders.\n"
        f"{routes}\n",
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def readiness_gate_text(extra: str = "", *, include_ai_boundary: bool = True) -> str:
    ai_boundary = (
        "AI/advisory lane remains Python and off execution-critical paths; it stays "
        "asynchronous, approval gate protected, and non-authoritative for Rust "
        "production paths.\n"
        if include_ai_boundary
        else ""
    )
    return (
        "NT v2 compatibility note: legacy Cython/v1/TradingNode guidance in this "
        "file is retained only for migration/reference-only labelling; prefer "
        "Rust v2/PyO3 and LiveNode for new Rust-backed work.\n"
        "## NT V2 Rust readiness gates\n"
        "\n"
        "| Gate | Description | Status | Evidence |\n"
        "|---|---|---|---|\n"
        "| G0 Scope and ownership | Verify latest docs and upstream commit. | Pass | `git rev-parse HEAD` recorded in `README.md`. |\n"
        "| G1 Legacy labelling | Mark Cython, v1, and TradingNode guidance reference-only. | Pending | Awaiting `uv run python tools/check_dev_guide_sync.py`. |\n"
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pending | Awaiting upstream-backed example validation. |\n"
        "| G3 Rust bindings/PyO3 | Verify Rust bindings, PyO3 registration, callback routing, and crate paths. | Pending | Awaiting PyO3 boundary audit. |\n"
        "| G4 Functional gates | Classify Rust/Python/AI lanes and use current LiveNode, builder, and message-bus APIs. | Pending | Awaiting lane and API audit. |\n"
        "| G5 References and templates | Record command evidence before readiness is Pass. | Pending | Awaiting targeted tests. |\n"
        "| G6 Operational and migration boundaries | Enforce fail-closed risk, secrets, precision, and runtime boundaries. | Pending | Awaiting review. |\n"
        "| G7 Durable evidence | Report every gate. | Pending | Awaiting reconciliation. |\n"
        f"{ai_boundary}"
        f"{extra}"
    )


def rust_lane_text() -> str:
    return (
        "## Rust production lane\n"
        "Rust owns production behavior.\n"
        "## PyO3 control-plane lane\n"
        "PyO3 is limited to control-plane integration.\n"
        "## Migration/reference lane\n"
        "See migration_reference/python for quarantined Python guidance.\n"
        "## Source-pinned upstream lane\n"
        f"See references/developer_guide/rust.md at {CURRENT_SYNC_COMMIT}.\n"
    )


def test_reports_missing_entry_skill(tmp_path: Path) -> None:
    result = run_checks(tmp_path)

    assert result.ok is False
    assert "missing NautilusTrader entry skill: skills/nt/SKILL.md" in result.errors


def test_reports_incomplete_entry_skill_routes(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt/SKILL.md",
        "---\nname: nt\ndescription: Entry-point/router skill.\n---\n"
        "# Entry-point/router skill\n## Source of truth\n"
        "nautechsystems/nautilus_trader\n"
        "nt-trading only\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "entry skill does not route to nt-architect in skills/nt/SKILL.md"
        in result.errors
    )


def test_reports_missing_required_guide_files(tmp_path: Path) -> None:
    write(tmp_path / "references/developer_guide/index.md", "# Developer Guide\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing required guide file: references/developer_guide/design_principles.md"
        in result.errors
    )
    assert (
        "missing required guide file: references/developer_guide/spec_data_testing.md"
        in result.errors
    )
    assert (
        "missing required guide file: references/developer_guide/release_security.md"
        in result.errors
    )
    assert (
        "missing required guide file: references/developer_guide/spec_exec_testing.md"
        in result.errors
    )
    assert (
        "missing required guide file: references/developer_guide/test_datasets.md"
        in result.errors
    )


def test_reports_missing_source_metadata(tmp_path: Path) -> None:
    for relative in [
        "references/developer_guide/design_principles.md",
        "references/developer_guide/spec_data_testing.md",
        "references/developer_guide/spec_exec_testing.md",
        "references/developer_guide/test_datasets.md",
    ]:
        write(tmp_path / relative, "# Guide\n\nNo metadata here.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert any("missing source metadata" in error for error in result.errors)


def test_reports_stale_metadata_target(tmp_path: Path) -> None:
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name).replace("develop", "v1.227.0") + f"# {name}\n",
        )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert any("stale target" in error for error in result.errors)


def test_reports_stale_source_commit(tmp_path: Path) -> None:
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name).replace(CURRENT_SYNC_COMMIT, "0" * 40)
            + f"# {name}\n",
        )

    result = run_checks(tmp_path)

    assert any("stale source commit" in error for error in result.errors)


def test_current_target_tracks_github_develop_baseline() -> None:
    assert "develop" in CURRENT_TARGET
    assert "v1.227.0" not in CURRENT_TARGET


def test_ignores_omx_runtime_context(tmp_path: Path) -> None:
    write_entry_skill(tmp_path)
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name) + f"# {name}\n",
        )
    write(
        tmp_path / ".omx/context/runtime.md",
        "Historical notes may mention references/guides/spec_exec_testing.md.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "stale references/guides path in .omx/context/runtime.md" not in result.errors
    )


def test_ignores_hidden_superpowers_sdd_scratch(tmp_path: Path) -> None:
    write(
        tmp_path / ".superpowers/sdd/task-notes.md",
        "Historical notes mention references/guides/spec_exec_testing.md.\n",
    )

    result = run_checks(tmp_path)

    assert not any(".superpowers/sdd/task-notes.md" in error for error in result.errors)


def test_checks_non_sdd_superpowers_markdown(tmp_path: Path) -> None:
    write(
        tmp_path / ".superpowers/review/findings.md",
        "Use references/guides/spec_exec_testing.md.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "stale references/guides path in .superpowers/review/findings.md"
        in result.errors
    )


def test_reports_stale_references_guides_path(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Read references/guides/spec_data_testing.md before testing.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "stale references/guides path in skills/nt-testing/SKILL.md" in result.errors


def test_reports_unqualified_pre_commit_install(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-dev/SKILL.md", "Run pre-commit install during setup.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "unqualified pre-commit install in skills/nt-dev/SKILL.md" in result.errors


def test_reports_stale_capnp_version_file(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-dev/SKILL.md", "Read capnp-version before install.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "stale cap'n proto version source in skills/nt-dev/SKILL.md" in result.errors


def test_reports_imprecise_ld_library_path_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "export LD_LIBRARY_PATH=\"$(python -c 'import sys; print(sys.base_prefix)')/lib:$LD_LIBRARY_PATH\"\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "imprecise LD_LIBRARY_PATH guidance in skills/nt-dev/SKILL.md" in result.errors
    )


def test_reports_stale_uv_required_version_01112(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        'pyproject.toml pins required-version = "==0.11.12" for uv.\n',
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "stale uv required-version guidance in skills/nt-dev/SKILL.md" in result.errors
    )


def test_reports_copied_current_nautilus_version_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "Current official baseline: Python package 1.228.0, Rust crate 0.58.0.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "copied current Nautilus version guidance in skills/nt-dev/SKILL.md"
        in result.errors
    )


def test_reports_stale_nt_testing_commands(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Run pytest tests/ -v and cargo test --workspace as primary checks.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "stale pytest command in skills/nt-testing/SKILL.md" in result.errors
    assert "stale cargo test command in skills/nt-testing/SKILL.md" in result.errors


def test_reports_missing_testing_policy_deltas(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Use DataTester and ExecTester evidence.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing invariant 'DST readiness' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing dataset metadata field 'size_bytes' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing v1.227 ExecTester flag 'limit_aggressive' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing v1.227 ExecTester flag 'test_modify_rejected' in skills/nt-testing/SKILL.md"
        in result.errors
    )


def test_reports_missing_required_invariants(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-live/SKILL.md", "# Live\n")
    write(tmp_path / "skills/nt-testing/SKILL.md", "# Testing\n")
    write(tmp_path / "skills/nt-adapters/SKILL.md", "# Adapters\n")
    write(tmp_path / "skills/nt-architect/SKILL.md", "# Architect\n")
    write(tmp_path / "skills/nt-implement/SKILL.md", "# Implement\n")
    write(tmp_path / "skills/nt-backtest/SKILL.md", "# Backtest\n")
    write(tmp_path / "skills/nt-dev/SKILL.md", "# Dev\n")
    write(tmp_path / "skills/nt-dex-adapter/SKILL.md", "# DEX\n")
    write(tmp_path / "skills/nt-model/SKILL.md", "# Model\n")
    write(tmp_path / "skills/nt-review/SKILL.md", "# Review\n")
    write(tmp_path / "skills/nt-strategy-builder-rust/SKILL.md", "# Rust strat\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "missing invariant 'LiveNode' in skills/nt-live/SKILL.md" in result.errors
    assert "missing invariant 'file_config' in skills/nt-live/SKILL.md" in result.errors
    assert (
        "missing invariant 'PortfolioSnapshot' in skills/nt-live/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'DataTester' in skills/nt-testing/SKILL.md" in result.errors
    )
    assert (
        "missing invariant 'ExecTester' in skills/nt-testing/SKILL.md" in result.errors
    )
    assert (
        "missing invariant 'nautilus_network::http::HttpClient' in skills/nt-adapters/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'time_bars_origin_offset' in skills/nt-adapters/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'message immutability' in skills/nt-architect/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'crates/adapters/' in skills/nt-architect/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'V2 cutover' in skills/nt-implement/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'BacktestEngine' in skills/nt-backtest/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'cargo nextest' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'crates/adapters/' in skills/nt-dex-adapter/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'crates/model' in skills/nt-model/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'Rust-oriented v2.0 readiness' in skills/nt-review/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'pub trait Strategy' in skills/nt-strategy-builder-rust/SKILL.md"
        in result.errors
    )


def test_reports_missing_strategy_language_routing_invariants(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt/SKILL.md", "# Router\n")
    write(tmp_path / "skills/nt-implement/SKILL.md", "# Implement\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing invariant 'no cross-contamination' in skills/nt/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'no cross-contamination' in skills/nt-implement/SKILL.md"
        in result.errors
    )


def test_reports_missing_rust_strategy_runtime_shape(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder-rust/SKILL.md",
        "Rust-native strategies mention pub trait Strategy, StrategyConfig, and "
        "submit_order but omit the runtime wiring shape.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing invariant 'StrategyCore' in skills/nt-strategy-builder-rust/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'nautilus_strategy!' in skills/nt-strategy-builder-rust/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant 'impl DataActor' in skills/nt-strategy-builder-rust/SKILL.md"
        in result.errors
    )
    assert (
        "missing invariant '..Default::default()' in skills/nt-strategy-builder-rust/SKILL.md"
        in result.errors
    )


def test_reports_legacy_tradingnode_live_fallback_wording(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/SKILL.md",
        "For production live, use LiveNode or legacy Python-live TradingNode as fallback.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "legacy TradingNode fallback offered for new live/production work in "
        "skills/nt-strategy-builder/SKILL.md"
    ) in result.errors


def test_reports_generic_python_strategy_builder_routing_without_language_gate(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "README.md",
        "| Run a backtest | nt-strategy-builder |\n"
        "| Deploy live trading | nt-strategy-builder |\n",
    )
    write(
        tmp_path / "skills/nt/SKILL.md",
        "New trading system -> nt-strategy-builder\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "generic backtest/live workflow routes to Python strategy builder without "
        "language gate in README.md"
    ) in result.errors
    assert (
        "generic new trading system workflow routes to Python strategy builder without "
        "language gate in skills/nt/SKILL.md"
    ) in result.errors


def test_reports_generic_python_strategy_builder_routing_even_with_rust_mentions(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "README.md",
        "| Run a backtest | nt-strategy-builder |\n"
        "| Deploy live trading | nt-strategy-builder |\n"
        "Elsewhere, Rust production uses nt-strategy-builder-rust.\n",
    )
    write(
        tmp_path / "skills/nt/SKILL.md",
        "New trading system -> nt-strategy-builder\n"
        "Elsewhere, Rust production uses nt-strategy-builder-rust.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "generic backtest/live workflow routes to Python strategy builder without "
        "language gate in README.md"
    ) in result.errors
    assert (
        "generic new trading system workflow routes to Python strategy builder without "
        "language gate in skills/nt/SKILL.md"
    ) in result.errors


def test_reports_architect_strategy_logic_defaulting_to_python(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-architect/SKILL.md",
        "| User strategy logic, config, orchestration | **Python** | "
        "Strategy/config boundaries |\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "production/performance strategy logic defaults to Python in "
        "skills/nt-architect/SKILL.md"
    ) in result.errors


def test_reports_unlabelled_data_tester_config_new(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-adapters/references/examples/rust_adapters/example.rs",
        "let tester_config = DataTesterConfig::new(client_id, instrument_ids);\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-adapters/references/examples/rust_adapters/example.rs"
    ) in result.errors


def test_reports_missing_live_runtime_boundary_terms(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-live/SKILL.md", "Prefer LiveNode.\n")
    write(tmp_path / "skills/nt-strategy-builder/SKILL.md", "Use TradingNode.\n")
    write(tmp_path / "skills/nt-review/SKILL.md", "Review live nodes.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "missing live runtime boundary in skills/nt-live/SKILL.md" in result.errors
    assert (
        "missing live runtime boundary in skills/nt-strategy-builder/SKILL.md"
        in result.errors
    )
    assert "missing live runtime boundary in skills/nt-review/SKILL.md" in result.errors


def test_reports_retired_upstream_reference_files(tmp_path: Path) -> None:
    write(
        tmp_path / "references/integrations/coinbase_intx.md",
        "# Coinbase International\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "retired upstream reference still present: references/integrations/coinbase_intx.md"
        in result.errors
    )


def test_reports_missing_current_integration_links(tmp_path: Path) -> None:
    write(tmp_path / "references/integrations/index.md", "# Integrations\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing current integration guide link derive.md in references/integrations/index.md"
        in result.errors
    )
    assert (
        "missing current integration guide link lighter.md in references/integrations/index.md"
        in result.errors
    )
    assert (
        "missing current integration guide link coinbase.md in references/integrations/index.md"
        in result.errors
    )


def test_reports_broken_integration_guide_links(tmp_path: Path) -> None:
    write(
        tmp_path / "references/integrations/index.md",
        "| Docs |\n|---|\n| [Guide](missing.md) |\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "broken integration guide link missing.md in references/integrations/index.md"
        in result.errors
    )


def test_reports_retired_api_adapter_index_links(tmp_path: Path) -> None:
    write(
        tmp_path / "references/api_reference/adapters/index.md",
        "   coinbase_intx.md\n   mt5.md\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "retired API adapter link coinbase_intx.md in references/api_reference/adapters/index.md"
        in result.errors
    )
    assert (
        "retired API adapter link mt5.md in references/api_reference/adapters/index.md"
        in result.errors
    )


def test_reports_stale_coinbase_beta_integration_status(tmp_path: Path) -> None:
    write(
        tmp_path / "references/integrations/index.md",
        "| [Coinbase](https://coinbase.com) | `COINBASE` | CEX | "
        "![status](https://img.shields.io/badge/beta-yellow) | [Guide](coinbase.md) |\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "stale Coinbase integration status in references/integrations/index.md"
        in result.errors
    )


def test_reports_stale_coinbase_intx_strategy_builder_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/SKILL.md",
        "Nautilus ships Coinbase IntX adapters.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "stale Coinbase IntX adapter guidance in skills/nt-strategy-builder/SKILL.md"
        in result.errors
    )


def test_reports_missing_current_reference_deltas(tmp_path: Path) -> None:
    write_entry_skill(tmp_path)
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name) + f"# {name}\n",
        )

    result = run_checks(tmp_path)

    assert (
        "missing current guide delta 'Handler initialization handshake' "
        "in references/developer_guide/adapters.md" in result.errors
    )
    assert (
        "missing current guide delta 'Ambiguous outcome failures' "
        "in references/developer_guide/spec_exec_testing.md" in result.errors
    )
    assert (
        "missing current guide delta 'local prepare-failure carve-out' "
        "in references/developer_guide/spec_exec_testing.md" in result.errors
    )
    assert (
        "missing current guide delta 'CancellationToken' "
        "in references/developer_guide/adapters.md" in result.errors
    )
    assert (
        "missing current guide delta 'Trusted Publishing' "
        "in references/developer_guide/release_security.md" in result.errors
    )
    assert (
        "missing current guide delta 'Python v2 live callback routing' "
        "in references/developer_guide/python.md" in result.errors
    )
    assert (
        "missing current guide delta 'Typed CVec wrappers and Send' "
        "in references/developer_guide/ffi.md" in result.errors
    )


def test_reports_missing_current_skill_alignment_deltas(tmp_path: Path) -> None:
    write_entry_skill(tmp_path)
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name)
            + "Handler initialization handshake\n"
            + "Auth-token rotation\n"
            + "CancellationToken\n"
            + "execution-path rate-limit response\n"
            + "unknown outcome\n"
            + "idempotent\n"
            + "Ambiguous outcome failures\n"
            + "local prepare-failure carve-out\n"
            + "OrderCancelRejected\n"
            + "OrderModifyRejected\n"
            + "TC-E74\n"
            + "TC-E78\n"
            + "due_post_only=true\n"
            + "trigger-order signing expiry\n"
            + "Trusted Publishing\n"
            + "Sigstore\n"
            + "SLSA posture\n"
            + "cosign\n"
            + "Python v2 live callback routing\n"
            + "Do not call `Python::attach` from Tokio worker tasks\n"
            + "Generated FFI bindings and precision mode\n"
            + "HIGH_PRECISION=true\n"
            + "Typed CVec wrappers and Send\n"
            + "Rust-owned CVec capsules with explicit drop\n"
            + "Do not copy current version numbers\n"
            + "rustup toolchain install nightly\n"
            + "get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work.\n"
            + "Generated Python artifacts make py-stubs-v2 uv version pinned by `required-version` bon::bon try_order.\n"
            + "rust-toolchain.toml 1.97.1 2.0.0rc1 2.0.0rcN release-candidate Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
            + "arrow,ffi,python,high-precision,streaming,defi --lib --tests.\n"
            + "ExecTesterConfig::builder() StrategyConfig build()? .\n"
            + "export TAG= export REPO= gh attestation verify.\n",
        )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use nautilus_network::http::HttpClient and get_runtime().spawn().\n"
        "Never use get_runtime().block_on() inside trait method implementations.\n"
        "Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations; spawn work immediately.\n"
        "Live DataClient and ExecutionClient trait methods spawn work; get_runtime().block_on() only outside an ambient Tokio runtime, such as PyO3.\n"
        "Use time_bars_origin_offset and Binance/Kraken `Live` / `LIVE` environments.\n",
    )
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
        "Use DataTester and ExecTester evidence with limit_aggressive and test_modify_rejected.\n"
        "DST readiness uses deterministic runtime seams.\n"
        "Required dataset metadata: file sha256 size_bytes original_url licence added_at.\n",
    )
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "1.231.0 2.0.0rc1 2.0.0rcN release-candidate rust-toolchain.toml 1.97.1 "
        "Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
        "Use tools.toml for Cap'n Proto.\n"
        'PYTHON_LIB_DIR uses sysconfig.get_config_var("LIBDIR").\n',
    )

    result = run_checks(tmp_path)

    assert (
        "missing current skill delta 'SetClient' in skills/nt-adapters/SKILL.md"
        in result.errors
    )
    assert (
        "missing current skill delta 'execution-path rate-limit response' "
        "in skills/nt-adapters/SKILL.md" in result.errors
    )
    assert (
        "missing current skill delta 'TC-E74' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing current skill delta 'local prepare-failure carve-out' "
        "in skills/nt-testing/SKILL.md" in result.errors
    )
    assert (
        "missing current skill delta 'Python v2 live callback routing' "
        "in skills/nt-dev/SKILL.md" in result.errors
    )


def test_reports_missing_rust_and_adapter_compliance_terms(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-dev/SKILL.md", "Use Rust and PyO3 carefully.\n")
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use get_runtime().spawn() in adapters.\n",
    )
    write(tmp_path / "skills/nt-testing/SKILL.md", "Use ExecTester evidence.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing Rust compliance term 'cargo nextest' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing Rust compliance term 'cargo clippy' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing Rust compliance term 'cargo deny' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing Rust compliance term 'rstest' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing adapter runtime term 'Never use get_runtime().block_on() inside trait method implementations' "
        "in skills/nt-adapters/SKILL.md" in result.errors
    )
    assert (
        "missing execution testing term 'Adapter baseline matrix' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing execution testing term 'Account reconciliation matrix' in skills/nt-testing/SKILL.md"
        in result.errors
    )


def test_reports_missing_runtime_boundary_contracts(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "Adapter sync-to-async bridges should use get_runtime().block_on().\n"
        "Run Rust checks with cargo nextest, cargo clippy, cargo deny, and rstest.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use get_runtime().spawn(). Never use get_runtime().block_on() "
        "inside trait method implementations.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing Rust compliance contract 'block_on boundary' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing adapter runtime contract 'block_on boundary' in skills/nt-adapters/SKILL.md"
        in result.errors
    )


def test_reports_runtime_boundary_without_canonical_negative_phrase(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-implement/SKILL.md",
        "Use get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3. "
        "Mention DataClient and ExecutionClient and spawn, but without the canonical warning.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing adapter runtime contract 'block_on canonical warning' "
        "in skills/nt-implement/SKILL.md" in result.errors
    )


def test_reports_runtime_boundary_terms_scattered_across_paragraphs(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-implement/SKILL.md",
        "Never use vague runtime guidance without a local reason.\n\n"
        "get_runtime().block_on() can appear in a historical note.\n\n"
        "inside live systems, DataClient behavior matters.\n\n"
        "ExecutionClient trait method implementations should spawn work.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing adapter runtime contract 'block_on canonical warning' "
        "in skills/nt-implement/SKILL.md" in result.errors
    )


def test_reports_missing_execution_testing_contract_details(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Use DataTester and ExecTester evidence. limit_aggressive "
        "test_modify_rejected DST readiness "
        "file sha256 size_bytes original_url licence added_at TC-E74 TC-E78 "
        "local prepare-failure carve-out OrderCancelRejected OrderModifyRejected "
        "due_post_only=true trigger-order signing expiry.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing execution testing contract 'ExecTester baseline and reconciliation' "
        "in skills/nt-testing/SKILL.md" in result.errors
    )


def test_contract_checks_accept_markdown_wrapped_terms(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "cargo nextest cargo clippy cargo deny rstest.\n"
        "Use block_on only outside an ambient\n"
        "Tokio runtime with PyO3. Never use it in DataClient or\n"
        "ExecutionClient trait methods; spawn work instead.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "nautilus_network::http::HttpClient get_runtime().spawn() "
        "time_bars_origin_offset `Live` / `LIVE`.\n"
        "Never use\n"
        "get_runtime().block_on() inside trait method implementations.\n"
        "DataClient and ExecutionClient paths spawn work; block_on is only valid "
        "outside an ambient Tokio runtime such as PyO3.\n",
    )
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "DataTester ExecTester limit_aggressive test_modify_rejected DST readiness.\n"
        "file sha256 size_bytes original_url licence added_at.\n"
        "Adapter baseline matrix Account reconciliation matrix.\n"
        "ExecTester groups 1–5 and capability matrix after DataTester.\n"
        "unknown outcomes stay non-terminal; reconcile balances, open orders, "
        "fills, positions, and startup\n"
        "state. TC-E74 TC-E78 local prepare-failure carve-out OrderCancelRejected "
        "OrderModifyRejected due_post_only=true trigger-order signing expiry.\n",
    )

    result = run_checks(tmp_path)

    assert not any(
        "Rust compliance contract 'block_on boundary'" in e for e in result.errors
    )
    assert not any("adapter runtime term" in e for e in result.errors)
    assert not any(
        "adapter runtime contract 'block_on boundary'" in e for e in result.errors
    )
    assert not any(
        "execution testing contract 'ExecTester baseline and reconciliation'" in e
        for e in result.errors
    )


def test_reports_adapter_adjacent_block_on_boundary_drift(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-implement/SKILL.md",
        "Use get_runtime().block_on() for sync-to-async bridges.\n",
    )
    write(
        tmp_path / "skills/nt-dex-adapter/rules/dos_and_donts.md",
        "Async call goes to Rust client via get_runtime().block_on().\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing adapter runtime contract 'block_on boundary' in skills/nt-implement/SKILL.md"
        in result.errors
    )
    assert (
        "missing adapter runtime contract 'block_on boundary' "
        "in skills/nt-dex-adapter/rules/dos_and_donts.md" in result.errors
    )


def test_reports_reference_block_on_boundary_drift(tmp_path: Path) -> None:
    write(
        tmp_path / "references/developer_guide/rust.md",
        "Use get_runtime().block_on() for sync-to-async bridges.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/references/guides/rust.md",
        "Use get_runtime().block_on() for sync-to-async bridges.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing adapter runtime contract 'block_on boundary' "
        "in references/developer_guide/rust.md" in result.errors
    )
    assert (
        "missing adapter runtime contract 'block_on boundary' "
        "in skills/nt-adapters/references/guides/rust.md" in result.errors
    )


def test_reports_latest_upstream_alignment_deltas(tmp_path: Path) -> None:
    write(
        tmp_path / "references/developer_guide/rust.md", "Generated Python artifacts.\n"
    )
    write(
        tmp_path / "references/developer_guide/testing.md",
        "cargo nextest run --workspace.\n",
    )
    write(
        tmp_path / "references/developer_guide/spec_exec_testing.md",
        "ExecTesterConfig::new(...).\n",
    )
    write(
        tmp_path / "references/developer_guide/release_security.md",
        "Fish-compatible example.\n",
    )
    write(tmp_path / "skills/nt-dev/SKILL.md", "Run Rust checks.\n")
    write(tmp_path / "skills/nt-testing/SKILL.md", "Use ExecTesterConfig.\n")
    write(tmp_path / "skills/nt-review/SKILL.md", "Review generated stubs.\n")
    write(tmp_path / "skills/nt-data/SKILL.md", "Use order_owned.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing latest upstream delta 'arrow,ffi,python,high-precision,streaming,defi' "
        "in references/developer_guide/testing.md" in result.errors
    )
    assert (
        "missing latest upstream delta 'ExecTesterConfig::builder()' "
        "in references/developer_guide/spec_exec_testing.md" in result.errors
    )
    assert (
        "missing latest upstream delta 'export TAG=' "
        "in references/developer_guide/release_security.md" in result.errors
    )
    assert (
        "missing latest skill alignment 'make py-stubs-v2' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing latest skill alignment 'ExecTesterConfig::builder()' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing latest skill alignment 'Generated Python artifacts' in skills/nt-review/SKILL.md"
        in result.errors
    )
    assert (
        "missing latest skill alignment 'try_order' in skills/nt-data/SKILL.md"
        in result.errors
    )


def test_reports_unlabelled_tradingnode_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/templates/live_node.py",
        "from nautilus_trader.live.node import TradingNode\n"
        "node = TradingNode(config=config)\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-strategy-builder/templates/live_node.py" in result.errors
    )


def test_accepts_labelled_tradingnode_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/templates/live_node.py",
        "NT v2 compatibility note: Python live/integration-specific "
        "TradingNode example; for Rust v2 / Rust-backed work use LiveNode.\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "node = TradingNode(config=config)\n",
    )

    result = run_checks(tmp_path)

    assert not any("unlabelled TradingNode guidance" in e for e in result.errors)


def test_reports_unlabelled_tradingnode_guidance_in_docs(tmp_path: Path) -> None:
    write(
        tmp_path / "docs" / "end_to_end_guide.md",
        "Enable Redis/Postgres in TradingNodeConfig to save state.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled TradingNode guidance in docs/end_to_end_guide.md"
        in result.errors
    )


def test_ignores_superpowers_meta_docs(tmp_path: Path) -> None:
    write(
        tmp_path / "docs" / "superpowers" / "plans" / "migration.md",
        "Treat nautilus_trader.live.node.TradingNode as legacy v1.\n",
    )

    result = run_checks(tmp_path)

    assert not any(
        "unlabelled TradingNode guidance" in e
        for e in result.errors
    )


def test_reports_unlabelled_legacy_cython_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/references/guides/ffi.md",
        "Expose this type through Cython and update the .pyx wrapper.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-dev/references/guides/ffi.md" in result.errors
    )


def test_reports_unlabelled_cython_language_constructs(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-data/templates/wrangler.py",
        "cimport nautilus_trader.model.objects as objects\n"
        "cdef class RustBypassWrangler:\n"
        "    cpdef object handle(self, object item):\n"
        "        return item\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-data/templates/wrangler.py" in result.errors
    )


def test_reports_unlabelled_legacy_guidance_in_rust_references(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-adapters/references/examples/rust_adapter.rs",
        "let config = ExecTesterConfig::new(strategy_id, instrument_id, client_id, qty);\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-adapters/references/examples/rust_adapter.rs" in result.errors
    )


def test_accepts_labelled_legacy_guidance_in_rust_references(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-adapters/references/examples/rust_adapter.rs",
        "// NT v2 compatibility note: migration/reference-only legacy constructor; "
        "prefer ExecTesterConfig::builder() for new Rust examples.\n"
        "let config = ExecTesterConfig::new(strategy_id, instrument_id, client_id, qty);\n",
    )

    result = run_checks(tmp_path)

    assert not any("unlabelled legacy/Cython/v1 guidance" in e for e in result.errors)


def test_accepts_locally_labelled_legacy_reference_block(tmp_path: Path) -> None:
    write(
        tmp_path / "references/developer_guide/ffi.md",
        "NT v2 compatibility note: legacy Cython/v1 references are retained "
        "for migration/reference-only context; prefer Rust v2 PyO3 guidance "
        "when exposing this type through Cython and updating the .pyx wrapper.\n",
    )

    result = run_checks(tmp_path)

    assert not any("unlabelled legacy/Cython/v1 guidance" in e for e in result.errors)


def test_reports_later_unlabelled_guidance_after_reference_header(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "references/developer_guide/ffi.md",
        "NT v2 compatibility note: legacy Cython/v1 references are retained "
        "for migration/reference-only context; prefer Rust v2 PyO3 guidance.\n\n"
        "General FFI overview without actionable legacy terms.\n\n"
        "Expose this type through Cython and update the .pyx wrapper.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled legacy/Cython/v1 guidance in references/developer_guide/ffi.md"
        in result.errors
    )


def test_ignores_non_core_legacy_and_version_mentions(tmp_path: Path) -> None:
    write(
        tmp_path / "references/concepts/positions.md",
        "Legacy systems may export data under dataset path v1/my-dataset; "
        "Tardis exposes /v1/exchanges for metadata.\n",
    )

    result = run_checks(tmp_path)

    assert not any("unlabelled legacy/Cython/v1 guidance" in e for e in result.errors)




def test_ignores_hyper_util_client_legacy_logging_paths(tmp_path: Path) -> None:
    write(
        tmp_path / "references" / "concepts" / "logging.md",
        "```\n"
        "2026-01-24T05:51:42.809619000Z [DEBUG] "
        "hyper_util::client::legacy::connect::http: connecting to 104.18.5.240:443\n"
        "2026-01-24T05:51:42.810543000Z [DEBUG] "
        "hyper_util::client::legacy::pool: pooling idle connection for "
        '("https", api.example.com)\n'
        "```\n",
    )

    errors = run_checks(tmp_path).errors

    assert not any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_reports_unlabelled_generic_legacy_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills" / "nt-testing" / "SKILL.md",
        "# Skill\n\nCopy the legacy adapter template when building a new venue.\n",
    )

    errors = run_checks(tmp_path).errors

    assert any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_reports_unlabelled_tradingnode_guidance_in_root_agents(tmp_path: Path) -> None:
    write(tmp_path / "AGENTS.md", "Use Python TradingNode for live work.\n")

    errors = run_checks(tmp_path).errors

    assert "unlabelled TradingNode guidance in AGENTS.md" in errors


def test_reports_unlabelled_v1_runtime_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills" / "nt-testing" / "SKILL.md",
        "# Skill\n\nUse the v1 runtime adapter template for new venues.\n",
    )

    errors = run_checks(tmp_path).errors

    assert any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_allows_api_v1_paths_in_current_adapter_docs(tmp_path: Path) -> None:
    write(
        tmp_path / "references" / "integrations" / "venue.md",
        "| `GET /api/v1/orders` | Adapter paginates current exchange orders. |\n",
    )

    errors = run_checks(tmp_path).errors

    assert not any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_reports_unlabelled_exec_tester_config_new(tmp_path: Path) -> None:
    write(
        tmp_path / "references" / "developer_guide" / "spec_exec_testing.md",
        "# Spec Exec Testing\n\n"
        "```rust\n"
        "let config = ExecTesterConfig::new(StrategyConfig::default());\n"
        "```\n",
    )

    errors = run_checks(tmp_path).errors

    assert any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_primary_adapter_template_must_be_rust_first(tmp_path: Path) -> None:
    write(
        tmp_path / "skills" / "nt-adapters" / "templates" / "exchange.py",
        "# Default Python DataClient and ExecClient factory for TradingNode.\n",
    )

    errors = run_checks(tmp_path).errors

    assert any("not Rust-first" in error for error in errors)


def test_primary_adapter_template_accepts_rust_first_livenode_boundary(tmp_path: Path) -> None:
    write(
        tmp_path / "skills" / "nt-adapters" / "templates" / "exchange.py",
        "# Rust-first adapter template\n"
        "# Rust core + PyO3 bindings with LiveNode Python control-plane wiring.\n"
        "# TradingNode is legacy/reference-only and not the default.\n",
    )

    errors = run_checks(tmp_path).errors

    assert not any("not Rust-first" in error for error in errors)


def test_source_sync_metadata_reports_stale_snapshot() -> None:
    errors: list[str] = []

    sync._check_source_sync_metadata(
        errors,
        current_date="2026-07-09",
        sync_date="2026-06-08",
        stale_after_days=14,
    )

    assert any("Source baseline snapshot is stale" in error for error in errors)


def test_source_sync_metadata_accepts_recent_snapshot() -> None:
    errors: list[str] = []

    sync._check_source_sync_metadata(
        errors,
        current_date="2026-07-09",
        sync_date="2026-07-08",
        stale_after_days=14,
    )

    assert errors == []

def test_file_level_legacy_label_does_not_exempt_later_guidance(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/templates/live_node.py",
        "# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode\n"
        "# references in this file are retained for migration/reference-only context.\n"
        "# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.\n\n"
        "# General setup text.\n\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "node = TradingNode(config=config)\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-strategy-builder/templates/live_node.py" in result.errors
    )


def test_legacy_migration_path_does_not_exempt_unlabelled_guidance(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-example/legacy_migration/example.py",
        "from nautilus_trader.live.node import TradingNode\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-example/legacy_migration/example.py" in result.errors
    )


def test_adapter_example_legacy_migration_path_needs_exact_header(
    tmp_path: Path,
) -> None:
    write(
        tmp_path
        / "skills/nt-adapters/references/examples/legacy_migration/venue/node.py",
        "from nautilus_trader.live.node import TradingNode\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-adapters/references/examples/legacy_migration/venue/node.py"
        in result.errors
    )


def test_block_local_note_only_labels_adjacent_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-example/SKILL.md",
        "NT v2 compatibility note: legacy Cython example; use PyO3 for new work.\n\n"
        "Use cdef only while migrating this example.\n\n"
        "Current setup.\n\n"
        "Use cpdef for this later executable block.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled legacy/Cython/v1 guidance in skills/nt-example/SKILL.md"
        in result.errors
    )


def test_source_pinned_snapshot_policy_labels_upstream_legacy_content(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "references/developer_guide/testing.md",
        current_metadata("testing.md")
        + "# Testing\n\nUpstream still documents a Cython v1 example.\n",
    )

    errors = run_checks(tmp_path).errors

    assert not any(
        error
        == "unlabelled legacy/Cython/v1 guidance in references/developer_guide/testing.md"
        for error in errors
    )


def test_source_pinned_snapshot_missing_file_level_legacy_policy_fails(
    tmp_path: Path,
) -> None:
    metadata = current_metadata("testing.md").replace(
        f"legacy_policy: {PINNED_SNAPSHOT_LEGACY_POLICY}\n",
        "",
    )
    write(
        tmp_path / "references/developer_guide/testing.md",
        metadata + "# Testing\n\nUpstream still documents a Cython v1 example.\n",
    )

    errors = run_checks(tmp_path).errors

    assert (
        "missing pinned snapshot legacy policy in references/developer_guide/testing.md"
        in errors
    )
    assert (
        "unlabelled legacy/Cython/v1 guidance in references/developer_guide/testing.md"
        in errors
    )


def test_source_pinned_snapshot_body_legacy_policy_is_not_file_metadata(
    tmp_path: Path,
) -> None:
    metadata = current_metadata("testing.md").replace(
        f"legacy_policy: {PINNED_SNAPSHOT_LEGACY_POLICY}\n",
        "",
    )
    write(
        tmp_path / "references/developer_guide/testing.md",
        metadata
        + "# Testing\n\n"
        + f"legacy_policy: {PINNED_SNAPSHOT_LEGACY_POLICY}\n\n"
        + "Upstream still documents a Cython v1 example.\n",
    )

    errors = run_checks(tmp_path).errors

    assert (
        "missing pinned snapshot legacy policy in references/developer_guide/testing.md"
        in errors
    )
    assert (
        "unlabelled legacy/Cython/v1 guidance in references/developer_guide/testing.md"
        in errors
    )


def test_replacement_terms_alone_do_not_label_legacy_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/references/guides/ffi.md",
        "Expose this type through Cython; compare with PyO3 before choosing.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-dev/references/guides/ffi.md" in result.errors
    )


def test_replacement_terms_alone_do_not_label_tradingnode_guidance(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/templates/live_node.py",
        "Use TradingNode in this example; LiveNode is another node.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-strategy-builder/templates/live_node.py" in result.errors
    )


def test_descriptive_terms_alone_do_not_label_tradingnode_guidance(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder/templates/live_node.py",
        "TradingNode remains Python live integration-specific runtime guidance.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled TradingNode guidance in "
        "skills/nt-strategy-builder/templates/live_node.py" in result.errors
    )


def test_descriptive_terms_alone_do_not_label_legacy_cython_guidance(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-dev/references/guides/ffi.md",
        "Cython is deprecated; expose this type through the wrapper.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-dev/references/guides/ffi.md" in result.errors
    )


def test_marker_alone_does_not_label_legacy_cython_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/references/guides/ffi.md",
        "NT v2 compatibility note: Cython wrapper guidance.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unlabelled legacy/Cython/v1 guidance in "
        "skills/nt-dev/references/guides/ffi.md" in result.errors
    )


def test_reports_python_label_before_shebang(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-adapters/references/examples/binance/example.py",
        "# NT v2 compatibility note: Python live TradingNode reference-only.\n"
        "#!/usr/bin/env python3\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    result = run_checks(tmp_path)

    assert (
        "python shebang is not on first line in "
        "skills/nt-adapters/references/examples/binance/example.py" in result.errors
    )


def test_reports_uncommented_python_fence_compatibility_label(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "references/concepts/live.md",
        "```python\n"
        "NT v2 compatibility note: Python live/integration-specific TradingNode.\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "```\n",
    )

    result = run_checks(tmp_path)

    assert (
        "uncommented NT v2 compatibility note in Python fence in "
        "references/concepts/live.md" in result.errors
    )


def test_reports_duplicate_adjacent_compatibility_labels(tmp_path: Path) -> None:
    write(
        tmp_path / "references/concepts/live.md",
        "NT v2 compatibility note: Python live/integration-specific TradingNode; "
        "use LiveNode for Rust v2/Rust-backed work.\n"
        "NT v2 compatibility note: Python live/integration-specific TradingNode; "
        "use LiveNode for Rust v2/Rust-backed work.\n"
        "from nautilus_trader.live.node import TradingNode\n",
    )

    result = run_checks(tmp_path)

    assert (
        "duplicate adjacent NT v2 compatibility note in references/concepts/live.md"
        in result.errors
    )


def test_reports_blank_separated_duplicate_compatibility_labels(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "references/developer_guide/ffi.md",
        "NT v2 compatibility note: legacy Cython/v1 reference-only; "
        "prefer Rust v2/PyO3 for new work.\n\n"
        "NT v2 compatibility note: legacy Cython/v1 reference-only; "
        "prefer Rust v2/PyO3 for new work.\n\n"
        "Expose this type through Cython and update the .pyx wrapper.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "duplicate repeated NT v2 compatibility note in "
        "references/developer_guide/ffi.md" in result.errors
    )


def test_reports_duplicate_python_fence_compatibility_labels(tmp_path: Path) -> None:
    write(
        tmp_path / "references/concepts/live.md",
        "```python\n"
        "# NT v2 compatibility note: Python live/integration-specific TradingNode.\n"
        "# NT v2 compatibility note: Python live/integration-specific TradingNode.\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "```\n",
    )

    result = run_checks(tmp_path)

    assert (
        "duplicate NT v2 compatibility note in Python fence in "
        "references/concepts/live.md" in result.errors
    )




def test_reports_missing_rust_oriented_v2_readiness_boundary(tmp_path: Path) -> None:
    write(tmp_path / "README.md", "Nautilus skills.\n")
    write(tmp_path / "skills/nt/SKILL.md", "Route NautilusTrader skills.\n")
    write(tmp_path / "skills/nt-dev/SKILL.md", "Rust v2 development.\n")
    write(tmp_path / "skills/nt-review/SKILL.md", "Review Rust code.\n")
    write(tmp_path / "skills/nt-architect/SKILL.md", "Keep advisory workflows isolated.\n")

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing Rust-oriented v2 readiness term 'Rust-oriented v2.0 readiness' "
        "in skills/nt-dev/SKILL.md" in result.errors
    )
    assert (
        "missing Rust-oriented v2 readiness term 'Rust-oriented v2.0 readiness' "
        "in skills/nt-review/SKILL.md" in result.errors
    )


def test_reports_missing_nt_v2_rust_readiness_gate_section(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "Use Rust for production data wranglers and record test evidence.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing NT V2 Rust readiness gates section in skills/nt-data/SKILL.md"
        in result.errors
    )


def test_reports_incomplete_nt_v2_rust_readiness_gate_vocabulary(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "## NT V2 Rust readiness gates\n"
        "Statuses: Pass, Pending.\n"
        "- G0 Scope and ownership: latest docs.\n"
        "- G1 Legacy labelling: label legacy.\n"
        "- G2 Pinned V2 examples: validate examples.\n"
        "- G3 Rust bindings/PyO3: verify bindings.\n"
        "- G4 Functional gates: current APIs.\n"
        "- G5 References and templates: command evidence.\n"
        "- G6 Operational and migration boundaries: safety review.\n"
        "- G7 Durable evidence: report gates.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert "missing NT V2 readiness table in skills/nt-data/SKILL.md" in result.errors


def test_reports_readiness_table_without_status_and_evidence_columns(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "## NT V2 Rust readiness gates\n"
        "| Gate | Required check |\n"
        "|---|---|\n"
        "| G0 Scope and ownership | Pass after docs review. |\n"
        "| G1 Legacy labelling | Pending. |\n"
        "| G2 Pinned V2 examples | Blocked. |\n"
        "| G3 Rust bindings/PyO3 | Pending. |\n"
        "| G4 Functional gates | Pending. |\n"
        "| G5 References and templates | Pending. |\n"
        "| G6 Operational and migration boundaries | Pending. |\n"
        "| G7 Durable evidence | Pending. |\n",
    )

    errors = run_checks(tmp_path).errors

    assert (
        "invalid NT V2 readiness table columns in skills/nt-data/SKILL.md"
        in errors
    )


def test_readiness_intro_with_legacy_terms_does_not_need_separate_label(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "NT v2 compatibility note: legacy Cython/v1 and Python live `TradingNode` "
        "references in this file are retained for migration/reference-only context.\n\n"
        "## NT V2 Rust readiness gates\n"
        "\n"
        "Use these gates for newly built work. Complete the status gate before coding "
        "and mark each gate `Pass`, `Pending`, or `Blocked`; "
        "`Pass` requires explicit docs, diff, or command evidence.\n"
        "| Gate | Description | Status | Evidence |\n"
        "| --- | --- | --- | --- |\n"
        "| G0 Scope and ownership | Confirm upstream docs. | Pass | `git rev-parse HEAD` recorded in `README.md`. |\n"
        "| G1 Legacy labelling | Label legacy Cython/v1 and TradingNode guidance. | Pass | Compatibility note above labels legacy Cython/v1 and Python live `TradingNode` as migration/reference-only. |\n"
        "| G2 Pinned V2 examples | Validate examples against the pinned baseline. | Pending | Awaiting example validation. |\n"
        "| G3 Rust bindings/PyO3 | Verify current binding paths. | Pending | Awaiting PyO3 reconciliation. |\n"
        "| G4 Functional gates | Classify Rust or Python and use current APIs. | Pending | Awaiting lane and API audit. |\n"
        "| G5 References and templates | Record command evidence. | Pending | Awaiting targeted tests. |\n"
        "| G6 Operational and migration boundaries | Enforce safety boundaries. | Pending | Awaiting review. |\n"
        "| G7 Durable evidence | Report every gate. | Pending | Awaiting reconciliation. |\n",
    )

    errors = run_checks(tmp_path).errors

    assert not any("unlabelled TradingNode guidance" in error for error in errors)
    assert not any("unlabelled legacy/Cython/v1 guidance" in error for error in errors)


def test_reports_pass_readiness_gate_without_measurable_evidence(
    tmp_path: Path,
) -> None:
    card = readiness_gate_text().replace(
        "`git rev-parse HEAD` recorded in `README.md`.",
        "Looks correct.",
    )
    write(tmp_path / "skills/nt-data/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert (
        "NT V2 readiness gate G0 Pass lacks measurable evidence in "
        "skills/nt-data/SKILL.md" in errors
    )


def test_reports_readiness_status_outside_mission_contract(tmp_path: Path) -> None:
    card = readiness_gate_text().replace(
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pending |",
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | N/A |",
    )
    write(tmp_path / "skills/nt-data/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert (
        "invalid NT V2 readiness status 'N/A' for G2 in skills/nt-data/SKILL.md"
        in errors
    )


def test_reports_self_referential_pass_readiness_evidence(tmp_path: Path) -> None:
    card = readiness_gate_text().replace(
        "`git rev-parse HEAD` recorded in `README.md`.",
        "`grep -R \"Rust owns production\" skills/nt*/SKILL.md` finds the gate text.",
    )
    write(tmp_path / "skills/nt-data/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert (
        "NT V2 readiness gate G0 Pass uses self-referential evidence in "
        "skills/nt-data/SKILL.md" in errors
    )


def test_reports_card_validator_used_as_non_g2_evidence(tmp_path: Path) -> None:
    card = readiness_gate_text().replace(
        "`git rev-parse HEAD` recorded in `README.md`.",
        "`uv run python tools/check_skill_g2_harnesses.py --check-cards` passed.",
    )
    write(tmp_path / "skills/nt-data/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert (
        "NT V2 readiness gate G0 Pass uses the card validator as evidence in "
        "skills/nt-data/SKILL.md" in errors
    )


def test_reports_pass_gate_with_unscoped_shared_example_evidence(tmp_path: Path) -> None:
    card = readiness_gate_text().replace(
        "Awaiting upstream-backed example validation.",
        "`python3 tools/check_rust_trading_reference_sync.py --compile` passed.",
    ).replace(
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pending |",
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pass |",
    )
    write(tmp_path / "skills/nt-data/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert (
        "NT V2 readiness gate G2 Pass uses unscoped shared Rust-example evidence in "
        "skills/nt-data/SKILL.md" in errors
    )


def test_allows_shared_example_evidence_for_rust_strategy_skill(tmp_path: Path) -> None:
    card = readiness_gate_text().replace(
        "Awaiting upstream-backed example validation.",
        "`python3 tools/check_rust_trading_reference_sync.py --compile` passed.",
    ).replace(
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pending |",
        "| G2 Pinned V2 examples | Compile or validate examples against the pinned NT V2 master/develop baseline. | Pass |",
    )
    write(tmp_path / "skills/nt-strategy-builder-rust/SKILL.md", card)

    errors = run_checks(tmp_path).errors

    assert not any("unscoped shared Rust-example evidence" in error for error in errors)


def test_reports_incomplete_nt_v2_rust_readiness_gate_labels(
    tmp_path: Path,
) -> None:
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "## NT V2 Rust readiness gates\n"
        "Statuses: Pass, Pending, Blocked.\n"
        "- G0 Scope and ownership: latest docs.\n"
        "- G1 Legacy labelling: label legacy.\n"
        "- G2 Pinned V2 examples: validate examples.\n"
        "- G3 Rust bindings/PyO3: verify bindings.\n"
        "- G4 Functional gates: current APIs.\n"
        "- G5 References and templates: command evidence.\n"
        "- G7 Durable evidence: report gates.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing NT V2 readiness gate 'G6 Operational and migration boundaries' "
        "in skills/nt-data/SKILL.md" in result.errors
    )


def test_reports_missing_nt_v2_rust_checker_gate_terms(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-strategy-builder-rust/SKILL.md",
        readiness_gate_text(
            "Build Rust strategies with StrategyCore and nautilus_strategy!.\n"
        ),
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing NT V2 Rust checker gate term 'cargo nextest' "
        "in skills/nt-strategy-builder-rust/SKILL.md" in result.errors
    )
    assert (
        "missing NT V2 Rust checker gate term 'cargo clippy' "
        "in skills/nt-strategy-builder-rust/SKILL.md" in result.errors
    )
    assert (
        "missing NT V2 Rust checker gate term 'cargo deny' "
        "in skills/nt-strategy-builder-rust/SKILL.md" in result.errors
    )


def test_reports_missing_nt_v2_cutover_alignment(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "Python v2 controller subclassing, subclassable execution algorithms, FeeModel, "
        "FillModel.\n",
    )
    write(tmp_path / "skills/nt-live/SKILL.md", "Use LiveNode for Rust v2.\n")
    write(tmp_path / "skills/nt-review/SKILL.md", "Review PyO3 code.\n")
    write(tmp_path / "skills/nt-testing/SKILL.md", "Use DataTester and ExecTester.\n")
    write(
        tmp_path / "references/developer_guide/rust.md",
        "Rust guidance with rust-toolchain.toml 1.97.1 "
        "Generated Python bindings HIGH_PRECISION=true py-stubs-v2 "
        "ffi,python,high-precision,defi "
        "arrow,ffi,python,high-precision,streaming,defi.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing NT v2 cutover term 'v1.230.0' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing NT v2 cutover term 'rust-toolchain.toml' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing NT v2 cutover term '1.97.1' in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing NT v2 live term 'with_clock_factory' in skills/nt-live/SKILL.md"
        in result.errors
    )
    assert (
        "missing NT v2 review term 'v2 wranglers' in skills/nt-review/SKILL.md"
        in result.errors
    )
    assert (
        "missing NT v2 testing term 'Python v2 controller subclassing' "
        "in skills/nt-testing/SKILL.md" in result.errors
    )


def test_reports_release_security_fish_syntax_in_bash_examples(tmp_path: Path) -> None:
    write(
        tmp_path / "references/developer_guide/release_security.md",
        "trusted publishing Sigstore SLSA provenance cosign export TAG= export REPO= "
        "gh attestation verify.\n"
        "```bash\n"
        "export TAG= v1.228.0\n"
        "set -gx REPO nautechsystems/nautilus_trader\n"
        "set -gx URL (curl -sS https://example.invalid)\n"
        "test (sha256sum file | cut -d ' ' -f 1) = abc\n"
        "```\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "invalid release-security bash example in references/developer_guide/release_security.md"
        in result.errors
    )


def test_accepts_release_security_bash_array_assignments(tmp_path: Path) -> None:
    write(
        tmp_path / "references/developer_guide/release_security.md",
        "trusted publishing Sigstore SLSA provenance cosign export TAG= export REPO= "
        "gh attestation verify.\n"
        "```bash\n"
        "export TAG=v1.228.0\n"
        'artifacts=("nautilus_trader-1.228.0.tar.gz" "SHA256SUMS")\n'
        "printf '%s\\n' \"${artifacts[@]}\"\n"
        "```\n",
    )

    result = run_checks(tmp_path)

    assert (
        "invalid release-security bash example in references/developer_guide/release_security.md"
        not in result.errors
    )


def test_reports_copied_uv_required_version_guidance(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-dev/SKILL.md", 'required-version = "==0.11.14"\n')

    result = run_checks(tmp_path)

    assert (
        "copied uv required-version guidance in skills/nt-dev/SKILL.md" in result.errors
    )


def test_reports_unbounded_polymarket_allowance_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "references/integrations/polymarket.md",
        "Approve the maximum possible amount of pUSD using MAX_INT.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "unbounded Polymarket allowance guidance in references/integrations/polymarket.md"
        in result.errors
    )


def test_reports_nonexistent_dex_instrument_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-dex-adapter/SKILL.md",
        "Parse perp markets into CryptoPermanentContract instruments.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "nonexistent DEX instrument class CryptoPermanentContract in skills/nt-dex-adapter/SKILL.md"
        in result.errors
    )


def test_reports_missing_secret_ignore_patterns(tmp_path: Path) -> None:
    write(
        tmp_path / ".gitignore",
        "__pycache__/\n.venv\n",
    )

    result = run_checks(tmp_path)

    assert "missing secret ignore pattern '.env' in .gitignore" in result.errors
    assert "missing secret ignore pattern '*.pem' in .gitignore" in result.errors


def test_reports_missing_gitignore(tmp_path: Path) -> None:
    result = run_checks(tmp_path)

    assert "missing .gitignore with secret ignore patterns" in result.errors


def test_success_when_required_files_metadata_paths_and_invariants_exist(
    tmp_path: Path,
) -> None:
    write_entry_skill(tmp_path)
    write(tmp_path / ".gitignore", ".env\n.env.*\n*.pem\n*.key\n")

    guide_bodies = {
        "adapters.md": (
            "Handler initialization handshake Auth-token rotation CancellationToken "
            "execution-path rate-limit response unknown outcome idempotent\n"
        ),
        "spec_exec_testing.md": (
            "Ambiguous outcome failures local prepare-failure carve-out "
            "OrderCancelRejected OrderModifyRejected TC-E74 TC-E78 "
            "due_post_only=true trigger-order signing expiry\n"
        ),
        "environment_setup.md": (
            "current version numbers into docs rustup toolchain install nightly "
            "pip-audit maturin\n"
        ),
        "rust.md": (
            "rust-toolchain.toml 1.97.1 "
            "Generated FFI bindings and precision mode HIGH_PRECISION=true\n"
            "Generated Python artifacts make py-stubs-v2 bon::bon try_order.\n"
            "Generated Python bindings arrow,ffi,python,high-precision,streaming,defi\n"
            "get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work.\n"
        ),
        "python.md": (
            "Python v2 live callback routing Do not call `Python::attach` "
            "from Tokio worker tasks\n"
        ),
        "ffi.md": "Typed CVec wrappers and Send Rust-owned CVec capsules with explicit drop\n",
        "release_security.md": "Trusted Publishing Sigstore SLSA posture cosign export TAG= export REPO= gh attestation verify\n",
    }
    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name) + f"# {name}\n" + guide_bodies.get(name, ""),
        )

    write(
        tmp_path / "skills/nt-live/SKILL.md",
        "NT v2 compatibility note: Python live/integration-specific TradingNode; "
        "use LiveNode for Rust v2/Rust-backed work.\n"
        "Prefer LiveNode for Rust v2; TradingNode remains Python live/integration-specific.\n"
        "NT v2 compatibility note: legacy Cython/v1 reference-only; "
        "prefer Rust v2/PyO3 for new work.\n"
        "Legacy v1/Cython-oriented example with file_config and PortfolioSnapshot.\n"
        "SIGTERM with_clock_factory event_store v1.227-v1.229 LiveNode metrics "
        "WebSocket transport backend RecencyMap.\n",
    )
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
        "Use DataTester and ExecTester evidence with limit_aggressive and test_modify_rejected.\n"
        "Adapter baseline matrix and Account reconciliation matrix required.\n"
        "ExecTesterConfig::builder() StrategyConfig build()? for Rust examples.\n"
        "ExecTester groups 1–5 after DataTester, capability matrix, unknown outcomes stay non-terminal.\n"
        "Reconcile balances, open orders, fills, positions, and startup state.\n"
        "Cover TC-E74 through TC-E78 ambiguous outcome failures, due_post_only=true, "
        "local prepare-failure carve-out, OrderCancelRejected, OrderModifyRejected, "
        "and trigger-order signing expiry.\n"
        "DST readiness uses deterministic runtime seams.\n"
        "Required dataset metadata: file sha256 size_bytes original_url licence added_at.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use nautilus_network::http::HttpClient and get_runtime().spawn().\n"
        "Never use get_runtime().block_on() inside trait method implementations.\n"
        "Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations; spawn work immediately.\n"
        "Live DataClient and ExecutionClient trait methods spawn work; get_runtime().block_on() only outside an ambient Tokio runtime, such as PyO3.\n"
        "Use time_bars_origin_offset and Binance/Kraken `Live` / `LIVE` environments.\n"
        "Use SetClient before publishing command channels, support auth-token rotation, "
        "CancellationToken shutdown, ambiguous outcome failures, and execution-path "
        "rate-limit response handling as an unknown outcome unless idempotent.\n",
    )
    write(
        tmp_path / "skills/nt-architect/SKILL.md",
        "Preserve message immutability in designs. Layout Rust adapters under crates/adapters/.\n"
        "Rust-oriented v2.0 readiness means Rust core owns networking and execution-critical state. "
        "The AI/advisory lane remains Python.\n",
    )
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "Use time_bars_origin_offset, order_owned, try_order, and try_order_owned snapshots.\n",
    )
    write(
        tmp_path / "skills/nt-signals/SKILL.md",
        "Use priority for ContinuousFutureAdjustmentType signal flows.\n",
    )
    write(
        tmp_path / "skills/nt-trading/SKILL.md",
        "Use PortfolioSnapshot and TryFrom<OrderInitialized>.\n",
    )
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "NT v2 compatibility note: legacy Cython/v1 reference-only; "
        "prefer Rust v2/PyO3 for new work.\n"
        "Rust-oriented v2.0 readiness: v1.230.0 latest release, 1.231.0 develop source, "
        "2.0.0rc1 readiness, 2.0.0rcN release-candidate line, rust-toolchain.toml 1.97.1. "
        "Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
        "Use tools.toml for Cap'n Proto.\n"
        "Do not copy current version numbers into docs. Generated FFI bindings and precision mode "
        "must be checked before committing FFI work. Python v2 live callback routing keeps "
        "Tokio worker threads from running Python code. Typed CVec wrappers and Send are required "
        "for capsule payloads.\n"
        "Fuzz targets require rustup toolchain install nightly.\n"
        "v1.230.0 rust-toolchain.toml 1.97.1 "
        "Generated Python artifacts make py-stubs-v2 arrow,ffi,python,high-precision,streaming,defi.\n"
        "Run Rust checks with cargo nextest, cargo clippy, cargo deny, and rstest.\n"
        "Use get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work instead.\n"
        'PYTHON_LIB_DIR uses sysconfig.get_config_var("LIBDIR").\n',
    )
    write(
        tmp_path / "skills/nt-strategy-builder/SKILL.md",
        "NT v2 compatibility note: Python live/integration-specific TradingNode; "
        "use LiveNode for Rust v2/Rust-backed work.\n"
        "LiveNode for Rust v2; TradingNode remains Python live/integration-specific.\n",
    )
    write(
        tmp_path / "skills/nt-review/SKILL.md",
        "NT v2 compatibility note: Python live/integration-specific TradingNode; "
        "use LiveNode for Rust v2/Rust-backed work.\n"
        "NT v2 compatibility note: migration/reference-only legacy labels in this file; "
        "prefer Rust v2/PyO3 for new work.\n"
        "Rust-oriented v2.0 readiness rejects unlabelled legacy/Cython/v1 guidance. "
        "Review LiveNode for Rust v2 and TradingNode as Python live/integration-specific. "
        "Generated Python artifacts make py-stubs-v2. Python v2 config stub/readback drift, "
        "subclassable PyO3 stubs, v2 wranglers, raw fixed-point overflow, RecencyMap, "
        "DataActor, and message bus.\n",
    )
    write(
        tmp_path / "skills/nt-implement/SKILL.md",
        "Use get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; "
        "Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work instead. "
        "V2 cutover: route networking/parsing adapters under crates/adapters/ to Rust. Strategy language is gated to avoid cross-contamination: no cross-contamination between the Python and Rust strategy builders.\n",
    )
    write(
        tmp_path / "skills/nt-dex-adapter/rules/dos_and_donts.md",
        "Use get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; "
        "Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work instead.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/references/guides/rust.md",
        "Use get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; "
        "Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work instead.\n",
    )

    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name)
            + "Handler initialization handshake\n"
            + "Auth-token rotation\n"
            + "CancellationToken\n"
            + "execution-path rate-limit response\n"
            + "unknown outcome\n"
            + "idempotent\n"
            + "Ambiguous outcome failures\n"
            + "local prepare-failure carve-out\n"
            + "OrderCancelRejected\n"
            + "OrderModifyRejected\n"
            + "TC-E74\n"
            + "TC-E78\n"
            + "due_post_only=true\n"
            + "trigger-order signing expiry\n"
            + "Trusted Publishing\n"
            + "Sigstore\n"
            + "SLSA posture\n"
            + "cosign\n"
            + "Python v2 live callback routing\n"
            + "Do not call `Python::attach` from Tokio worker tasks\n"
            + "Generated FFI bindings and precision mode\n"
            + "HIGH_PRECISION=true\n"
            + "Typed CVec wrappers and Send\n"
            + "Rust-owned CVec capsules with explicit drop\n"
            + "Do not copy current version numbers\n"
            + "current version numbers into docs\n"
            + "pip-audit\n"
            + "maturin\n"
            + "rustup toolchain install nightly\n"
            + "synchronous adapter code can use get_runtime().block_on() to call an async function.\n"
            + "Never use `block_on` in trait methods for DataClient or ExecutionClient; spawn the operation and return.\n"
            + "get_runtime().block_on() only outside an ambient Tokio runtime such as PyO3; Never use get_runtime().block_on() inside live DataClient or ExecutionClient trait method implementations, spawn work.\n"
            + "Generated Python artifacts make py-stubs-v2 bon::bon try_order.\n"
            + "rust-toolchain.toml 1.97.1 Generated Python bindings HIGH_PRECISION=true py-stubs-v2.\n"
            + "2.0.0rc1 2.0.0rcN release-candidate Python v2 controller subclassing subclassable execution algorithms FeeModel FillModel.\n"
            + "arrow,ffi,python,high-precision,streaming,defi --lib --tests.\n"
            + "ExecTesterConfig::builder() StrategyConfig build()? .\n"
            + "export TAG= export REPO= gh attestation verify.\n",
        )

    write(
        tmp_path / "skills/nt-backtest/SKILL.md",
        "BacktestEngine runs historical venues with actor fill models.\n",
    )
    write(
        tmp_path / "skills/nt-dex-adapter/SKILL.md",
        "DEX adapter spec mirrors crates/adapters/ layout for on-chain plumbing.\n",
    )
    write(
        tmp_path / "skills/nt-model/SKILL.md",
        "Domain model types live in Rust crates/model and are exposed via PyO3.\n",
    )
    write(
        tmp_path / "skills/nt-strategy-builder-rust/SKILL.md",
        "Rust-native strategies implement pub trait Strategy with a StrategyConfig "
        "builder, store StrategyCore, invoke nautilus_strategy!, implement "
        "impl DataActor handlers, include ..Default::default(), provide "
        "from_config, and call submit_order(order, None, None, None).\n",
    )

    readiness_extras = {
        Path("skills/nt/SKILL.md"): (
            "Route all strategy implementation to Rust-first skills. "
            "AI and advisory work are outside this repository.\n"
        ),
        Path("skills/nt-adapters/SKILL.md"): (
            "Adapter evidence includes cargo nextest, cargo clippy, cargo deny, and fuzz-adapter.\n"
        ),
        Path("skills/nt-architect/SKILL.md"): (
            "Architecture includes a component ownership matrix: Rust owns strategy/configuration and production paths; Python is migration/reference material, and AI and advisory work are outside this repository.\n"
        ),
        Path("skills/nt-backtest/SKILL.md"): (
            "Rust BacktestEngine evidence includes cargo nextest, cargo clippy, cargo deny, and Python research/config is labelled.\n"
        ),
        Path("skills/nt-data/SKILL.md"): (
            "Data readiness covers Arrow serialization, fixed-point validation, cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-dev/SKILL.md"): (
            "Development readiness includes cargo fmt --check, cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-dex-adapter/SKILL.md"): (
            "Rust-first default for on-chain adapters requires cargo nextest, cargo clippy, cargo deny, and fuzz.\n"
        ),
        Path("skills/nt-implement/SKILL.md"): (
            "AI/advisory lane remains Python; require status gate before coding plus cargo nextest, cargo clippy, and cargo deny for Rust.\n"
        ),
        Path("skills/nt-live/SKILL.md"): (
            "LiveNode readiness includes cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-model/SKILL.md"): (
            "PyO3 model readiness includes cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-review/SKILL.md"): (
            "AI/advisory lane remains Python; approval requires command evidence for cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-signals/SKILL.md"): (
            "AI/advisory lane remains Python; Rust production signals require cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-strategy-builder/SKILL.md"): (
            "AI/advisory lane remains Python; migration/reference-only Python material. route all new strategy work to nt-strategy-builder-rust.\n"
        ),
        Path("skills/nt-strategy-builder-rust/SKILL.md"): (
            "AI/advisory lane remains Python; StrategyCore evidence includes cargo nextest, cargo clippy, and cargo deny.\n"
        ),
        Path("skills/nt-testing/SKILL.md"): (
            "Testing evidence includes cargo nextest, cargo clippy, cargo deny, ExecTesterConfig::builder(), and DataTesterConfig::builder().\n"
        ),
        Path("skills/nt-trading/SKILL.md"): (
            "AI/advisory lane remains Python; Rust order readiness includes cargo nextest, cargo clippy, and cargo deny.\n"
        ),
    }
    for relative in sync.NT_V2_READINESS_GATE_TARGETS:
        absolute = tmp_path / relative
        if absolute.exists():
            lane_contract = (
                rust_lane_text()
                if relative.parent.name
                in {"nt-trading", "nt-backtest", "nt-signals", "nt-live", "nt-data", "nt-implement"}
                else ""
            )
            absolute.write_text(
                readiness_gate_text(readiness_extras.get(relative, ""))
                + lane_contract
                + absolute.read_text(),
                encoding="utf-8",
            )

    result = run_checks(tmp_path)

    assert result == CheckResult(ok=True, errors=[])
