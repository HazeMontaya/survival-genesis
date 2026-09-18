from genesis.agent import GenesisAgent
from genesis.policy import PolicyEngine
from genesis.constitution import Constitution
from genesis.state import StateStore

def test_policy_denies_external_dangerous_action(tmp_path):
    a=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    d=a.execution_policy.evaluate("live_trade","dangerous","external",{"symbol":"BTC/EUR"})
    assert not d.allowed

def test_policy_denies_protected_self_modification(tmp_path):
    a=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    d=a.execution_policy.evaluate("write_file","caution","self",{"path":"genesis/constitution.py"})
    assert not d.allowed

def test_safe_tool_is_audited_and_allowed(tmp_path):
    a=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    d=a.execution_policy.evaluate("list_files","safe","self",{"path":"."})
    assert d.allowed
    assert (tmp_path/"policy.jsonl").exists()
