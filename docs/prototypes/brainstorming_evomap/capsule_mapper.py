# Copyright (C) 2025 Nautech Systems, Inc. All rights reserved.
# Nautech Systems, Inc. Proprietary and Confidential.
# Use subject to license terms.

"""Capsule mapper for converting brainstorming artifacts to EvoMap assets."""

import re
from dataclasses import dataclass, field
from typing import Any
from typing import Final

try:
    from .envelope import compute_content_hash
except ImportError:
    from envelope import compute_content_hash


DEFAULT_ALLOWED_METADATA_KEYS: Final = frozenset(
    {
        "approaches",
        "constraints",
        "decision_ids",
        "section_type",
        "summary",
        "tags",
    }
)
DEFAULT_ALLOWED_DECISION_KEYS: Final = frozenset(
    {"id", "summary", "rationale", "accepted", "rejected", "refined"}
)
SENSITIVE_TEXT_PATTERNS: Final = (
    (re.compile(r"0x[a-fA-F0-9]{64}\b"), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"0x[a-fA-F0-9]{40}\b"), "[REDACTED_ADDRESS]"),
    (re.compile(r"\b[a-fA-F0-9]{64}\b"), "[REDACTED_PRIVATE_KEY]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]+\b"), "[REDACTED_TOKEN]"),
)


@dataclass(frozen=True, slots=True)
class SanitizedPayload:
    value: Any
    redacted_fields: list[str]


@dataclass(frozen=True, slots=True)
class CapsulePolicy:
    allowed_metadata_keys: frozenset[str] = field(
        default_factory=lambda: DEFAULT_ALLOWED_METADATA_KEYS
    )
    allowed_decision_keys: frozenset[str] = field(
        default_factory=lambda: DEFAULT_ALLOWED_DECISION_KEYS
    )

    def sanitize_text(self, value: str, field_name: str = "content") -> SanitizedPayload:
        redacted_fields: list[str] = []
        sanitized = value
        for pattern, replacement in SENSITIVE_TEXT_PATTERNS:
            sanitized, replacements = pattern.subn(replacement, sanitized)
            if replacements:
                redacted_fields.append(field_name)
        return SanitizedPayload(value=sanitized, redacted_fields=redacted_fields)

    def sanitize_value(self, value: Any, field_name: str) -> SanitizedPayload:
        if isinstance(value, str):
            return self.sanitize_text(value, field_name)
        if isinstance(value, list):
            redacted_fields: list[str] = []
            sanitized_items: list[Any] = []
            for index, item in enumerate(value):
                sanitized_item = self.sanitize_value(item, f"{field_name}.{index}")
                sanitized_items.append(sanitized_item.value)
                redacted_fields.extend(sanitized_item.redacted_fields)
            return SanitizedPayload(value=sanitized_items, redacted_fields=redacted_fields)
        if isinstance(value, dict):
            redacted_fields: list[str] = []
            sanitized_dict: dict[str, Any] = {}
            for key, item in value.items():
                sanitized_item = self.sanitize_value(item, f"{field_name}.{key}")
                sanitized_dict[key] = sanitized_item.value
                redacted_fields.extend(sanitized_item.redacted_fields)
            return SanitizedPayload(value=sanitized_dict, redacted_fields=redacted_fields)
        return SanitizedPayload(value=value, redacted_fields=[])

    def sanitize_metadata(self, metadata: dict[str, Any]) -> SanitizedPayload:
        sanitized: dict[str, Any] = {}
        redacted_fields: list[str] = []
        for key, value in metadata.items():
            if key not in self.allowed_metadata_keys:
                redacted_fields.append(f"metadata.{key}")
                continue
            sanitized_value = self.sanitize_value(value, f"metadata.{key}")
            sanitized[key] = sanitized_value.value
            redacted_fields.extend(sanitized_value.redacted_fields)
        return SanitizedPayload(value=sanitized, redacted_fields=redacted_fields)

    def sanitize_decisions(self, decisions: list[dict[str, Any]]) -> SanitizedPayload:
        sanitized_decisions: list[dict[str, Any]] = []
        redacted_fields: list[str] = []
        for index, decision in enumerate(decisions):
            sanitized_decision: dict[str, Any] = {}
            for key, value in decision.items():
                if key not in self.allowed_decision_keys:
                    redacted_fields.append(f"decisions.{index}.{key}")
                    continue
                sanitized_value = self.sanitize_value(
                    value, f"decisions.{index}.{key}"
                )
                sanitized_decision[key] = sanitized_value.value
                redacted_fields.extend(sanitized_value.redacted_fields)
            sanitized_decisions.append(sanitized_decision)
        return SanitizedPayload(value=sanitized_decisions, redacted_fields=redacted_fields)


def _active_policy(policy: CapsulePolicy | None) -> CapsulePolicy:
    return policy if policy is not None else CapsulePolicy()


