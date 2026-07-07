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

RUST_COMPLIANCE_TARGETS = {
    Path("skills/nt-dev/SKILL.md"): [
        "cargo nextest",
        "cargo clippy",
        "cargo deny",
        "rstest",
    ],
}

ADAPTER_RUNTIME_TARGETS = {
    Path("skills/nt-adapters/SKILL.md"): [
        "Never use get_runtime().block_on() inside trait method implementations",
    ],
}

EXECUTION_TESTING_TARGETS = {
    Path("skills/nt-testing/SKILL.md"): [
        "Adapter baseline matrix",
        "Account reconciliation matrix",
    ],
}

CONTRACT_TERM_GROUPS = {
    (Path("skills/nt-dev/SKILL.md"), "Rust compliance", "block_on boundary"): [
        "outside an ambient Tokio runtime",
        "PyO3",
        "DataClient",
        "ExecutionClient",
        "spawn",
    ],
    (Path("skills/nt-adapters/SKILL.md"), "adapter runtime", "block_on boundary"): [
        "DataClient",
        "ExecutionClient",
        "outside an ambient Tokio runtime",
        "PyO3",
        "spawn",
    ],
    (Path("skills/nt-implement/SKILL.md"), "adapter runtime", "block_on boundary"): [
        "outside an ambient Tokio runtime",
        "PyO3",
        "DataClient",
        "ExecutionClient",
        "spawn",
    ],
    (
        Path("skills/nt-dex-adapter/rules/dos_and_donts.md"),
        "adapter runtime",
        "block_on boundary",
    ): [
        "outside an ambient Tokio runtime",
        "PyO3",
        "DataClient",
        "ExecutionClient",
        "spawn",
    ],
    (
        Path("references/developer_guide/rust.md"),
        "adapter runtime",
        "block_on boundary",
    ): [
        "outside an ambient Tokio runtime",
        "PyO3",
        "DataClient",
        "ExecutionClient",
        "spawn",
    ],
    (
        Path("skills/nt-adapters/references/guides/rust.md"),
        "adapter runtime",
        "block_on boundary",
    ): [
        "outside an ambient Tokio runtime",
        "PyO3",
        "DataClient",
        "ExecutionClient",
        "spawn",
    ],
    (
        Path("skills/nt-testing/SKILL.md"),
        "execution testing",
        "ExecTester baseline and reconciliation",
    ): [
        "groups 1–5",
        "capability matrix",
        "DataTester",
        "unknown outcomes stay",
        "balances",
        "open orders",
        "fills",
        "positions",
        "startup state",
    ],
}

LATEST_UPSTREAM_DELTA_TARGETS = {
    Path("references/developer_guide/rust.md"): [
        "uv version pinned by `required-version`",
        "Generated Python artifacts",
        "make py-stubs-v2",
        "bon::bon",
        "try_order",
    ],
    Path("references/developer_guide/testing.md"): [
        "arrow,ffi,python,high-precision,streaming,defi",
        "--lib --tests",
    ],
    Path("references/developer_guide/spec_exec_testing.md"): [
        "ExecTesterConfig::builder()",
        "StrategyConfig",
        "build()?",
    ],
    Path("references/developer_guide/release_security.md"): [
        "export TAG=",
        "export REPO=",
        "gh attestation verify",
    ],
}


NT_V2_CUTOVER_TARGETS = {
    Path("skills/nt-dev/SKILL.md"): [
        "1.231.0",
        "final 1.x",
        "2.0.0rc1",
        "develop_v1",
        "Rust MSRV 1.96.1",
        "Python v2 controller subclassing",
        "subclassable execution algorithms",
        "FeeModel",
        "FillModel",
    ],
}

NT_V2_LIVE_TARGETS = {
    Path("skills/nt-live/SKILL.md"): [
        "SIGTERM",
        "with_clock_factory",
        "event_store",
        "v1.227-v1.229",
        "LiveNode metrics",
        "WebSocket transport backend",
        "RecencyMap",
    ],
}

NT_V2_REVIEW_TARGETS = {
    Path("skills/nt-review/SKILL.md"): [
        "Python v2 config stub/readback drift",
        "subclassable PyO3 stubs",
        "v2 wranglers",
        "raw fixed-point overflow",
        "RecencyMap",
        "DataActor",
        "message bus",
    ],
}

NT_V2_TESTING_TARGETS = {
    Path("skills/nt-testing/SKILL.md"): [
        "Python v2 controller subclassing",
        "subclassable execution algorithms",
        "FeeModel",
        "FillModel",
    ],
}

