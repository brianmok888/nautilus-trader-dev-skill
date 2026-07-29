from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_skill_g2_harnesses as g2


def test_dex_g2_pins_current_compliance_and_keeps_rust_production_checks() -> None:
    harness = g2.HARNESSES["nt-dex-adapter"]

    assert harness.steps == (
        g2.repository_step(
            g2.PYTHON,
            "tools/run_pinned_v2_pytest.py",
            "skills/nt-dex-adapter/tests/test_dex_compliance.py",
        ),
        g2.upstream_step(
            "cargo",
            "check",
            "-p",
            "nautilus-hyperliquid",
            "--examples",
            "--features",
            "examples",
        ),
        g2.upstream_step(
            "cargo",
            "check",
            "-p",
            "nautilus-blockchain",
            "--examples",
            "--features",
            "hypersync",
        ),
    )


def test_dex_g2_excludes_legacy_python_adapter_execution() -> None:
    command_text = " ".join(
        argument
        for step in g2.HARNESSES["nt-dex-adapter"].steps
        for argument in step.command
    )

    assert "test_legacy_migration_fail_closed.py" not in command_text
    assert "test_nonproduction_migration_templates.py" not in command_text
    assert "skills/nt-dex-adapter/tests " not in command_text
