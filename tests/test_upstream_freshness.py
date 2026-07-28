from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_upstream_freshness import (
    FreshnessStatus,
    build_freshness_report,
    render_text_report,
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()



def _commit(repo: Path, filename: str, text: str, message: str) -> str:
    (repo / filename).write_text(text, encoding="utf-8")
    _git(repo, "add", filename)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")



def _make_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "upstream"
    repo.mkdir()
    _git(repo, "init", "-b", "develop")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    baseline = _commit(repo, "guide.md", "baseline\n", "baseline")
    current = _commit(repo, "guide.md", "current\n", "current")
    return repo, baseline, current



def test_report_distinguishes_pinned_baseline_from_current_drift(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
    )

    assert report.pinned_commit == baseline
    assert report.upstream_root == upstream
    assert report.refs[0].name == "develop"
    assert report.refs[0].current_commit == current
    assert report.refs[0].status is FreshnessStatus.DRIFTED
    assert report.refs[0].commits_ahead == 1
    assert report.refs[0].pinned_is_ancestor is True




def test_json_cli_is_read_only_and_does_not_mutate_baseline(tmp_path: Path) -> None:
    upstream, baseline, _current = _make_repo(tmp_path)
    baseline_file = REPO_ROOT / "tools" / "upstream_baseline.py"
    before = baseline_file.read_text(encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "tools/check_upstream_freshness.py",
            "--upstream-root",
            str(upstream),
            "--pinned-commit",
            baseline,
            "--ref",
            "develop",
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["pinned_commit"] == baseline
    assert payload["refs"][0]["status"] == "drifted"
    assert baseline_file.read_text(encoding="utf-8") == before




def test_text_report_names_reproducible_baseline_and_current_drift(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    report = build_freshness_report(upstream, baseline, ("develop",))

    text = render_text_report(report)

    assert "Pinned reproducible baseline" in text
    assert baseline[:12] in text
    assert "Current upstream refs" in text
    assert current[:12] in text
    assert "drifted" in text




def test_archival_headers_present_on_prominent_legacy_guides() -> None:
    targets = [
        REPO_ROOT / "skills/nt-signals/references/guides/indicators_guide.md",
        REPO_ROOT / "skills/nt-data/references/guides/databento.md",
        REPO_ROOT / "docs/superpowers/specs/2026-04-29-nautilus-dev-guide-full-sync-design.md",
        REPO_ROOT / "docs/superpowers/specs/2026-05-03-nautilus-dev-skill-latest-sync-design.md",
        REPO_ROOT / "docs/superpowers/plans/2026-04-29-nautilus-dev-guide-full-sync.md",
        REPO_ROOT / "docs/superpowers/plans/2026-05-03-nautilus-dev-skill-latest-sync.md",
    ]

    for target in targets:
        head = target.read_text(encoding="utf-8")[:800]
        assert "ARCHIVAL / MIGRATION NOTE" in head, target
        assert "Rust v2/PyO3" in head, target
        assert "LiveNode" in head, target
