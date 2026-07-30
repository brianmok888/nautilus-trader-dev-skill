from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".pytest_cache", ".ruff_cache", "__pycache__"}
MARKDOWN_LINK = re.compile(r"(?<!!)(?:\[[^\]]+\]|\[[^\]]+\]\[[^\]]*\])\(([^)]+)\)")


def test_full_repo_passes_ruff_quality_gate() -> None:
    # Given: the repository contains Python templates, examples, tools, and tests.
    # When: Ruff checks the complete tree rather than only recently changed files.
    result = subprocess.run(
        [
            "uv",
            "run",
            "--with",
            "ruff",
            "ruff",
            "check",
            "--no-force-exclude",
            ".",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: every Python file in the repo is lint-clean.
    assert result.returncode == 0, result.stdout + result.stderr


def test_active_ai_and_dex_migration_lanes_pass_ruff_quality_gate() -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--with",
            "ruff",
            "ruff",
            "check",
            "--no-force-exclude",
            "skills/nt-evomap-integration/python_sidecar",
            "skills/nt-evomap-integration/templates/advisory_actor.py",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_reference_python_compiles() -> None:
    result = subprocess.run(
        ["uv", "run", "python", "-m", "compileall", "-q", "references"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_reference_python_passes_ruff_without_force_exclusion() -> None:
    result = subprocess.run(
        [
            "uv",
            "run",
            "--with",
            "ruff",
            "ruff",
            "check",
            "--no-force-exclude",
            "references",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_ruff_quality_gate_has_explicit_snapshot_and_template_policy() -> None:
    config = (REPO_ROOT / "ruff.toml").read_text(encoding="utf-8")

    assert '"references/**/*.py"' not in config
    assert '"skills/*/references/**/*.py"' in config
    assert '"skills/*/templates/**/*.py"' not in config
    assert '"skills/nt-adapters/templates/**/*.py"' in config
    assert '"skills/nt-implement/templates/**/*.py"' in config
    assert '"skills/nt-strategy-builder/templates/**/*.py"' in config
    assert '"skills/nt-evomap-integration/templates/**/*.py"' not in config
    assert '"skills/*/migration_reference/**/*.py"' not in config
    assert '"skills/nt-dex-adapter/migration_reference/**/*.py"' in config
    assert '"skills/nt-strategy-builder/tests/**/*.py"' in config


def test_markdown_relative_links_resolve_within_repo() -> None:
    # Given: the repo vendors partial NautilusTrader reference trees for skill context.
    markdown_files = [
        path
        for path in REPO_ROOT.rglob("*.md")
        if not IGNORED_PARTS.intersection(path.relative_to(REPO_ROOT).parts)
    ]

    # When: markdown links point at local relative paths.
    broken_links = []
    for markdown_file in markdown_files:
        text = markdown_file.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK.finditer(text):
            target = match.group(1).strip().split("#", 1)[0]
            if not target or _is_external_or_anchor(target):
                continue
            resolved_target = (markdown_file.parent / target).resolve()
            if not resolved_target.exists():
                if _is_pinned_upstream_snapshot(markdown_file, text):
                    continue
                broken_links.append(
                    f"{markdown_file.relative_to(REPO_ROOT)} -> {target}"
                )

    # Then: every relative link resolves locally; copied partial trees use absolute upstream URLs instead.
    assert broken_links == []


def test_pinned_upstream_snapshot_detection_is_narrow(tmp_path: Path) -> None:
    snapshot = tmp_path / "references/developer_guide/snapshot.md"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        "---\n"
        "source_repo: nautechsystems/nautilus_trader/docs/developer_guide/rust.md\n"
        "source_commit: " + "a" * 40 + "\n"
        "target: NautilusTrader develop developer guide source snapshot\n"
        "legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only\n"
        "---\n",
        encoding="utf-8",
    )
    ordinary = tmp_path / "ordinary.md"
    ordinary.write_text("source_commit: " + "a" * 40, encoding="utf-8")

    assert _is_pinned_upstream_snapshot(snapshot, snapshot.read_text())
    assert not _is_pinned_upstream_snapshot(ordinary, ordinary.read_text())

    missing_policy = tmp_path / "references/developer_guide/missing-policy.md"
    missing_policy.write_text(
        snapshot.read_text().replace(
            "legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only\n",
            "",
        ),
        encoding="utf-8",
    )
    assert not _is_pinned_upstream_snapshot(missing_policy, missing_policy.read_text())


def _is_external_or_anchor(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#", "<"))


def _is_pinned_upstream_snapshot(path: Path, text: str) -> bool:
    return (
        "references/developer_guide" in path.as_posix()
        and "source_repo: nautechsystems/nautilus_trader/docs/developer_guide/" in text
        and re.search(r"^source_commit: [0-9a-f]{40}$", text, re.MULTILINE) is not None
        and "target: NautilusTrader develop developer guide source snapshot" in text
        and "legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only"
        in text
    )
