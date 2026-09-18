from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class Project:
    id: str
    title: str
    goal: str
    status: str = "planned"
    owner_agent: str = ""
    required_capabilities: list[str] = field(default_factory=list)
    task_ids: list[str] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

class ProjectBoard:
    def __init__(self,path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try: self.items=[Project(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception: self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def create(self,title,goal,owner_agent="",required_capabilities=None):
        now=datetime.now(timezone.utc).isoformat()
        p=Project(uuid.uuid4().hex[:10],title,goal,"planned",owner_agent,required_capabilities or [],[],[],[],now,now)
        self.items.append(p); self._save(); return p

    def get(self,project_id): return next((x for x in self.items if x.id==project_id),None)

    def attach_task(self,project_id,task_id):
        p=self.get(project_id)
        if p and task_id not in p.task_ids: p.task_ids.append(task_id); p.updated_at=datetime.now(timezone.utc).isoformat(); self._save()

    def transition(self,project_id,status,evidence=None):
        p=self.get(project_id)
        if not p: raise KeyError(project_id)
        p.status=status; p.updated_at=datetime.now(timezone.utc).isoformat()
        if evidence: p.evidence.append(evidence)
        self._save(); return p

    def snapshot(self): return [asdict(x) for x in self.items[-300:]]
