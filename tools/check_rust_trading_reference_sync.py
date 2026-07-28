from __future__ import annotations

import argparse
import filecmp
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

if __package__:
    from .upstream_baseline import UPSTREAM_COMMIT, default_upstream_root
else:  # Direct script execution adds tools/ to sys.path.
    from upstream_baseline import (  # pyright: ignore[reportImplicitRelativeImport]
        UPSTREAM_COMMIT,
        default_upstream_root,
    )

EXPECTED_UPSTREAM_COMMIT = UPSTREAM_COMMIT
UPSTREAM_EXAMPLES = Path("crates/trading/src/examples")
LOCAL_EXAMPLES = Path("skills/nt-trading/references/examples/rust_trading/examples")
CARGO_CHECK_COMMAND = (
    "cargo",
    "check",
    "-p",
    "nautilus-trading",
    "--features",
    "examples,high-precision",
    "--lib",
)


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


def assert_expected_upstream(upstream_root: Path) -> None:
    actual = upstream_commit(upstream_root)
    if actual != EXPECTED_UPSTREAM_COMMIT:
        raise SystemExit(
            f"Upstream checkout is {actual}, expected {EXPECTED_UPSTREAM_COMMIT}: {upstream_root}"
        )


def relative_files(root: Path) -> set[Path]:
    return {
        path.relative_to(root)
        for path in root.rglob("*")
        if path.is_file()
    }


def compare_examples(local_root: Path, upstream_root: Path) -> SyncResult:
    local_files = relative_files(local_root)
    upstream_files = relative_files(upstream_root)
    common = sorted(local_files & upstream_files)
    changed = tuple(
        rel for rel in common if not filecmp.cmp(local_root / rel, upstream_root / rel, shallow=False)
    )
    return SyncResult(
        missing=tuple(sorted(upstream_files - local_files)),
        extra=tuple(sorted(local_files - upstream_files)),
        changed=changed,
    )


def sync_examples(local_root: Path, upstream_root: Path) -> None:
    if local_root.exists():
        shutil.rmtree(local_root)
    shutil.copytree(upstream_root, local_root)


def format_paths(paths: tuple[Path, ...]) -> str:
    return "\n".join(f"  - {path.as_posix()}" for path in paths)


def report_sync(result: SyncResult) -> str:
    if result.ok:
        return "Rust trading references match pinned upstream examples."
    parts = ["Rust trading references differ from pinned upstream examples."]
    if result.missing:
        parts.append("Missing local files:\n" + format_paths(result.missing))
    if result.extra:
        parts.append("Extra local files:\n" + format_paths(result.extra))
    if result.changed:
        parts.append("Changed local files:\n" + format_paths(result.changed))
    return "\n".join(parts)


def copy_upstream_for_compile(
    upstream_root: Path, local_examples: Path, temp_root: Path
) -> Path:
    worktree = temp_root / "nautilus_trader"
    ignore = shutil.ignore_patterns(".git", "target", ".venv", "node_modules")
    shutil.copytree(upstream_root, worktree, ignore=ignore)
    destination = worktree / UPSTREAM_EXAMPLES
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(local_examples, destination)
    return worktree


def compile_examples(upstream_root: Path, local_examples: Path) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="nt-rust-reference-compile-") as temp_dir:
        worktree = copy_upstream_for_compile(upstream_root, local_examples, Path(temp_dir))
        return subprocess.run(
            CARGO_CHECK_COMMAND,
            cwd=worktree,
            check=False,
            capture_output=True,
            text=True,
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Rust trading reference examples against a pinned NautilusTrader upstream checkout."
    )
    parser.add_argument("--upstream-root", type=Path, default=default_upstream_root())
    parser.add_argument("--sync", action="store_true", help="Replace local references with exact upstream files.")
    parser.add_argument("--compile", action="store_true", help="Compile local references inside a temporary upstream checkout.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = repo_root()
    local_examples = root / LOCAL_EXAMPLES
    upstream_examples = args.upstream_root / UPSTREAM_EXAMPLES

    assert_expected_upstream(args.upstream_root)
    if args.sync:
        sync_examples(local_examples, upstream_examples)

    result = compare_examples(local_examples, upstream_examples)
    print(report_sync(result))
    if not result.ok:
        return 1

    if args.compile:
        compile_result = compile_examples(args.upstream_root, local_examples)
        if compile_result.stdout:
            print(compile_result.stdout)
        if compile_result.stderr:
            print(compile_result.stderr, file=sys.stderr)
        return compile_result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
