from __future__ import annotations

import ast
import importlib.util
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import ModuleType
from typing import Protocol

import pytest
from nautilus_trader.model import ActorId

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/nt-evomap-integration/templates/advisory_actor.py"
FORBIDDEN_HANDLERS = {
    "on_bar",
    "on_book",
    "on_book_deltas",
    "on_data",
    "on_historical_bars",
    "on_historical_data",
    "on_quote",
    "on_signal",
    "on_trade",
}
FORBIDDEN_CALLS = {
    "cancel_order",
    "close_position",
    "modify_order",
    "open",
    "publish_data",
    "publish_signal",
    "queue_for_executor",
    "request_bars",
    "run_in_executor",
    "shutdown_system",
    "submit_order",
    "subscribe_bars",
}
FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "httpx",
    "langchain",
    "langgraph",
    "nautilus_trader.execution",
    "nautilus_trader.model.data",
    "onnxruntime",
    "requests",
    "socket",
    "urllib",
}
REQUIRED_TYPES = {
    "AdvisoryAuditRecord",
    "AdvisoryBridgeActor",
    "AdvisoryDecision",
    "AdvisoryMailboxPort",
    "AdvisoryRequest",
    "AdvisoryResult",
}


class _MailboxPort(Protocol):
    def try_put_result(self, result) -> bool: ...


class _Actor(Protocol):
    _mailbox: _MailboxPort

    @property
    def staged_result(self): ...

    @property
    def authority(self): ...

    def request_review(self, request) -> bool: ...

    def poll_result(self, now_ns: int): ...

    def approve(self, decision) -> bool: ...


def _tree() -> ast.Module:
    return ast.parse(TEMPLATE.read_text(encoding="utf-8"), filename=str(TEMPLATE))


def _module() -> ModuleType:
    existing = sys.modules.get("nt_evomap_advisory_actor")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location("nt_evomap_advisory_actor", TEMPLATE)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _call_name(call: ast.Call) -> str:
    function = call.func
    if isinstance(function, ast.Attribute):
        return function.attr
    if isinstance(function, ast.Name):
        return function.id
    return ""


def _request(module: ModuleType, request_id: str = "request-1"):
    return module.AdvisoryRequest(
        request_id=request_id,
        artifact_hash="artifact-hash",
        deadline_ns=100,
    )


def _result(
    module: ModuleType,
    request_id: str = "request-1",
    suggestion_id: str = "suggestion-1",
    suggestion_hash: str = "suggestion-hash",
):
    return module.AdvisoryResult(
        request_id=request_id,
        suggestion_id=suggestion_id,
        artifact_hash="artifact-hash",
        suggestion_hash=suggestion_hash,
        received_ns=50,
    )


def _decision(
    module: ModuleType,
    request_id: str = "request-1",
    suggestion_id: str = "suggestion-1",
    suggestion_hash: str = "suggestion-hash",
    *,
    approved: bool = True,
    decided_ns: int = 60,
):
    return module.AdvisoryDecision(
        request_id=request_id,
        suggestion_id=suggestion_id,
        suggestion_hash=suggestion_hash,
        approved=approved,
        decided_ns=decided_ns,
    )


def _actor_with_mailbox(module: ModuleType, mailbox: _MailboxPort) -> _Actor:
    actor = module.AdvisoryBridgeActor(module.AdvisoryBridgeActorConfig())
    actor._mailbox = mailbox
    return actor


def test_ai_advisory_template_defines_required_boundary_types() -> None:
    definitions = {
        node.name
        for node in _tree().body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    }

    assert REQUIRED_TYPES <= definitions


def test_ai_advisory_actor_declares_no_market_data_handlers() -> None:
    actor = next(
        node
        for node in _tree().body
        if isinstance(node, ast.ClassDef) and node.name == "AdvisoryBridgeActor"
    )
    methods = {node.name for node in actor.body if isinstance(node, ast.FunctionDef)}

    assert methods.isdisjoint(FORBIDDEN_HANDLERS)


