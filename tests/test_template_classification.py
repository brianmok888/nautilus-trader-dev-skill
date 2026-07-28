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
REFERENCE_EXAMPLE_ROOT = Path("skills/nt-adapters/references/examples")
CLASSIFICATION_PREFIX = "# TEMPLATE_CLASSIFICATION: "
ALLOWED_CLASSIFICATIONS = (
    "supported NT V2 Python strategy; prefer Rust for performance-sensitive paths",
    "AI/advisory Python; non-production; off execution-critical paths",
    "Python research/config; non-production; off execution-critical paths",
    "Python control-plane for Rust/PyO3; non-production execution wrapper",
    "migration/reference-only; not a production default",
    "legacy executable; migration/reference-only; not a production default",
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


def test_python_tradingnode_reference_examples_are_legacy_quarantined() -> None:
    offenders: list[str] = []
    root = REPO_ROOT / REFERENCE_EXAMPLE_ROOT

    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if "TradingNode" not in text:
            continue
        relative = path.relative_to(REPO_ROOT)
        if not _is_legacy_quarantined_reference(relative):
            offenders.append(relative.as_posix())

    assert offenders == []


def test_generic_migration_banner_does_not_bless_default_live_tradingnode() -> None:
    text = (
        "# TEMPLATE_CLASSIFICATION: migration/reference-only; not a production default\n"
        "# NT v2 compatibility note: legacy Cython/v1 and Python live TradingNode\n"
        "# references in this file are retained for migration/reference-only context.\n"
        "# Prefer Rust v2/PyO3 guidance and LiveNode for new Rust-backed live work.\n\n"
        "from nautilus_trader.live.node import TradingNode\n"
        "node = TradingNode(config=config)"
    )

    assert not _has_allowed_classification(text)


def test_live_example_links_do_not_point_to_quarantined_legacy_paths() -> None:
    live_examples = REPO_ROOT / "skills/nt-live/references/examples/live"
    broken_links = [path for path in live_examples.rglob("*") if path.is_symlink() and not path.exists()]

    assert broken_links == []


def _is_legacy_quarantined_reference(relative: Path) -> bool:
    lowered_parts = {part.lower() for part in relative.parts}
    lowered_name = relative.name.lower()
    return "legacy_migration" in lowered_parts or lowered_name.startswith("legacy_")


def _has_allowed_classification(text: str) -> bool:
    header = "\n".join(text.splitlines()[:12])
    for classification in ALLOWED_CLASSIFICATIONS:
        if f"{CLASSIFICATION_PREFIX}{classification}" not in header:
            continue
        return not (
            "TradingNode" in text
            and classification == "migration/reference-only; not a production default"
        )
    return False
