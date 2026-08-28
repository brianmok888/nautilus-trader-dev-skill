from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ("tools/check_dev_guide_sync.py",),
    ("tools/check_dev_guide_snapshot_sync.py",),
    ("tools/check_legacy_labelling.py",),
    ("tools/check_findings_schema.py",),
    ("tools/markdown_lane_contract.py", "--check"),
    ("tools/template_classification.py", "--check"),
)


def main() -> int:
    for command in CHECKS:
        result = subprocess.run(
            [sys.executable, *command],
            cwd=REPO_ROOT,
            check=False,
        )
        if result.returncode != 0:
            return result.returncode
    cards = subprocess.run(
        [sys.executable, "tools/check_skill_g2_harnesses.py", "--check-cards"],
        cwd=REPO_ROOT,
        check=False,
    )
    return cards.returncode


if __name__ == "__main__":
    raise SystemExit(main())
