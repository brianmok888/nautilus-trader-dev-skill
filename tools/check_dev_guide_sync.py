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
    "release_security.md",
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
CURRENT_SYNC_DATE = "2026-06-08"
CURRENT_TARGET = "NautilusTrader develop developer guide source snapshot"


ENTRY_SKILL = Path("skills/nt/SKILL.md")
ENTRY_SKILL_ROUTING_TARGETS = [
    "nt-adapters",
    "nt-architect",
    "nt-backtest",
    "nt-data",
    "nt-dev",
    "nt-dex-adapter",
    "nt-evomap-integration",
    "nt-implement",
    "nt-learn",
    "nt-live",
    "nt-model",
    "nt-review",
    "nt-signals",
    "nt-strategy-builder",
    "nt-testing",
    "nt-trading",
]

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
    "derive.md",
    "dydx.md",
    "hyperliquid.md",
    "ib.md",
    "kraken.md",
    "lighter.md",
    "okx.md",
    "polymarket.md",
    "tardis.md",
]

INTEGRATION_INDEXES = [
    Path("references/integrations/index.md"),
    Path("skills/nt-adapters/references/integrations/index.md"),
]

RETIRED_API_INDEX_LINKS = ["coinbase_intx.md", "mt5.md"]

COINBASE_STATUS_TARGETS = [
    Path("references/integrations/index.md"),
    Path("skills/nt-adapters/references/integrations/index.md"),
]

INVARIANT_TARGETS = {
    Path("skills/nt-live/SKILL.md"): ["LiveNode", "file_config", "PortfolioSnapshot"],
    Path("skills/nt-testing/SKILL.md"): [
        "DataTester",
        "ExecTester",
        "limit_aggressive",
        "test_modify_rejected",
    ],
    Path("skills/nt-adapters/SKILL.md"): [
        "nautilus_network::http::HttpClient",
        "get_runtime().spawn()",
        "time_bars_origin_offset",
        "`Live` / `LIVE`",
    ],
    Path("skills/nt-architect/SKILL.md"): ["message immutability"],
    Path("skills/nt-data/SKILL.md"): ["time_bars_origin_offset", "order_owned"],
    Path("skills/nt-signals/SKILL.md"): ["priority", "ContinuousFutureAdjustmentType"],
    Path("skills/nt-trading/SKILL.md"): [
        "PortfolioSnapshot",
        "TryFrom<OrderInitialized>",
    ],
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
    Path("skills/nt-strategy-builder/SKILL.md"): [
        "LiveNode",
        "TradingNode",
        "Python live",
    ],
    Path("skills/nt-review/SKILL.md"): ["LiveNode", "TradingNode", "Python live"],
}

EVOMAP_DIRECT_A2A_TARGETS = [
    Path("docs/plans/2026-02-28-brainstorming-evomap-capsule-design.md"),
    Path("docs/plans/2026-02-28-brainstorming-evomap-capsule-implementation.md"),
    Path("skills/nt-evomap-integration/SKILL.md"),
    Path("skills/nt-implement/SKILL.md"),
]

EVOMAP_DIRECT_A2A_TERMS = [
    "/a2a/",
    "EvoMap A2A endpoints",
    "EvoMapCapsuleClient",
    "hello -> publish -> fetch -> report",
    "`hello`, `publish`, `fetch`, `report`",
    "hello, publish, fetch, report",
]

EVOMAP_PROXY_BOUNDARY_TARGET = Path("skills/nt-evomap-integration/SKILL.md")
EVOMAP_PROXY_BOUNDARY_TERMS = [
    "Proxy mailbox",
    "mailbox/send",
    "mailbox/poll",
    "asset/submit",
    "asset/fetch",
    "LangChain",
    "LangGraph",
    "StateGraph",
    "human-in-the-loop",
]

POLYMARKET_ALLOWANCE_TARGETS = [
    Path("references/integrations/polymarket.md"),
    Path("skills/nt-adapters/references/integrations/polymarket.md"),
]

SECRET_IGNORE_PATTERNS = [".env", ".env.*", "*.pem", "*.key"]

GUIDE_LINK_RE = re.compile(r"\[Guide\]\(([^)]+\.md)\)")
UV_REQUIRED_VERSION_RE = re.compile(r'required-version\s*=\s*"==[^"]+"')