def test_ai_advisory_template_contains_no_forbidden_capability_calls() -> None:
    tree = _tree()
    calls = {_call_name(node) for node in ast.walk(tree) if isinstance(node, ast.Call)}
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )

    assert calls.isdisjoint(FORBIDDEN_CALLS)
    assert not {
        imported
        for imported in imports
        if any(
            imported == forbidden or imported.startswith(f"{forbidden}.")
            for forbidden in FORBIDDEN_IMPORT_ROOTS
        )
    }


def test_advisory_config_preserves_v2_base_fields() -> None:
    module = _module()
    actor_id = ActorId("ADVISORY-001")

    config = module.AdvisoryBridgeActorConfig(
        actor_id=actor_id,
        log_events=False,
        log_commands=False,
        mailbox_capacity=8,
        poll_interval_ms=250,
    )

    assert config.actor_id == actor_id
    assert config.log_events is False
    assert config.log_commands is False
    assert config.mailbox_capacity == 8
    assert config.poll_interval_ms == 250


def test_advisory_records_are_frozen_and_slotted() -> None:
    module = _module()
    records = (
        _request(module),
        _result(module),
        _decision(module),
        module.AdvisoryAuditRecord(
            request_id="request-1",
            suggestion_id="suggestion-1",
            outcome="staged",
            reason="ready_for_review",
            recorded_ns=50,
        ),
    )

    for record in records:
        assert hasattr(type(record), "__dataclass_fields__")
        assert not hasattr(record, "__dict__")
        def mutate(candidate=record) -> None:
            candidate.request_id = "changed"

        with pytest.raises((FrozenInstanceError, AttributeError)):
            mutate()


def test_advisory_mailbox_rejects_write_when_capacity_is_exhausted() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=1)
    first = _request(module)

    assert mailbox.try_put_request(first) is True
    assert mailbox.try_put_request(_request(module, "request-2")) is False
    assert mailbox.try_take_request() == first


def test_advisory_result_is_staged_without_becoming_actionable() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    request = _request(module)

    assert actor.request_review(request) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert actor.staged_result == _result(module)
    assert actor.authority is module.AdvisoryAuthority.NONE


def test_advisory_approval_rejects_each_identity_mismatch() -> None:
    module = _module()
    mutations = (
        (_decision(module, request_id="wrong"), "request_id_mismatch"),
        (_decision(module, suggestion_id="wrong"), "suggestion_id_mismatch"),
        (_decision(module, suggestion_hash="wrong"), "suggestion_hash_mismatch"),
    )

    for decision, reason in mutations:
        mailbox = module.AdvisoryMailboxPort(capacity=4)
        actor = _actor_with_mailbox(module, mailbox)
        assert actor.request_review(_request(module)) is True
        assert mailbox.try_put_result(_result(module)) is True
        assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
        assert mailbox.try_take_audit().reason == "ready_for_review"

        assert actor.approve(decision) is False
        assert actor.authority is module.AdvisoryAuthority.NONE
        assert mailbox.try_take_audit().reason == reason


def test_advisory_approval_grants_only_offline_change_review_authority() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED

    assert actor.approve(_decision(module)) is True
    assert actor.authority is module.AdvisoryAuthority.OFFLINE_CHANGE_REVIEW


def test_approved_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED

    assert actor.approve(_decision(module)) is True
    assert actor.staged_result is None
    next_request = module.AdvisoryRequest(
        request_id="request-2",
        artifact_hash="artifact-hash",
        deadline_ns=300,
    )
    assert actor.request_review(next_request) is True


def test_rejected_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED

    assert actor.approve(_decision(module, approved=False)) is False
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2")) is True


def test_timed_out_review_releases_actor_for_next_request() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.TIMED_OUT
    assert mailbox.try_take_audit().reason == "request_timeout"
    assert actor.request_review(_request(module, "request-2")) is True


def test_timeout_audit_backpressure_keeps_request_pending() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2, audit_capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_append_audit(
        module.AdvisoryAuditRecord(
            request_id="occupied",
            suggestion_id=None,
            outcome="occupied",
            reason="test_backpressure",
            recorded_ns=90,
        ),
    ) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.AUDIT_BLOCKED
    assert actor.request_review(_request(module, "request-2")) is False
    assert mailbox.try_take_audit().reason == "test_backpressure"
    assert actor.poll_result(now_ns=101) == module.AdvisoryResultStatus.TIMED_OUT
    assert actor.request_review(_request(module, "request-2")) is True


