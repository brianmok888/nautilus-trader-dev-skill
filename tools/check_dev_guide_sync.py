from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


CURRENT_DEV_GUIDE_FILES = [
    "adapters.md",
    "benchmarking.md",
    "coding_standards.md",
    "design_principles.md",
    "docs.md",
    "environment_setup.md",
    "ffi.md",
    "index.md",
    "python.md",
    "releases.md",
    "rust.md",
    "spec_data_testing.md",
    "spec_exec_testing.md",
    "test_datasets.md",
    "testing.md",
]

REQUIRED_GUIDE_FILES = [
    Path("references/developer_guide") / name for name in CURRENT_DEV_GUIDE_FILES
]

METADATA_KEYS = ["source_url:", "source_repo:", "sync_date:", "target:", "confidence:"]

RETIRED_UPSTREAM_REFERENCE_FILES = [
    Path("references/developer_guide/cython.md"),
    Path("references/developer_guide/docs_style.md"),
    Path("references/developer_guide/packaged_data.md"),
    Path("references/api_reference/adapters/coinbase_intx.md"),
    Path("references/api_reference/adapters/mt5.md"),
    Path("references/integrations/coinbase_intx.md"),
    Path("references/integrations/mt5.md"),
]

CURRENT_INTEGRATION_GUIDES = [
    "architect_ax.md",
    "betfair.md",
    "binance.md",
    "bitmex.md",
    "bybit.md",
    "coinbase.md",
    "databento.md",
    "deribit.md",
    "dydx.md",
    "hyperliquid.md",
    "ib.md",
    "kraken.md",
    "okx.md",
    "polymarket.md",
    "tardis.md",
]

INTEGRATION_INDEXES = [
    Path("references/integrations/index.md"),
    Path("skills/nt-adapters/references/integrations/index.md"),
]

RETIRED_API_INDEX_LINKS = ["coinbase_intx.md", "mt5.md"]

INVARIANT_TARGETS = {
    Path("skills/nt-live/SKILL.md"): ["LiveNode"],
    Path("skills/nt-testing/SKILL.md"): ["DataTester", "ExecTester"],
    Path("skills/nt-adapters/SKILL.md"): [
        "nautilus_network::http::HttpClient",
        "get_runtime().spawn()",
    ],
    Path("skills/nt-architect/SKILL.md"): ["message immutability"],
}

DATASET_METADATA_FIELDS = [
    "file",
    "sha256",
    "size_bytes",
    "original_url",
    "licence",
    "added_at",
]

LIVE_RUNTIME_BOUNDARY_TARGETS = {
    Path("skills/nt-live/SKILL.md"): ["LiveNode", "TradingNode", "Python live"],
    Path("skills/nt-strategy-builder/SKILL.md"): ["LiveNode", "TradingNode", "Python live"],
    Path("skills/nt-review/SKILL.md"): ["LiveNode", "TradingNode", "Python live"],
}

GUIDE_LINK_RE = re.compile(r"\[Guide\]\(([^)]+\.md)\)")


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    errors: list[str]


def _iter_checked_markdown_files(root: Path) -> list[Path]:
    checked: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if ".git" in path.parts:
            continue
        if relative.parts[:2] == ("docs", "superpowers"):
            continue
        if relative.parts[:2] == ("skills", "nt-adapters") and "references" in relative.parts:
            continue
        if relative.parts[:2] == ("skills", "nt-dev") and "references" in relative.parts:
            continue
        if relative.parts[:2] == ("skills", "nt-live") and "references" in relative.parts:
            continue
        checked.append(path)
    return checked


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_required_guide_files(root: Path, errors: list[str]) -> None:
    for relative in REQUIRED_GUIDE_FILES:
        absolute = root / relative
        if not absolute.exists():
            errors.append(f"missing required guide file: {relative.as_posix()}")
            continue
        text = _read(absolute)
        missing_keys = [key for key in METADATA_KEYS if key not in text]
        if missing_keys:
            errors.append(
                f"missing source metadata in {relative.as_posix()}: {', '.join(missing_keys)}"
            )


