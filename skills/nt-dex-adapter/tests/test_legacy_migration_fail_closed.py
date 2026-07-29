import ast
from pathlib import Path


_TEMPLATES = Path(__file__).parent.parent / "templates" / "legacy_migration"
_EXEC_PATH = _TEMPLATES / "dex_exec_client.py"
_DATA_PATH = _TEMPLATES / "dex_data_client.py"


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _method_source(path: Path, class_name: str, method_name: str) -> str:
    source = _source(path)
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == method_name:
                    return ast.get_source_segment(source, member) or ""
    raise AssertionError(f"Missing {class_name}.{method_name}")


def test_submit_order_fails_before_lifecycle_events_when_broadcast_is_unimplemented() -> None:
    method = _method_source(_EXEC_PATH, "MyDEXExecutionClient", "_submit_order")

    assert "raise NotImplementedError" in method
    assert "generate_order_submitted" not in method
    assert "generate_order_rejected" not in method


def test_unimplemented_cancel_paths_fail_before_terminal_events() -> None:
    for method_name in ("_cancel_order", "_cancel_all_orders"):
        method = _method_source(_EXEC_PATH, "MyDEXExecutionClient", method_name)
        assert "raise NotImplementedError" in method
        assert "generate_order_canceled" not in method


def test_unimplemented_account_state_fails_closed() -> None:
    method = _method_source(_EXEC_PATH, "MyDEXExecutionClient", "_update_account_state")

    assert "raise NotImplementedError" in method
    assert "pass" not in method
    assert "generate_account_state" not in method


def test_unimplemented_reconciliation_never_returns_fake_authoritative_state() -> None:
    method_names = (
        "generate_order_status_report",
        "generate_order_status_reports",
        "generate_fill_reports",
        "generate_position_status_reports",
        "generate_mass_status",
    )

    for method_name in method_names:
        method = _method_source(_EXEC_PATH, "MyDEXExecutionClient", method_name)
        assert "raise NotImplementedError" in method
        assert "return None" not in method
        assert "return []" not in method


def test_receipt_monitor_does_not_fabricate_or_terminally_classify_unknown_outcomes() -> None:
    method = _method_source(_EXEC_PATH, "MyDEXExecutionClient", "_wait_for_receipt")

    assert "raise NotImplementedError" in method
    forbidden = (
        "receipt = None",
        "if True",
        '"1.000000"',
        "Money(0",
        "TradeId(tx_hash)",
        "VenueOrderId(tx_hash)",
        "generate_order_rejected",
        "generate_order_canceled",
        "generate_order_expired",
        "generate_order_filled",
    )
    assert all(term not in method for term in forbidden)


def test_non_positive_swap_amount_fails_before_trade_tick_creation() -> None:
    method = _method_source(_DATA_PATH, "MyDEXDataClient", "_swap_event_to_trade_tick")

    assert "if amount_in <= 0" in method
    assert "raise ValueError" in method
    assert "else 0.0" not in method


def test_templates_remain_classified_as_legacy_migration_only() -> None:
    for path in (_EXEC_PATH, _DATA_PATH):
        assert "TEMPLATE_CLASSIFICATION: legacy executable" in _source(path)
        assert path.parent.name == "legacy_migration"
