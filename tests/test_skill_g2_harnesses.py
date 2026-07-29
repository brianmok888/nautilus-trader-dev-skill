from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_skill_g2_harnesses as g2

EXPECTED_SKILLS = {
    "nt",
    "nt-adapters",
    "nt-architect",
    "nt-backtest",
    "nt-data",
    "nt-dev",
    "nt-dex-adapter",
    "nt-evomap-integration",
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


def test_manifest_covers_exactly_all_eighteen_nt_skills() -> None:
    assert set(g2.HARNESSES) == EXPECTED_SKILLS
    assert len(g2.HARNESSES) == 18


def test_each_harness_has_a_unique_domain_scope_and_nonempty_steps() -> None:
    scopes = [harness.scope for harness in g2.HARNESSES.values()]

    assert len(scopes) == len(set(scopes))
    assert all(harness.steps for harness in g2.HARNESSES.values())
    assert all(step.command for harness in g2.HARNESSES.values() for step in harness.steps)


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
    subprocess.run(("git", "config", "user.email", "g2@example.test"), cwd=tmp_path, check=True)
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


def test_supported_python_v2_harness_uses_the_pinned_upstream_runtime() -> None:
    harness = g2.HARNESSES["nt-strategy-builder"]

    assert any(step.cwd is g2.WorkingDirectory.UPSTREAM for step in harness.steps)
    assert any("python/.venv/bin/python" in step.command for step in harness.steps)


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
            g2.Step(("cargo", "check", "-p", "nautilus-data"), g2.WorkingDirectory.UPSTREAM),
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


def test_list_outputs_only_the_eighteen_harnesses(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = g2.main(["--list"])

    assert exit_code == 0
    assert set(capsys.readouterr().out.splitlines()) == EXPECTED_SKILLS


def test_each_harness_owns_its_skill_and_nonempty_content() -> None:
    root = g2.repo_root()
    empty_hash = g2.owned_content_hash(root, ())
    for skill, harness in g2.HARNESSES.items():
        assert Path("skills") / skill / "SKILL.md" in harness.owned_paths
        assert g2.owned_content_hash(root, harness.owned_paths) != empty_hash


def test_validator_rejects_empty_owned_paths() -> None:
    harness = replace(g2.HARNESSES["nt-data"], owned_paths=())

    errors = g2.validate_harnesses(
        {"nt-data": harness}, expected_skills={"nt-data"}
    )

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
        commands = [argument for step in g2.HARNESSES[skill].steps for argument in step.command]
        assert any(token in argument for argument in commands), (skill, commands)


def test_readiness_cards_reference_the_targeted_harness_command() -> None:
    errors = g2.validate_readiness_cards(
        g2.repo_root(), g2.HARNESSES, require_evidence=False
    )

    assert errors == []


def test_readiness_cards_do_not_report_stale_cutover_results() -> None:
    for skill in sorted(EXPECTED_SKILLS):
        text = (g2.repo_root() / "skills" / skill / "SKILL.md").read_text()

        assert "passed 270 tests" not in text
        assert "passed 110 safety" not in text
        assert "with residual Pending gates retained below" not in text
        assert "Cutover commits `9287019`" not in text


def test_card_evidence_is_not_a_self_certifying_status_check(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 V2 example validation | Validate. | Pass | "
        f"`{g2.evidence_command('nt-data')}` passed; evidence "
        "`references/g2-evidence/nt-data.json`. |\n"
    )
    harness = replace(g2.HARNESSES["nt-data"], evidence_file=None)

    errors = g2.validate_readiness_cards(tmp_path, {"nt-data": harness})

    assert "nt-data has no durable evidence artifact configured" in errors


def test_card_validation_rejects_missing_or_invalid_execution_evidence(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 V2 example validation | Validate. | Pass | "
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
                "owned_content_sha256": g2.owned_content_hash(tmp_path, ()),
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "steps": [{"returncode": 1}],
            }
        )
    )
    invalid_errors = g2.validate_readiness_cards(tmp_path, harnesses)
    assert "nt-data durable evidence contains a failed step" in invalid_errors


