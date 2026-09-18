from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import uuid

@dataclass
class Task:
    id: str
    agent: str
    room: str
    title: str
    priority: int = 50
    status: str = "queued"
    created_at: str = ""

class TaskBoard:
    def __init__(self):
        self.items=[]

    def create(self, agent, room, title, priority=50):
        t=Task(uuid.uuid4().hex[:10],agent,room,title,priority,"queued",datetime.now(timezone.utc).isoformat())
        self.items.append(t)
        return t

    def start_next(self):
        queued=[t for t in self.items if t.status=="queued"]
        if not queued: return None
        t=max(queued,key=lambda x:x.priority); t.status="active"; return t

    def snapshot(self):
        return [asdict(x) for x in self.items[-100:]]
