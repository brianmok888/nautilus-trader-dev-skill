from pathlib import Path

from tools.upstream_baseline import default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]

def snapshot_files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }

def test_nt_signals_analysis_snapshot_matches_pinned_upstream() -> None:
    local = REPO_ROOT / "skills/nt-signals/references/rust/analysis"
    upstream = default_upstream_root() / "crates/analysis"

    assert snapshot_files(local) == snapshot_files(upstream)
