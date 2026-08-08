from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tools.check_upstream_freshness import (
    FreshnessStatus,
    build_freshness_report,
    render_json_report,
    render_text_report,
)
from tools.upstream_baseline import UPSTREAM_REMOTE_REFS, default_upstream_root

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_only_authoritative_develop_is_a_required_moving_ref() -> None:
    assert UPSTREAM_REMOTE_REFS == ("origin/develop",)


def test_required_develop_ref_contains_current_nightly_history() -> None:
    report = build_freshness_report(default_upstream_root())

    assert report.nightly_contained is True
    assert report.ok is True


def test_upstream_root_is_portable_and_environment_overridable(
    tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("NT_UPSTREAM_ROOT", str(tmp_path / "custom-upstream"))

    assert default_upstream_root() == tmp_path / "custom-upstream"

    monkeypatch.delenv("NT_UPSTREAM_ROOT")
    resolved = default_upstream_root()
    assert resolved.name == "nautilus_trader"
    assert ".cache" in resolved.parts
    assert "nautilus_trader_upstream_audit_20260728" not in str(resolved)


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


def _write_manifest(
    path: Path,
    *,
    baseline: str,
    current: str,
    delta_commit: str,
    upstream_path: str = "guide.md",
) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "upstream_ref": "develop",
                "pinned_commit": baseline,
                "reviewed_commit": current,
                "deltas": [
                    {
                        "commit": delta_commit,
                        "subject": "current",
                        "upstream_paths": [upstream_path],
                        "affected_files": ["references/developer_guide/index.md"],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )



def _make_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "upstream"
    repo.mkdir()
    _git(repo, "init", "-b", "develop")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    baseline = _commit(repo, "guide.md", "baseline\n", "baseline")
    current = _commit(repo, "guide.md", "current\n", "current")
    _git(repo, "branch", "nightly", current)
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


def test_drift_report_enumerates_changed_commits_and_paths(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
    )

    assert report.refs[0].changed_commits == (current,)
    assert report.refs[0].changed_paths == ("guide.md",)
    payload = json.loads(render_json_report(report))
    assert payload["refs"][0]["changed_commits"] == [current]
    assert payload["refs"][0]["changed_paths"] == ["guide.md"]


def test_complete_review_manifest_is_reported_as_covering_delta(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    manifest = tmp_path / "upstream-delta-review.json"
    _write_manifest(
        manifest,
        baseline=baseline,
        current=current,
        delta_commit=current,
    )

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
        manifest_path=manifest,
    )

    assert report.manifest_reviewed is True
    assert report.manifest_error is None
    assert report.ok is True


def test_review_manifest_rejects_unmapped_delta_commit(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    manifest = tmp_path / "upstream-delta-review.json"
    _write_manifest(
        manifest,
        baseline=baseline,
        current=current,
        delta_commit=baseline,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["deltas"][0]["subject"] = "baseline"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
        manifest_path=manifest,
    )

    assert report.manifest_reviewed is False
    assert report.manifest_error is not None
    assert current in report.manifest_error


def test_review_manifest_requires_impact_or_explicit_no_impact(tmp_path: Path) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    manifest = tmp_path / "upstream-delta-review.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "upstream_ref": "develop",
                "pinned_commit": baseline,
                "reviewed_commit": current,
                "deltas": [
                        {
                            "commit": current,
                            "subject": "current",
                            "upstream_paths": ["guide.md"],
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
        manifest_path=manifest,
    )

    assert report.manifest_reviewed is False
    assert report.manifest_error is not None
    assert "affected_files or no_impact_rationale" in report.manifest_error


def test_review_manifest_rejects_subject_that_does_not_match_upstream_commit(
    tmp_path: Path,
) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    manifest = tmp_path / "upstream-delta-review.json"
    _write_manifest(
        manifest,
        baseline=baseline,
        current=current,
        delta_commit=current,
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["deltas"][0]["subject"] = "fabricated subject"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
        manifest_path=manifest,
    )

    assert report.manifest_reviewed is False
    assert report.manifest_error is not None
    assert "subject does not match upstream commit" in report.manifest_error


def test_review_manifest_rejects_paths_that_do_not_match_upstream_commit(
    tmp_path: Path,
) -> None:
    upstream, baseline, current = _make_repo(tmp_path)
    manifest = tmp_path / "upstream-delta-review.json"
    _write_manifest(
        manifest,
        baseline=baseline,
        current=current,
        delta_commit=current,
        upstream_path="fabricated.md",
    )

    report = build_freshness_report(
        upstream_root=upstream,
        pinned_commit=baseline,
        refs=("develop",),
        manifest_path=manifest,
    )

    assert report.manifest_reviewed is False
    assert report.manifest_error is not None
    assert "upstream_paths do not match upstream commit" in report.manifest_error




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
    ]

    for target in targets:
        head = target.read_text(encoding="utf-8")[:800]
        assert "ARCHIVAL / MIGRATION NOTE" in head, target
        assert "Rust v2/PyO3" in head, target
        assert "LiveNode" in head, target
