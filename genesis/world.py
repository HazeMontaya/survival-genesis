from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class WorldEntity:
    id: str
    type: str
    name: str
    state: str = "active"
    parent_id: str = ""
    owner_id: str = ""
    x: float = 0
    y: float = 0
    size: float = 1
    reason: str = ""
    created_at: str = ""

@dataclass
class WorldRelation:
    id: str
    source: str
    target: str
    kind: str
    state: str = "active"
    created_at: str = ""

class WorldModel:
    """The visual world is a projection of real runtime entities and relations."""
    def __init__(self,path):
        self.path=Path(path); self.entities=[]; self.relations=[]; self.events=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            raw=json.loads(self.path.read_text(encoding="utf-8"))
            self.entities=[WorldEntity(**x) for x in raw.get("entities",[])]
            self.relations=[WorldRelation(**x) for x in raw.get("relations",[])]
            self.events=raw.get("events",[])
        except Exception:
            self.entities,self.relations,self.events=[],[],[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps({
            "entities":[asdict(x) for x in self.entities[-2000:]],
            "relations":[asdict(x) for x in self.relations[-4000:]],
            "events":self.events[-2000:]
        },indent=2,ensure_ascii=False),encoding="utf-8")

    def _entity(self,entity_id):
        return next((x for x in self.entities if x.id==entity_id),None)

    def ensure(self,entity_id,entity_type,name,parent_id="",owner_id="",reason="",x=0,y=0,size=1):
        e=self._entity(entity_id)
        if e: return e
        now=datetime.now(timezone.utc).isoformat()
        e=WorldEntity(entity_id,entity_type,name,"active",parent_id,owner_id,x,y,size,reason,now)
        self.entities.append(e)
        self.events.append({"id":uuid.uuid4().hex[:10],"type":"welt_entitaet_entstanden","entity":asdict(e),"timestamp":now})
        self._save(); return e

    def relate(self,source,target,kind):
        if any(r.source==source and r.target==target and r.kind==kind for r in self.relations): return
        now=datetime.now(timezone.utc).isoformat()
        self.relations.append(WorldRelation(uuid.uuid4().hex[:10],source,target,kind,"active",now))
        self._save()

    def sync(self,agent):
        """Materialize only things that actually exist in runtime state."""
        self.ensure("genesis-core","core","GENESIS")
        for a in agent.agents.snapshot():
            self.ensure("agent:"+a["id"],"agent",a["name"],"genesis-core",a["id"],a["purpose"])
            if a.get("parent_id"): self.relate("agent:"+a["parent_id"],"agent:"+a["id"],"spawned")
        for c in agent.capabilities.snapshot():
            if c["state"] in ("verifiziert","aktiv","in_entwicklung","implementiert","getestet","geplant","entdeckt"):
                self.ensure("cap:"+c["id"],"capability",c["name"],"genesis-core",c.get("owner_agent",""),c["description"])
                if c.get("owner_agent"): self.relate("agent:"+c["owner_agent"],"cap:"+c["id"],"owns")
        for p in agent.projects.snapshot():
            self.ensure("project:"+p["id"],"project",p["title"],"genesis-core",p.get("owner_agent",""),p["goal"])
            for cid in p.get("required_capabilities",[]): self.relate("project:"+p["id"],"cap:"+cid,"requires")
            for tid in p.get("task_ids",[]): self.relate("project:"+p["id"],"task:"+tid,"contains")
        for t in agent.tasks.snapshot():
            self.ensure("task:"+t["id"],"task",t["title"],"genesis-core",t.get("agent",""),t.get("error",""))
            if t.get("agent"): self.relate("agent:"+t["agent"],"task:"+t["id"],"works_on")
            if t.get("capability_id"): self.relate("task:"+t["id"],"cap:"+t["capability_id"],"targets")
        for a in agent.artifacts.snapshot():
            self.ensure("artifact:"+a["id"],"artifact",a["title"],"genesis-core","",a.get("status",""))
        for c in agent.connectors.snapshot():
            if c.get("configured") or c.get("enabled"):
                self.ensure("connector:"+c["id"],"connector",c["id"],"genesis-core","",c.get("description",""))
        self._save()
        return self.snapshot(agent)

    def assess(self,agent):
        gaps=[]
        offers=agent.commerce.snapshot()["offers"]
        connectors={x["id"]:x for x in agent.connectors.snapshot()}
        if not offers:
            gaps.append(("offer_creation","Erstes nützliches Angebot","Ein verwertbares Ergebnis muss erzeugt werden.","genesis-1"))
        if offers and not any(x.get("published_url") for x in offers):
            gaps.append(("external_publishing","Veröffentlichungsfähigkeit","Ein lokales Angebot ist noch keine externe Veröffentlichung.","genesis-1"))
        if offers and not connectors.get("revenue_webhook",{}).get("configured"):
            gaps.append(("verified_revenue","Verifizierter Zahlungseingang","Ein Umsatzkanal braucht einen nachweisbaren Eingang.","genesis-1"))
        return gaps

    def snapshot(self,agent=None):
        gaps=self.assess(agent) if agent else []
        return {
            "entities":[asdict(x) for x in self.entities[-1500:]],
            "relations":[asdict(x) for x in self.relations[-3000:]],
            "events":self.events[-300:],
            "gaps":[{"id":g[0],"name":g[1],"reason":g[2],"owner":g[3]} for g in gaps],
            "nodes":[{"id":x.id,"kind":x.type,"name":x.name,"room":"genesis","status":x.state,"reason":x.reason,"created_at":x.created_at} for x in self.entities[-500:]],
            "counts":{
                "entities":len(self.entities),
                "relations":len(self.relations),
                "capabilities":sum(x.type=="capability" for x in self.entities),
                "agents":sum(x.type=="agent" for x in self.entities),
                "projects":sum(x.type=="project" for x in self.entities),
                "tasks":sum(x.type=="task" for x in self.entities)
            }
        }
