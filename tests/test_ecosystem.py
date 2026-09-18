from genesis.company import CompanyProfile
from genesis.tasks import TaskBoard
from genesis.memory import MemoryGraph

def test_company_identity():
    assert CompanyProfile().name == "SURVIVAL GENESIS"

def test_task_board():
    b=TaskBoard()
    b.create("scout","research","Scan opportunity surfaces",90)
    assert b.start_next().status == "active"

def test_memory_graph():
    m=MemoryGraph()
    m.remember("decision","Prioritize zero-cost experiments")
    assert len(m.snapshot()) == 1