CURRENT_GUIDE_DELTA_TARGETS = {
    Path("references/developer_guide/adapters.md"): [
        "Handler initialization handshake",
        "Auth-token rotation",
        "CancellationToken",
        "execution-path rate-limit response",
        "unknown outcome",
        "idempotent",
    ],
    Path("references/developer_guide/spec_exec_testing.md"): [
        "Ambiguous outcome failures",
        "local prepare-failure carve-out",
        "OrderCancelRejected",
        "OrderModifyRejected",
        "TC-E74",
        "TC-E78",
        "due_post_only=true",
        "trigger-order signing expiry",
    ],
    Path("references/developer_guide/environment_setup.md"): [
        "current version numbers into docs",
        "rustup toolchain install nightly",
        "pip-audit",
        "maturin",
    ],
    Path("references/developer_guide/rust.md"): [
        "Generated FFI bindings and precision mode",
        "HIGH_PRECISION=true",
    ],
    Path("references/developer_guide/python.md"): [
        "Python v2 live callback routing",
        "Do not call `Python::attach` from Tokio worker tasks",
    ],
    Path("references/developer_guide/ffi.md"): [
        "Typed CVec wrappers and Send",
        "Rust-owned CVec capsules with explicit drop",
    ],
    Path("references/developer_guide/release_security.md"): [
        "trusted publishing",
        "Sigstore",
        "SLSA provenance",
        "cosign",
    ],
}

CURRENT_SKILL_DELTA_TARGETS = {
    Path("skills/nt-adapters/SKILL.md"): [
        "SetClient",
        "auth-token rotation",
        "CancellationToken",
        "ambiguous outcome failures",
        "execution-path rate-limit response",
        "unknown outcome",
        "idempotent",
    ],
    Path("skills/nt-testing/SKILL.md"): [
        "TC-E74",
        "TC-E78",
        "local prepare-failure carve-out",
        "OrderCancelRejected",
        "OrderModifyRejected",
        "due_post_only=true",
        "trigger-order signing expiry",
    ],
    Path("skills/nt-dev/SKILL.md"): [
        "Do not copy current version numbers",
        "Generated FFI bindings and precision mode",
        "Python v2 live callback routing",
        "Typed CVec wrappers and Send",
    ],
    Path("skills/nt-evomap-integration/SKILL.md"): [
        "~/.evolver/settings.json",
        "EVOMAP_PROXY_PORT",
        "mailbox/ack",
        "mailbox/status",
        "mailbox/list",
        "task/subscribe",
        "task/list",
        "task/claim",
        "task/complete",
        "task/unsubscribe",
    ],
}


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
        if relative.parts and relative.parts[0] == ".omx":
            continue
        if relative.parts[:2] == ("docs", "superpowers"):
            continue
        if (
            relative.parts[:2] == ("skills", "nt-adapters")
            and "references" in relative.parts
        ):
            continue
        if (
            relative.parts[:2] == ("skills", "nt-dev")
            and "references" in relative.parts
        ):
            continue
        if (
            relative.parts[:2] == ("skills", "nt-live")
            and "references" in relative.parts
        ):
            continue
        checked.append(path)
    return checked


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _check_entry_skill(root: Path, errors: list[str]) -> None:
    absolute = root / ENTRY_SKILL
    if not absolute.exists():
        errors.append(f"missing NautilusTrader entry skill: {ENTRY_SKILL.as_posix()}")
        return

    text = _read(absolute)
    for required_text in [
        "name: nt",
        "Entry-point/router skill",
        "Source of truth",
        "nautechsystems/nautilus_trader",
    ]:
        if required_text not in text:
            errors.append(
                f"missing entry skill contract '{required_text}' in {ENTRY_SKILL.as_posix()}"
            )

    for skill_name in ENTRY_SKILL_ROUTING_TARGETS:
        if skill_name not in text:
            errors.append(
                f"entry skill does not route to {skill_name} in {ENTRY_SKILL.as_posix()}"
            )


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
        if f"sync_date: {CURRENT_SYNC_DATE}" not in text:
            errors.append(f"stale sync date in {relative.as_posix()}")
        if f"target: {CURRENT_TARGET}" not in text:
            errors.append(f"stale target in {relative.as_posix()}")


def _check_retired_references(root: Path, errors: list[str]) -> None:
    for relative in RETIRED_UPSTREAM_REFERENCE_FILES:
        if (root / relative).exists():
            errors.append(
                f"retired upstream reference still present: {relative.as_posix()}"
            )


def _check_integration_index(root: Path, relative: Path, errors: list[str]) -> None:
    absolute = root / relative
    if not absolute.exists():
        return

    text = _read(absolute)
    links = set(GUIDE_LINK_RE.findall(text))
    for guide in CURRENT_INTEGRATION_GUIDES:
        if guide not in links:
            errors.append(
                f"missing current integration guide link {guide} in {relative.as_posix()}"
            )

    for link in sorted(links):
        if not (absolute.parent / link).exists():
            errors.append(
                f"broken integration guide link {link} in {relative.as_posix()}"
            )


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
        errors.append(
            "stale Coinbase IntX adapter guidance in skills/nt-strategy-builder/SKILL.md"
        )


