from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from tools.upstream_baseline import DEFAULT_UPSTREAM_ROOT, UPSTREAM_COMMIT
except ModuleNotFoundError:  # Direct script execution adds tools/ to sys.path.
    from upstream_baseline import DEFAULT_UPSTREAM_ROOT, UPSTREAM_COMMIT

EXPECTED_UPSTREAM_COMMIT = UPSTREAM_COMMIT
UPSTREAM_GUIDE = Path("docs/developer_guide")
LOCAL_GUIDE = Path("references/developer_guide")


@dataclass(frozen=True)
class SyncResult:
    missing: tuple[Path, ...]
    extra: tuple[Path, ...]
    changed: tuple[Path, ...]

    @property
    def ok(self) -> bool:
        return not (self.missing or self.extra or self.changed)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def upstream_commit(upstream_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=upstream_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def strip_local_metadata(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    body = text[end + len("\n---\n") :]
    return body.removeprefix("\n")


def markdown_files(root: Path) -> set[Path]:
    return {path.relative_to(root) for path in root.glob("*.md") if path.is_file()}


def compare_snapshot(local_root: Path, upstream_root: Path) -> SyncResult:
    local_files = markdown_files(local_root)
    upstream_files = markdown_files(upstream_root)
    changed = tuple(
        relative
        for relative in sorted(local_files & upstream_files)
        if strip_local_metadata((local_root / relative).read_text(encoding="utf-8"))
        != (upstream_root / relative).read_text(encoding="utf-8")
    )
    return SyncResult(
        missing=tuple(sorted(upstream_files - local_files)),
        extra=tuple(sorted(local_files - upstream_files)),
        changed=changed,
    )


def format_paths(paths: tuple[Path, ...]) -> str:
    return "\n".join(f"  - {path.as_posix()}" for path in paths)


def report_sync(result: SyncResult) -> str:
    if result.ok:
        return "Developer guide snapshot bodies match pinned upstream."
    parts = ["Developer guide snapshot differs from pinned upstream."]
    if result.missing:
        parts.append("Missing local files:\n" + format_paths(result.missing))
    if result.extra:
        parts.append("Extra local files:\n" + format_paths(result.extra))
    if result.changed:
        parts.append("Changed local files:\n" + format_paths(result.changed))
    return "\n".join(parts)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare developer-guide snapshot bodies with the pinned, reproducible "
            "NautilusTrader checkout. This check intentionally does not report "
            "moving upstream drift; use tools/check_upstream_freshness.py for that."
        )
    )
    parser.add_argument("--upstream-root", type=Path, default=DEFAULT_UPSTREAM_ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    actual_commit = upstream_commit(args.upstream_root)
    if actual_commit != EXPECTED_UPSTREAM_COMMIT:
        print(
            f"Upstream checkout is {actual_commit}, expected {EXPECTED_UPSTREAM_COMMIT}: "
            f"{args.upstream_root}",
            file=sys.stderr,
        )
        return 1
    result = compare_snapshot(repo_root() / LOCAL_GUIDE, args.upstream_root / UPSTREAM_GUIDE)
    print(report_sync(result))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
