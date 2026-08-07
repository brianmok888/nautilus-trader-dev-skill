from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE_SKILLS = ROOT / "skills"

FORBIDDEN_DOWNSTREAM_MARKERS = (
    "Nautilus-Daedalus",
    "Nautilus Daedalus",
    "Daedalus",
    "nautilus-daedalus",
    "nd-authority",
    "nd-brain",
    "nd-runtime-persistence",
    "nd-promotion",
    "nd-observability",
    "nd-ui",
    "nd-predict-perps",
)


def test_generic_nt_skills_are_independent_of_downstream_projects() -> None:
    skill_files = sorted(CORE_SKILLS.glob("*/SKILL.md"))
    assert skill_files

    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_DOWNSTREAM_MARKERS:
            assert marker not in text, f"{path.relative_to(ROOT)} contains {marker!r}"


def test_generic_nt_router_does_not_advertise_a_downstream_route() -> None:
    router = (CORE_SKILLS / "nt" / "SKILL.md").read_text(encoding="utf-8")
    assert "generic NT skill layer" in router
    assert "downstream project-specific skills" in router
    assert "router never composes downstream consumers" in router
