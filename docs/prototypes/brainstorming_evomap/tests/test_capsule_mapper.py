# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Tests for capsule mapper."""

import importlib.util
import sys
from pathlib import Path

_module_dir = Path(__file__).parent.parent
if str(_module_dir) not in sys.path:
    sys.path.insert(0, str(_module_dir))


def _load_module(name: str):
    """Load a module directly from file path."""
    path = _module_dir / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


capsule_mapper = _load_module("capsule_mapper")


def test_mapper_builds_capsule_bundle_with_assets():
    """map_section_delta must return a bundle with assets."""
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="architecture",
        content="test content",
    )

    assert "assets" in bundle
    assert bundle["assets"]
    assert len(bundle["assets"]) == 3  # Gene, Capsule, EvolutionEvent


def test_bundle_contains_gene_capsule_event():
    """Bundle must contain Gene, Capsule, and EvolutionEvent assets."""
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="components",
        content="component content",
    )

    asset_types = {a["type"] for a in bundle["assets"]}
    assert "gene" in asset_types
    assert "capsule" in asset_types
    assert "evolution_event" in asset_types


def test_gene_has_content_hash():
    """Gene asset must have content_hash."""
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="test",
        content="content",
    )

    gene = next(a for a in bundle["assets"] if a["type"] == "gene")
    assert "content_hash" in gene
    assert len(gene["content_hash"]) == 64  # SHA256 hex length


def test_capsule_references_gene():
    """Capsule must reference the Gene."""
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="test",
        content="content",
    )

    gene = next(a for a in bundle["assets"] if a["type"] == "gene")
    capsule = next(a for a in bundle["assets"] if a["type"] == "capsule")

    assert gene["id"] in capsule["data"]["gene_refs"]


def test_evolution_event_references_capsule():
    """EvolutionEvent must reference the Capsule."""
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="test",
        content="content",
    )

    capsule = next(a for a in bundle["assets"] if a["type"] == "capsule")
    event = next(a for a in bundle["assets"] if a["type"] == "evolution_event")

    assert event["data"]["capsule_ref"] == capsule["id"]


def test_bundle_metadata_contains_session_and_section():
    """Bundle metadata must include session_id and section_id."""
    bundle = capsule_mapper.map_section_delta(
        session_id="session_123",
        section_id="data_flow",
        content="content",
    )

    assert bundle["metadata"]["session_id"] == "session_123"
    assert bundle["metadata"]["section_id"] == "data_flow"


def test_section_delta_redacts_sensitive_content_and_denies_metadata():
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="security",
        content=(
            "Use POLYGON_PRIVATE_KEY=0x"
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa "
            "with wallet 0x1111111111111111111111111111111111111111"
        ),
        metadata={
            "approaches": ["least privilege"],
            "api_key": "sk-live-secret",
            "wallet_address": "0x1111111111111111111111111111111111111111",
        },
    )

    gene = next(a for a in bundle["assets"] if a["type"] == "gene")
    data = gene["data"]

    assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" not in data[
        "content_preview"
    ]
    assert "0x1111111111111111111111111111111111111111" not in data["content_preview"]
    assert data["metadata"] == {"approaches": ["least privilege"]}
    assert "redacted_fields" in bundle["metadata"]
    assert "metadata.api_key" in bundle["metadata"]["redacted_fields"]


def test_section_delta_redacts_sensitive_values_in_allowed_metadata():
    bundle = capsule_mapper.map_section_delta(
        session_id="s1",
        section_id="security",
        content="safe content",
        metadata={
            "summary": "token sk-live-secret",
            "constraints": [
                "private key "
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            ],
        },
    )

    gene = next(a for a in bundle["assets"] if a["type"] == "gene")
    metadata = gene["data"]["metadata"]

    assert "sk-live-secret" not in metadata["summary"]
    assert "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" not in metadata[
        "constraints"
    ][0]
    assert metadata["summary"] == "token [REDACTED_TOKEN]"


def test_design_doc_redacts_content_and_decisions_before_export():
    bundle = capsule_mapper.map_design_doc(
        session_id="s1",
        design_doc_path="docs/design.md",
        content=(
            "# Design\n\nprivate_key=0x"
            "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        ),
        decisions=[
            {
                "id": "d1",
                "summary": "Use sandbox first",
                "private_key": "0x"
                "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            }
        ],
    )

    gene = next(a for a in bundle["assets"] if a["type"] == "gene")
    event = next(a for a in bundle["assets"] if a["type"] == "evolution_event")

    assert "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" not in gene[
        "data"
    ]["content_preview"]
    assert event["data"]["decisions"] == [{"id": "d1", "summary": "Use sandbox first"}]


def test_design_doc_redacts_sensitive_values_in_allowed_decisions():
    bundle = capsule_mapper.map_design_doc(
        session_id="s1",
        design_doc_path="docs/design.md",
        content="safe content",
        decisions=[
            {
                "id": "d1",
                "summary": "wallet 0x1111111111111111111111111111111111111111",
                "rationale": "token sk-live-secret",
            }
        ],
    )

    event = next(a for a in bundle["assets"] if a["type"] == "evolution_event")
    decision = event["data"]["decisions"][0]

    assert "0x1111111111111111111111111111111111111111" not in decision["summary"]
    assert "sk-live-secret" not in decision["rationale"]


def test_map_design_doc_creates_final_design_bundle():
    """map_design_doc must create a final_design bundle."""
    bundle = capsule_mapper.map_design_doc(
        session_id="s1",
        design_doc_path="docs/design.md",
        content="# Design\n\nContent here",
    )

    assert bundle["metadata"]["bundle_type"] == "final_design"
    assert bundle["metadata"]["doc_path"] == "docs/design.md"


def test_map_decision_report_format():
    """map_decision_report must return correct structure."""
    report = capsule_mapper.map_decision_report(
        session_id="s1",
        accepted=["suggestion_1"],
        rejected=["suggestion_2"],
        refined=["suggestion_3"],
    )

    assert report["session_id"] == "s1"
    assert report["decisions"]["accepted"] == ["suggestion_1"]
    assert report["decisions"]["rejected"] == ["suggestion_2"]
    assert report["decisions"]["refined"] == ["suggestion_3"]
    assert report["counts"]["accepted"] == 1
    assert report["counts"]["rejected"] == 1
    assert report["counts"]["refined"] == 1
