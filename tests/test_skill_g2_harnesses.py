from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_skill_g2_harnesses as g2
from tools import g2_owned_content as ownership

EXPECTED_SKILLS = {
    "nt",
    "nt-adapters",
    "nt-architect",
    "nt-backtest",
    "nt-data",
    "nt-dev",
    "nt-dex-adapter",
    "nt-implement",
    "nt-learn",
    "nt-live",
    "nt-model",
    "nt-review",
    "nt-signals",
    "nt-strategy-builder",
    "nt-strategy-builder-rust",
    "nt-testing",
    "nt-trading",
}


def test_manifest_covers_exactly_all_seventeen_nt_skills() -> None:
    assert set(g2.HARNESSES) == EXPECTED_SKILLS
    assert len(g2.HARNESSES) == 17


def test_each_harness_has_a_unique_domain_scope_and_nonempty_steps() -> None:
    scopes = [harness.scope for harness in g2.HARNESSES.values()]

    assert len(scopes) == len(set(scopes))
    assert all(harness.steps for harness in g2.HARNESSES.values())
    assert all(
        step.command for harness in g2.HARNESSES.values() for step in harness.steps
    )


def test_each_harness_declares_machine_checkable_scope_tokens() -> None:
    for harness in g2.HARNESSES.values():
        assert harness.allowed_tokens
        for step in harness.steps:
            assert g2.command_matches_scope(step.command, harness.allowed_tokens)


def test_example_steps_enable_the_manifest_required_feature() -> None:
    for harness in g2.HARNESSES.values():
        for step in harness.steps:
            if "--examples" not in step.command and "--example" not in step.command:
                continue
            assert "--features" in step.command, (harness.skill, step.command)


def test_unrelated_shared_trading_compile_is_rejected() -> None:
    harness = g2.Harness(
        skill="nt-data",
        scope="upstream:crates/data",
        summary="Bad shared evidence",
        allowed_tokens=("nautilus-data",),
        steps=(
            g2.Step(
                command=(
                    "cargo",
                    "check",
                    "-p",
                    "nautilus-trading",
                    "--features",
                    "examples,high-precision",
                    "--lib",
                ),
                cwd=g2.WorkingDirectory.UPSTREAM,
            ),
        ),
    )

    errors = g2.validate_harnesses({"nt-data": harness}, expected_skills={"nt-data"})

    assert "nt-data reuses the unrelated shared nautilus-trading compile" in errors


def test_reordered_unrelated_command_is_rejected_by_scope_tokens() -> None:
    harness = g2.Harness(
        skill="nt-data",
        scope="upstream:crates/data",
        summary="Bad reordered evidence",
        allowed_tokens=("nautilus-data",),
        steps=(g2.Step(("cargo", "check", "--lib", "-p", "nautilus-trading")),),
    )

    errors = g2.validate_harnesses({"nt-data": harness}, expected_skills={"nt-data"})

    assert "nt-data command falls outside its declared scope" in errors


def test_missing_and_unknown_harnesses_fail_closed() -> None:
    harnesses = dict(g2.HARNESSES)
    harnesses.pop("nt-data")
    harnesses["nt-made-up"] = next(iter(harnesses.values()))

    errors = g2.validate_harnesses(harnesses, expected_skills=EXPECTED_SKILLS)

    assert "missing G2 harness: nt-data" in errors
    assert "unknown G2 harness: nt-made-up" in errors


def test_all_upstream_steps_pin_the_authoritative_commit() -> None:
    errors = g2.validate_harnesses(g2.HARNESSES, expected_skills=EXPECTED_SKILLS)

    assert errors == []
    assert g2.EXPECTED_UPSTREAM_COMMIT == g2.UPSTREAM_COMMIT


def test_ffi_steps_preserve_the_pinned_high_precision_bindings() -> None:
    ffi_steps = [
        step
        for harness in g2.HARNESSES.values()
        for step in harness.steps
        if step.cwd is g2.WorkingDirectory.UPSTREAM
        and any("ffi" in argument.split(",") for argument in step.command)
    ]

    assert ffi_steps
    for step in ffi_steps:
        features = step.command[step.command.index("--features") + 1].split(",")
        assert "high-precision" in features, step.command