NT_V2_RUST_TARGETS = {
    Path("references/developer_guide/rust.md"): [
        "Rust MSRV 1.96.1",
        "2.0.0rc1",
        "develop_v1",
        "Python v2 controller subclassing",
        "subclassable execution algorithms",
        "FeeModel",
        "FillModel",
    ],
}

LATEST_SKILL_ALIGNMENT_TARGETS = {
    Path("skills/nt-dev/SKILL.md"): [
        "make py-stubs-v2",
        "Generated Python artifacts",
        "arrow,ffi,python,high-precision,streaming,defi",
    ],
    Path("skills/nt-testing/SKILL.md"): [
        "ExecTesterConfig::builder()",
        "StrategyConfig",
        "build()?",
    ],
    Path("skills/nt-review/SKILL.md"): [
        "Generated Python artifacts",
        "make py-stubs-v2",
    ],
    Path("skills/nt-data/SKILL.md"): [
        "try_order",
        "try_order_owned",
    ],
}


LEGACY_GUIDANCE_ROOTS = ("skills", "references")
LEGACY_GUIDANCE_SUFFIXES = {".md", ".py"}
LEGACY_GUIDANCE_EXCLUDED_PARTS = {".git", ".omx", "__pycache__"}
TRADING_NODE_TERM = "TradingNode"
TRADING_NODE_LABEL_TERMS = [
    "Python live",
    "integration-specific",
    "Legacy",
    "legacy",
    "reference-only",
]
LEGACY_GUIDANCE_TERMS = [
    "Cython",
    ".pyx",
    ".pxd",
    "as_legacy_cython",
    "legacy Cython",
    "legacy v1 core",
    "Cython v1",
]
LEGACY_LABEL_TERMS = [
    "migration",
    "reference-only",
    "deprecated",
    "removed",
    "replaced",
    "rename",
    "renamed",
]

SECRET_IGNORE_PATTERNS = [".env", ".env.*", "*.pem", "*.key"]

GUIDE_LINK_RE = re.compile(r"\[Guide\]\(([^)]+\.md)\)")
UV_REQUIRED_VERSION_RE = re.compile(r'required-version\s*=\s*"==[^"]+"')


