from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

LANE_ORDER: Final = (
    "Rust production lane",
    "PyO3 control-plane lane",
    "Migration/reference lane",
    "Source-pinned upstream lane",
)
SHA_RE: Final = re.compile(r"\b[0-9a-f]{40}\b")
FORBIDDEN_PYTHON_CALLS: Final = frozenset(
    {
        "cancel_order",
        "close_position",
        "modify_order",
        "submit_order",
        "subscribe_bars",
        "subscribe_book_deltas",
        "subscribe_quote_ticks",
        "subscribe_trade_ticks",
    }
)


@dataclass(frozen=True, slots=True)
class Section:
    heading: str
    line_number: int
    body: tuple[str, ...]


def validate_rust_skill_lanes(path: Path, root: Path) -> list[str]:
    sections = _sections(path.read_text(encoding="utf-8"))
    headings = [section.heading for section in sections]
    label = path.relative_to(root).as_posix()
    errors: list[str] = []
    if headings.count("NT V2 Rust readiness gates") != 1:
        errors.append(f"{label}: requires exactly one NT V2 Rust readiness gates H2")
    lane_positions: list[int] = []
    for lane in LANE_ORDER:
        if headings.count(lane) != 1:
            errors.append(f"{label}: requires exactly one {lane} H2")
        elif (position := headings.index(lane)) >= 0:
            lane_positions.append(position)
    if len(lane_positions) == len(LANE_ORDER) and lane_positions != sorted(lane_positions):
        errors.append(f"{label}: lane H2s are not in Rust-first order")
    errors.extend(_validate_lane_bodies(sections, path, root))
    return errors


def _validate_lane_bodies(sections: tuple[Section, ...], path: Path, root: Path) -> list[str]:
    errors: list[str] = []
    by_heading = {section.heading: section for section in sections}
    for heading in LANE_ORDER:
        section = by_heading.get(heading)
        if section is None:
            continue
        body = "\n".join(section.body)
        label = f"{path.relative_to(root).as_posix()}:{section.line_number} {heading}"
        if heading == "Rust production lane" and "```python" in body:
            errors.append(f"{label}: Rust production lane contains a Python fence")
        elif heading == "Migration/reference lane":
            if "```" in body:
                errors.append(f"{label}: migration lane must be pointer-only")
            if "migration_reference" not in body:
                errors.append(f"{label}: migration lane lacks physical quarantine pointer")
        elif heading == "Source-pinned upstream lane":
            if "references/developer_guide/" not in body:
                errors.append(f"{label}: source-pinned lane lacks developer-guide link")
            if not SHA_RE.search(body):
                errors.append(f"{label}: source-pinned lane lacks immutable source metadata")
        elif heading == "PyO3 control-plane lane":
            errors.extend(_pyo3_errors(label, body))
    return errors


def _sections(text: str) -> tuple[Section, ...]:
    sections: list[Section] = []
    heading = ""
    line_number = 0
    body: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            if heading:
                sections.append(Section(heading, line_number, tuple(body)))
            heading = line.removeprefix("## ")
            line_number = index
            body = []
        elif heading:
            body.append(line)
    if heading:
        sections.append(Section(heading, line_number, tuple(body)))
    return tuple(sections)


def _pyo3_errors(label: str, body: str) -> list[str]:
    errors: list[str] = []
    for python in _python_fences(body):
        try:
            tree = ast.parse(python)
        except SyntaxError as exc:
            errors.append(f"{label}: PyO3 Python fence does not parse: {exc.msg}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else node.func.id
                if isinstance(node.func, ast.Name)
                else ""
            )
            if name in FORBIDDEN_PYTHON_CALLS:
                errors.append(f"{label}: PyO3 Python fence exposes execution authority: {name}")
    return errors


def _python_fences(body: str) -> tuple[str, ...]:
    fences: list[str] = []
    active = False
    lines: list[str] = []
    for line in body.splitlines():
        if not active and line == "```python":
            active = True
            lines = []
        elif active and line == "```":
            fences.append("\n".join(lines))
            active = False
        elif active:
            lines.append(line)
    return tuple(fences)