def test_dirty_or_wrong_upstream_checkout_fails_closed(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    subprocess.run(
        ("git", "config", "user.email", "g2@example.test"), cwd=tmp_path, check=True
    )
    subprocess.run(("git", "config", "user.name", "G2 Test"), cwd=tmp_path, check=True)
    (tmp_path / "tracked").write_text("clean\n")
    subprocess.run(("git", "add", "tracked"), cwd=tmp_path, check=True)
    subprocess.run(("git", "commit", "-qm", "test"), cwd=tmp_path, check=True)

    with pytest.raises(RuntimeError, match="expected"):
        g2.assert_expected_upstream(tmp_path)

    actual = g2.upstream_commit(tmp_path)
    (tmp_path / "tracked").write_text("dirty\n")
    with pytest.raises(RuntimeError, match="uncommitted changes"):
        g2.assert_expected_upstream(tmp_path, expected_commit=actual)


def test_untracked_upstream_content_fails_closed(tmp_path: Path) -> None:
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    subprocess.run(
        ("git", "config", "user.email", "g2@example.test"), cwd=tmp_path, check=True
    )
    subprocess.run(("git", "config", "user.name", "G2 Test"), cwd=tmp_path, check=True)
    (tmp_path / "tracked").write_text("clean\n")
    subprocess.run(("git", "add", "tracked"), cwd=tmp_path, check=True)
    subprocess.run(("git", "commit", "-qm", "test"), cwd=tmp_path, check=True)
    actual = g2.upstream_commit(tmp_path)
    (tmp_path / "untracked.rs").write_text("pub const CONTAMINATION: bool = true;\n")

    assert g2.upstream_is_clean(tmp_path) is False
    with pytest.raises(RuntimeError, match="uncommitted changes"):
        g2.assert_expected_upstream(tmp_path, expected_commit=actual)


def test_supported_python_v2_harness_uses_the_pinned_upstream_runtime() -> None:
    harness = g2.HARNESSES["nt-strategy-builder"]

    assert any(
        step.cwd is g2.WorkingDirectory.UPSTREAM_PYTHON for step in harness.steps
    )
    assert any("../.venv/bin/python" in step.command for step in harness.steps)


def test_learning_example_command_has_no_stray_positional_package() -> None:
    example_step = next(
        step for step in g2.HARNESSES["nt-learn"].steps if "--example" in step.command
    )

    assert example_step.command == (
        "cargo",
        "check",
        "-p",
        "nautilus-backtest",
        "--example",
        "engine-ema-cross",
        "--features",
        "examples",
    )


def test_plan_rejects_unknown_requested_skill() -> None:
    with pytest.raises(ValueError, match="unknown requested skill: nt-made-up"):
        g2.plan_harnesses({"nt-made-up"})


def test_plan_selects_only_requested_skill() -> None:
    plan = g2.plan_harnesses({"nt-data"})

    assert [harness.skill for harness in plan] == ["nt-data"]


def test_runner_executes_every_step_for_the_selected_skill(tmp_path: Path) -> None:
    calls: list[tuple[tuple[str, ...], Path]] = []
    harness = g2.Harness(
        skill="nt-data",
        scope="upstream:crates/data",
        summary="Data crate compile",
        allowed_tokens=("nautilus-data", "compileall"),
        steps=(
            g2.Step(
                ("cargo", "check", "-p", "nautilus-data"), g2.WorkingDirectory.UPSTREAM
            ),
            g2.Step((sys.executable, "-m", "compileall", "skills/nt-data")),
        ),
    )

    def recording_runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 0)

    result = g2.run_harness(
        replace(harness, evidence_file=None),
        repo_root=tmp_path / "repo",
        upstream_root=tmp_path / "upstream",
        runner=recording_runner,
    )

    assert result.ok
    assert calls == [
        (("cargo", "check", "-p", "nautilus-data"), tmp_path / "upstream"),
        ((sys.executable, "-m", "compileall", "skills/nt-data"), tmp_path / "repo"),
    ]


def test_runner_stops_on_first_failed_step(tmp_path: Path) -> None:
    calls: list[tuple[str, ...]] = []
    harness = g2.Harness(
        skill="nt-data",
        scope="upstream:crates/data",
        summary="Data crate compile",
        allowed_tokens=("false", "must-not-run"),
        steps=(
            g2.Step(("false",)),
            g2.Step(("must-not-run",)),
        ),
    )

    def failing_runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 1)

    result = g2.run_harness(
        replace(harness, evidence_file=None),
        repo_root=tmp_path,
        upstream_root=tmp_path,
        runner=failing_runner,
    )

    assert not result.ok
    assert calls == [("false",)]


def test_runner_returns_blocked_when_step_executable_is_missing(tmp_path: Path) -> None:
    # Given a harness whose required executable is unavailable
    harness = g2.Harness(
        skill="nt-data",
        scope="repository:missing-prerequisite",
        summary="Missing prerequisite",
        allowed_tokens=("missing-tool",),
        steps=(g2.Step(("missing-tool", "--version")),),
    )

    def missing_runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        # When the harness attempts to launch that executable
        raise FileNotFoundError(command[0])

    result = g2.run_harness(
        replace(harness, evidence_file=None),
        repo_root=tmp_path / "repo",
        upstream_root=tmp_path / "upstream",
        runner=missing_runner,
    )

    # Then the result is blocked instead of crashing the full readiness run
    assert result.status is g2.RunStatus.BLOCKED
    assert result.failed_step == harness.steps[0]


