from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REQUIRED_COMMANDS = (
    "uv run pytest -q --ignore=tests/test_quality_gates.py",
    "uv run pytest -q tests/test_quality_gates.py",
    "uv run --with ruff ruff check .",
    "uv run python tools/check_legacy_labelling.py",
    "uv run python tools/check_dev_guide_sync.py",
    "uv run python tools/check_dev_guide_snapshot_sync.py",
    "uv run python tools/check_upstream_freshness.py",
    "uv run python tools/check_skill_g2_harnesses.py --check-cards",
    "python3 -m compileall -q tools tests skills/nt-evomap-integration/python_sidecar/brainstorming_evomap",
    "git diff --check",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _current_sha(repo_root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _manifest_path(repo_root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _validate_artifact(
    repo_root: Path,
    artifact: object,
    field: str,
) -> tuple[str, ...]:
    if not isinstance(artifact, dict):
        return (f"{field}: expected an object",)
    raw_path = artifact.get("path")
    expected_hash = artifact.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        return (f"{field}.path: expected a non-empty string",)
    if not isinstance(expected_hash, str):
        return (f"{field}.sha256: expected a string",)
    path = _manifest_path(repo_root, raw_path)
    try:
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        return (f"{field}.path: cannot read {path}: {exc}",)
    if actual_hash != expected_hash:
        return (f"{field}.sha256: does not match artifact content",)
    return ()


def _validate_review_artifact(
    repo_root: Path,
    artifact: object,
    field: str,
    repo_sha: str,
    decision: str,
) -> tuple[str, ...]:
    errors = list(_validate_artifact(repo_root, artifact, field))
    if errors or not isinstance(artifact, dict):
        return tuple(errors)
    raw_path = artifact.get("path")
    if not isinstance(raw_path, str):
        return tuple(errors)
    text = _manifest_path(repo_root, raw_path).read_text(encoding="utf-8")
    if repo_sha not in text:
        errors.append(f"{field}: does not name exact repository SHA {repo_sha}")
    if decision not in text:
        errors.append(f"{field}: does not contain required decision {decision}")
    return tuple(errors)


def _validate_command_artifact(
    repo_root: Path,
    artifact: object,
    field: str,
    repo_sha: str,
    command: str,
    returncode: int,
) -> tuple[str, ...]:
    errors = list(_validate_artifact(repo_root, artifact, field))
    if errors or not isinstance(artifact, dict):
        return tuple(errors)
    raw_path = artifact.get("path")
    if not isinstance(raw_path, str):
        return tuple(errors)
    lines = _manifest_path(repo_root, raw_path).read_text(encoding="utf-8").splitlines()
    required_lines = (
        ("COMMAND:", f"COMMAND: {command}", "exact command"),
        ("REPO_SHA:", f"REPO_SHA: {repo_sha}", f"exact repository SHA {repo_sha}"),
        ("RETURN_CODE:", f"RETURN_CODE: {returncode}", f"return code {returncode}"),
    )
    for prefix, expected, description in required_lines:
        matching = [line for line in lines if line.startswith(prefix)]
        if matching != [expected]:
            errors.append(f"{field}: does not name {description}")
    return tuple(errors)


def validate_attestation(attestation_path: Path, repo_root: Path) -> tuple[str, ...]:
    try:
        payload = json.loads(attestation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (f"attestation: cannot read JSON: {exc}",)
    if not isinstance(payload, dict):
        return ("attestation: root must be an object",)

    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    repo_sha = payload.get("repo_sha")
    if repo_sha != _current_sha(repo_root):
        errors.append("repo_sha: does not match current repository HEAD")
    exact_sha = repo_sha if isinstance(repo_sha, str) else "<invalid>"

    manifest = payload.get("manifest")
    if not isinstance(manifest, dict):
        errors.append("manifest: expected an object")
    else:
        raw_path = manifest.get("path")
        expected_hash = manifest.get("sha256")
        if not isinstance(raw_path, str) or not raw_path:
            errors.append("manifest.path: expected a non-empty string")
        elif not isinstance(expected_hash, str):
            errors.append("manifest.sha256: expected a string")
        else:
            path = _manifest_path(repo_root, raw_path)
            try:
                actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError as exc:
                errors.append(f"manifest.path: cannot read {path}: {exc}")
            else:
                if actual_hash != expected_hash:
                    errors.append("manifest.sha256: does not match manifest content")

    commands = payload.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append("commands: expected at least one command result")
    else:
        recorded_commands: set[str] = set()
        for index, command in enumerate(commands):
            if not isinstance(command, dict):
                errors.append(f"commands[{index}]: expected an object")
                continue
            if not isinstance(command.get("command"), str) or not command["command"]:
                errors.append(f"commands[{index}].command: expected a non-empty string")
            else:
                recorded_commands.add(command["command"])
            if command.get("returncode") != 0:
                errors.append(f"commands[{index}].returncode: expected 0")
            command_text = command.get("command")
            returncode = command.get("returncode")
            if isinstance(command_text, str) and isinstance(returncode, int):
                errors.extend(
                    _validate_command_artifact(
                        repo_root,
                        command.get("output"),
                        f"commands[{index}].output",
                        exact_sha,
                        command_text,
                        returncode,
                    ),
                )
        missing_commands = sorted(set(REQUIRED_COMMANDS) - recorded_commands)
        if missing_commands:
            errors.append("commands: missing required commands: " + ", ".join(missing_commands))

    code_reviewer = payload.get("code_reviewer")
    if not isinstance(code_reviewer, dict) or code_reviewer.get("verdict") != "APPROVE":
        errors.append("code_reviewer.verdict: expected APPROVE")
    else:
        errors.extend(
            _validate_review_artifact(
                repo_root,
                code_reviewer.get("artifact"),
                "code_reviewer.artifact",
                exact_sha,
                "VERDICT: APPROVE",
            ),
        )
    architect = payload.get("architect")
    if not isinstance(architect, dict) or architect.get("status") != "CLEAR":
        errors.append("architect.status: expected CLEAR")
    else:
        errors.extend(
            _validate_review_artifact(
                repo_root,
                architect.get("artifact"),
                "architect.artifact",
                exact_sha,
                "ARCHITECTURE: CLEAR",
            ),
        )
    return tuple(errors)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an externally produced exact-SHA cutover attestation.",
    )
    parser.add_argument("--attestation", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    errors = validate_attestation(args.attestation, _repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Cutover attestation valid: {args.attestation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
