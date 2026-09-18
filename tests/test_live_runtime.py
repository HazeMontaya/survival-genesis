from genesis.agent import GenesisAgent
from genesis.state import StateStore
from genesis.commerce import CommerceEngine
from genesis.artifacts import ArtifactStore
from genesis.memory import MemoryGraph

def test_cycle_builds_live_state(tmp_path):
    store=StateStore(tmp_path/"state.json")
    a=GenesisAgent(store=store)
    out=a.tick()
    assert out["selected"]["name"]
    assert out["commerce"]["offers"]
    assert out["commerce"]["leads"]
    assert out["signals"]
    assert store.events()

def test_commerce_persists(tmp_path):
    store=StateStore(tmp_path/"state.json")
    c=CommerceEngine(store,ArtifactStore(tmp_path/"artifacts"),MemoryGraph(tmp_path/"memory.json"))
    class O:
        name="test_offer"; channel="service"; expected_margin_eur=10
    offer=c.create_offer(O())
    assert offer["status"]=="entwurf"
    assert CommerceEngine(store,ArtifactStore(tmp_path/"artifacts"),MemoryGraph(tmp_path/"memory.json")).snapshot()["offers"]

def test_world_contract():
    from pathlib import Path
    p=Path(__file__).parents[1]/"world"/"index.html"
    assert p.exists()
    html=p.read_text(encoding="utf-8")
    assert "<svg" in html
    assert "/api/state" in html
