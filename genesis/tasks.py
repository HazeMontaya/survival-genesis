from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class Task:
    id: str
    agent: str
    room: str
    title: str
    priority: int = 50
    status: str = "queued"
    created_at: str = ""
    updated_at: str = ""
    capability_id: str = ""
    project_id: str = ""
    dependencies: list[str] = field(default_factory=list)
    attempts: int = 0
    max_retries: int = 2
    error: str = ""
    result: str = ""
    evidence: list[dict] = field(default_factory=list)

class TaskBoard:
    def __init__(self,path="workspace/tasks.json"):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            raw=json.loads(self.path.read_text(encoding="utf-8"))
            defaults={"capability_id":"","project_id":"","dependencies":[],"attempts":0,"max_retries":2,"error":"","result":"","evidence":[]}
            self.items=[Task(**{**defaults,**x}) for x in raw]
        except Exception: self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-1000:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def create(self,agent,room,title,priority=50,capability_id="",project_id="",dependencies=None,max_retries=2):
        for t in self.items:
            if t.status in ("queued","active","verifying","blocked") and t.agent==agent and t.title==title:
                return t
        now=datetime.now(timezone.utc).isoformat()
        t=Task(uuid.uuid4().hex[:10],agent,room,title,priority,"queued",now,now,capability_id,project_id,dependencies or [],0,max_retries,"","",[])
        self.items.append(t); self._save(); return t

    def get(self,task_id): return next((t for t in self.items if t.id==task_id),None)

    def _deps_done(self,t):
        return all((self.get(d) and self.get(d).status=="done") for d in t.dependencies)

    def start_next(self,agent=None):
        candidates=[t for t in self.items if t.status=="queued" and (agent is None or t.agent==agent)]
        for t in candidates:
            if not self._deps_done(t):
                t.status="blocked"; t.updated_at=datetime.now(timezone.utc).isoformat()
        candidates=[t for t in candidates if t.status=="queued" and self._deps_done(t)]
        if not candidates:
            self._save(); return None
        t=max(candidates,key=lambda x:x.priority)
        t.status="active"; t.attempts+=1; t.updated_at=datetime.now(timezone.utc).isoformat(); self._save(); return t

    def verify(self,task_id,result,evidence=None):
        t=self.get(task_id)
        if not t: raise KeyError(task_id)
        t.status="verifying"; t.result=result; t.evidence.append(evidence or {"verified":False}); t.updated_at=datetime.now(timezone.utc).isoformat(); self._save(); return t

    def complete(self,task_id,evidence=None,result=""):
        t=self.get(task_id)
        if not t: raise KeyError(task_id)
        t.status="done"; t.result=result or t.result; t.evidence.append(evidence or {"verified":True}); t.updated_at=datetime.now(timezone.utc).isoformat(); self._save(); return t

    def fail(self,task_id,error):
        t=self.get(task_id)
        if not t: raise KeyError(task_id)
        t.error=str(error); t.updated_at=datetime.now(timezone.utc).isoformat()
        t.status="queued" if t.attempts <= t.max_retries else "failed"
        self._save(); return t

    def unblock(self):
        changed=False
        for t in self.items:
            if t.status=="blocked" and self._deps_done(t):
                t.status="queued"; t.updated_at=datetime.now(timezone.utc).isoformat(); changed=True
        if changed: self._save()

    def snapshot(self): return [asdict(x) for x in self.items[-300:]]
