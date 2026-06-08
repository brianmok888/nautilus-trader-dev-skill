from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.check_dev_guide_sync import CheckResult
from tools.check_dev_guide_sync import CURRENT_SYNC_DATE
from tools.check_dev_guide_sync import CURRENT_TARGET
from tools.check_dev_guide_sync import CURRENT_DEV_GUIDE_FILES
from tools.check_dev_guide_sync import ENTRY_SKILL_ROUTING_TARGETS
from tools.check_dev_guide_sync import run_checks


def current_metadata(name: str = "design_principles.md") -> str:
    slug = "" if name == "index.md" else name.removesuffix(".md") + "/"
    return (
        "---\n"
        f"source_url: https://nautilustrader.io/docs/latest/developer_guide/{slug}\n"
        f"source_repo: nautechsystems/nautilus_trader/docs/developer_guide/{name}\n"
        f"sync_date: {CURRENT_SYNC_DATE}\n"
        f"target: {CURRENT_TARGET}\n"
        "confidence: high\n"
        "---\n"
    )


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
        f"{routes}\n",
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
            current_metadata(name).replace("develop", "v1.227.0")
            + f"# {name}\n",
        )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert any("stale target" in error for error in result.errors)


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

    assert "stale references/guides path in .omx/context/runtime.md" not in result.errors


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
    assert "stale uv required-version guidance in skills/nt-dev/SKILL.md" in result.errors


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


def test_reports_stale_evomap_direct_a2a_guidance(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-evomap-integration/SKILL.md",
        "Use EvoMapCapsuleClient to call hello, publish, fetch, report on evomap.ai.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "stale direct EvoMap A2A guidance in skills/nt-evomap-integration/SKILL.md"
        in result.errors
    )


def test_reports_missing_evomap_proxy_boundary_terms(tmp_path: Path) -> None:
    write(
        tmp_path / "skills/nt-evomap-integration/SKILL.md",
        "EvoMap remains advisory-only with fallback and provenance.\n",
    )

    result = run_checks(tmp_path)

    assert result.ok is False
    assert (
        "missing EvoMap proxy boundary in skills/nt-evomap-integration/SKILL.md"
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
        "in references/developer_guide/adapters.md"
        in result.errors
    )
    assert (
        "missing current guide delta 'Ambiguous outcome failures' "
        "in references/developer_guide/spec_exec_testing.md"
        in result.errors
    )
    assert (
        "missing current guide delta 'Python v2 live callback routing' "
        "in references/developer_guide/python.md"
        in result.errors
    )
    assert (
        "missing current guide delta 'Typed CVec wrappers and Send' "
        "in references/developer_guide/ffi.md"
        in result.errors
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
            + "Ambiguous outcome failures\n"
            + "TC-E74\n"
            + "TC-E78\n"
            + "due_post_only=true\n"
            + "trigger-order signing expiry\n"
            + "Python v2 live callback routing\n"
            + "Do not call `Python::attach` from Tokio worker tasks\n"
            + "Generated FFI bindings and precision mode\n"
            + "HIGH_PRECISION=true\n"
            + "Typed CVec wrappers and Send\n"
            + "Rust-owned CVec capsules with explicit drop\n"
            + "Do not copy current version numbers\n"
            + "rustup toolchain install nightly\n",
        )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use nautilus_network::http::HttpClient and get_runtime().spawn().\n"
        "Use time_bars_origin_offset and Binance/Kraken `Live` / `LIVE` environments.\n",
    )
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Use DataTester and ExecTester evidence with limit_aggressive and test_modify_rejected.\n"
        "DST readiness uses deterministic runtime seams.\n"
        "Required dataset metadata: file sha256 size_bytes original_url licence added_at.\n",
    )
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "Use tools.toml for Cap'n Proto.\n"
        'PYTHON_LIB_DIR uses sysconfig.get_config_var("LIBDIR").\n',
    )
    write(
        tmp_path / "skills/nt-evomap-integration/SKILL.md",
        "Use local Proxy mailbox endpoints mailbox/send, mailbox/poll, asset/submit, "
        "and asset/fetch. LangChain model/tool wrappers and LangGraph StateGraph "
        "or human-in-the-loop checkpoints stay advisory-only and off hot handlers.\n",
    )

    result = run_checks(tmp_path)

    assert (
        "missing current skill delta 'SetClient' in skills/nt-adapters/SKILL.md"
        in result.errors
    )
    assert (
        "missing current skill delta 'TC-E74' in skills/nt-testing/SKILL.md"
        in result.errors
    )
    assert (
        "missing current skill delta 'Python v2 live callback routing' "
        "in skills/nt-dev/SKILL.md"
        in result.errors
    )
    assert (
        "missing current skill delta '~/.evolver/settings.json' "
        "in skills/nt-evomap-integration/SKILL.md"
        in result.errors
    )