def _check_required_terms(
    root: Path,
    errors: list[str],
    targets: dict[Path, list[str]],
    error_label: str,
) -> None:
    for relative, required_terms in targets.items():
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        for term in required_terms:
            if term not in text:
                errors.append(
                    f"missing current {error_label} delta '{term}' in {relative.as_posix()}"
                )


def _check_secret_ignore_patterns(root: Path, errors: list[str]) -> None:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        errors.append("missing .gitignore with secret ignore patterns")
        return

    patterns = set(_read(gitignore).splitlines())
    for pattern in SECRET_IGNORE_PATTERNS:
        if pattern not in patterns:
            errors.append(f"missing secret ignore pattern '{pattern}' in .gitignore")


def _check_coinbase_status(root: Path, errors: list[str]) -> None:
    for relative in COINBASE_STATUS_TARGETS:
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        coinbase_lines = [line for line in text.splitlines() if "Coinbase" in line]
        if any("beta-yellow" in line for line in coinbase_lines) or (
            coinbase_lines and not any("stable-green" in line for line in coinbase_lines)
        ):
            errors.append(
                f"stale Coinbase integration status in {relative.as_posix()}"
            )

def _check_security_guidance(root: Path, errors: list[str]) -> None:
    for relative in POLYMARKET_ALLOWANCE_TARGETS:
        absolute = root / relative
        if not absolute.exists():
            continue

        text = _read(absolute)
        if "maximum possible amount of pUSD" in text:
            errors.append(
                f"unbounded Polymarket allowance guidance in {relative.as_posix()}"
            )

    for markdown_file in _iter_checked_markdown_files(root):
        text = _read(markdown_file)
        if "CryptoPermanentContract" in text:
            errors.append(
                "nonexistent DEX instrument class CryptoPermanentContract "
                f"in {_relative(markdown_file, root)}"
            )


def run_checks(root: Path) -> CheckResult:
    errors: list[str] = []

    _check_entry_skill(root, errors)
    _check_required_guide_files(root, errors)
    _check_retired_references(root, errors)
    _check_official_index_alignment(root, errors)
    _check_coinbase_status(root, errors)
    _check_secret_ignore_patterns(root, errors)
    _check_security_guidance(root, errors)

    for markdown_file in _iter_checked_markdown_files(root):
        text = _read(markdown_file)
        relative = _relative(markdown_file, root)
        if "references/guides/" in text:
            errors.append(f"stale references/guides path in {relative}")
        if "pre-commit install" in text and "prek install" not in text:
            errors.append(f"unqualified pre-commit install in {relative}")
        if "capnp-version" in text:
            errors.append(f"stale cap'n proto version source in {relative}")
        if (
            "LD_LIBRARY_PATH" in text
            and 'sysconfig.get_config_var("LIBDIR")' not in text
        ):
            errors.append(f"imprecise LD_LIBRARY_PATH guidance in {relative}")
        if "v1.226.0 / latest docs" in text:
            errors.append(f"stale upstream baseline in {relative}")
        if (
            'required-version = "==0.11.2"' in text
            or 'required-version = "==0.11.8"' in text
            or 'required-version = "==0.11.12"' in text
        ):
            errors.append(f"stale uv required-version guidance in {relative}")
        if UV_REQUIRED_VERSION_RE.search(text):
            errors.append(f"copied uv required-version guidance in {relative}")
        if "Current official baseline:" in text and "Python package" in text:
            errors.append(f"copied current Nautilus version guidance in {relative}")

    _check_required_terms(root, errors, CURRENT_GUIDE_DELTA_TARGETS, "guide")
    _check_required_terms(root, errors, CURRENT_SKILL_DELTA_TARGETS, "skill")

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
        if "limit_aggressive" not in text:
            errors.append(
                "missing v1.227 ExecTester flag 'limit_aggressive' in skills/nt-testing/SKILL.md"
            )
        if "test_modify_rejected" not in text:
            errors.append(
                "missing v1.227 ExecTester flag 'test_modify_rejected' in skills/nt-testing/SKILL.md"
            )
        if "DST readiness" not in text:
            errors.append(
                "missing invariant 'DST readiness' in skills/nt-testing/SKILL.md"
            )
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

    for relative in EVOMAP_DIRECT_A2A_TARGETS:
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        if any(term in text for term in EVOMAP_DIRECT_A2A_TERMS):
            errors.append(
                f"stale direct EvoMap A2A guidance in {relative.as_posix()}"
            )

    evomap = root / EVOMAP_PROXY_BOUNDARY_TARGET
    if evomap.exists():
        text = _read(evomap)
        if not all(term in text for term in EVOMAP_PROXY_BOUNDARY_TERMS):
            errors.append(
                f"missing EvoMap proxy boundary in {EVOMAP_PROXY_BOUNDARY_TARGET.as_posix()}"
            )

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
