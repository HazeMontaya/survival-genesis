from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class AgentRecord:
    id: str
    name: str
    purpose: str
    parent_id: str = ""
    state: str = "alive"
    capabilities: list[str] = field(default_factory=list)
    tool_ids: list[str] = field(default_factory=list)
    memory_scope: str = "local"
    lineage_depth: int = 0
    created_at: str = ""
    updated_at: str = ""

class AgentDirectory:
    def __init__(self,path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try: self.items=[AgentRecord(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception: self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def ensure_genesis(self):
        if self.items:
            a=self.items[0]
            required=["read_file","write_file","list_files","run_tests","run_python","remember","send_message"]
            changed=False
            for tool in required:
                if tool not in a.tool_ids: a.tool_ids.append(tool); changed=True
            if changed:
                a.updated_at=datetime.now(timezone.utc).isoformat()
                self._save()
            return a
        now=datetime.now(timezone.utc).isoformat()
        a=AgentRecord("genesis-1","Genesis","Verstehe das Ziel, sichere die eigene Existenz und baue die fehlende Umgebung auf.", "", "alive", [], ["read_file","write_file","list_files","run_tests","run_python","remember","send_message"], "global", 0, now, now)
        self.items.append(a); self._save(); return a

    def spawn(self,name,purpose,parent_id,capabilities=None,tool_ids=None):
        parent=self.get(parent_id)
        now=datetime.now(timezone.utc).isoformat()
        depth=(parent.lineage_depth+1) if parent else 0
        a=AgentRecord(uuid.uuid4().hex[:12],name,purpose,parent_id,"alive",capabilities or [],tool_ids or [],"local",depth,now,now)
        self.items.append(a); self._save(); return a

    def get(self,agent_id): return next((x for x in self.items if x.id==agent_id),None)
    def assign_capability(self,agent_id,capability_id):
        a=self.get(agent_id)
        if a and capability_id not in a.capabilities: a.capabilities.append(capability_id); a.updated_at=datetime.now(timezone.utc).isoformat(); self._save()
    def snapshot(self): return [asdict(x) for x in self.items[-300:]]
