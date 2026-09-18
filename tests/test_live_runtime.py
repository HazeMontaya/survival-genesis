from genesis.agent import GenesisAgent
from genesis.state import StateStore
from genesis.commerce import CommerceEngine
from genesis.artifacts import ArtifactStore
from genesis.memory import MemoryGraph

def test_genesis_starts_as_single_seed_and_grows(tmp_path):
    store=StateStore(tmp_path/"state.json")
    a=GenesisAgent(store=store)
    assert len(a.agents.snapshot())==1
    assert a.agents.snapshot()[0]["parent_id"]==""
    first=a.tick()
    assert first["decision"]["capability"]=="observe_environment"
    assert first["capabilities"][0]["state"]=="aktiv"
    assert len(first["world"]["entities"])>=2
    second=a.tick()
    assert second["decision"]["capability"]=="goal_decomposition"
    third=a.tick()
    assert third["decision"]["capability"]=="agent_creation"
    assert len(a.agents.snapshot())>=2
    fourth=a.tick()
    assert fourth["commerce"]["offers"]
    assert fourth["world"]["counts"]["agents"]>=2

def test_commerce_persists(tmp_path):
    store=StateStore(tmp_path/"state.json")
    c=CommerceEngine(store,ArtifactStore(tmp_path/"artifacts"),MemoryGraph(tmp_path/"memory.json"))
    class O:
        name="test_offer"; channel="service"; expected_margin_eur=10
    offer=c.create_offer(O())
    assert offer["status"]=="entwurf"
    assert CommerceEngine(store,ArtifactStore(tmp_path/"artifacts"),MemoryGraph(tmp_path/"memory.json")).snapshot()["offers"]

def test_task_dependencies_and_retry(tmp_path):
    from genesis.tasks import TaskBoard
    board=TaskBoard(tmp_path/"tasks.json")
    a=board.create("genesis-1","genesis","A")
    b=board.create("genesis-1","genesis","B",dependencies=[a.id])
    assert board.start_next("genesis-1").id==a.id
    board.complete(a.id)
    assert board.start_next("genesis-1").id==b.id

def test_world_contract():
    from pathlib import Path
    p=Path(__file__).parents[1]/"world"/"index.html"
    assert p.exists()
    html=p.read_text(encoding="utf-8")
    assert "<svg" in html
    assert "/api/state" in html
    assert "world.entities" in html
