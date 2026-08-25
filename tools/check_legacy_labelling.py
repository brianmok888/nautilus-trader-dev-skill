from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Final

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_dev_guide_sync as canonical

SCOPED_PATTERNS: Final = (
    "skills/**/*.md",
    "references/**/*.md",
    "templates/**/*.md",
)
LEGACY_PATTERNS: Final = (
    re.compile(
        r"(?<![A-Za-z0-9_])(?:Cython|cdef|cpdef|cimport)(?![A-Za-z0-9_])",
        re.IGNORECASE,
    ),
    re.compile(r"(?<![A-Za-z0-9_])\.pyx(?![A-Za-z0-9_])", re.IGNORECASE),
    re.compile(r"(?<!/api/)(?<![A-Za-z0-9_])v1(?![A-Za-z0-9_.])", re.IGNORECASE),
)
LABEL_PATTERNS: Final = (
    re.compile(r"\blegacy\s*:", re.IGNORECASE),
    re.compile(r"\bmigration(?:/reference-only| note| reference)\b", re.IGNORECASE),
    re.compile(r"\bNT v2 compatibility note\b", re.IGNORECASE),
)
LABEL_DISTANCE: Final = 5

# Symbols and Python import paths verified absent from the pinned/reviewed V2
# upstream baseline (develop 73d4dd5b): the flat `nautilus_trader.model` surface,
# `testkit` naming, and the Live*Config → Execution/DataClientConfig renames.
REMOVED_V2_SYMBOL_PATTERNS: Final = (
    re.compile(
        r"(?<![A-Za-z0-9_])(?:LiveExecEngineConfig|LiveExecClientConfig|LiveDataClientConfig|LiveExecFactoryConfig|LiveDataFactoryConfig|FillModelConfig|ImportableFillModelConfig|DeriveExecClientConfig|DeriveDataClientConfig)(?![A-Za-z0-9_])",
    ),
    re.compile(
        r"\bfrom\s+nautilus_trader\.(?:backtest\.(?:engine|models|config)"
        r"|core\.(?:rust\.model[A-Za-z0-9_.]*|data[A-Za-z0-9_.]*|message[A-Za-z0-9_.]*)"
        r"|common\.(?:actor|component|providers)"
        r"|test_kit[A-Za-z0-9_.]*"
        r"|analysis\.statistic[A-Za-z0-9_.]*"
        r"|model\.(?:identifiers|objects|enums|custom|currencies|data|events|instruments|orders)"
        r"|data\.(?:config|messages)"
        r"|live\.(?:config|node)"
        r"|execution\.(?:messages|reports)"
        r"|persistence\.(?:catalog|config|wranglers)"
        r"|serialization\.(?:arrow\.serializer|base)"
        r"|trading\.(?:strategy|algorithm)"
        r"|examples\.algorithms\.twap)\s+import",
    ),
    re.compile(
        r"\bimport\s+nautilus_trader\.(?:backtest\.(?:engine|models|config)"
        r"|core\.(?:rust\.model[A-Za-z0-9_.]*|data[A-Za-z0-9_.]*|message[A-Za-z0-9_.]*)"
        r"|common\.(?:actor|component|providers)"
        r"|test_kit[A-Za-z0-9_.]*"
        r"|analysis\.statistic[A-Za-z0-9_.]*)\b",
    ),
)


def legacy_labelling_errors(root: Path) -> list[str]:
    canonical_errors: list[str] = []
    canonical._check_unlabelled_tradingnode_guidance(root, canonical_errors)
    canonical._check_unlabelled_legacy_guidance(root, canonical_errors)
    errors = [
        error
        for error in canonical_errors
        if _canonical_error_is_scoped(root, error)
    ]
    for path in _scoped_markdown(root):
        if canonical._is_current_source_pinned_dev_guide_snapshot(path, root):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        text = "\n".join(lines)
        if canonical._has_file_level_label(text, canonical.LEGACY_LABEL_TERMS):
            continue
        for index, line in enumerate(lines):
            if not any(pattern.search(line) for pattern in LEGACY_PATTERNS):
                continue
            start = max(0, index - LABEL_DISTANCE)
            end = min(len(lines), index + LABEL_DISTANCE + 1)
            if any(
                pattern.search(context)
                for context in lines[start:end]
                for pattern in LABEL_PATTERNS
            ):
                continue
            relative = path.relative_to(root).as_posix()
            error = f"unlabelled legacy/Cython/v1 guidance in {relative}:{index + 1}"
            if not any(existing.startswith(error.rsplit(":", 1)[0]) for existing in errors):
                errors.append(error)
    errors.extend(_removed_v2_symbol_errors(root))
    return sorted(errors)

def _removed_v2_symbol_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for path in _scoped_markdown(root):
        if canonical._is_current_source_pinned_dev_guide_snapshot(path, root):
            continue
        if "migration_reference/" in path.as_posix() or "legacy_migration/" in path.as_posix():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        text = "\n".join(lines)
        if canonical._has_file_level_label(text, canonical.LEGACY_LABEL_TERMS):
            continue
        fence_starts = {
            index
            for index, line in enumerate(lines)
            if line.lstrip().startswith("```")
        }
        for index, line in enumerate(lines):
            if not any(pattern.search(line) for pattern in REMOVED_V2_SYMBOL_PATTERNS):
                continue
            start = max(0, index - LABEL_DISTANCE)
            end = min(len(lines), index + LABEL_DISTANCE + 1)
            if any(
                pattern.search(context)
                for context in lines[start:end]
                for pattern in LABEL_PATTERNS
            ):
                continue
            # A label near the opening fence labels the entire fenced block,
            # matching the canonical block-labelling semantics.
            fence_start = max(
                (f for f in fence_starts if f <= index),
                default=None,
            )
            if (
                fence_start is not None
                and any(
                    pattern.search(context)
                    for context in lines[max(0, fence_start - LABEL_DISTANCE): fence_start]
                    for pattern in LABEL_PATTERNS
                )
            ):
                continue
            relative = path.relative_to(root).as_posix()
            error = f"unlabelled removed-v2-symbol guidance in {relative}:{index + 1}"
            if not any(existing.startswith(error.rsplit(":", 1)[0]) for existing in errors):
                errors.append(error)
    return errors


def _canonical_error_is_scoped(root: Path, error: str) -> bool:
    prefix = error.rsplit(" in ", 1)
    if len(prefix) != 2:
        return False
    relative = Path(prefix[1])
    absolute = root / relative
    return absolute in _scoped_markdown(root)


def _scoped_markdown(root: Path) -> tuple[Path, ...]:
    return tuple(
        sorted(
            {
                path
                for pattern in SCOPED_PATTERNS
                for path in root.glob(pattern)
                if path.is_file()
            }
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reject unlabelled legacy Cython/v1 guidance in shipped Markdown.",
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"Legacy labelling check failed: scan root does not exist: {root}")
        return 1

    errors = legacy_labelling_errors(root)
    if errors:
        print("Legacy labelling check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Legacy labelling check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
