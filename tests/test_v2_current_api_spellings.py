from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

ACTIVE_GUIDANCE_DIRS = (
    "skills",
    "references/concepts",
    "references/integrations",
    "references/api_reference",
    "references/developer_guide",
)

REMOVED_SPELLINGS = (
    "OrderBookDepth10",
    "OrderBookDepth10DataWrangler",
    "subscribe_book_depth10",
    "unsubscribe_book_depth10",
    "book_depth10_to_arrow_record_batch_bytes",
    "load_tardis_depth10",
    "stream_tardis_depth10",
    "TardisDepth10StreamIterator",
)

def active_guidance_files() -> list[Path]:
    files: list[Path] = []
    for rel in ACTIVE_GUIDANCE_DIRS:
        root = REPO_ROOT / rel
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix in {".md", ".py", ".rs", ".json"}:
                files.append(path)
    return files

def is_snapshot_governed(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return rel.startswith("references/developer_guide/")

def is_migration_labelled(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return "migration_reference/" in rel or "legacy_migration/" in rel

def test_active_guidance_drops_removed_depth10_spellings() -> None:
    offenders: list[str] = []
    for path in active_guidance_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if is_snapshot_governed(path):
            continue
        if is_migration_labelled(path):
            continue
        for token in REMOVED_SPELLINGS:
            if token in text:
                offenders.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {token}")
    assert offenders == []

def test_depth10_config_value_taught_as_depth() -> None:
    tardis_guide = (REPO_ROOT / "skills/nt-data/references/guides/tardis.md").read_text(encoding="utf-8")
    assert '"depth"' in tardis_guide
    assert 'book_snapshot_output": "depth10"' not in tardis_guide
    assert "stream_tardis_depth_from_snapshot25" in tardis_guide

def test_nautilusdatatype_teaching_uses_current_variants() -> None:
    combined = "\n".join(
        (REPO_ROOT / rel).read_text(encoding="utf-8")
        for rel in (
            "skills/nt-backtest/SKILL.md",
            "skills/nt-backtest/references/guides/run_rust_backtest.md",
            "skills/nt-backtest/references/examples/rust_backtest/node_ema_cross.rs",
        )
    )
    assert "NautilusDataType::OrderBook" not in combined
    assert "persistence import NautilusDataType" not in combined
    assert "from nautilus_trader.persistence import NautilusDataType" not in combined