def test_nt_implement_run_reports_pending_without_capnp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    harness = replace(g2.HARNESSES["nt-implement"], evidence_file=None)

    def passing_runner(
        command: tuple[str, ...], *, cwd: Path, check: bool, text: bool
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(g2.shutil, "which", lambda _name: None)

    result = g2.run_harness(
        harness,
        repo_root=tmp_path,
        upstream_root=tmp_path,
        runner=passing_runner,
    )

    assert result.status is g2.RunStatus.PENDING
    assert result.ok is False


def test_execute_prints_pending_for_nt_implement_without_capnp(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(g2, "assert_expected_upstream", lambda _root: None)
    monkeypatch.setattr(
        g2, "assert_owned_content_tracked", lambda _root, _harness: None
    )
    monkeypatch.setattr(
        g2,
        "run_harness",
        lambda *_args, **_kwargs: g2.RunResult(
            skill="nt-implement",
            status=g2.RunStatus.PENDING,
        ),
    )

    exit_code = g2.main(["--execute", "--skill", "nt-implement"])

    assert exit_code == 0
    assert "PENDING nt-implement" in capsys.readouterr().out


def test_dry_run_prints_commands_without_executing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("dry-run executed a subprocess")

    monkeypatch.setattr(g2.subprocess, "run", fail_if_called)

    exit_code = g2.main(["--dry-run", "--skill", "nt-data"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "nt-data" in output
    assert "nautilus-data" in output


def test_list_outputs_only_the_eighteen_harnesses(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exit_code = g2.main(["--list"])

    assert exit_code == 0
    assert set(capsys.readouterr().out.splitlines()) == EXPECTED_SKILLS


def test_each_harness_owns_its_skill_and_nonempty_content() -> None:
    root = g2.repo_root()
    empty_hash = ownership.owned_content_hash(root, ())
    for skill, harness in g2.HARNESSES.items():
        assert Path("skills") / skill / "SKILL.md" in harness.owned_paths
        assert g2.harness_content_hash(root, harness) != empty_hash


def test_validator_rejects_empty_owned_paths() -> None:
    harness = replace(g2.HARNESSES["nt-data"], owned_paths=())

    errors = g2.validate_harnesses({"nt-data": harness}, expected_skills={"nt-data"})

    assert "nt-data has no owned paths" in errors


def test_validator_requires_the_skill_file_in_owned_paths(tmp_path: Path) -> None:
    owned = tmp_path / "tests/test_data.py"
    owned.parent.mkdir(parents=True)
    owned.write_text("def test_placeholder():\n    pass\n")
    harness = replace(
        g2.HARNESSES["nt-data"],
        owned_paths=(Path("tests/test_data.py"),),
    )

    errors = g2.validate_harnesses(
        {"nt-data": harness}, expected_skills={"nt-data"}, root=tmp_path
    )

    assert "nt-data owned paths omit skills/nt-data/SKILL.md" in errors


def test_validator_rejects_missing_owned_paths(tmp_path: Path) -> None:
    skill = tmp_path / "skills/nt-data/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Data\n")
    harness = replace(
        g2.HARNESSES["nt-data"],
        owned_paths=(Path("skills/nt-data/SKILL.md"), Path("tests/missing.py")),
    )

    errors = g2.validate_harnesses(
        {"nt-data": harness}, expected_skills={"nt-data"}, root=tmp_path
    )

    assert "nt-data owned path does not exist: tests/missing.py" in errors


def test_validator_rejects_evidence_inside_owned_content(tmp_path: Path) -> None:
    skill = tmp_path / "skills/nt-data/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Data\n")
    evidence_root = tmp_path / "references/g2-evidence"
    evidence_root.mkdir(parents=True)
    harness = replace(
        g2.HARNESSES["nt-data"],
        owned_paths=(Path("skills/nt-data/SKILL.md"), Path("references/g2-evidence")),
    )

    errors = g2.validate_harnesses(
        {"nt-data": harness}, expected_skills={"nt-data"}, root=tmp_path
    )

    assert "nt-data evidence artifact is included in owned content" in errors


def test_missing_rust_first_harnesses_have_targeted_executable_checks() -> None:
    expected_tokens = {
        "nt-live": "nautilus-live",
        "nt-trading": "test_rust_trading_reference_sync.py",
        "nt-strategy-builder-rust": "test_rust_strategy_skill_example_compiles",
    }
    for skill, token in expected_tokens.items():
        commands = [
            argument for step in g2.HARNESSES[skill].steps for argument in step.command
        ]
        assert any(token in argument for argument in commands), (skill, commands)


def test_readiness_cards_use_the_master_prompt_gate_contract() -> None:
    labels = {
        "G0 Scope and ownership",
        "G1 Legacy labelling",
        "G2 Pinned V2 examples",
        "G3 Rust bindings/PyO3",
        "G4 Functional gates",
        "G5 References and templates",
        "G6 Operational and migration boundaries",
        "G7 Durable evidence",
    }

    for skill in sorted(EXPECTED_SKILLS):
        text = (g2.repo_root() / "skills" / skill / "SKILL.md").read_text()
        actual = {
            line.strip("|").split("|", maxsplit=1)[0].strip()
            for line in text.splitlines()
            if line.startswith(tuple(f"| G{index} " for index in range(8)))
        }
        assert actual == labels, skill


def test_readiness_cards_reference_the_targeted_harness_command() -> None:
    errors = g2.validate_readiness_cards(
        g2.repo_root(), g2.HARNESSES, require_evidence=False
    )

    assert errors == []


def test_current_readiness_evidence_matches_owned_content() -> None:
    errors = g2.validate_readiness_cards(
        g2.repo_root(),
        g2.HARNESSES,
        require_evidence=True,
        excluded_evidence={"nt"},
    )

    assert errors == []


def test_strategy_builder_harness_uses_current_v2_and_static_legacy_checks() -> None:
    harness = g2.HARNESSES["nt-strategy-builder"]
    commands = [step.command for step in harness.steps]

    assert (
        sys.executable,
        "tools/run_pinned_v2_pytest.py",
        "tests/test_strategy_builder_v2_contract.py",
    ) in commands
    assert (
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "skills/nt-strategy-builder/tests",
    ) not in commands
    assert all(
        "nautilus_trader.backtest.engine" not in " ".join(command)
        for command in commands
    )


def test_current_strategy_builder_card_records_hybrid_v2_evidence() -> None:
    card = (g2.repo_root() / "skills/nt-strategy-builder/SKILL.md").read_text()

    assert "| G2 Pinned V2 examples" in card
    assert "| Pass |" in card
    assert "tests/test_strategy_builder_v2_contract.py" in card
    assert "static migration/reference checks" in card


def test_readiness_card_requires_exactly_one_row_for_every_gate(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pending | "
        f"`{g2.evidence_command('nt-data')}` ran; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )

    errors = g2.validate_readiness_cards(
        tmp_path,
        {"nt-data": g2.HARNESSES["nt-data"]},
        require_evidence=False,
    )

    assert (
        "nt-data readiness card must declare exactly one row for each G0-G7 gate"
        in errors
    )


def test_readiness_cards_do_not_report_stale_cutover_results() -> None:
    for skill in sorted(EXPECTED_SKILLS):
        text = (g2.repo_root() / "skills" / skill / "SKILL.md").read_text()

        assert "passed 270 tests" not in text
        assert "passed 110 safety" not in text
        assert "passed 308 tests" not in text
        assert "passed 113 safety" not in text
        assert "2026-07-28:" not in text
        assert "with residual Pending gates retained below" not in text
        assert "Cutover commits `9287019`" not in text


def test_readiness_cards_use_bounded_shared_gate_claims() -> None:
    for skill in sorted(EXPECTED_SKILLS):
        text = (g2.repo_root() / "skills" / skill / "SKILL.md").read_text()

        assert "passed 25 tests" not in text
        assert "passed 24 tests" not in text
        if "| G3 Rust bindings/PyO3 |" in text:
            assert "selected Rust/PyO3 ownership" in text
        if "| G6 Operational and migration boundaries |" in text:
            assert "selected repository policy checks" in text


def test_card_evidence_is_not_a_self_certifying_status_check(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    harness = replace(g2.HARNESSES["nt-data"], evidence_file=None)

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert "nt-data has no durable evidence artifact configured" in errors


def test_all_pass_gate_rows_reject_the_card_validator_as_evidence(
    tmp_path: Path,
) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G0 Scope and ownership | Validate. | Pass | "
        "`uv run python tools/check_skill_g2_harnesses.py --check-cards` passed. |\n"
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )

    errors = g2.validate_readiness_cards(
        tmp_path,
        {"nt-data": g2.HARNESSES["nt-data"]},
        require_evidence=False,
    )

    assert any(
        "G0 readiness row uses the card validator as evidence" in error
        for error in errors
    )


def test_card_validation_rejects_missing_or_invalid_execution_evidence(
    tmp_path: Path,
) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )

    harnesses = {"nt-data": g2.HARNESSES["nt-data"]}
    missing_errors = g2.validate_readiness_cards(tmp_path, harnesses)
    assert "nt-data durable evidence artifact is missing" in missing_errors

    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "skill": "nt-data",
                "scope": g2.HARNESSES["nt-data"].scope,
                "owned_content_sha256": ownership.owned_content_hash(tmp_path, ()),
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "steps": [{"returncode": 1}],
            }
        )
    )
    invalid_errors = g2.validate_readiness_cards(tmp_path, harnesses)
    assert "nt-data durable evidence contains a failed step" in invalid_errors


