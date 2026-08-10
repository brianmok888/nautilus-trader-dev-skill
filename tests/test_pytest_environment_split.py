from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools import run_pinned_v2_pytest

ROOT = Path(__file__).resolve().parents[1]

PINNED_V2_TEST = "skills/nt-dex-adapter/tests/test_instrument_parsing.py"


def test_pinned_v2_runner_clears_repository_pytest_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    upstream_root = tmp_path / "nautilus_trader"
    python = upstream_root / "python/.venv/bin/python"
    python.parent.mkdir(parents=True)
    python.touch()
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


def test_pinned_v2_runner_uses_host_python_for_static_tests_when_upstream_env_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    upstream_root = tmp_path / "nautilus_trader"
    calls: list[tuple[tuple[str, ...], Path]] = []

    def accept_upstream(_root: Path) -> None:
        pass

    monkeypatch.setattr(run_pinned_v2_pytest, "default_upstream_root", lambda: upstream_root)
    monkeypatch.setattr(run_pinned_v2_pytest, "assert_expected_upstream", accept_upstream)

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

    test_path = "skills/nt-dex-adapter/tests/test_dex_compliance.py"
    assert run_pinned_v2_pytest.main([test_path]) == 0
    assert calls == [
        (
            (sys.executable, "-m", "pytest", "-q", "-o", "addopts=", test_path),
            ROOT,
        ),
    ]


def test_host_python_allowlist_rejects_runtime_and_unknown_tests() -> None:
    assert run_pinned_v2_pytest.uses_host_python(
        ["skills/nt-dex-adapter/tests/test_dex_compliance.py"],
    )
    assert not run_pinned_v2_pytest.uses_host_python([PINNED_V2_TEST])
    assert not run_pinned_v2_pytest.uses_host_python(["tests/unknown_static_test.py"])
    assert not run_pinned_v2_pytest.uses_host_python(
        ["skills/nt-dex-adapter/tests/test_dex_compliance.py", PINNED_V2_TEST],
    )
