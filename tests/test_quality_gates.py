from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tools.upstream_baseline import default_upstream_root

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

    owned = tmp_path / "skills/nt-adapters/references/guides/rust.md"
    owned.parent.mkdir(parents=True)
    owned.write_text(snapshot.read_text())
    assert _is_pinned_upstream_snapshot(owned, owned.read_text())
    assert not _is_pinned_upstream_snapshot(
        owned, owned.read_text().replace("a" * 40, "not-a-commit")
    )
    assert not _is_pinned_upstream_snapshot(
        owned,
        owned.read_text().replace("nautechsystems/nautilus_trader/", "other/project/"),
    )
    for original, replacement in (
        ("docs/developer_guide/rust.md", "docs/developer_guide/../rust.md"),
        ("docs/developer_guide/rust.md", "docs/developer_guide/"),
        ("source_commit: " + "a" * 40, "source_commit: " + "a" * 41),
        ("legacy_policy:", "other_policy:"),
        ("target:", "other_target:"),
    ):
        assert not _is_pinned_upstream_snapshot(
            owned, owned.read_text().replace(original, replacement)
        )
    assert not _is_pinned_upstream_snapshot(
        owned, "---\ntitle: ordinary guide\n---\n" + owned.read_text()
    )

def test_snapshot_link_exemption_preserves_ordinary_broken_links(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(globals(), "REPO_ROOT", tmp_path)
    owned = tmp_path / "skills/nt-adapters/references/guides/official_adapter_spec.md"
    owned.parent.mkdir(parents=True)
    metadata = (
        "---\n"
        "source_repo: nautechsystems/nautilus_trader/docs/developer_guide/adapters.md\n"
        "source_commit: " + "a" * 40 + "\n"
        "target: NautilusTrader develop developer guide source snapshot\n"
        "legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only\n"
        "---\n"
    )
    owned.write_text(metadata + "[Upstream guide](missing.md)\n", encoding="utf-8")
    test_markdown_relative_links_resolve_within_repo()
    owned.write_text("[Ordinary guide](missing.md)\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="missing.md"):
        test_markdown_relative_links_resolve_within_repo()


def _is_external_or_anchor(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "#", "<"))


def _is_pinned_upstream_snapshot(path: Path, text: str) -> bool:
    copied_examples = (
        REPO_ROOT / "skills/nt-trading/references/examples/rust_trading/examples"
    )
    if path.is_relative_to(copied_examples):
        source = (
            default_upstream_root() / "crates/trading/src/examples"
            / path.relative_to(copied_examples)
        )
        return source.is_file() and source.read_text(encoding="utf-8") == text
    metadata = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if metadata is None:
        return False
    header = metadata.group(1)
    return (
        re.search(
            r"(?:^|/)(?:references/developer_guide|skills/nt[^/]*/references/guides)/[^/]+\.md$",
            path.as_posix(),
        ) is not None
        and re.search(
            r"^source_repo: nautechsystems/nautilus_trader/docs/developer_guide/[A-Za-z0-9_-]+\.md$",
            header, re.MULTILINE,
        ) is not None
        and re.search(r"^source_commit: [0-9a-f]{40}$", header, re.MULTILINE) is not None
        and "target: NautilusTrader develop developer guide source snapshot" in header.splitlines()
        and "legacy_policy: source-pinned upstream snapshot; historical guidance is migration/reference-only"
        in header.splitlines()
    )


def test_static_quality_runner_includes_findings_schema() -> None:
    text = (REPO_ROOT / "tools/check_static_quality.py").read_text(encoding="utf-8")

    assert "tools/check_findings_schema.py" in text
    assert "tools/check_legacy_labelling.py" in text
    assert "--check-cards" in text


def test_static_quality_runner_covers_binding_deterministic_validators() -> None:
    from tools.check_static_quality import CHECKS

    declared = {command[0] for command in CHECKS}
    required = {
        "tools/check_dev_guide_sync.py",
        "tools/check_dev_guide_snapshot_sync.py",
        "tools/check_rust_trading_reference_sync.py",
        "tools/check_upstream_freshness.py",
        "tools/check_legacy_labelling.py",
        "tools/check_findings_schema.py",
        "tools/markdown_lane_contract.py",
        "tools/template_classification.py",
    }

    assert required <= declared
    assert all((REPO_ROOT / command[0]).is_file() for command in CHECKS)
    freshness = next(command for command in CHECKS if command[0].endswith("upstream_freshness.py"))

    assert freshness == (
        "tools/check_upstream_freshness.py",
        "--format",
        "json",
    )