BASH_CODE_BLOCK_RE = re.compile(
    r"^```(?:bash|sh)\s*\n(.*?)^```", re.MULTILINE | re.DOTALL
)
INVALID_RELEASE_SECURITY_BASH_PATTERNS = [
    re.compile(r"^\s*set\s+-gx\b", re.MULTILINE),
    re.compile(r"^\s*export\s+[A-Za-z_][A-Za-z0-9_]*=\s+\S", re.MULTILINE),
    re.compile(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*=\s*\([^)]*\|", re.MULTILINE),
    re.compile(r"^\s*test\s+\(", re.MULTILINE),
]
PYTHON_CODE_BLOCK_RE = re.compile(
    r"^```(?:python|py)\s*\n(.*?)^```", re.MULTILINE | re.DOTALL
)

BLOCK_ON_CANONICAL_WARNING_TARGETS = [
    Path("skills/nt-dev/SKILL.md"),
    Path("skills/nt-adapters/SKILL.md"),
    Path("skills/nt-implement/SKILL.md"),
    Path("skills/nt-dex-adapter/rules/dos_and_donts.md"),
    Path("references/developer_guide/rust.md"),
    Path("skills/nt-adapters/references/guides/rust.md"),
    Path("skills/nt-dev/references/guides/rust_conventions.md"),
]

BLOCK_ON_CANONICAL_WARNING_TERMS = [
    "Never use",
    "get_runtime().block_on()",
    "inside live",
    "DataClient",
    "ExecutionClient",
    "trait method implementations",
    "spawn work",
]

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


def _contains_term(text: str, term: str) -> bool:
    normalized_text = " ".join(text.split())
    normalized_term = " ".join(term.split())
    return normalized_term in normalized_text


def _contains_terms_in_single_paragraph(text: str, terms: list[str]) -> bool:
    paragraphs = re.split(r"\n\s*\n", text)
    return any(
        all(_contains_term(paragraph, term) for term in terms)
        for paragraph in paragraphs
    )


def _iter_legacy_guidance_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for root_name in LEGACY_GUIDANCE_ROOTS:
        base = root / root_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in LEGACY_GUIDANCE_SUFFIXES:
                continue
            relative = path.relative_to(root)
            if any(part in LEGACY_GUIDANCE_EXCLUDED_PARTS for part in relative.parts):
                continue
            files.append(path)
    return files


def _split_guidance_blocks(text: str) -> list[str]:
    blocks = re.split(r"\n\s*\n", text)
    return [block for block in blocks if block.strip()]


def _block_with_previous_context(blocks: list[str], index: int) -> str:
    if index > 0 and _contains_term(blocks[index - 1], "NT v2 compatibility note"):
        return f"{blocks[index - 1]}\n\n{blocks[index]}"
    return blocks[index]


def _block_has_label(block: str, labels: list[str]) -> bool:
    return _contains_term(block, "NT v2 compatibility note") and any(
        _contains_term(block, label) for label in labels
    )


def _strip_labelled_python_fences(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        block = match.group(1)
        if _block_has_label(block, TRADING_NODE_LABEL_TERMS) or _block_has_label(
            block,
            LEGACY_LABEL_TERMS,
        ):
            return ""
        return match.group(0)

    return PYTHON_CODE_BLOCK_RE.sub(replace, text)


def _check_python_shebang_positions(root: Path, errors: list[str]) -> None:
    for path in _iter_legacy_guidance_files(root):
        if path.suffix != ".py":
            continue
        lines = _read(path).splitlines()
        if any(line.startswith("#!") for line in lines[1:]):
            errors.append(
                f"python shebang is not on first line in {_relative(path, root)}"
            )


def _check_python_fence_compatibility_labels(root: Path, errors: list[str]) -> None:
    for path in _iter_legacy_guidance_files(root):
        if path.suffix != ".md":
            continue
        text = _read(path)
        for block in PYTHON_CODE_BLOCK_RE.findall(text):
            labels_in_block = 0
            for line in block.splitlines():
                stripped = line.lstrip()
                if stripped.startswith("NT v2 compatibility note:"):
                    errors.append(
                        "uncommented NT v2 compatibility note in Python fence in "
                        f"{_relative(path, root)}"
                    )
                    break
                if stripped.startswith("# NT v2 compatibility note:"):
                    labels_in_block += 1
            if labels_in_block > 1:
                errors.append(
                    "duplicate NT v2 compatibility note in Python fence in "
                    f"{_relative(path, root)}"
                )


def _check_duplicate_compatibility_labels(root: Path, errors: list[str]) -> None:
    for path in _iter_legacy_guidance_files(root):
        text = _read(path)
        previous_note: str | None = None
        note_cluster: set[str] = set()
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                previous_note = None
                continue
            note = stripped.removeprefix("# ").strip()
            if not note.startswith("NT v2 compatibility note:"):
                previous_note = None
                note_cluster.clear()
                continue
            if note == previous_note:
                errors.append(
                    "duplicate adjacent NT v2 compatibility note in "
                    f"{_relative(path, root)}"
                )
                break
            if note in note_cluster:
                errors.append(
                    "duplicate repeated NT v2 compatibility note in "
                    f"{_relative(path, root)}"
                )
                break
            note_cluster.add(note)
            previous_note = note


def _check_unlabelled_legacy_guidance(root: Path, errors: list[str]) -> None:
    for path in _iter_legacy_guidance_files(root):
        text = _read(path)
        if path.suffix == ".md":
            text = _strip_labelled_python_fences(text)
        relative = _relative(path, root)
        blocks = _split_guidance_blocks(text)

        if TRADING_NODE_TERM in text:
            if not all(
                _block_has_label(
                    _block_with_previous_context(blocks, index),
                    TRADING_NODE_LABEL_TERMS,
                )
                for index, block in enumerate(blocks)
                if TRADING_NODE_TERM in block
            ):
                errors.append(f"unlabelled TradingNode guidance in {relative}")

        if any(term in text for term in LEGACY_GUIDANCE_TERMS):
            if not all(
                _block_has_label(
                    _block_with_previous_context(blocks, index),
                    LEGACY_LABEL_TERMS,
                )
                for index, block in enumerate(blocks)
                if any(term in block for term in LEGACY_GUIDANCE_TERMS)
            ):
                errors.append(f"unlabelled legacy/Cython/v1 guidance in {relative}")


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
        if not _contains_term(text, required_text):
            errors.append(
                f"missing entry skill contract '{required_text}' in {ENTRY_SKILL.as_posix()}"
            )

    for skill_name in ENTRY_SKILL_ROUTING_TARGETS:
        if not _contains_term(text, skill_name):
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
        missing_keys = [key for key in METADATA_KEYS if not _contains_term(text, key)]
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
            if not _contains_term(text, term):
                if error_label in {"guide", "skill"}:
                    errors.append(
                        f"missing current {error_label} delta '{term}' "
                        f"in {relative.as_posix()}"
                    )
                elif error_label == "latest upstream":
                    errors.append(
                        f"missing latest upstream delta '{term}' in {relative.as_posix()}"
                    )
                elif error_label == "latest skill alignment":
                    errors.append(
                        f"missing latest skill alignment '{term}' in {relative.as_posix()}"
                    )
                else:
                    errors.append(
                        f"missing {error_label} term '{term}' in {relative.as_posix()}"
                    )


def _check_contract_term_groups(root: Path, errors: list[str]) -> None:
    for (
        relative,
        error_label,
        contract_name,
    ), required_terms in CONTRACT_TERM_GROUPS.items():
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        if not all(_contains_term(text, term) for term in required_terms):
            errors.append(
                f"missing {error_label} contract '{contract_name}' in {relative.as_posix()}"
            )


def _check_block_on_canonical_warnings(root: Path, errors: list[str]) -> None:
    for relative in BLOCK_ON_CANONICAL_WARNING_TARGETS:
        absolute = root / relative
        if not absolute.exists():
            continue

        text = _read(absolute)
        if not _contains_terms_in_single_paragraph(
            text, BLOCK_ON_CANONICAL_WARNING_TERMS
        ):
            errors.append(
                "missing adapter runtime contract 'block_on canonical warning' "
                f"in {relative.as_posix()}"
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
            coinbase_lines
            and not any("stable-green" in line for line in coinbase_lines)
        ):
            errors.append(f"stale Coinbase integration status in {relative.as_posix()}")


def _check_release_security_bash_examples(root: Path, errors: list[str]) -> None:
    relative = Path("references/developer_guide/release_security.md")
    absolute = root / relative
    if not absolute.exists():
        return

    text = _read(absolute)
    for block in BASH_CODE_BLOCK_RE.findall(text):
        if any(
            pattern.search(block) for pattern in INVALID_RELEASE_SECURITY_BASH_PATTERNS
        ):
            errors.append(
                f"invalid release-security bash example in {relative.as_posix()}"
            )
            return


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
    _check_release_security_bash_examples(root, errors)
    _check_python_shebang_positions(root, errors)
    _check_python_fence_compatibility_labels(root, errors)
    _check_duplicate_compatibility_labels(root, errors)
    _check_unlabelled_legacy_guidance(root, errors)

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

    _check_required_terms(root, errors, RUST_COMPLIANCE_TARGETS, "Rust compliance")
    _check_required_terms(root, errors, ADAPTER_RUNTIME_TARGETS, "adapter runtime")
    _check_required_terms(root, errors, EXECUTION_TESTING_TARGETS, "execution testing")
    _check_contract_term_groups(root, errors)
    _check_block_on_canonical_warnings(root, errors)
    _check_required_terms(
        root, errors, LATEST_UPSTREAM_DELTA_TARGETS, "latest upstream"
    )
    _check_required_terms(
        root, errors, LATEST_SKILL_ALIGNMENT_TARGETS, "latest skill alignment"
    )

    _check_required_terms(root, errors, NT_V2_CUTOVER_TARGETS, "NT v2 cutover")
    _check_required_terms(root, errors, NT_V2_LIVE_TARGETS, "NT v2 live")
    _check_required_terms(root, errors, NT_V2_REVIEW_TARGETS, "NT v2 review")
    _check_required_terms(root, errors, NT_V2_TESTING_TARGETS, "NT v2 testing")
    _check_required_terms(root, errors, NT_V2_RUST_TARGETS, "NT v2 rust")

    for relative, required_terms in INVARIANT_TARGETS.items():
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        for term in required_terms:
            if not _contains_term(text, term):
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
        if not all(_contains_term(text, term) for term in required_terms):
            errors.append(f"missing live runtime boundary in {relative.as_posix()}")

    for relative in EVOMAP_DIRECT_A2A_TARGETS:
        absolute = root / relative
        if not absolute.exists():
            continue
        text = _read(absolute)
        if any(term in text for term in EVOMAP_DIRECT_A2A_TERMS):
            errors.append(f"stale direct EvoMap A2A guidance in {relative.as_posix()}")

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
