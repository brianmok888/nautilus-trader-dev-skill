from __future__ import annotations

from pathlib import Path

from tools.check_dev_guide_snapshot_sync import strip_local_metadata
from tools.upstream_baseline import UPSTREAM_COMMIT, default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_lighter_guides_teach_current_tester_startup_convention() -> None:
    for path in (
        "skills/nt-adapters/references/integrations/lighter.md",
        "references/integrations/lighter.md",
    ):
        guide = read(path)

        for obsolete in (
            "--run",
            "--live-orders",
            "default to a dry build",
        ):
            assert obsolete not in guide, (
                f"{path} teaches removed tester opt-in {obsolete}"
            )

        for current in (
            "module-level constants",
            "dry_run=False",
            "LIGHTER_ENVIRONMENT",
        ):
            assert current in guide, (
                f"{path} lacks current tester convention marker {current}"
            )


def test_network_config_guides_use_current_field_names() -> None:
    spec = read("skills/nt-adapters/references/guides/official_adapter_spec.md")

    assert f"source_commit: {UPSTREAM_COMMIT}\n" in spec
    assert strip_local_metadata(spec) == (
        default_upstream_root() / "docs/developer_guide/adapters.md"
    ).read_text(encoding="utf-8")
    assert "heartbeat_msg" not in spec
    config = (
        default_upstream_root() / "crates/network/src/websocket/config.rs"
    ).read_text()
    assert "pub heartbeat_payload: Option<String>" in config
    assert "pub heartbeat_interval_secs: Option<u64>" in config
    assert "venue text heartbeats" in spec
    assert "protocol control frames" in spec

    for path in (
        "skills/nt-adapters/references/integrations/betfair_v2.md",
        "references/integrations/betfair_v2.md",
    ):
        guide = read(path)

        for obsolete in (
            "stream_heartbeat_ms",
            "stream_idle_timeout_ms",
        ):
            assert obsolete not in guide, f"{path} teaches removed field {obsolete}"

        assert "| `stream_heartbeat_secs` " in guide
        assert "| `stream_heartbeat_timeout_secs` " in guide

def test_reconnect_outcomes_match_current_transport_and_socket_handle() -> None:
    upstream = default_upstream_root()
    spec = read("skills/nt-adapters/references/guides/official_adapter_spec.md")
    mode = (upstream / "crates/network/src/mode.rs").read_text(encoding="utf-8")
    outcomes = mode.split("pub enum ReconnectRequestOutcome {", 1)[1].split("\n}", 1)[0]
    for outcome in ("Accepted", "AlreadyReconnecting", "Disconnected", "Closed", "Unsupported"):
        assert f"    {outcome}," in outcomes
    assert "ReconnectRequestOutcome" in spec
    assert "Stream-mode clients own their reconnect loop" in spec
    assert "handles report `Unsupported`" in spec
    socket = (upstream / "crates/live/src/socket.rs").read_text(encoding="utf-8")
    assert "pub struct SocketReconnectHandle" in socket
    assert "pub fn request_reconnect(&self) -> ReconnectRequestOutcome" in socket


def test_adapter_spec_covers_fallible_commission_contract() -> None:
    spec = read("skills/nt-adapters/references/guides/official_adapter_spec.md")

    for marker in (
        "calculate_commission",
        "Ok(Some(commission))",
        "Ok(None)",
        "Fail closed",
        "Err(error)",
        "Never replace",
    ):
        assert marker in spec, f"spec lacks commission contract marker {marker}"


def test_live_guide_covers_hosted_async_run_modes() -> None:
    live = read("skills/nt-live/references/guides/run_rust_live_trading.md")

    for marker in (
        "run_async()",
        "LiveNodeHandle",
        "hosted",
        "signal handling",
        "e166a5e57c",
    ):
        assert marker in live, f"live guide lacks run-mode marker {marker}"


def test_betfair_guides_cover_current_replacement_recovery() -> None:
    for path in (
        "skills/nt-adapters/references/integrations/betfair_v2.md",
        "references/integrations/betfair_v2.md",
    ):
        guide = read(path)

        for marker in (
            "customerOrderRef",
            "customerRef",
            "CANCELLED_NOT_PLACED",
            "OrderUpdated",
            "45-second",
            "pending",
            "reconciliation",
            "10,000",
            "tracked order",
            "8e51f957c",
        ):
            assert marker in guide, f"{path} lacks Betfair recovery marker {marker}"


def test_betfair_v2_is_primary_and_v1_cleared() -> None:
    for path in (
        "skills/nt-adapters/references/integrations/betfair.md",
        "references/integrations/betfair.md",
    ):
        stub = read(path)

        assert "superseded by `betfair_v2.md`" in stub, (
            f"{path} lacks the v2 supersession pointer"
        )
        assert "NT v2 compatibility note" in stub, f"{path} lacks the legacy label"
        for substantive in (
            "Recovering an ambiguous modification",
            "Session management and reconnection",
            "## Fees",
        ):
            assert substantive not in stub, (
                f"{path} still carries cleared v1 section {substantive!r}"
            )

    for path in (
        "skills/nt-adapters/references/integrations/betfair_v2.md",
        "references/integrations/betfair_v2.md",
    ):
        guide = read(path)

        assert "primary Betfair guide" in guide, (
            f"{path} does not declare primary status"
        )

    for path in (
        "references/integrations/index.md",
        "skills/nt-adapters/references/integrations/index.md",
    ):
        index = read(path)
        row = next(
            line
            for line in index.splitlines()
            if "betfair_v2.md" in line or "](betfair.md)" in line
        )
        assert "](betfair_v2.md)" in row and "](betfair.md)" in row, (
            f"{path} Betfair row does not route v2 first with the v1 kept as legacy"
        )


def test_nt_adapters_routes_betfair_v2_first() -> None:
    skill = read("skills/nt-adapters/SKILL.md")

    assert "betfair_v2.md" in skill, (
        "nt-adapters SKILL does not route the Betfair v2 guide"
    )
    assert "primary Betfair" in skill or "Betfair work routes" in skill, (
        "nt-adapters SKILL lacks the v2-first Betfair routing statement"
    )


def test_betfair_v2_guides_cover_socket_state_and_targeted_reconnect() -> None:
    for path in (
        "skills/nt-adapters/references/integrations/betfair_v2.md",
        "references/integrations/betfair_v2.md",
    ):
        guide = read(path)

        assert "d2b62d35a7" in guide, (
            f"{path} lacks the pinned socket-state source commit"
        )
        assert "betfair-data-streams" in guide and "betfair-user-streams" in guide, (
            f"{path} lacks the stable socket endpoint labels"
        )
        assert "SocketReconnectRegistry" in guide, (
            f"{path} lacks the targeted reconnect registry teaching"
        )
