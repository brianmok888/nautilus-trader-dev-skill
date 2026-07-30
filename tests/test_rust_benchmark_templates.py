from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "references/dev_templates"
TEMPLATES = (
    TEMPLATE_DIR / "criterion_template.rs",
    TEMPLATE_DIR / "iai_template.rs",
)
BOX_BANNER = re.compile(r"^//\s*[-=*_]{8,}\s*$", flags=re.MULTILINE)


def test_rust_benchmark_templates_do_not_use_box_banner_comments() -> None:
    offenders = [
        path.name
        for path in TEMPLATES
        if BOX_BANNER.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


@pytest.mark.skipif(shutil.which("rustfmt") is None, reason="rustfmt is unavailable")
def test_rust_benchmark_templates_are_rustfmt_clean() -> None:
    result = subprocess.run(
        ["rustfmt", "--edition", "2024", "--check", *map(str, TEMPLATES)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo is unavailable")
@pytest.mark.parametrize(
    ("template_name", "dependency_name", "stub_source"),
    (
        (
            "criterion_template.rs",
            "criterion",
            """pub struct Criterion;
pub struct Bencher;

impl Criterion {
    pub fn bench_function<F>(&mut self, _name: &str, mut function: F)
    where
        F: FnMut(&mut Bencher),
    {
        function(&mut Bencher);
    }
}

impl Bencher {
    pub fn iter<F, R>(&mut self, mut routine: F)
    where
        F: FnMut() -> R,
    {
        std::hint::black_box(routine());
    }
}

#[macro_export]
macro_rules! criterion_group {
    ($group:ident, $benchmark:path) => {
        fn $group(criterion: &mut $crate::Criterion) {
            $benchmark(criterion);
        }
    };
}

#[macro_export]
macro_rules! criterion_main {
    ($group:path) => {
        fn main() {
            let mut criterion = $crate::Criterion;
            $group(&mut criterion);
        }
    };
}
""",
        ),
        (
            "iai_template.rs",
            "iai",
            """#[macro_export]
macro_rules! main {
    ($($benchmark:path),+ $(,)?) => {
        fn main() {
            $(std::hint::black_box($benchmark());)+
        }
    };
}
""",
        ),
    ),
)
def test_rust_benchmark_template_compiles_in_temporary_crate(
    tmp_path: Path,
    template_name: str,
    dependency_name: str,
    stub_source: str,
) -> None:
    crate = tmp_path / "benchmark-smoke"
    dependency = tmp_path / dependency_name
    (crate / "benches").mkdir(parents=True)
    (dependency / "src").mkdir(parents=True)
    shutil.copyfile(TEMPLATE_DIR / template_name, crate / "benches/template.rs")
    (crate / "src").mkdir()
    (crate / "src/lib.rs").write_text("", encoding="utf-8")
    (crate / "Cargo.toml").write_text(
        f"""[package]
name = "benchmark-smoke"
version = "0.1.0"
edition = "2024"

[dev-dependencies]
{dependency_name} = {{ path = "../{dependency_name}" }}

[[bench]]
name = "template"
harness = false
""",
        encoding="utf-8",
    )
    (dependency / "Cargo.toml").write_text(
        f"""[package]
name = "{dependency_name}"
version = "0.0.0"
edition = "2024"
""",
        encoding="utf-8",
    )
    (dependency / "src/lib.rs").write_text(stub_source, encoding="utf-8")

    result = subprocess.run(
        [
            "cargo",
            "check",
            "--offline",
            "--manifest-path",
            str(crate / "Cargo.toml"),
            "--bench",
            "template",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
