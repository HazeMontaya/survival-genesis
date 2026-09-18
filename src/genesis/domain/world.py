from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, uuid

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
    room: str = ""
    visual_state: str = "idle"
    created_at: str = ""

@dataclass
class WorldRelation:
    id: str
    source: str
    target: str
    kind: str
    state: str = "active"
    intensity: float = 1.0
    created_at: str = ""

class WorldModel:
    """Authoritative projection for the physical world and neural layer.

    The renderer may animate this projection, but it may never invent entities,
    work, evidence, money or success.
    """
    def __init__(self,path):
        self.path=Path(path); self.entities=[]; self.relations=[]; self.events=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            raw=json.loads(self.path.read_text(encoding="utf-8"))
            self.entities=[WorldEntity(**{**x,"room":x.get("room",""),"visual_state":x.get("visual_state","idle")}) for x in raw.get("entities",[])]
            self.relations=[WorldRelation(**{**x,"intensity":x.get("intensity",1.0)}) for x in raw.get("relations",[])]
            self.events=raw.get("events",[])
        except Exception:
            self.entities,self.relations,self.events=[],[],[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps({
            "entities":[asdict(x) for x in self.entities[-2000:]],
            "relations":[asdict(x) for x in self.relations[-5000:]],
            "events":self.events[-2000:]
        },indent=2,ensure_ascii=False),encoding="utf-8")

    def _entity(self,entity_id):
        return next((x for x in self.entities if x.id==entity_id),None)

    def ensure(self,entity_id,entity_type,name,parent_id="",owner_id="",reason="",room="",visual_state="idle",size=1):
        e=self._entity(entity_id)
        if e:
            if room: e.room=room
            if visual_state: e.visual_state=visual_state
            return e
        now=datetime.now(timezone.utc).isoformat()
        e=WorldEntity(entity_id,entity_type,name,"active",parent_id,owner_id,0,0,size,reason,room,visual_state,now)
        self.entities.append(e)
        self.events.append({"id":uuid.uuid4().hex[:10],"type":"world_entity_created","entity":asdict(e),"timestamp":now})
        return e

    def relate(self,source,target,kind,intensity=1.0):
        existing=next((r for r in self.relations if r.source==source and r.target==target and r.kind==kind),None)
        if existing:
            existing.intensity=min(5.0,max(0.1,float(intensity))); return
        self.relations.append(WorldRelation(uuid.uuid4().hex[:10],source,target,kind,"active",float(intensity),datetime.now(timezone.utc).isoformat()))

    @staticmethod
    def _room_for_agent(agent):
        purpose=agent.get("purpose","").lower()
        if "research" in purpose or "signal" in purpose or "markt" in purpose: return "intelligence"
        if "prüf" in purpose or "critic" in purpose: return "quality"
        if "schreib" in purpose or "content" in purpose: return "production"
        return "core"

    @staticmethod
    def _visual_state(agent_id,tasks):
        task=next((t for t in tasks if t.get("agent")==agent_id and t.get("status")=="active"),None)
        if not task: return "idle"
        cap=task.get("capability_id","")
        if "research" in cap or "observe" in cap: return "searching"
        if "test" in cap or "critic" in cap: return "reviewing"
        return "working"

    def sync(self,agent):
        self.ensure("genesis-core","core","GENESIS",room="core",visual_state="running" if getattr(agent.runtime_db,"snapshot",lambda:{})().get("events",0) else "idle")
        tasks=agent.tasks.snapshot()
        for a in agent.agents.snapshot():
            aid="agent:"+a["id"]
            self.ensure(aid,"agent",a["name"],"genesis-core",a["id"],a["purpose"],room=self._room_for_agent(a),visual_state=self._visual_state(a["id"],tasks))
            if a.get("parent_id"): self.relate("agent:"+a["parent_id"],aid,"spawned",1.5)
        for c in agent.capabilities.snapshot():
            if c["state"] in ("verifiziert","aktiv","in_entwicklung","implementiert","getestet","geplant","entdeckt"):
                cid="cap:"+c["id"]; self.ensure(cid,"capability",c["name"],"genesis-core",c.get("owner_agent",""),c["description"],room="intelligence",visual_state="working" if c["state"]=="in_entwicklung" else "idle")
                if c.get("owner_agent"): self.relate("agent:"+c["owner_agent"],cid,"owns",1.2)
        for p in agent.projects.snapshot():
            pid="project:"+p["id"]; self.ensure(pid,"project",p["title"],"genesis-core",p.get("owner_agent",""),p["goal"],room="production",visual_state="working" if p.get("status")=="active" else "idle")
            for cid in p.get("required_capabilities",[]): self.relate(pid,"cap:"+cid,"requires",1.0)
            for tid in p.get("task_ids",[]): self.relate(pid,"task:"+tid,"contains",1.0)
        for t in tasks:
            tid="task:"+t["id"]; visual="working" if t["status"]=="active" else ("complete" if t["status"]=="done" else ("blocked" if t["status"]=="blocked" else "idle"))
            self.ensure(tid,"task",t["title"],"genesis-core",t.get("agent",""),t.get("error",""),room=t.get("room","core"),visual_state=visual)
            if t.get("agent"): self.relate("agent:"+t["agent"],tid,"works_on",2.0 if t["status"]=="active" else .5)
            if t.get("capability_id"): self.relate(tid,"cap:"+t["capability_id"],"targets",1.0)
        for a in agent.artifacts.snapshot():
            self.ensure("artifact:"+a["id"],"artifact",a["title"],"genesis-core","",a.get("status",""),room="production",visual_state="complete" if a.get("status")=="ready" else "idle")
        for c in agent.connectors.snapshot():
            if c.get("configured") or c.get("enabled"): self.ensure("connector:"+c["id"],"connector",c["id"],"genesis-core","",c.get("description",""),room="gateway")
        for s in agent.skills.snapshot(): self.ensure("skill:"+s["id"],"skill",s["name"],"genesis-core","",s["purpose"],room="knowledge")
        for t in agent.tools.snapshot():
            if t.get("enabled"): self.ensure("tool:"+t["id"],"tool",t["id"],"genesis-core","","Werkzeug: "+t["description"],room="factory")
        for e in agent.evidence.snapshot():
            self.ensure("evidence:"+e["id"],"evidence",e.get("kind","evidence"),"genesis-core",e.get("subject_id",""),e.get("summary",""),room="knowledge",visual_state=e.get("status","observed"))
        for o in agent.orders.snapshot():
            self.ensure("order:"+o["id"],"order",o.get("title",o["id"]),"genesis-core",o.get("agent_id",""),o.get("status",""),room="commerce",visual_state=o.get("status","idle"))
        offers=agent.commerce.snapshot().get("offers",[])
        for o in offers:
            self.ensure("offer:"+o["id"],"offer",o.get("title",o["id"]),"genesis-core","","",room="commerce",visual_state="published" if o.get("published_url") else "draft")
        self._save()
        return self.snapshot(agent)

    def assess(self,agent):
        gaps=[]
        offers=agent.commerce.snapshot()["offers"]
        connectors={x["id"]:x for x in agent.connectors.snapshot()}
        if not offers: gaps.append(("offer_creation","Erstes nützliches Angebot","Ein verwertbares Ergebnis muss erzeugt werden.","genesis-1"))
        if offers and not any(x.get("published_url") for x in offers): gaps.append(("external_publishing","Veröffentlichungsfähigkeit","Ein lokales Angebot ist noch keine externe Veröffentlichung.","genesis-1"))
        if offers and not connectors.get("revenue_webhook",{}).get("configured"): gaps.append(("verified_revenue","Verifizierter Zahlungseingang","Ein Umsatzkanal braucht einen nachweisbaren Eingang.","genesis-1"))
        return gaps

    def snapshot(self,agent=None):
        gaps=self.assess(agent) if agent else []
        return {
            "entities":[asdict(x) for x in self.entities[-1500:]],
            "relations":[asdict(x) for x in self.relations[-3000:]],
            "events":self.events[-300:],
            "gaps":[{"id":g[0],"name":g[1],"reason":g[2],"owner":g[3]} for g in gaps],
            "nodes":[{"id":x.id,"kind":x.type,"name":x.name,"room":x.room,"status":x.state,"visual_state":x.visual_state,"reason":x.reason,"created_at":x.created_at} for x in self.entities[-700:]],
            "counts":{"entities":len(self.entities),"relations":len(self.relations),"capabilities":sum(x.type=="capability" for x in self.entities),"agents":sum(x.type=="agent" for x in self.entities),"projects":sum(x.type=="project" for x in self.entities),"tasks":sum(x.type=="task" for x in self.entities),"skills":sum(x.type=="skill" for x in self.entities),"tools":sum(x.type=="tool" for x in self.entities),"evidence":sum(x.type=="evidence" for x in self.entities),"orders":sum(x.type=="order" for x in self.entities)},
            "layers":{"physical":"rooms + agents + tasks","neural":"relations + evidence + knowledge","economic":"offers + orders + treasury"}
        }
