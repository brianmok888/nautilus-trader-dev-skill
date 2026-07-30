from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

_CACHE_NAMES = frozenset({"__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"})
_EVIDENCE_ROOT = Path("references/g2-evidence")


class OwnedContentError(RuntimeError):
    """Raised when G2 ownership cannot be resolved safely."""


class HarnessOwnership(Protocol):
    @property
    def skill(self) -> str: ...

    @property
    def owned_paths(self) -> tuple[Path, ...]: ...


@dataclass(frozen=True, slots=True)
class _Record:
    logical_path: Path
    entry_type: str
    payload: bytes = b""


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def _relative_to_root(root: Path, path: Path) -> Path:
    try:
        return _absolute(path).relative_to(root)
    except ValueError as exc:
        raise OwnedContentError(f"owned path escapes repository: {path}") from exc


def _is_excluded(root: Path, path: Path) -> bool:
    relative = _relative_to_root(root, path)
    return (
        relative == _EVIDENCE_ROOT
        or _EVIDENCE_ROOT in relative.parents
        or any(part in _CACHE_NAMES for part in relative.parts)
        or relative.suffix == ".pyc"
    )


def _walk_owned(
    root: Path,
    path: Path,
    logical_path: Path,
    active: frozenset[Path],
) -> tuple[list[_Record], set[Path]]:
    absolute = _absolute(path)
    _ = _relative_to_root(root, absolute)
    if _is_excluded(root, absolute):
        return [], set()
    if absolute in active:
        raise OwnedContentError(f"owned symlink cycle at {logical_path.as_posix()}")
    try:
        metadata = absolute.lstat()
    except FileNotFoundError as exc:
        raise OwnedContentError(f"owned path is broken: {logical_path.as_posix()}") from exc

    sources = {_relative_to_root(root, absolute)}
    if stat.S_ISLNK(metadata.st_mode):
        target_text = os.readlink(absolute)
        target = _absolute(absolute.parent / target_text)
        _ = _relative_to_root(root, target)
        record = _Record(logical_path, "symlink", os.fsencode(target_text))
        if _is_excluded(root, target):
            return [record], sources
        target_records, target_sources = _walk_owned(
            root,
            target,
            logical_path,
            active | {absolute},
        )
        return [record, *target_records], sources | target_sources

    if stat.S_ISREG(metadata.st_mode):
        return [_Record(logical_path, "file", absolute.read_bytes())], sources

    if stat.S_ISDIR(metadata.st_mode):
        records: list[_Record] = []
        for child in sorted(absolute.iterdir(), key=lambda candidate: candidate.name):
            child_records, child_sources = _walk_owned(
                root,
                child,
                logical_path / child.name,
                active | {absolute},
            )
            records.extend(child_records)
            sources.update(child_sources)
        return records, sources

    raise OwnedContentError(f"unsupported owned entry: {logical_path.as_posix()}")


def _minimal_roots(paths: Iterable[Path]) -> tuple[Path, ...]:
    roots: list[Path] = []
    for path in paths:
        if path in roots or any(parent == path or parent in path.parents for parent in roots):
            continue
        roots = [candidate for candidate in roots if path not in candidate.parents]
        roots.append(path)
    return tuple(roots)


def harness_owned_paths(harness: HarnessOwnership) -> tuple[Path, ...]:
    skill_root = Path("skills") / harness.skill
    return _minimal_roots((skill_root, *harness.owned_paths))


def _records_and_sources(
    root: Path,
    paths: Iterable[Path],
) -> tuple[list[_Record], set[Path]]:
    absolute_root = _absolute(root)
    records: list[_Record] = []
    sources: set[Path] = set()
    for relative in _minimal_roots(paths):
        path_records, path_sources = _walk_owned(
            absolute_root,
            absolute_root / relative,
            relative,
            frozenset(),
        )
        records.extend(path_records)
        sources.update(path_sources)
    return records, sources


def owned_content_hash(root: Path, paths: tuple[Path, ...]) -> str:
    records, _ = _records_and_sources(root, paths)
    digest = hashlib.sha256()
    for record in sorted(records, key=lambda item: (item.logical_path.as_posix(), item.entry_type)):
        digest.update(record.logical_path.as_posix().encode())
        digest.update(b"\0")
        digest.update(record.entry_type.encode())
        digest.update(b"\0")
        digest.update(record.payload)
        digest.update(b"\0")
    return digest.hexdigest()


def harness_content_hash(root: Path, harness: HarnessOwnership) -> str:
    return owned_content_hash(root, harness_owned_paths(harness))


def untracked_owned_paths(root: Path, harness: HarnessOwnership) -> tuple[Path, ...]:
    _, sources = _records_and_sources(root, harness_owned_paths(harness))
    result = subprocess.run(
        ("git", "ls-files", "--others", "--exclude-standard", "-z"),
        cwd=root,
        check=True,
        capture_output=True,
    )
    untracked = {Path(os.fsdecode(item)) for item in result.stdout.split(b"\0") if item}
    return tuple(sorted(untracked & sources))


def assert_owned_content_tracked(root: Path, harness: HarnessOwnership) -> None:
    untracked = untracked_owned_paths(root, harness)
    if untracked:
        joined = ", ".join(path.as_posix() for path in untracked)
        raise OwnedContentError(f"{harness.skill} owns untracked content: {joined}")
