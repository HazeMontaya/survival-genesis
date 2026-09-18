from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from .state import StateStore

@dataclass
class Room:
    id:str
    name:str
    subtitle:str
    color:str
    status:str="online"
    load:int=0

ROOMS=[
 Room("command","Genesis Command","Strategy · Memory · Governance","violet"),
 Room("research","Research Lab","Signals · Evidence · Opportunities","cyan"),
 Room("forge","Product Forge","Products · Offers · Assets","orange"),
 Room("growth","Growth Studio","Content · Distribution","pink"),
 Room("sales","Revenue Floor","Leads · Conversion","green"),
 Room("treasury","Treasury","Ledger · Reserves · Reinvestment","gold"),
 Room("operations","Operations","Fulfillment · QA · Automation","blue"),
 Room("evolution","Evolution Lab","Experiments · Learning","purple"),
]
AGENT_DEFS=[
 ("ceo","Genesis","Executive Orchestrator","command"),
 ("scout","Scout","Market Intelligence","research"),
 ("analyst","Atlas","Opportunity Analyst","research"),
 ("maker","Forge","Product Builder","forge"),
 ("writer","Muse","Content & Brand","growth"),
 ("seller","Closer","Sales Agent","sales"),
 ("ledger","Ledger","Treasury Controller","treasury"),
 ("operator","Ops","Operations Agent","operations"),
 ("evolver","Evo","Experiment Scientist","evolution"),
]
def ecosystem_snapshot(agent):
    ledger=agent.store.load(); tasks=agent.tasks.snapshot()
    active={t["agent"]:t for t in tasks if t["status"]=="active"}
    rooms=[]
    for r in ROOMS:
        queued=[t for t in tasks if t["room"]==r.id and t["status"] in ("queued","active")]
        rooms.append({**asdict(r),"load":len(queued),"queued":sum(t["status"]=="queued" for t in queued),"active":sum(t["status"]=="active" for t in queued)})
    agents=[]
    for aid,name,role,room in AGENT_DEFS:
        t=active.get(aid)
        agents.append({"id":aid,"name":name,"role":role,"room":room,"status":"working" if t else "idle","task":t["title"] if t else "No active task","energy":100})
    return {"company":agent.company.snapshot(),"rooms":rooms,"agents":agents,"tasks":tasks,
            "memory":agent.memory.snapshot(),"clock":datetime.now(timezone.utc).isoformat(),"ledger":ledger.__dict__}
