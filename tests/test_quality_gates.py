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
        ["uv", "run", "--with", "ruff", "ruff", "check", "."],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    # Then: every Python file in the repo is lint-clean.
    assert result.returncode == 0, result.stdout + result.stderr


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
                broken_links.append(
                    f"{markdown_file.relative_to(REPO_ROOT)} -> {target}"
                )

    # Then: every relative link resolves locally; copied partial trees use absolute upstream URLs instead.
    assert broken_links == []


def _is_external_or_anchor(target: str) -> bool:
    return (
        target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
        or target.startswith("#")
        or target.startswith("<")
    )