def map_section_delta(
    session_id: str,
    section_id: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    policy: CapsulePolicy | None = None,
) -> dict[str, Any]:
    """Map a brainstorming section delta to an EvoMap capsule bundle.

    Parameters
    ----------
    session_id : str
        Brainstorming session identifier
    section_id : str
        Section identifier (e.g., 'architecture', 'components')
    content : str
        Section content text
    metadata : dict[str, Any], optional
        Additional metadata (approaches, constraints, decisions)

    Returns
    -------
    dict[str, Any]
        Bundle with assets (Gene, Capsule, EvolutionEvent)
    """
    if metadata is None:
        metadata = {}
    active_policy = _active_policy(policy)
    sanitized_content = active_policy.sanitize_text(content)
    sanitized_metadata = active_policy.sanitize_metadata(metadata)
    redacted_fields = (
        sanitized_content.redacted_fields + sanitized_metadata.redacted_fields
    )

    # Create Gene asset (represents the core idea/concept)
    gene_id = f"gene_{session_id}_{section_id}"
    gene = {
        "id": gene_id,
        "type": "gene",
        "content_hash": compute_content_hash(
            {"content": sanitized_content.value, "metadata": sanitized_metadata.value}
        ),
        "data": {
            "section": section_id,
            "content_preview": (
                sanitized_content.value[:500]
                if len(sanitized_content.value) > 500
                else sanitized_content.value
            ),
            "metadata": sanitized_metadata.value,
        },
    }

    # Create Capsule asset (container for related genes)
    capsule_id = f"capsule_{session_id}_{section_id}"
    capsule = {
        "id": capsule_id,
        "type": "capsule",
        "content_hash": compute_content_hash(
            {"genes": [gene_id], "session": session_id}
        ),
        "data": {
            "session_id": session_id,
            "section_id": section_id,
            "gene_refs": [gene_id],
        },
    }

    # Create EvolutionEvent asset (tracks the evolution)
    event_id = f"event_{session_id}_{section_id}"
    evolution_event = {
        "id": event_id,
        "type": "evolution_event",
        "content_hash": compute_content_hash(
            {"capsule": capsule_id, "action": "section_delta"}
        ),
        "data": {
            "capsule_ref": capsule_id,
            "action": "section_delta",
            "session_id": session_id,
        },
    }

    return {
        "assets": [gene, capsule, evolution_event],
        "metadata": {
            "session_id": session_id,
            "section_id": section_id,
            "bundle_type": "brainstorming_delta",
            "redacted_fields": redacted_fields,
        },
    }


def map_design_doc(
    session_id: str,
    design_doc_path: str,
    content: str,
    decisions: list[dict[str, Any]] | None = None,
    policy: CapsulePolicy | None = None,
) -> dict[str, Any]:
    """Map a finalized design document to an EvoMap capsule bundle.

    Parameters
    ----------
    session_id : str
        Brainstorming session identifier
    design_doc_path : str
        Path to the design document
    content : str
        Full design document content
    decisions : list[dict[str, Any]], optional
        List of decisions made during brainstorming

    Returns
    -------
    dict[str, Any]
        Bundle with assets representing the finalized design
    """
    if decisions is None:
        decisions = []
    active_policy = _active_policy(policy)
    sanitized_content = active_policy.sanitize_text(content)
    sanitized_decisions = active_policy.sanitize_decisions(decisions)
    redacted_fields = (
        sanitized_content.redacted_fields + sanitized_decisions.redacted_fields
    )

    # Create Gene for the full design
    gene_id = f"gene_{session_id}_design_final"
    gene = {
        "id": gene_id,
        "type": "gene",
        "content_hash": compute_content_hash({"content": sanitized_content.value}),
        "data": {
            "type": "design_document",
            "path": design_doc_path,
            "content_preview": (
                sanitized_content.value[:1000]
                if len(sanitized_content.value) > 1000
                else sanitized_content.value
            ),
        },
    }

    # Create Capsule for the complete design
    capsule_id = f"capsule_{session_id}_design_final"
    capsule = {
        "id": capsule_id,
        "type": "capsule",
        "content_hash": compute_content_hash(
            {"genes": [gene_id], "decisions": sanitized_decisions.value}
        ),
        "data": {
            "session_id": session_id,
            "type": "final_design",
            "gene_refs": [gene_id],
            "decision_count": len(decisions),
        },
    }

    # Create EvolutionEvent for the design finalization
    event_id = f"event_{session_id}_design_final"
    evolution_event = {
        "id": event_id,
        "type": "evolution_event",
        "content_hash": compute_content_hash(
            {"capsule": capsule_id, "action": "design_finalized"}
        ),
        "data": {
            "capsule_ref": capsule_id,
            "action": "design_finalized",
            "session_id": session_id,
            "decisions": sanitized_decisions.value,
        },
    }

    return {
        "assets": [gene, capsule, evolution_event],
        "metadata": {
            "session_id": session_id,
            "bundle_type": "final_design",
            "doc_path": design_doc_path,
            "redacted_fields": redacted_fields,
        },
    }


def map_decision_report(
    session_id: str,
    accepted: list[str],
    rejected: list[str],
    refined: list[str],
) -> dict[str, Any]:
    """Map a decision report to EvoMap format.

    Parameters
    ----------
    session_id : str
        Brainstorming session identifier
    accepted : list[str]
        IDs of accepted suggestions
    rejected : list[str]
        IDs of rejected suggestions
    refined : list[str]
        IDs of refined/modified suggestions

    Returns
    -------
    dict[str, Any]
        Decision report payload for EvoMap
    """
    return {
        "session_id": session_id,
        "decisions": {
            "accepted": accepted,
            "rejected": rejected,
            "refined": refined,
        },
        "counts": {
            "accepted": len(accepted),
            "rejected": len(rejected),
            "refined": len(refined),
        },
    }