def _check_retired_references(root: Path, errors: list[str]) -> None:
    for relative in RETIRED_UPSTREAM_REFERENCE_FILES:
        if (root / relative).exists():
            errors.append(f"retired upstream reference still present: {relative.as_posix()}")


def _check_integration_index(root: Path, relative: Path, errors: list[str]) -> None:
    absolute = root / relative
    if not absolute.exists():
        return

    text = _read(absolute)
    links = set(GUIDE_LINK_RE.findall(text))
    for guide in CURRENT_INTEGRATION_GUIDES:
        if guide not in links:
            errors.append(f"missing current integration guide link {guide} in {relative.as_posix()}")

    for link in sorted(links):
        if not (absolute.parent / link).exists():
            errors.append(f"broken integration guide link {link} in {relative.as_posix()}")


def _check_official_index_alignment(root: Path, errors: list[str]) -> None:
    for relative in INTEGRATION_INDEXES:
        _check_integration_index(root, relative, errors)

    api_index = root / "references/api_reference/adapters/index.md"
    if api_index.exists():
        text = _read(api_index)
        for stale_link in RETIRED_API_INDEX_LINKS:
            if stale_link in text:
                errors.append(
                    f"retired API adapter link {stale_link} "
                    "in references/api_reference/adapters/index.md"
                )

    strategy_builder = root / "skills/nt-strategy-builder/SKILL.md"
    if strategy_builder.exists() and "Coinbase IntX" in _read(strategy_builder):
        errors.append("stale Coinbase IntX adapter guidance in skills/nt-strategy-builder/SKILL.md")


def run_checks(root: Path) -> CheckResult:
    errors: list[str] = []

    _check_required_guide_files(root, errors)
    _check_retired_references(root, errors)
    _check_official_index_alignment(root, errors)

    for markdown_file in _iter_checked_markdown_files(root):
        text = _read(markdown_file)
        relative = _relative(markdown_file, root)
        if "references/guides/" in text:
            errors.append(f"stale references/guides path in {relative}")
        if "pre-commit install" in text and "prek install" not in text:
            errors.append(f"unqualified pre-commit install in {relative}")
        if "capnp-version" in text:
            errors.append(f"stale cap'n proto version source in {relative}")
        if "LD_LIBRARY_PATH" in text and 'sysconfig.get_config_var("LIBDIR")' not in text:
            errors.append(f"imprecise LD_LIBRARY_PATH guidance in {relative}")

    for relative, required_terms in INVARIANT_TARGETS.items():
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        for term in required_terms:
            if term not in text:
                errors.append(f"missing invariant '{term}' in {relative.as_posix()}")

    nt_testing = root / "skills/nt-testing/SKILL.md"
    if nt_testing.exists():
        text = _read(nt_testing)
        if "pytest tests/ -v" in text:
            errors.append("stale pytest command in skills/nt-testing/SKILL.md")
        if "cargo test --workspace" in text:
            errors.append("stale cargo test command in skills/nt-testing/SKILL.md")
        if "DST readiness" not in text:
            errors.append("missing invariant 'DST readiness' in skills/nt-testing/SKILL.md")
        for field in DATASET_METADATA_FIELDS:
            if field not in text:
                errors.append(
                    f"missing dataset metadata field '{field}' in skills/nt-testing/SKILL.md"
                )

    for relative, required_terms in LIVE_RUNTIME_BOUNDARY_TARGETS.items():
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        if not all(term in text for term in required_terms):
            errors.append(f"missing live runtime boundary in {relative.as_posix()}")

    return CheckResult(ok=not errors, errors=errors)


def main() -> int:
    result = run_checks(Path.cwd())
    if result.ok:
        print("Developer guide sync checks passed.")
        return 0
    print("Developer guide sync checks failed:")
    for error in result.errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