def test_card_validation_rejects_mismatched_execution_provenance(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 V2 example validation | Validate. | Pass | "
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
                "owned_content_sha256": g2.owned_content_hash(
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


def test_card_validation_rejects_mismatched_owned_content_provenance(tmp_path: Path) -> None:
    skill_path = tmp_path / "skills/nt-data/SKILL.md"
    skill_path.parent.mkdir(parents=True)
    evidence_path = tmp_path / "references/g2-evidence/nt-data.json"
    evidence_path.parent.mkdir(parents=True)
    skill_path.write_text(
        "| G2 V2 example validation | Validate. | Pass | "
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
                "owned_content_sha256": "not-the-owned-content",
                "upstream_commit": g2.EXPECTED_UPSTREAM_COMMIT,
                "upstream_clean": True,
                "steps": [
                    {"command": list(step.command), "cwd": step.cwd.value, "returncode": 0}
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
    assert "repository_commit" not in payload
    assert payload["owned_content_sha256"] == g2.owned_content_hash(
        tmp_path, harness.owned_paths
    )


def test_router_harness_requires_subordinate_card_declarations() -> None:
    command = g2.HARNESSES["nt"].steps[1].command

    assert command[-1] == "--check-card-declarations"


def test_ai_advisory_skill_stays_python_and_off_execution_paths() -> None:
    text = (g2.repo_root() / "skills/nt-evomap-integration/SKILL.md").read_text()

    assert "AI/advisory lane remains Python" in text
    assert "Nautilus remains the only execution authority" in text
    assert "No external network I/O" in text
    assert "Every accepted or rejected suggestion must be traceable" in text


def test_ai_advisory_contract_forbids_order_authority_and_hot_handler_io() -> None:
    errors = g2.validate_ai_advisory_contract(g2.repo_root())

    assert errors == []


def test_ai_advisory_contract_rejects_execution_authority(tmp_path: Path) -> None:
    skill = tmp_path / "skills/nt-evomap-integration/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Nautilus remains the only execution authority\n"
        "No external network I/O\n"
        "timeout fallback approval gate\n"
        "Every accepted or rejected suggestion must be traceable\n"
        "self.submit_order(order)\n"
    )

    errors = g2.validate_ai_advisory_contract(tmp_path)

    assert any("forbidden execution authority" in error for error in errors)


def test_ai_advisory_contract_rejects_market_handler_and_publication_capabilities(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "skills/nt-evomap-integration/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Nautilus remains the only execution authority\n"
        "No external network I/O\n"
        "timeout fallback approval gate\n"
        "Every accepted or rejected suggestion must be traceable\n"
    )
    leak = skill.parent / "templates/leak.py"
    leak.parent.mkdir()
    leak.write_text(
        "class UnsafeActor:\n"
        "    def on_bar(self, bar):\n"
        "        self.publish_signal(name='unsafe', value=bar)\n"
    )

    errors = g2.validate_ai_advisory_contract(tmp_path)

    assert any("market handler" in error for error in errors)
    assert any("publication capability" in error for error in errors)


def test_ai_advisory_contract_scans_nested_owned_surfaces(tmp_path: Path) -> None:
    skill = tmp_path / "skills/nt-evomap-integration/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Nautilus remains the only execution authority\n"
        "No external network I/O\n"
        "timeout fallback approval gate\n"
        "Every accepted or rejected suggestion must be traceable\n"
    )
    leak = skill.parent / "templates/leak.py"
    leak.parent.mkdir()
    leak.write_text("self.submit_order(order)\n")

    errors = g2.validate_ai_advisory_contract(tmp_path)

    assert any("templates/leak.py" in error for error in errors)


def test_ai_advisory_contract_allows_networking_in_external_proxy_surface(
    tmp_path: Path,
) -> None:
    skill = tmp_path / "skills/nt-evomap-integration/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "Nautilus remains the only execution authority\n"
        "No external network I/O\n"
        "timeout fallback approval gate\n"
        "Every accepted or rejected suggestion must be traceable\n"
    )
    proxy = skill.parent / "templates/external_proxy.py"
    proxy.parent.mkdir()
    proxy.write_text(
        "import requests\n\n"
        "class ExternalProxy:\n"
        "    def send(self, payload):\n"
        "        return requests.post('http://127.0.0.1', json=payload)\n"
    )

    errors = g2.validate_ai_advisory_contract(tmp_path)

    assert errors == []


def test_ai_advisory_harness_uses_pinned_v2_runner() -> None:
    harness = g2.HARNESSES["nt-evomap-integration"]

    assert any("tools/run_pinned_v2_pytest.py" in step.command for step in harness.steps)
    assert Path("tools/run_pinned_v2_pytest.py") in harness.owned_paths
    assert Path("tests/test_ai_advisory_boundary.py") in harness.owned_paths


def test_ai_advisory_g2_owns_entire_skill_directory() -> None:
    harness = g2.HARNESSES["nt-evomap-integration"]

    assert Path("skills/nt-evomap-integration") in harness.owned_paths


def test_ai_advisory_contract_accepts_canonical_advisory_template() -> None:
    errors = g2.validate_ai_advisory_contract(g2.repo_root())

    assert errors == []
    assert (
        g2.repo_root()
        / "skills/nt-evomap-integration/templates/advisory_actor.py"
    ).is_file()
