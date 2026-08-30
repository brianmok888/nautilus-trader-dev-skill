from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_master_prompt_defines_complete_governance_protocol() -> None:
    prompt = (ROOT / "docs/prompts/master-prompt.md").read_text(encoding="utf-8")

    required = (
        "spec-deltas: []",
        "docs/specs/README.md",
        "schema version 1",
        "owner_stage",
        "evidence_state",
        "output_sha256",
        "verifier-owned receipts",
        "python3 tools/check_governance_receipts.py",
        "Never lower a finding's P0/P1/P2 impact",
        "Never store raw credentials",
    )
    for phrase in required:
        assert phrase in prompt

    assert "<finding-id>.txt" not in prompt
    assert "downgrade it to a P2" not in prompt


def test_approved_spec_bootstrap_defines_deterministic_deltas() -> None:
    index = (ROOT / "docs/specs/README.md").read_text(encoding="utf-8")
    workflow = (ROOT / "docs/specs/workflow-governance.md").read_text(
        encoding="utf-8"
    )
    authority = (ROOT / "docs/specs/skill-pack-authority.md").read_text(
        encoding="utf-8"
    )

    assert "Status: approved bootstrap" in index
    assert "spec-deltas: []" in index
    for operation in ("`add`", "`amend`", "`remove`"):
        assert operation in index
    assert "executable validators and tests remain primary truth" in index
    assert "receipt-ownership" in workflow
    assert "NautilusTrader development only" in authority


def test_repository_instructions_reference_governance_protocol() -> None:
    instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert "docs/specs/README.md" in instructions
    assert "docs/tracking/receipts/" in instructions
    assert "python3 tools/check_governance_receipts.py" in instructions
