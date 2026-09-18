from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class Need:
    id: str
    kind: str
    reason: str
    capability_id: str
    priority: int = 50
    prerequisites: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    state: str = "open"
    created_at: str = ""
    updated_at: str = ""

class NeedStore:
    """Persistent gap/need layer. Needs are derived from runtime state, never invented as success."""
    def __init__(self, path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            self.items=[Need(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception:
            self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-1000:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def upsert(self,kind,reason,capability_id,priority=50,prerequisites=None,evidence=None):
        open_need=next((n for n in self.items if n.state=="open" and n.kind==kind and n.capability_id==capability_id),None)
        now=datetime.now(timezone.utc).isoformat()
        if open_need:
            open_need.priority=max(open_need.priority,priority)
            open_need.updated_at=now
            if evidence: open_need.evidence.extend(evidence)
            self._save()
            return open_need
        n=Need(uuid.uuid4().hex[:10],kind,reason,capability_id,priority,prerequisites or [],evidence or [],"open",now,now)
        self.items.append(n); self._save(); return n

    def close_for(self,capability_id):
        changed=False
        now=datetime.now(timezone.utc).isoformat()
        for n in self.items:
            if n.state=="open" and n.capability_id==capability_id:
                n.state="satisfied"; n.updated_at=now; changed=True
        if changed: self._save()

    def open(self):
        return [n for n in self.items if n.state=="open"]

    def snapshot(self):
        return [asdict(n) for n in self.items[-500:]]

class NeedDetector:
    """Derives the next unsatisfied need from the actual state graph."""
    def __init__(self, store):
        self.store=store

    def detect(self,agent):
        self.store.items=[n for n in self.store.items if n.state!="open"]
        memory=agent.memory.snapshot()
        capabilities={c["id"]:c for c in agent.capabilities.snapshot()}
        offers=agent.commerce.snapshot()["offers"]
        agents=agent.agents.snapshot()
        skills=agent.skills.snapshot()
        connectors={c["id"]:c for c in agent.connectors.snapshot()}
        needs=[]

        def require(cid,kind,reason,priority,prereqs=None):
            c=capabilities.get(cid)
            if not c or c["state"] not in ("aktiv","verifiziert"):
                need=self.store.upsert(kind,reason,cid,priority,prereqs)
                needs.append(need)

        if not memory:
            require("observe_environment","bootstrap","Der Startzustand und externe Signale sind unbekannt.",100)
        else:
            require("goal_decomposition","planning","Die Mission wurde noch nicht in überprüfbare Arbeit zerlegt.",95,["observe_environment"])

        if memory:
            require("agent_creation","capacity","Genesis hat noch keine spezialisierte Arbeitskraft aufgebaut.",85,["goal_decomposition"])

        if agents and not offers:
            require("offer_creation","value_creation","Es existiert noch kein überprüfbares, lieferbares Ergebnis.",80)

        if offers and not any("research" in a["purpose"].lower() for a in agents):
            require("specialist_research","evidence","Angebote brauchen reale Markt-/Evidenzsignale.",65,["agent_creation"])

        if not skills and len(agents)>1:
            require("skill_creation","learning","Verifizierte Arbeit soll als wiederverwendbare Fähigkeit gespeichert werden.",55,["agent_creation"])

        if not (capabilities.get("self_testing") or {}).get("state") in ("aktiv","verifiziert"):
            require("self_testing","verification","Neue Fähigkeiten müssen reproduzierbar geprüft werden.",70)

        if offers and not any(x.get("published_url") for x in offers):
            if connectors.get("webhook",{}).get("configured"):
                require("external_publishing","distribution","Ein lokales Angebot ist noch nicht extern veröffentlicht.",50)

        return sorted(needs,key=lambda n:(-n.priority,n.created_at))
