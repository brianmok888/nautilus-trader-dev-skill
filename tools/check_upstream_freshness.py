from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).resolve().parents[1] / "references/upstream-delta-review.json"

if __package__:
    from .upstream_baseline import (
        UPSTREAM_COMMIT,
        UPSTREAM_REMOTE_REFS,
        default_upstream_root,
    )
else:  # Direct script execution adds tools/ to sys.path.
    from upstream_baseline import (  # pyright: ignore[reportImplicitRelativeImport]
        UPSTREAM_COMMIT,
        UPSTREAM_REMOTE_REFS,
        default_upstream_root,
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
    changed_commits: tuple[str, ...] = ()
    changed_paths: tuple[str, ...] = ()
    error: str | None = None


@dataclass(frozen=True)
class FreshnessReport:
    upstream_root: Path
    pinned_commit: str
    refs: tuple[RefFreshness, ...]
    manifest_path: Path
    manifest_reviewed: bool
    manifest_error: str | None
    nightly_contained: bool

    @property
    def ok(self) -> bool:
        develop = next(
            (ref for ref in self.refs if ref.name.rsplit("/", 1)[-1] == "develop"),
            None,
        )
        return (
            self.manifest_reviewed
            and develop is not None
            and develop.status in {FreshnessStatus.CURRENT, FreshnessStatus.DRIFTED}
            and all(ref.status is not FreshnessStatus.MISSING for ref in self.refs)
            and self.nightly_contained
        )


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


def _changed_commits(
    upstream_root: Path,
    pinned_commit: str,
    current_commit: str,
) -> tuple[str, ...]:
    result = _git(
        upstream_root,
        "rev-list",
        "--reverse",
        f"{pinned_commit}..{current_commit}",
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def _changed_paths(
    upstream_root: Path,
    pinned_commit: str,
    current_commit: str,
) -> tuple[str, ...]:
    result = _git(
        upstream_root,
        "diff",
        "--name-only",
        f"{pinned_commit}..{current_commit}",
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def _commit_subject(upstream_root: Path, commit: str) -> str:
    return _git(upstream_root, "show", "-s", "--format=%s", commit).stdout.strip()


def _commit_paths(upstream_root: Path, commit: str) -> tuple[str, ...]:
    result = _git(
        upstream_root,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "--root",
        commit,
    )
    return tuple(line for line in result.stdout.splitlines() if line)


def check_ref(upstream_root: Path, pinned_commit: str, ref: str) -> RefFreshness:
    try:
        current_commit = _resolve_ref(upstream_root, ref)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        return RefFreshness(
            ref,
            None,
            FreshnessStatus.MISSING,
            None,
            None,
            error=str(exc),
        )

    if current_commit == pinned_commit:
        return RefFreshness(ref, current_commit, FreshnessStatus.CURRENT, 0, True)

    pinned_is_ancestor = _is_ancestor(upstream_root, pinned_commit, current_commit)
    ahead = _commits_ahead(upstream_root, pinned_commit, current_commit) if pinned_is_ancestor else None
    status = FreshnessStatus.DRIFTED if pinned_is_ancestor else FreshnessStatus.DIVERGED
    changed_commits = (
        _changed_commits(upstream_root, pinned_commit, current_commit)
        if pinned_is_ancestor
        else ()
    )
    changed_paths = (
        _changed_paths(upstream_root, pinned_commit, current_commit)
        if pinned_is_ancestor
        else ()
    )
    return RefFreshness(
        ref,
        current_commit,
        status,
        ahead,
        pinned_is_ancestor,
        changed_commits,
        changed_paths,
    )


def _manifest_error(
    manifest_path: Path,
    pinned_commit: str,
    refs: tuple[RefFreshness, ...],
    upstream_root: Path,
) -> str | None:
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"cannot read review manifest {manifest_path}: {exc}"
    if not isinstance(payload, dict):
        return "review manifest root must be an object"
    if payload.get("schema_version") != 1:
        return "review manifest schema_version must be 1"
    if payload.get("pinned_commit") != pinned_commit:
        return "review manifest pinned_commit does not match the requested baseline"

    develop = next(
        (ref for ref in refs if ref.name.rsplit("/", 1)[-1] == "develop"),
        None,
    )
    if develop is None or develop.current_commit is None:
        return "review manifest requires a resolved develop ref"
    if payload.get("reviewed_commit") != develop.current_commit:
        return "review manifest reviewed_commit does not match the resolved develop ref"

    deltas = payload.get("deltas")
    if not isinstance(deltas, list):
        return "review manifest deltas must be an array"
    reviewed: set[str] = set()
    for index, delta in enumerate(deltas):
        if not isinstance(delta, dict):
            return f"review manifest deltas[{index}] must be an object"
        commit = delta.get("commit")
        if not isinstance(commit, str):
            return f"review manifest deltas[{index}].commit must be a string"
        subject = delta.get("subject")
        if not isinstance(subject, str) or not subject:
            return f"review manifest deltas[{index}].subject must be a non-empty string"
        paths = delta.get("upstream_paths")
        if not isinstance(paths, list) or not paths or not all(
            isinstance(path, str) and path for path in paths
        ):
            return f"review manifest deltas[{index}].upstream_paths must be non-empty strings"
        try:
            actual_subject = _commit_subject(upstream_root, commit)
            actual_paths = set(_commit_paths(upstream_root, commit))
        except (subprocess.CalledProcessError, FileNotFoundError):
            return f"review manifest deltas[{index}].commit is not resolvable upstream"
        if subject != actual_subject:
            return f"review manifest deltas[{index}].subject does not match upstream commit"
        if set(paths) != actual_paths:
            return f"review manifest deltas[{index}].upstream_paths do not match upstream commit"
        affected = delta.get("affected_files")
        rationale = delta.get("no_impact_rationale")
        has_affected = isinstance(affected, list) and bool(affected) and all(
            isinstance(path, str) and path for path in affected
        )
        has_rationale = isinstance(rationale, str) and bool(rationale.strip())
        if has_affected == has_rationale:
            return (
                f"review manifest deltas[{index}] must provide exactly one of "
                "affected_files or no_impact_rationale"
            )
        reviewed.add(commit)

    expected = set(develop.changed_commits)
    missing = sorted(expected - reviewed)
    extra = sorted(reviewed - expected)
    if missing:
        return "review manifest is missing delta commits: " + ", ".join(missing)
    if extra:
        return "review manifest contains commits outside the delta: " + ", ".join(extra)
    return None


def build_freshness_report(
    upstream_root: Path,
    pinned_commit: str = UPSTREAM_COMMIT,
    refs: Iterable[str] = UPSTREAM_REMOTE_REFS,
    manifest_path: Path = DEFAULT_MANIFEST,
) -> FreshnessReport:
    checked_refs = tuple(check_ref(upstream_root, pinned_commit, ref) for ref in refs)
    manifest_error = _manifest_error(
        manifest_path,
        pinned_commit,
        checked_refs,
        upstream_root,
    )
    try:
        nightly_commit = _resolve_ref(upstream_root, "origin/nightly")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            nightly_commit = _resolve_ref(upstream_root, "nightly")
        except (subprocess.CalledProcessError, FileNotFoundError):
            nightly_commit = None
    develop = next(
        (ref for ref in checked_refs if ref.name.rsplit("/", 1)[-1] == "develop"),
        None,
    )
    if nightly_commit is None or develop is None or develop.current_commit is None:
        nightly_contained = False
    else:
        nightly_contained = _is_ancestor(
            upstream_root,
            nightly_commit,
            develop.current_commit,
        )
    return FreshnessReport(
        upstream_root=upstream_root,
        pinned_commit=pinned_commit,
        refs=checked_refs,
        manifest_path=manifest_path,
        manifest_reviewed=manifest_error is None,
        manifest_error=manifest_error,
        nightly_contained=nightly_contained,
    )


def _report_to_jsonable(report: FreshnessReport) -> dict[str, object]:
    payload = asdict(report)
    payload["upstream_root"] = str(report.upstream_root)
    payload["manifest_path"] = str(report.manifest_path)
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
        for commit in ref.changed_commits:
            lines.append(f"  commit: {commit}")
        for path in ref.changed_paths:
            lines.append(f"  path: {path}")
    manifest_status = "reviewed" if report.manifest_reviewed else "invalid"
    lines.append(f"Delta review manifest: {manifest_status} ({report.manifest_path})")
    lines.append(
        "Nightly history containment: "
        + ("covered by origin/develop" if report.nightly_contained else "not covered")
    )
    if report.manifest_error:
        lines.append(f"Manifest error: {report.manifest_error}")
    lines.append("This command is read-only and does not update tools/upstream_baseline.py.")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-root", type=Path, default=default_upstream_root())
    parser.add_argument("--pinned-commit", default=UPSTREAM_COMMIT)
    parser.add_argument(
        "--ref",
        dest="refs",
        action="append",
        help="Upstream ref to compare; repeatable. Defaults to the baseline freshness refs.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    refs = tuple(args.refs) if args.refs else UPSTREAM_REMOTE_REFS
    report = build_freshness_report(
        args.upstream_root,
        args.pinned_commit,
        refs,
        args.manifest,
    )
    if args.format == "json":
        print(render_json_report(report), end="")
    else:
        print(render_text_report(report), end="")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