def test_card_validation_accepts_blocked_status_with_a_reason(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    harness = g2.HARNESSES["nt-data"]
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Blocked | "
        f"`{g2.evidence_command('nt-data')}` blocked; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "skill": "nt-data",
                "scope": harness.scope,
                "status": "blocked",
                "blocked_reason": "required executable unavailable",
                "owned_content_sha256": ownership.owned_content_hash(
                    tmp_path, harness.owned_paths
                ),
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "verified_at": "2026-08-23T10:00:00+00:00",
                "steps": [
                    {
                        "command": list(harness.steps[0].command),
                        "cwd": harness.steps[0].cwd.value,
                        "duration_seconds": 0.1,
                        "returncode": 0,
                    }
                ],
            }
        )
    )

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert not [error for error in errors if "durable evidence" in error]


def test_card_validation_rejects_mismatched_execution_provenance(
    tmp_path: Path,
) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    harness = g2.HARNESSES["nt-data"]
    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "skill": "nt-data",
                "scope": harness.scope,
                "owned_content_sha256": ownership.owned_content_hash(
                    tmp_path, harness.owned_paths
                ),
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "steps": [
                    {
                        "command": ["cargo", "check", "-p", "nautilus-trading"],
                        "cwd": "repository",
                        "returncode": 0,
                    }
                ],
            }
        )
    )

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert "nt-data durable evidence commands do not match its harness" in errors


