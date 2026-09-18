from genesis.runtime.agent import GenesisAgent
from genesis.core.state import StateStore

def test_genesis_boots_and_ticks(tmp_path):
    agent=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    result=agent.tick()
    assert result["mode"]=="bootstrap"
    assert result["ledger"]["cash_eur"]==0
    assert result["runtime"]["events"]>0
    assert agent.runtime_db.verify_event_chain()
