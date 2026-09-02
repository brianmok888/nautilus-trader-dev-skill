from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_current_develop_contract_overlays_cover_registration_reconnect_and_blockchain() -> None:
    testing = read("skills/nt-testing/SKILL.md")
    adapters = read("skills/nt-adapters/references/guides/official_adapter_spec.md")
    dex = read("skills/nt-dex-adapter/SKILL.md")
    benchmark = read("skills/nt-dev/SKILL.md")

    for marker in ("ensure_registered", "before actor registration", "PyResult"):
        assert marker in testing
    for marker in (
        "SocketReconnectRegistry",
        "ReconnectSocket",
        "AlreadyPending",
        "Unavailable",
        "endpoint",
    ):
        assert marker in adapters
    for marker in (
        "WalletAccount",
        "chain ID",
        "nonce",
        "local signing",
        "reservation",
        "transaction lifecycle",
    ):
        assert marker in dex
    for marker in (
        "canonical.rs",
        "workload identifier",
        "release profile",
        "baseline comparison",
    ):
        assert marker in benchmark


def test_live_guidance_covers_current_cache_and_queue_observability() -> None:
    # Given current-develop live guidance
    text = read("skills/nt-live/SKILL.md")

    # When an agent looks for persistent cache and runner-pressure contracts
    # Then the exact public contracts and their version boundary are present
    assert "with_cache_database_factory" in text
    assert "QueueStateChanged" in text
    assert "dispatch_busy_ns" in text
    assert "0caf26d216c4196d60cc35991492337b07568c22" in text
    assert "42ff42b346ec42eeba4486f618f24e5cc15b2d02" in text


def test_adapter_guidance_covers_current_retry_and_venue_safety_contracts() -> None:
    # Given current-develop adapter guidance
    text = read("skills/nt-adapters/SKILL.md")

    # When an agent implements retry and venue lifecycle behavior
    # Then typed retry evidence and current venue safety facts are visible
    assert "RetryError" in text
    assert "ElapsedBudgetExceeded" in text
    assert "replacement ID" in text
    assert "five seconds" in text
    assert "23 September 2026 at 04:00 UTC" in text


def test_backtest_guidance_covers_current_window_boundary_semantics() -> None:
    # Given current-develop Rust backtest guidance
    text = read("skills/nt-backtest/SKILL.md")

    # When an agent reasons about a bounded run window with streamed data
    # Then post-window retention and the no-data horizon are explicit
    assert "requested_end" in text
    assert "first item past" in text
    assert "10 seconds" in text
    assert "4175a5f09a4e3563a00423f43625f9a187823f4a" in text


def test_model_and_signal_guidance_cover_current_correctness_fixes() -> None:
    # Given current-develop model and indicator guidance
    model_text = read("skills/nt-model/SKILL.md")
    signal_text = read("skills/nt-signals/SKILL.md")

    # When an agent reviews stateful calculations
    # Then both current correctness invariants are named and source-pinned
    assert "stake-weighted" in model_text
    assert "fa507199deb34430a983144e4af028046f2af926" in model_text
    assert "`reset` must preserve configuration" in signal_text
    assert "8003bed6ef75d3cea8271dc368aba2630d7f9db6" in signal_text


def test_current_baseline_abbreviation_is_consistent() -> None:
    # Given user-facing references to the current pinned develop baseline
    documents = (
        read("docs/end_to_end_guide.md"),
        read("skills/nt-dev/SKILL.md"),
        read("skills/nt-testing/SKILL.md"),
        read("skills/nt-adapters/SKILL.md"),
        read("skills/nt-adapters/references/integrations/betfair.md"),
        read("skills/nt-adapters/references/integrations/betfair_v2.md"),
    )

    # Then every abbreviated citation uses the resolvable 10-character prefix
    assert all("4692bac35" in document for document in documents)


def test_contingent_order_guidance_covers_strategy_managed_semantics() -> None:
    # Given current-develop strategy-managed contingencies (81eedc7ce)
    live = read("skills/nt-adapters/references/concepts/live.md")
    orders = read("skills/nt-trading/references/concepts/orders.md")
    builder = read("skills/nt-strategy-builder-rust/SKILL.md")

    # When an agent configures or reviews contingent order management
    # Then the flag scope, ownership boundary, and version pin are explicit
    for marker in ("manage_contingent_orders", "non-active-local"):
        assert marker in live
        assert marker in orders
        assert marker in builder
    for marker in (
        "Strategy-managed contingencies",
        "OrderEmulator",
        "cumulative filled",
        "4692bac35bb11a25eeebb8d7af4d51c55afe53ec",
    ):
        assert marker in orders
    assert "4692bac35bb11a25eeebb8d7af4d51c55afe53ec" in builder
