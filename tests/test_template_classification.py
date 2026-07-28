from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_EXAMPLE_ROOT = Path("skills/nt-adapters/references/examples")
CLASSIFICATION_PREFIX = "# TEMPLATE_CLASSIFICATION: "
ALLOWED_CLASSIFICATIONS = (
    "AI/advisory Python; non-production; off execution-critical paths",
    "migration/reference-only; not a production default",
    "legacy executable; migration/reference-only; not a production default",
)

MIGRATION_ONLY_PYTHON_STRATEGY_TEMPLATES = {
    Path("skills/nt-implement/templates/strategy.py"),
    Path("skills/nt-trading/templates/strategy.py"),
}


def test_python_templates_are_explicitly_classified() -> None:
    unclassified: list[str] = []

    for path in sorted((REPO_ROOT / "skills").glob("nt*/**/templates/**/*.py")):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if not _has_allowed_classification(text):
            unclassified.append(path.relative_to(REPO_ROOT).as_posix())

    assert unclassified == []


def test_active_ai_python_templates_live_under_canonical_ai_skill() -> None:
    offenders: list[str] = []
    canonical_root = REPO_ROOT / "skills/nt-evomap-integration"
    for path in sorted((REPO_ROOT / "skills").glob("nt*/**/*.py")):
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        if "TEMPLATE_CLASSIFICATION: AI/advisory Python" not in header:
            continue
        if not path.is_relative_to(canonical_root):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []


def test_all_non_ai_python_skill_files_are_migration_namespaced_or_classified() -> None:
    offenders: list[str] = []
    canonical_ai_root = REPO_ROOT / "skills/nt-evomap-integration"
    for path in sorted((REPO_ROOT / "skills").glob("nt*/**/*.py")):
        if "__pycache__" in path.parts or "tests" in path.parts:
            continue
        if path.is_relative_to(canonical_ai_root):
            continue
        relative = path.relative_to(REPO_ROOT)
        header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        migration_namespace = (
            "legacy_migration" in relative.parts
            or "references" in relative.parts
            or "templates" in relative.parts
        )
        migration_label = any(
            f"{CLASSIFICATION_PREFIX}{classification}" in header
            for classification in (
                "migration/reference-only; not a production default",
                "legacy executable; migration/reference-only; not a production default",
            )
        )
        if not migration_namespace and not migration_label:
            offenders.append(relative.as_posix())

    assert offenders == []


def test_non_ai_python_strategy_templates_are_migration_only() -> None:
    expected = f"{CLASSIFICATION_PREFIX}migration/reference-only; not a production default"
    for relative in MIGRATION_ONLY_PYTHON_STRATEGY_TEMPLATES:
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


def test_active_live_namespace_does_not_alias_quarantined_legacy_paths() -> None:
    live_examples = REPO_ROOT / "skills/nt-live/references/examples/live"
    offenders: list[str] = []
    if not live_examples.exists():
        return
    for path in live_examples.rglob("*"):
        if not path.is_symlink():
            continue
        resolved = path.resolve(strict=False)
        if "legacy_migration" in resolved.parts:
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []


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
