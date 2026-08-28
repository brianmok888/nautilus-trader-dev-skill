from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_adapter_guidance_uses_the_official_ten_phase_dependency_structure() -> None:
    expected_phases = (
        "Phase 1: Define scope",
        "Phase 2: Build the protocol core",
        "Phase 3: Implement instruments",
        "Phase 4: Implement market data",
        "Phase 5: Implement execution",
        "Phase 6: Add optional venue capabilities",
        "Phase 7: Complete factories and projection",
        "Phase 8: Prove conformance",
        "Phase 9: Measure performance and robustness",
        "Phase 10: Finish documentation and operations",
    )

    for relative_path in (
        "skills/nt-learn/curriculum/12-adapter-development.md",
        "skills/nt-adapters/SKILL.md",
        "skills/nt-dex-adapter/SKILL.md",
        "skills/nt-implement/SKILL.md",
        "skills/nt-review/AGENTS.md",
    ):
        text = read(relative_path)
        positions = [text.index(phase) for phase in expected_phases]
        assert positions == sorted(positions), relative_path
        assert "7-Phase" not in text
        assert "7-phase" not in text

    readme = read("README.md")
    assert "7-phase" not in readme
    assert "7 Phases" not in readme


def test_g2_guidance_limits_cargo_check_to_compilation_evidence() -> None:
    for relative_path in (
        "skills/nt-adapters/SKILL.md",
        "skills/nt-implement/SKILL.md",
        "skills/nt-review/AGENTS.md",
    ):
        text = read(relative_path)
        assert "compilation only" in text, relative_path
        for excluded_proof in ("spec", "testnet", "resilience", "fuzz", "operations"):
            assert excluded_proof in text, (relative_path, excluded_proof)


def test_polymarket_guidance_uses_instrument_fee_schedule_and_probability_model() -> (
    None
):
    text = read("references/integrations/polymarket.md")

    assert "instrument.fee_schedule.rate" in text
    assert "instrument.fee_schedule.exponent" in text
    assert "ProbabilityPriceFeeModel" in text
    assert "Crypto" in text and "0.07" in text
    assert "Sports" in text and "0.05" in text
    assert "exponent" in text and "1" in text
    assert "other exponents" in text
    assert "rebate behavior" in text
    # Upstream at 8e51f957c ships a Rust adapter fee model for backtests
    # (nautilus_polymarket::models::PolymarketFeeModel, reads rate/rebateRate/
    # exponent/takerOnly). The old prohibition predates that type; the mirror
    # is sync-enforced to carry the upstream Backtest fee model section.
    assert "nautilus_polymarket::models::PolymarketFeeModel" in text
    assert "future exponent" not in text.lower()


def test_lighter_restart_guidance_requires_cached_venue_order_identity() -> None:
    text = read("references/integrations/lighter.md")

    assert "31-bit" in text or "31‑bit" in text
    assert "probe" in text.lower()
    assert "collision" in text.lower()
    assert "VenueOrderId" in text
    assert "cached" in text.lower()
    assert "restart" in text.lower()
    assert "never infer" in text.lower()
    assert "ClientOrderId" in text
    assert "numeric index alone" in text.lower()
