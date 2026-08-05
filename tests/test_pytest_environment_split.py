from __future__ import annotations

import configparser
import subprocess
from pathlib import Path

import pytest

from tools import run_pinned_v2_pytest

ROOT = Path(__file__).resolve().parents[1]

PINNED_V2_TEST = "tests/test_ai_advisory_boundary.py"


def test_default_pytest_excludes_the_pinned_v2_only_module() -> None:
    config = configparser.ConfigParser()
    parsed = config.read(ROOT / "pytest.ini", encoding="utf-8")

    assert parsed == [str(ROOT / "pytest.ini")]
    addopts = config["pytest"]["addopts"].split()

    assert f"--ignore={PINNED_V2_TEST}" in addopts


def test_pinned_v2_runner_clears_the_default_pytest_exclusion(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    upstream_root = tmp_path / "nautilus_trader"
    python = upstream_root / "python/.venv/bin/python"
    calls: list[tuple[tuple[str, ...], Path]] = []

    monkeypatch.setattr(
        run_pinned_v2_pytest,
        "default_upstream_root",
        lambda: upstream_root,
    )

    def accept_upstream(_root: Path) -> None:
        pass

    monkeypatch.setattr(
        run_pinned_v2_pytest,
        "assert_expected_upstream",
        accept_upstream,
    )

    def recording_run(
        command: tuple[str, ...],
        *,
        cwd: Path,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        assert check is False
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", recording_run)

    assert run_pinned_v2_pytest.main([PINNED_V2_TEST]) == 0
    assert calls == [
        (
            (
                str(python),
                "-m",
                "pytest",
                "-q",
                "-o",
                "addopts=",
                PINNED_V2_TEST,
            ),
            ROOT,
        ),
    ]
