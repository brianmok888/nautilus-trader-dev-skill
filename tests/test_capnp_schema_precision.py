"""Behavioral regressions for the replacement of retired Cap'n Proto G2 work."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from tools import check_skill_g2_harnesses as g2


def test_current_serialization_compile_failure_stops_implementation_harness(
    tmp_path: Path,
) -> None:
    calls: list[tuple[tuple[str, ...], Path]] = []

    def runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, cwd))
        serialization_compile = (
            command[:2] == ("cargo", "check")
            and "nautilus-serialization" in command
        )
        return subprocess.CompletedProcess(command, 1 if serialization_compile else 0)

    result = g2.run_harness(
        replace(g2.HARNESSES["nt-implement"], evidence_file=None),
        repo_root=tmp_path / "repo",
        upstream_root=tmp_path / "upstream",
        runner=runner,
    )

    assert result.status is g2.RunStatus.BLOCKED
    assert result.failed_step is not None
    assert calls[-1] == (result.failed_step.command, tmp_path / "upstream")
    assert "nautilus-serialization" in result.failed_step.command


def test_validation_rejects_missing_serialization_compile() -> None:
    harness = g2.HARNESSES["nt-implement"]
    without_serialization = replace(
        harness,
        steps=tuple(
            step for step in harness.steps
            if "nautilus-serialization" not in step.command
        ),
    )

    errors = g2.validate_harnesses({"nt-implement": without_serialization})

    assert "nt-implement: harness must compile the upstream serialization owner" in errors


@pytest.mark.parametrize("capnp_available", [False, True])
def test_successful_execution_and_evidence_ignore_retired_compiler(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capnp_available: bool,
) -> None:
    monkeypatch.setattr(
        shutil, "which",
        lambda executable: "/usr/bin/capnp" if capnp_available else None,
    )
    calls: list[tuple[str, ...]] = []
    harness = replace(g2.HARNESSES["nt-implement"], owned_paths=())
    skill = tmp_path / "skills/nt-implement/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("Implementation fixture\n", encoding="utf-8")
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    monkeypatch.setattr(g2, "upstream_commit", lambda root: g2.EXPECTED_UPSTREAM_COMMIT)
    monkeypatch.setattr(g2, "upstream_is_clean", lambda root: True)

    def runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        assert cwd == upstream
        assert command[:2] == ("cargo", "check")
        return subprocess.CompletedProcess(command, 0)

    result = g2.run_harness(
        harness, repo_root=tmp_path, upstream_root=upstream, runner=runner,
    )

    assert result.status is g2.RunStatus.PASS
    assert calls == [step.command for step in harness.steps]
    assert harness.evidence_file is not None
    evidence = json.loads((tmp_path / harness.evidence_file).read_text(encoding="utf-8"))
    assert evidence["status"] == "pass"
    assert "pending_reason" not in evidence
