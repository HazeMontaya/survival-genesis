from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json

STATES = ("entdeckt","geplant","in_entwicklung","implementiert","getestet","verifiziert","aktiv","fehlgeschlagen")

@dataclass
class Capability:
    id: str
    name: str
    description: str
    owner_agent: str = ""
    prerequisites: list[str] = field(default_factory=list)
    state: str = "entdeckt"
    version: int = 1
    implementation: str = ""
    evidence: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

class CapabilityRegistry:
    def __init__(self, path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try: self.items=[Capability(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception: self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-1000:]], indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, capability_id):
        return next((x for x in self.items if x.id==capability_id), None)

    def active(self, capability_id):
        c=self.get(capability_id)
        return bool(c and c.state=="aktiv")

    def ensure(self, capability_id, name, description, prerequisites=None, owner_agent=""):
        c=self.get(capability_id)
        if c: return c
        now=datetime.now(timezone.utc).isoformat()
        c=Capability(capability_id,name,description,owner_agent,prerequisites or [],"entdeckt",1,"",[],now,now)
        self.items.append(c); self._save(); return c

    def transition(self, capability_id, state, evidence=None, implementation=""):
        if state not in STATES: raise ValueError(f"invalid capability state: {state}")
        c=self.get(capability_id)
        if not c: raise KeyError(capability_id)
        c.state=state; c.updated_at=datetime.now(timezone.utc).isoformat()
        if evidence: c.evidence.append(evidence)
        if implementation: c.implementation=implementation
        if state=="aktiv": c.version=max(1,c.version)
        self._save(); return c

    def snapshot(self):
        return [asdict(x) for x in self.items[-500:]]

    def gaps(self):
        return [asdict(x) for x in self.items if x.state not in ("aktiv","verifiziert")]
