from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOTS = [
    Path("skills/nt-implement/templates"),
    Path("skills/nt-adapters/templates"),
    Path("skills/nt-dex-adapter/templates"),
    Path("skills/nt-backtest/templates"),
    Path("skills/nt-signals/templates"),
    Path("skills/nt-trading/templates"),
    Path("skills/nt-strategy-builder/templates"),
]
CLASSIFICATION_PREFIX = "# TEMPLATE_CLASSIFICATION: "
ALLOWED_CLASSIFICATIONS = (
    "supported NT V2 Python strategy; prefer Rust for performance-sensitive paths",
    "AI/advisory Python; non-production; off execution-critical paths",
    "Python research/config; non-production; off execution-critical paths",
    "Python control-plane for Rust/PyO3; non-production execution wrapper",
    "migration/reference-only; not a production default",
)

SUPPORTED_PYTHON_STRATEGY_TEMPLATES = {
    Path("skills/nt-implement/templates/strategy.py"),
    Path("skills/nt-trading/templates/strategy.py"),
}


def test_python_templates_are_explicitly_classified() -> None:
    unclassified: list[str] = []

    for template_root in TEMPLATE_ROOTS:
        root = REPO_ROOT / template_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            if not _has_allowed_classification(text):
                unclassified.append(path.relative_to(REPO_ROOT).as_posix())

    assert unclassified == []


def test_current_python_strategy_templates_are_not_migration_only() -> None:
    expected = (
        f"{CLASSIFICATION_PREFIX}supported NT V2 Python strategy; "
        "prefer Rust for performance-sensitive paths"
    )
    for relative in SUPPORTED_PYTHON_STRATEGY_TEMPLATES:
        header = "\n".join((REPO_ROOT / relative).read_text().splitlines()[:12])
        assert expected in header


def _has_allowed_classification(text: str) -> bool:
    header = "\n".join(text.splitlines()[:12])
    return any(
        f"{CLASSIFICATION_PREFIX}{classification}" in header
        for classification in ALLOWED_CLASSIFICATIONS
    )
