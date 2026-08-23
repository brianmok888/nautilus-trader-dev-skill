from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_ROOTS = (REPO_ROOT / "skills", REPO_ROOT / "references", REPO_ROOT / "templates")

def test_active_guidance_uses_ascii_hyphens() -> None:
    offenders: list[str] = []
    for root in ACTIVE_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            if "\u2011" in path.read_text(encoding="utf-8"):
                offenders.append(path.relative_to(REPO_ROOT).as_posix())

    assert offenders == []
