from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")

def test_dex_python_live_templates_are_quarantined_and_not_approvable() -> None:
    agents = read("skills/nt-dex-adapter/AGENTS.md")
    checklist = read("skills/nt-dex-adapter/rules/compliance_checklist.md")

    assert "legacy_migration/dex_data_client.py" in agents
    assert "legacy_migration/dex_exec_client.py" in agents
    assert "Rust `LiveNodeBuilder`" in agents
    assert "Rust Core (if applicable)" not in checklist
    assert "N/A if Python-only" not in checklist
    assert "Python-only" in checklist
    assert "cannot receive APPROVED FOR USE" in checklist

def test_dex_canonical_skill_is_unconditionally_rust_first() -> None:
    text = read("skills/nt-dex-adapter/SKILL.md")
    canonical = text.split("## Migration/reference-only Python architecture", 1)[0]

    assert "Rust Core Infrastructure (if Rust-first)" not in canonical
    assert "Phase 0: Define scope" in canonical
    assert "Phase 1: Build the protocol core" in canonical
    assert "Rust `InstrumentProvider`, data and execution client" in canonical
    assert "LiveNodeBuilder" in canonical
    assert "registered with `TradingNode`" not in canonical
    assert "nautilus_trader/adapters/my_dex/" not in canonical

def test_dex_current_compliance_does_not_import_migration_executables() -> None:
    current = read("skills/nt-dex-adapter/tests/test_dex_compliance.py")
    migration = read(
        "skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py"
    )
    checklist = read("skills/nt-dex-adapter/rules/compliance_checklist.md")

    assert "legacy_migration" not in current
    assert "MyDEXLiveDataClientFactory" not in current
    assert "MyDEXLiveExecClientFactory" not in current
    assert "legacy_migration" in migration
    assert "non-production migration smoke" in checklist
    assert "does not gate production approval" in checklist

def test_dex_current_compliance_loads_no_classified_python_templates() -> None:
    current = read("skills/nt-dex-adapter/tests/test_dex_compliance.py")
    migration = read(
        "skills/nt-dex-adapter/tests/test_nonproduction_migration_templates.py"
    )

    classified_templates = {
        path.name
        for path in (REPO_ROOT / "skills/nt-dex-adapter/templates").rglob("*.py")
        if path.read_text(encoding="utf-8").startswith("# TEMPLATE_CLASSIFICATION:")
    }
    loaded_by_current = {
        template
        for template in classified_templates
        if template.removesuffix(".py") in current
    }

    assert loaded_by_current == set()
    assert "dex_config" in migration
    assert "dex_instrument_provider" in migration
