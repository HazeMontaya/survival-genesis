from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from .state import StateStore

@dataclass
class Room:
    id: str
    name: str
    subtitle: str
    color: str
    status: str = "online"
    load: int = 0

@dataclass
class AgentNode:
    id: str
    name: str
    role: str
    room: str
    status: str = "idle"
    task: str = "Awaiting assignment"
    energy: int = 100

ROOMS=[
 Room("command","Genesis Command","Strategy · Memory · Governance","violet"),
 Room("research","Research Lab","Signals · Markets · Opportunities","cyan"),
 Room("forge","Product Forge","Products · Code · Assets","orange"),
 Room("growth","Growth Studio","Brand · Content · Distribution","pink"),
 Room("sales","Revenue Floor","Offers · Leads · Conversion","green"),
 Room("treasury","Treasury","Ledger · Reserves · Reinvestment","gold"),
 Room("operations","Operations","Fulfillment · QA · Automation","blue"),
 Room("evolution","Evolution Lab","Experiments · Learning · Expansion","purple"),
]
AGENTS=[
 AgentNode("ceo","Genesis","Executive Orchestrator","command","active","Choosing the next highest-value action"),
 AgentNode("scout","Scout","Market Intelligence","research","scanning","Scanning opportunity surfaces"),
 AgentNode("analyst","Atlas","Opportunity Analyst","research","idle","Ranking zero-capital experiments"),
 AgentNode("maker","Forge","Product Builder","forge","ready","Waiting for a validated product brief"),
 AgentNode("writer","Muse","Content & Brand","growth","idle","Preparing distribution assets"),
 AgentNode("seller","Closer","Sales Agent","sales","guarded","External outreach disabled by policy"),
 AgentNode("ledger","Ledger","Treasury Controller","treasury","watching","Verifying revenue before recognition"),
 AgentNode("operator","Ops","Operations Agent","operations","idle","Monitoring execution queue"),
 AgentNode("evolver","Evo","Experiment Scientist","evolution","learning","Measuring system feedback"),
]
def ecosystem_snapshot(agent):
    ledger=agent.store.load()
    tasks=agent.tasks.snapshot()
    active={t["agent"]:t for t in tasks if t["status"]=="active"}
    rooms=[]
    for r in ROOMS:
        load=sum(1 for t in tasks if t["room"]==r.id and t["status"] in ("queued","active"))
        rooms.append({**asdict(r),"load":load})
    agents=[]
    for a in AGENTS:
        x=asdict(a)
        if a.id in active:
            x["status"]="working"; x["task"]=active[a.id]["title"]
        agents.append(x)
    return {
      "company":agent.company.snapshot(),
      "rooms":rooms,
      "agents":agents,
      "tasks":tasks,
      "memory":agent.memory.snapshot(),
      "clock":datetime.now(timezone.utc).isoformat(),
      "ledger":ledger.__dict__,
    }
