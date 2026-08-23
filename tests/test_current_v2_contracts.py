from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

def read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_architect_actor_example_uses_current_data_actor_contract() -> None:
    text = read("skills/nt-architect/SKILL.md")

    assert "DataActorCore" in text
    assert "nautilus_actor!(RegimeActor)" in text
    assert "fn on_data(&mut self, data: &CustomData)" in text
    assert "publish_data(" in text or "publish_signal(" in text
    assert "self.publish(next.into())" not in text

def test_adapter_guidance_uses_real_factory_and_live_node_apis() -> None:
    text = read("skills/nt-adapters/SKILL.md")

    assert "impl DataClientFactory" in text
    assert "impl ExecutionClientFactory" in text
    assert ".add_data_client(" in text
    assert ".add_exec_client(" in text
    assert "AdapterRegistry" not in text

def test_rust_lifecycle_guidance_covers_current_callbacks() -> None:
    text = read("skills/nt-strategy-builder-rust/SKILL.md")

    for callback in (
        "on_start",
        "on_stop",
        "on_resume",
        "on_reset",
        "on_dispose",
        "on_degrade",
        "on_fault",
    ):
        assert f"`{callback}`" in text
