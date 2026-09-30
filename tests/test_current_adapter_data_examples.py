from __future__ import annotations

import ast
import inspect
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tools.upstream_baseline import UPSTREAM_COMMIT, default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path",
    [
        "references/concepts/data.md",
        "skills/nt-data/references/concepts/data.md",
        "skills/nt-signals/references/concepts/data.md",
    ],
)
def test_streaming_examples_execute_current_constructor(path: str) -> None:
    source = subprocess.check_output(
        [
            "git",
            "-C",
            str(default_upstream_root()),
            "show",
            f"{UPSTREAM_COMMIT}:crates/persistence/src/python/config.rs",
        ],
        text=True,
    )
    signature = re.search(
        r"impl StreamingConfig.*?signature = \((.*?)\)\)", source, re.DOTALL
    )
    assert signature is not None
    parameters = ast.parse(
        f"def constructor({signature.group(1).replace('false', 'False').replace('true', 'True')}): pass"
    ).body[0]
    assert isinstance(parameters, ast.FunctionDef)
    required_count = len(parameters.args.args) - len(parameters.args.defaults)
    constructor = inspect.Signature(
        [
        inspect.Parameter(
            argument.arg,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=inspect.Parameter.empty if index < required_count else None,
        )
        for index, argument in enumerate(parameters.args.args)
        ]
    )
    text = (REPO_ROOT / path).read_text()
    calls = []
    for fence in re.findall(r"```python\n(.*?)```", text, re.DOTALL):
        if "StreamingConfig(" not in fence:
            continue
        for node in ast.walk(ast.parse(fence)):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "StreamingConfig"
            ):
                calls.append(node)
    assert len(calls) == 2
    for call in calls:
        kwargs = {keyword.arg: object() for keyword in call.keywords}
        bound = constructor.bind(**kwargs)
        result = bound.arguments
        assert result["writer_path"] is kwargs["writer_path"]
        assert result["catalog"] is kwargs["catalog"]


def test_current_adapter_inventory_excludes_retired_module() -> None:
    for base in (
        "references/api_reference/adapters",
        "skills/nt-adapters/references/api/adapters",
    ):
        text = (REPO_ROOT / base / "index.md").read_text()
        assert "bitmex.md" not in text
    for path in (
        "references/integrations/index.md",
        "skills/nt-adapters/references/integrations/index.md",
    ):
        text = (REPO_ROOT / path).read_text()
        table_rows = "\n".join(line for line in text.splitlines() if line.startswith("|"))
        links = re.findall(r"\[Guide\]\((.*?)\)", table_rows)
        assert "bitmex.md" not in links


@pytest.mark.skipif(os.environ.get("NT_CURRENT_BINDINGS") != "1", reason="requires pinned V2 bindings")
@pytest.mark.parametrize("path", [
    "references/concepts/data.md",
    "skills/nt-data/references/concepts/data.md",
    "skills/nt-signals/references/concepts/data.md",
])
def test_streaming_examples_execute_real_bindings(path: str, tmp_path: Path) -> None:
    fences = re.findall(r"```python\n(.*?)```", (REPO_ROOT / path).read_text(), re.DOTALL)
    snippets = []
    for fence in fences:
        if "StreamingConfig(" not in fence:
            continue
        tree = ast.parse(fence)
        statements = []
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module in (
                "nautilus_trader.config", "nautilus_trader.persistence",
            ):
                statements.append(node)
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Name) and call.func.id == "StreamingConfig":
                    statements.append(node)
                    snippets.append(ast.unparse(ast.Module(body=statements, type_ignores=[])))
    assert len(snippets) == 2
    setup = f"from types import SimpleNamespace\ncatalog = SimpleNamespace(path={str(tmp_path)!r})\nGreeksData = object\n"
    for snippet in snippets:
        result = subprocess.run([sys.executable, "-c", setup + snippet], capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