def test_card_validation_rejects_mismatched_owned_content_provenance(
    tmp_path: Path,
) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    harness = g2.HARNESSES["nt-data"]
    evidence_path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "skill": "nt-data",
                "scope": harness.scope,
                "status": "pass",
                "owned_content_sha256": "not-the-owned-content",
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "steps": [
                    {
                        "command": list(step.command),
                        "cwd": step.cwd.value,
                        "returncode": 0,
                    }
                    for step in harness.steps
                ],
            }
        )
    )

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert "nt-data durable evidence does not match owned skill content" in errors


def test_evidence_schema_has_no_self_referential_repository_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    skill = tmp_path / "skills/nt-data/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Data\n")
    harness = replace(
        g2.HARNESSES["nt-data"],
        owned_paths=(Path("skills/nt-data/SKILL.md"),),
    )
    monkeypatch.setattr(g2, "upstream_commit", lambda _: g2.EXPECTED_UPSTREAM_COMMIT)
    monkeypatch.setattr(g2, "upstream_is_clean", lambda _: True)

    g2.write_evidence(harness, root=tmp_path, upstream_root=tmp_path, results=[])

    assert harness.evidence_file is not None
    payload = json.loads((tmp_path / harness.evidence_file).read_text())
    assert payload["schema_version"] == 2
    assert payload["status"] == "pass"
    assert "repository_commit" not in payload
    assert payload["owned_content_sha256"] == g2.harness_content_hash(tmp_path, harness)


def test_router_harness_requires_subordinate_card_declarations() -> None:
    command = g2.HARNESSES["nt"].steps[1].command

    assert command[-1] == "--check-card-declarations"


def test_readiness_cards_do_not_embed_volatile_test_counts() -> None:
    for skill in sorted(EXPECTED_SKILLS):
        text = (g2.repo_root() / "skills" / skill / "SKILL.md").read_text()
        for line in text.splitlines():
            if not line.startswith("| G"):
                continue
            assert "passed 356 tests" not in line
            assert "2026-07-29:" not in line


def test_implement_g2_validates_capnp_without_compiling_migration_python() -> None:
    harness = g2.HARNESSES["nt-implement"]
    command_text = " ".join(
        argument for step in harness.steps for argument in step.command
    )

    assert "fixed-point-schema" in harness.scope
    assert "compileall" not in command_text
    assert "tests/test_capnp_schema_precision.py" in command_text
    assert any(step.cwd is g2.WorkingDirectory.REPOSITORY for step in harness.steps)
    assert any(step.cwd is g2.WorkingDirectory.UPSTREAM for step in harness.steps)


def test_implement_g2_passes_with_standard_capnp() -> None:
    evidence_path = g2.repo_root() / "references/g2-evidence/nt-implement.json"
    payload = json.loads(evidence_path.read_text())
    skill_text = (g2.repo_root() / "skills/nt-implement/SKILL.md").read_text()

    assert payload["status"] == "pass"
    assert "pending_reason" not in payload
    assert payload["steps"]
    assert any(
        "test_capnp_schema_precision.py" in " ".join(step["command"])
        for step in payload["steps"]
    )
    assert "| G2 Pinned V2 examples |" in skill_text
    assert "| Pass |" in skill_text

    if g2.shutil.which("capnp") is None:
        pytest.skip("capnp unavailable in this environment")