def test_advisory_audit_backpressure_prevents_state_transition() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2, audit_capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert mailbox.try_take_audit().reason == "ready_for_review"
    assert mailbox.try_append_audit(
        module.AdvisoryAuditRecord(
            request_id="occupied",
            suggestion_id=None,
            outcome="occupied",
            reason="test_backpressure",
            recorded_ns=55,
        ),
    ) is True

    assert actor.approve(_decision(module)) is False
    assert actor.authority is module.AdvisoryAuthority.NONE


def test_advisory_poll_backpressure_retains_result_until_audit_accepts() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=2, audit_capacity=1)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_append_audit(
        module.AdvisoryAuditRecord(
            request_id="occupied",
            suggestion_id=None,
            outcome="occupied",
            reason="test_backpressure",
            recorded_ns=45,
        ),
    ) is True
    assert mailbox.try_put_result(result) is True

    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.AUDIT_BLOCKED
    assert mailbox.try_take_audit().reason == "test_backpressure"
    assert actor.poll_result(now_ns=51) == module.AdvisoryResultStatus.STAGED
    assert actor.staged_result == result


def test_timely_result_replay_is_rejected() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert mailbox.try_take_audit().reason == "ready_for_review"

    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=51) == module.AdvisoryResultStatus.REJECTED
    assert mailbox.try_take_audit().reason == "result_replay"


def test_late_approval_ends_request_and_releases_actor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert mailbox.try_take_audit().reason == "ready_for_review"

    late = module.AdvisoryDecision(
        request_id="request-1",
        suggestion_id="suggestion-1",
        suggestion_hash="suggestion-hash",
        approved=True,
        decided_ns=100,
    )
    assert actor.approve(late) is False
    assert mailbox.try_take_audit().reason == "decision_late"
    assert actor.authority is module.AdvisoryAuthority.NONE
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2")) is True


def test_rejected_advisory_decision_is_terminal_and_releases_actor() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True
    assert actor.poll_result(now_ns=50) == module.AdvisoryResultStatus.STAGED
    assert mailbox.try_take_audit().reason == "ready_for_review"

    rejected = module.AdvisoryDecision(
        request_id="request-1",
        suggestion_id="suggestion-1",
        suggestion_hash="suggestion-hash",
        approved=False,
        decided_ns=60,
    )
    assert actor.approve(rejected) is False
    assert mailbox.try_take_audit().reason == "operator_rejected"
    assert actor.authority is module.AdvisoryAuthority.NONE
    assert actor.staged_result is None
    assert actor.request_review(_request(module, "request-2")) is True


def test_advisory_result_at_or_after_deadline_is_rejected_as_late() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    assert actor.request_review(_request(module)) is True
    assert mailbox.try_put_result(_result(module)) is True

    assert actor.poll_result(now_ns=100) == module.AdvisoryResultStatus.LATE
    assert actor.staged_result is None
    assert mailbox.try_take_audit().reason == "late_result"


def test_advisory_result_for_timed_out_request_remains_rejected_on_replay() -> None:
    module = _module()
    mailbox = module.AdvisoryMailboxPort(capacity=4)
    actor = _actor_with_mailbox(module, mailbox)
    result = _result(module)
    assert actor.request_review(_request(module)) is True

    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=101) == module.AdvisoryResultStatus.LATE
    assert mailbox.try_take_audit().reason == "late_result"
    next_request = module.AdvisoryRequest(
        request_id="request-2",
        artifact_hash="artifact-hash",
        deadline_ns=300,
    )
    assert actor.request_review(next_request) is True
    assert mailbox.try_put_result(result) is True
    assert actor.poll_result(now_ns=200) == module.AdvisoryResultStatus.REJECTED
    assert mailbox.try_take_audit().reason == "result_replay"
    assert actor.staged_result is None
