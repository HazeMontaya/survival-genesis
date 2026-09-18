from genesis.company import CompanyProfile
from genesis.tasks import TaskBoard
from genesis.memory import MemoryGraph
from genesis.artifacts import ArtifactStore
def test_company_identity(): assert CompanyProfile().name=="SURVIVAL GENESIS"
def test_task_board(tmp_path):
    b=TaskBoard(tmp_path/"tasks.json"); b.create("scout","research","Scan opportunity surfaces",90); assert b.start_next().status=="active"; assert b.start_next() is None
def test_task_persistence(tmp_path):
    p=tmp_path/"tasks.json"; b=TaskBoard(p); t=b.create("forge","forge","Build asset",70); assert TaskBoard(p).snapshot()[0]["id"]==t.id
def test_memory_graph(tmp_path):
    p=tmp_path/"memory.json"; MemoryGraph(p).remember("decision","Prioritize zero-cost experiments"); assert len(MemoryGraph(p).snapshot())==1
def test_artifact_store(tmp_path):
    root=tmp_path/"artifacts"; a=ArtifactStore(root).create_markdown("First Asset","# Ready"); assert a.status=="ready"; assert (root/"first-asset.md").exists()
