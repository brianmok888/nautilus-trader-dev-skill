from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

if __package__:
    from .upstream_baseline import (
        DEFAULT_UPSTREAM_ROOT,
        UPSTREAM_COMMIT,
        UPSTREAM_REMOTE_REFS,
    )
else:  # Direct script execution adds tools/ to sys.path.
    from upstream_baseline import (  # pyright: ignore[reportImplicitRelativeImport]
        DEFAULT_UPSTREAM_ROOT,
        UPSTREAM_COMMIT,
        UPSTREAM_REMOTE_REFS,
    )


class FreshnessStatus(Enum):
    CURRENT = "current"
    DRIFTED = "drifted"
    DIVERGED = "diverged"
    MISSING = "missing"


@dataclass(frozen=True)
class RefFreshness:
    name: str
    current_commit: str | None
    status: FreshnessStatus
    commits_ahead: int | None
    pinned_is_ancestor: bool | None
    error: str | None = None


@dataclass(frozen=True)
class FreshnessReport:
    upstream_root: Path
    pinned_commit: str
    refs: tuple[RefFreshness, ...]

    @property
    def ok(self) -> bool:
        return all(ref.status is FreshnessStatus.CURRENT for ref in self.refs)


def _git(
    upstream_root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=upstream_root,
        check=check,
        capture_output=True,
        text=True,
    )


def _resolve_ref(upstream_root: Path, ref: str) -> str:
    return _git(upstream_root, "rev-parse", "--verify", ref).stdout.strip()


def _is_ancestor(upstream_root: Path, ancestor: str, descendant: str) -> bool:
    result = _git(
        upstream_root,
        "merge-base",
        "--is-ancestor",
        ancestor,
        descendant,
        check=False,
    )
    return result.returncode == 0


def _commits_ahead(
    upstream_root: Path,
    pinned_commit: str,
    current_commit: str,
) -> int | None:
    result = _git(
        upstream_root,
        "rev-list",
        "--count",
        f"{pinned_commit}..{current_commit}",
        check=False,
    )
    if result.returncode != 0:
        return None
    return int(result.stdout.strip())


def check_ref(upstream_root: Path, pinned_commit: str, ref: str) -> RefFreshness:
    try:
        current_commit = _resolve_ref(upstream_root, ref)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return RefFreshness(ref, None, FreshnessStatus.MISSING, None, None, str(exc))

    if current_commit == pinned_commit:
        return RefFreshness(ref, current_commit, FreshnessStatus.CURRENT, 0, True)

    pinned_is_ancestor = _is_ancestor(upstream_root, pinned_commit, current_commit)
    ahead = _commits_ahead(upstream_root, pinned_commit, current_commit) if pinned_is_ancestor else None
    status = FreshnessStatus.DRIFTED if pinned_is_ancestor else FreshnessStatus.DIVERGED
    return RefFreshness(ref, current_commit, status, ahead, pinned_is_ancestor)


def build_freshness_report(
    upstream_root: Path,
    pinned_commit: str = UPSTREAM_COMMIT,
    refs: Iterable[str] = UPSTREAM_REMOTE_REFS,
) -> FreshnessReport:
    return FreshnessReport(
        upstream_root=upstream_root,
        pinned_commit=pinned_commit,
        refs=tuple(check_ref(upstream_root, pinned_commit, ref) for ref in refs),
    )


def _report_to_jsonable(report: FreshnessReport) -> dict[str, object]:
    payload = asdict(report)
    payload["upstream_root"] = str(report.upstream_root)
    for ref in payload["refs"]:  # type: ignore[index]
        ref["status"] = ref["status"].value
    return payload


def render_json_report(report: FreshnessReport) -> str:
    return json.dumps(_report_to_jsonable(report), indent=2, sort_keys=True) + "\n"


def _short(commit: str | None) -> str:
    return commit[:12] if commit else "<unresolved>"


def render_text_report(report: FreshnessReport) -> str:
    lines = [
        "NautilusTrader upstream freshness report",
        f"Upstream checkout: {report.upstream_root}",
        f"Pinned reproducible baseline: {_short(report.pinned_commit)} ({report.pinned_commit})",
        "Current upstream refs:",
    ]
    for ref in report.refs:
        detail = f"{ref.name}: {ref.status.value} at {_short(ref.current_commit)}"
        if ref.commits_ahead is not None:
            detail += f" ({ref.commits_ahead} commits ahead of pinned baseline)"
        if ref.error:
            detail += f" [{ref.error}]"
        lines.append(f"- {detail}")
    lines.append("This command is read-only and does not update tools/upstream_baseline.py.")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-root", type=Path, default=DEFAULT_UPSTREAM_ROOT)
    parser.add_argument("--pinned-commit", default=UPSTREAM_COMMIT)
    parser.add_argument(
        "--ref",
        dest="refs",
        action="append",
        help="Upstream ref to compare; repeatable. Defaults to the baseline freshness refs.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    refs = tuple(args.refs) if args.refs else UPSTREAM_REMOTE_REFS
    report = build_freshness_report(args.upstream_root, args.pinned_commit, refs)
    if args.format == "json":
        print(render_json_report(report), end="")
    else:
        print(render_text_report(report), end="")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
