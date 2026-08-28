from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_skill_commands_use_module_safe_pytest_invocation() -> None:
    offenders = []
    for path in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        if "uv run pytest" in path.read_text(encoding="utf-8"):
            offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []
