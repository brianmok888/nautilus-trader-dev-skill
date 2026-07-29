from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import check_skill_g2_harnesses as g2
from tools import g2_owned_content as ownership


def _harness() -> g2.Harness:
    return g2.Harness(
        skill="nt-data",
        scope="repository:test",
        summary="Test ownership",
        allowed_tokens=("true",),
        steps=(g2.repository_step("true"),),
        owned_paths=(Path("skills/nt-data/SKILL.md"),),
    )


def _write_skill(root: Path) -> None:
    skill = root / "skills/nt-data/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Data\n")


def test_harness_hash_automatically_owns_complete_skill_tree(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    before = ownership.harness_content_hash(tmp_path, _harness())

    reference = tmp_path / "skills/nt-data/references/new.md"
    reference.parent.mkdir()
    reference.write_text("new guidance\n")

    assert ownership.harness_content_hash(tmp_path, _harness()) != before


def test_owned_hash_binds_logical_path_and_entry_type(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    first = tmp_path / "skills/nt-data/reference.md"
    first.write_text("same bytes\n")
    file_hash = ownership.harness_content_hash(tmp_path, _harness())

    first.unlink()
    renamed = tmp_path / "skills/nt-data/renamed.md"
    renamed.write_text("same bytes\n")

    assert ownership.harness_content_hash(tmp_path, _harness()) != file_hash


def test_owned_hash_binds_symlink_target_text_and_target_content(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    shared = tmp_path / "shared"
    shared.mkdir()
    first = shared / "first.md"
    second = shared / "second.md"
    first.write_text("same bytes\n")
    second.write_text("same bytes\n")
    link = tmp_path / "skills/nt-data/shared.md"
    link.symlink_to("../../shared/first.md")
    first_hash = ownership.harness_content_hash(tmp_path, _harness())

    link.unlink()
    link.symlink_to("../../shared/second.md")
    retargeted_hash = ownership.harness_content_hash(tmp_path, _harness())
    second.write_text("changed target\n")

    assert retargeted_hash != first_hash
    assert ownership.harness_content_hash(tmp_path, _harness()) != retargeted_hash


def test_directory_symlink_closure_excludes_generated_evidence(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    references = tmp_path / "references"
    evidence = references / "g2-evidence/nt-data.json"
    evidence.parent.mkdir(parents=True)
    evidence.write_text('{"run": 1}\n')
    guide = references / "guide.md"
    guide.write_text("guide one\n")
    (tmp_path / "skills/nt-data/references").symlink_to("../../references")
    before = ownership.harness_content_hash(tmp_path, _harness())

    evidence.write_text('{"run": 2}\n')
    evidence_only = ownership.harness_content_hash(tmp_path, _harness())
    guide.write_text("guide two\n")

    assert evidence_only == before
    assert ownership.harness_content_hash(tmp_path, _harness()) != evidence_only


@pytest.mark.parametrize("target", ("missing.md", "../../../../outside.md"))
def test_owned_hash_rejects_broken_or_escaping_symlinks(
    tmp_path: Path,
    target: str,
) -> None:
    _write_skill(tmp_path)
    (tmp_path / "skills/nt-data/link").symlink_to(target)

    with pytest.raises(ownership.OwnedContentError):
        ownership.harness_content_hash(tmp_path, _harness())


def test_owned_hash_rejects_symlink_cycles(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    (tmp_path / "skills/nt-data/loop").symlink_to(".")

    with pytest.raises(ownership.OwnedContentError, match="cycle"):
        ownership.harness_content_hash(tmp_path, _harness())


def test_owned_hash_rejects_unsupported_entries(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    fifo = tmp_path / "skills/nt-data/events"
    os.mkfifo(fifo)

    with pytest.raises(ownership.OwnedContentError, match="unsupported"):
        ownership.harness_content_hash(tmp_path, _harness())


def test_untracked_owned_source_is_reported_fail_closed(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    subprocess.run(("git", "init", "-q"), cwd=tmp_path, check=True)
    subprocess.run(("git", "config", "user.email", "g2@example.test"), cwd=tmp_path, check=True)
    subprocess.run(("git", "config", "user.name", "G2 Test"), cwd=tmp_path, check=True)
    subprocess.run(("git", "add", "."), cwd=tmp_path, check=True)
    subprocess.run(("git", "commit", "-qm", "fixture"), cwd=tmp_path, check=True)
    untracked = tmp_path / "skills/nt-data/references/new.md"
    untracked.parent.mkdir()
    untracked.write_text("not reviewed\n")

    assert ownership.untracked_owned_paths(tmp_path, _harness()) == (
        Path("skills/nt-data/references/new.md"),
    )
    with pytest.raises(ownership.OwnedContentError, match="owns untracked content"):
        ownership.assert_owned_content_tracked(tmp_path, _harness())
