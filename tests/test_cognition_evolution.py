from genesis.runtime.cognition import CognitionLoop
from genesis.runtime.evolution import EvolutionManager
from genesis.runtime.database import RuntimeDatabase
from genesis.runtime.policy import PolicyEngine
from genesis.integrations.tools import ToolRegistry
from genesis.core.state import StateStore


def test_cognition_is_bounded_and_policy_gated(tmp_path):
    store=StateStore(tmp_path/"state.json")
    db=RuntimeDatabase(tmp_path/"runtime.db")
    policy=PolicyEngine(db,tmp_path)
    tools=ToolRegistry(tmp_path,store,policy=policy)
    calls=[]
    def planner(ctx,obs):
        calls.append(1)
        return {"tool":"remember","args":{"kind":"observation","content":f"turn-{len(calls)}","confidence":1}}
    result=CognitionLoop(policy,tools,max_turns=2).run(planner)
    assert result.status=="budget_exhausted"
    assert result.turns==2
    assert db.verify_event_chain()


def test_evolution_requires_verification_before_deploy(tmp_path):
    manager=EvolutionManager(tmp_path/"evolution.json")
    proposal=manager.propose("src/example.py","reduce unnecessary work","patch")
    try:
        manager.mark_deployed(proposal.id)
        assert False
    except ValueError:
        pass
    verified=manager.verify(proposal.id,"evidence-1")
    assert verified["status"]=="verified"
    assert manager.mark_deployed(proposal.id)["status"]=="deployed"
