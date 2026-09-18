from genesis.runtime.agent import GenesisAgent
from genesis.runtime.database import RuntimeDatabase
from genesis.runtime.policy import PolicyEngine
from genesis.core.state import StateStore


def test_agent_uses_runtime_control_plane(tmp_path):
    agent = GenesisAgent(store=StateStore(tmp_path / "state.json"))
    result = agent.tick()
    assert result["runtime"]["events"] > 0
    assert result["runtime"]["path"].endswith("runtime.db")
    assert agent.runtime_db.verify_event_chain()
    assert agent.runtime_db.snapshot()["policy_decisions"] >= 0


def test_policy_blocks_protected_paths_and_journals_decision(tmp_path):
    db = RuntimeDatabase(tmp_path / "runtime.db")
    policy = PolicyEngine(db, tmp_path)
    decision = policy.evaluate("write_file", {"path": "treasury.json", "content": "x"})
    assert not decision.allowed
    assert decision.reason == "protected or secret path"
    assert db.snapshot()["policy_decisions"] == 1


def test_audit_chain_detects_tampering(tmp_path):
    db = RuntimeDatabase(tmp_path / "runtime.db")
    db.event("one", {"value": 1}, actor="test")
    db.event("two", {"value": 2}, actor="test")
    assert db.verify_event_chain()
    with db._connect() as conn:
        conn.execute("UPDATE events SET payload='{\"value\":999}' WHERE kind='one'")
    assert not db.verify_event_chain()
