"""Static contract gate for current Rust DEX production guidance."""

from pathlib import Path

_SKILL = Path(__file__).parent.parent / "SKILL.md"
_CHECKLIST = Path(__file__).parent.parent / "rules/compliance_checklist.md"


def test_canonical_skill_requires_rust_client_stack() -> None:
    text = _SKILL.read_text(encoding="utf-8")
    canonical = text.split("## Migration/reference-only Python architecture", 1)[0]

    required = (
        "Phase 0: Define scope",
        "Phase 1: Build the protocol core",
        "Phase 2: Implement instruments",
        "Phase 3: Implement market data",
        "Phase 4: Implement execution",
        "Phase 5: Add optional venue capabilities",
        "Phase 6: Complete factories and projection",
        "Phase 7: Prove conformance",
        "Phase 8: Measure performance and robustness",
        "Phase 9: Finish documentation and operations",
        "nautilus_network::http::HttpClient",
        "nautilus_network::websocket::WebSocketClient",
        "Rust `InstrumentProvider`, data and execution client",
        "LiveNodeBuilder",
    )
    assert all(term in canonical for term in required)


def test_canonical_skill_keeps_python_live_out_of_production_contract() -> None:
    text = _SKILL.read_text(encoding="utf-8")
    canonical = text.split("## Migration/reference-only Python architecture", 1)[0]

    forbidden = (
        "Rust Core Infrastructure (if Rust-first)",
        "registered with `Trading" + "Node`",
        "nautilus_trader/adapters/my_dex/",
        "LiveMarketDataClient",
        "LiveExecutionClient",
        "ClientFactory",
    )
    assert all(term not in canonical for term in forbidden)


def test_production_checklist_requires_rust_factories_and_livenode_builder() -> None:
    text = _CHECKLIST.read_text(encoding="utf-8")

    required = (
        "Rust core, clients, factories, and `LiveNodeBuilder` wiring complete",
        "Rust data and execution client factory implementations compile",
        "Factories are registered through `LiveNode::builder(...)` / `LiveNodeBuilder`",
        "PyO3 callbacks",
        "Required",
    )
    assert all(term in text for term in required)