def test_strategy_builder_uses_documented_python_v2_working_directory() -> None:
    harness = g2.HARNESSES["nt-strategy-builder"]
    upstream_step = harness.steps[1]

    assert upstream_step.cwd is g2.WorkingDirectory.UPSTREAM_PYTHON
    assert upstream_step.command == (
        "../.venv/bin/python",
        "-m",
        "pytest",
        "-q",
        "tests/acceptance/test_backtest.py",
        "tests/unit/live/test_live_configs.py",
    )


def test_strategy_builder_preflight_fails_closed_for_missing_pyo3_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    upstream = tmp_path / "upstream"
    python_root = upstream / "python"
    python_root.mkdir(parents=True)
    interpreter = upstream / ".venv/bin/python"
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text("", encoding="utf-8")

    calls: list[tuple[tuple[str, ...], Path]] = []

    def fake_run(
        command: tuple[str, ...],
        *,
        cwd: Path,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, cwd))
        return subprocess.CompletedProcess(command, 1, "", "missing extension")

    with pytest.raises(
        g2.PythonV2RuntimeError, match="make sync && make build-debug"
    ) as exc_info:
        g2.assert_python_v2_runtime(upstream, runner=fake_run)

    assert "nautilus_trader._libnautilus.common" in str(exc_info.value)
    assert "--upstream-root" in str(exc_info.value)
    assert calls == [
        (
            (str(interpreter), "-c", "import nautilus_trader._libnautilus.common"),
            python_root,
        )
    ]


def test_check_card_declarations_rejects_invalid_harness_manifest(monkeypatch) -> None:
    harnesses = dict(g2.HARNESSES)
    harnesses["nt-data"] = replace(
        harnesses["nt-data"],
        scope=harnesses["nt-adapters"].scope,
    )
    monkeypatch.setattr(g2, "HARNESSES", harnesses)

    assert g2.main(["--check-card-declarations"]) == 1


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ({"upstream_clean": 1}, "upstream_clean must be a boolean"),
        ({"returncode": False}, "returncode must be an integer"),
        (
            {"verified_at": None},
            "verified_at must be a timezone-aware ISO-8601 timestamp",
        ),
        ({"duration_seconds": None}, "duration_seconds must be a nonnegative number"),
    ],
)
def test_durable_evidence_rejects_wrong_json_types(
    tmp_path: Path, mutation: dict[str, object], expected_error: str
) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    harness = g2.HARNESSES["nt-data"]
    skill_path.write_text(
        "| G2 Pinned V2 examples | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    payload: dict[str, object] = {
        "schema_version": 2,
        "skill": "nt-data",
        "scope": harness.scope,
        "status": "pass",
        "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
        "upstream_clean": True,
        "owned_content_sha256": ownership.harness_content_hash(tmp_path, harness),
        "verified_at": "2026-08-23T10:00:00+00:00",
        "steps": [
            {
                "command": list(harness.steps[0].command),
                "cwd": harness.steps[0].cwd.value,
                "duration_seconds": 0.1,
                "returncode": 0,
            }
        ],
    }
    steps = payload["steps"]
    assert isinstance(steps, list)
    step = steps[0]
    assert isinstance(step, dict)
    if "returncode" in mutation:
        step["returncode"] = mutation["returncode"]
    elif "duration_seconds" in mutation:
        step["duration_seconds"] = mutation["duration_seconds"]
    else:
        payload.update(mutation)
    evidence_path.write_text(json.dumps(payload))

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert any(expected_error in error for error in errors)


def test_strategy_builder_upstream_step_resolves_root_venv() -> None:
    steps = g2.HARNESSES["nt-strategy-builder"].steps
    upstream_steps = [s for s in steps if s.cwd is g2.WorkingDirectory.UPSTREAM_PYTHON]
    assert upstream_steps, "nt-strategy-builder must exercise the upstream venv"
    for step in upstream_steps:
        assert step.command[0].startswith("../.venv/bin/"), (
            "upstream-python steps run with cwd=<upstream>/python, so the interpreter "
            "must resolve the root-level UV_PROJECT_ENVIRONMENT venv"
        )