def test_reports_copied_uv_required_version_guidance(tmp_path: Path) -> None:
    write(tmp_path / "skills/nt-dev/SKILL.md", 'required-version = "==0.11.14"\n')

    result = run_checks(tmp_path)

    assert "copied uv required-version guidance in skills/nt-dev/SKILL.md" in result.errors


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

    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name) + f"# {name}\n",
        )

    write(
        tmp_path / "skills/nt-live/SKILL.md",
        "Prefer LiveNode for Rust v2; TradingNode remains Python live/integration-specific.\n"
        "Legacy v1/Cython-oriented example with file_config and PortfolioSnapshot.\n",
    )
    write(
        tmp_path / "skills/nt-testing/SKILL.md",
        "Use DataTester and ExecTester evidence with limit_aggressive and test_modify_rejected.\n"
        "Cover TC-E74 through TC-E78 ambiguous outcome failures, due_post_only=true, "
        "and trigger-order signing expiry.\n"
        "DST readiness uses deterministic runtime seams.\n"
        "Required dataset metadata: file sha256 size_bytes original_url licence added_at.\n",
    )
    write(
        tmp_path / "skills/nt-adapters/SKILL.md",
        "Use nautilus_network::http::HttpClient and get_runtime().spawn().\n"
        "Use time_bars_origin_offset and Binance/Kraken `Live` / `LIVE` environments.\n"
        "Use SetClient before publishing command channels, support auth-token rotation, "
        "CancellationToken shutdown, and ambiguous outcome failures.\n",
    )
    write(
        tmp_path / "skills/nt-architect/SKILL.md",
        "Preserve message immutability in designs.\n",
    )
    write(
        tmp_path / "skills/nt-data/SKILL.md",
        "Use time_bars_origin_offset and order_owned snapshots.\n",
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
        tmp_path / "skills/nt-evomap-integration/SKILL.md",
        "Use local Proxy mailbox endpoints mailbox/send, mailbox/poll, asset/submit, "
        "and asset/fetch. LangChain model/tool wrappers and LangGraph StateGraph "
        "or human-in-the-loop checkpoints stay advisory-only and off hot handlers.\n"
        "Discover Proxy via ~/.evolver/settings.json, support EVOMAP_PROXY_PORT, "
        "mailbox/ack, mailbox/status, mailbox/list, task/subscribe, task/list, "
        "task/claim, task/complete, and task/unsubscribe.\n",
    )
    write(
        tmp_path / "skills/nt-dev/SKILL.md",
        "Use tools.toml for Cap'n Proto.\n"
        "Do not copy current version numbers into docs. Generated FFI bindings and precision mode "
        "must be checked before committing FFI work. Python v2 live callback routing keeps "
        "Tokio worker threads from running Python code. Typed CVec wrappers and Send are required "
        "for capsule payloads.\n"
        "Fuzz targets require rustup toolchain install nightly.\n"
        'PYTHON_LIB_DIR uses sysconfig.get_config_var("LIBDIR").\n',
    )
    write(
        tmp_path / "skills/nt-strategy-builder/SKILL.md",
        "LiveNode for Rust v2; TradingNode remains Python live/integration-specific.\n",
    )
    write(
        tmp_path / "skills/nt-review/SKILL.md",
        "Review LiveNode for Rust v2 and TradingNode as Python live/integration-specific.\n",
    )

    for name in CURRENT_DEV_GUIDE_FILES:
        write(
            tmp_path / "references/developer_guide" / name,
            current_metadata(name)
            + "Handler initialization handshake\n"
            + "Auth-token rotation\n"
            + "CancellationToken\n"
            + "Ambiguous outcome failures\n"
            + "TC-E74\n"
            + "TC-E78\n"
            + "due_post_only=true\n"
            + "trigger-order signing expiry\n"
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
            + "rustup toolchain install nightly\n",
        )

    result = run_checks(tmp_path)

    assert result == CheckResult(ok=True, errors=[])
