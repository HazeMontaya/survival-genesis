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


def test_need_engine_and_real_tool_handlers(tmp_path):
    store=StateStore(tmp_path/"state.json")
    a=GenesisAgent(store=store)
    assert a.needs.detect()[0]["capability"]=="observe_environment"
    a.memory.remember("observation","test observation",0.9)
    a.tools.call("remember",kind="observation",content="tool observation",confidence=0.9)
    assert any(x["content"]=="tool observation" for x in a.memory.snapshot())
    child=a.agents.spawn("Helper","test", "genesis-1", [], ["send_message"])
    result=a.tools.call("send_message",sender="genesis-1",recipient=child.id,content="hello",kind="task")
    assert result["sent"]
    assert a.messages.inbox(child.id)

def test_no_fake_revenue_on_bootstrap(tmp_path):
    store=StateStore(tmp_path/"state.json")
    a=GenesisAgent(store=store)
    for _ in range(4): a.tick()
    assert a.store.load().earned_eur==0
    assert a.store.load().cash_eur==0


def test_treasury_requires_owner_binding_and_limits(tmp_path,monkeypatch):
    monkeypatch.setenv("GENESIS_OWNER_BIND_TOKEN","owner-secret")
    monkeypatch.setenv("GENESIS_TREASURY_ENABLED","1")
    monkeypatch.setenv("GENESIS_TREASURY_PAYOUT","1")
    monkeypatch.setenv("GENESIS_MAX_PAYOUT_EUR","20")
    monkeypatch.setenv("GENESIS_DAILY_PAYOUT_LIMIT_EUR","20")
    monkeypatch.setenv("GENESIS_MIN_CASH_RESERVE_EUR","5")
    monkeypatch.setenv("GENESIS_ALLOWED_PAYOUT_HASHES","")
    from genesis.treasury import Treasury
    store=StateStore(tmp_path/"state.json")
    t=Treasury(store)
    try:
        t.bind_owner_account("test","owner-account","OWNER","wrong")
        assert False
    except PermissionError:
        pass
    bound=t.bind_owner_account("test","owner-account","OWNER","owner-secret")
    assert bound["account"]["verified"]
    assert not t.can_payout(10,destination="owner-account",current_cash_eur=100)
