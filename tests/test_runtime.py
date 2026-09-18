from genesis.runtime.agent import GenesisAgent
from genesis.core.state import StateStore
from genesis.core.database import RuntimeDatabase
from genesis.core.policy import PolicyEngine
from genesis.domain.economy import Economy,RevenueEvent
from genesis.domain.treasury import Treasury
from genesis.platform.artifacts import ArtifactStore
from genesis.knowledge.memory import MemoryGraph

def test_zero_cost_seed(tmp_path):
 a=GenesisAgent(StateStore(tmp_path/"state.json"));assert len(a.agents.snapshot())==1;assert a.snapshot()["mode"]=="bootstrap"

def test_growth_order(tmp_path):
 a=GenesisAgent(StateStore(tmp_path/"state.json"));assert a.tick()["decision"]["capability"]=="observe_environment";assert a.tick()["decision"]["capability"]=="goal_decomposition";r=a.tick();assert r["decision"]["capability"]=="agent_creation";assert len(a.agents.snapshot())==2

def test_dependencies(tmp_path):
 from genesis.work.tasks import TaskBoard
 b=TaskBoard(tmp_path/"tasks.json");x=b.create("g","A");y=b.create("g","B",dependencies=[x.id]);assert b.start_next("g").id==x.id;b.complete(x.id,{"verified":True});assert b.start_next("g").id==y.id

def test_policy_gate(tmp_path):
 db=RuntimeDatabase(tmp_path/"runtime.db");p=PolicyEngine(db,tmp_path);assert not p.evaluate("publish",authority="self").allowed;assert p.evaluate("read_file",{"path":"x.txt"}).allowed;assert db.verify_chain() 

def test_tools_are_policy_gated(tmp_path):
 a=GenesisAgent(StateStore(tmp_path/"state.json"));a.tools.call("remember",content="ok");assert any(x["content"]=="ok" for x in a.memory.snapshot())

def test_no_fake_revenue(tmp_path):
 s=StateStore(tmp_path/"state.json");e=Economy(s)
 try:e.record_revenue(RevenueEvent("x",10,False));assert False
 except ValueError:pass

def test_commerce_persists(tmp_path):
 from genesis.domain.opportunities import Opportunity
 c=__import__("genesis.domain.commerce",fromlist=["CommerceEngine"]).CommerceEngine(StateStore(tmp_path/"state.json"),ArtifactStore(tmp_path/"artifacts"),MemoryGraph(tmp_path/"memory.json"),RuntimeDatabase(tmp_path/"runtime.db"));o=c.create_offer(Opportunity("x","service",0,10,1,.5));assert o["status"]=="entwurf"

def test_treasury_owner_gate(tmp_path,monkeypatch):
 monkeypatch.setenv("GENESIS_OWNER_BIND_TOKEN","owner-secret");monkeypatch.setenv("GENESIS_TREASURY_ENABLED","1");monkeypatch.setenv("GENESIS_TREASURY_PAYOUT","1");monkeypatch.setenv("GENESIS_MAX_PAYOUT_EUR","20");monkeypatch.setenv("GENESIS_DAILY_PAYOUT_LIMIT_EUR","20");t=Treasury(StateStore(tmp_path/"state.json"));
 try:t.bind_owner_account("x","y","OWNER","wrong");assert False
 except PermissionError:pass
 assert t.bind_owner_account("x","y","OWNER","owner-secret")["account"]["verified"]
