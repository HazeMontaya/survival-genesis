from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

AGENT_STATES={"alive","paused","archived","blocked"}

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
    location: str = "core"
    activity: str = "idle"
    created_at: str = ""
    updated_at: str = ""

class AgentDirectory:
    """Persistent agent identity, lifecycle and world-location projection source."""
    def __init__(self,path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:self.items=[AgentRecord(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception:self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def ensure_genesis(self):
        if self.items:
            a=self.items[0]
            required=["read_file","write_file","list_files","run_tests","run_python","remember","send_message"]
            changed=False
            for tool in required:
                if tool not in a.tool_ids:a.tool_ids.append(tool);changed=True
            if changed:self.touch(a)
            return a
        now=datetime.now(timezone.utc).isoformat()
        a=AgentRecord("genesis-1","Genesis","Verstehe das Ziel, sichere die eigene Existenz und baue die fehlende Umgebung auf.","","alive",[],["read_file","write_file","list_files","run_tests","run_python","remember","send_message"],"global",0,"core","idle",now,now)
        self.items.append(a);self._save();return a

    def spawn(self,name,purpose,parent_id,capabilities=None,tool_ids=None):
        parent=self.get(parent_id)
        if parent is None: raise ValueError(f"parent agent not found: {parent_id}")
        if parent.state!="alive": raise ValueError("only a live agent may spawn an agent")
        now=datetime.now(timezone.utc).isoformat()
        a=AgentRecord(uuid.uuid4().hex[:12],name,purpose,parent_id,"alive",capabilities or [],tool_ids or [],"local",parent.lineage_depth+1,self.default_room(purpose),"idle",now,now)
        self.items.append(a);self._save();return a

    @staticmethod
    def default_room(purpose):
        p=str(purpose).lower()
        if any(x in p for x in ("research","scout","signal","market")):return "intelligence"
        if any(x in p for x in ("critic","quality","test","review")):return "quality"
        if any(x in p for x in ("writer","write","content","design","production")):return "production"
        if any(x in p for x in ("memory","knowledge")):return "knowledge"
        return "core"

    def set_activity(self,agent_id,activity,location=None):
        if activity not in {"idle","thinking","searching","walking","collaborating","processing","reviewing","blocked","error","completed"}: raise ValueError("invalid agent activity")
        a=self.get(agent_id)
        if not a: raise KeyError(agent_id)
        if a.state!="alive" and activity not in {"idle","blocked"}: raise ValueError("inactive agent cannot perform activity")
        a.activity=activity
        if location is not None:a.location=str(location)
        self.touch(a)

    def pause(self,agent_id):
        a=self.get(agent_id)
        if not a:raise KeyError(agent_id)
        a.state="paused";a.activity="idle";self.touch(a)

    def resume(self,agent_id):
        a=self.get(agent_id)
        if not a:raise KeyError(agent_id)
        if a.state!="paused":raise ValueError("agent is not paused")
        a.state="alive";self.touch(a)

    def archive(self,agent_id):
        a=self.get(agent_id)
        if not a:raise KeyError(agent_id)
        if a.id=="genesis-1":raise ValueError("Genesis cannot be archived")
        a.state="archived";a.activity="idle";self.touch(a)

    def touch(self,a):
        a.updated_at=datetime.now(timezone.utc).isoformat();self._save()

    def get(self,agent_id):return next((x for x in self.items if x.id==agent_id),None)
    def assign_capability(self,agent_id,capability_id):
        a=self.get(agent_id)
        if not a:raise KeyError(agent_id)
        if capability_id not in a.capabilities:a.capabilities.append(capability_id);self.touch(a)
    def snapshot(self):return [asdict(x) for x in self.items[-300:]]
