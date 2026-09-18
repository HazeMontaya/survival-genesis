from dataclasses import dataclass, asdict
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

class TaskBoard:
    def __init__(self, path="workspace/tasks.json"):
        self.path=Path(path)
        self.items=[]
        self._load()

    def _load(self):
        if self.path.exists():
            self.items=[Task(**x) for x in json.loads(self.path.read_text())]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2))

    def create(self, agent, room, title, priority=50):
        now=datetime.now(timezone.utc).isoformat()
        t=Task(uuid.uuid4().hex[:10],agent,room,title,priority,"queued",now,now)
        self.items.append(t); self._save(); return t

    def start_next(self, agent=None):
        queued=[t for t in self.items if t.status=="queued" and (agent is None or t.agent==agent)]
        if not queued: return None
        t=max(queued,key=lambda x:x.priority); t.status="active"; t.updated_at=datetime.now(timezone.utc).isoformat()
        self._save(); return t

    def complete(self, task_id, result=""):
        for t in self.items:
            if t.id==task_id:
                t.status="done"; t.updated_at=datetime.now(timezone.utc).isoformat()
                self._save(); return t
        raise KeyError(task_id)

    def fail(self, task_id, error):
        for t in self.items:
            if t.id==task_id:
                t.status="failed"; t.updated_at=datetime.now(timezone.utc).isoformat()
                self._save(); return t
        raise KeyError(task_id)

    def snapshot(self):
        return [asdict(x) for x in self.items[-100:]]
