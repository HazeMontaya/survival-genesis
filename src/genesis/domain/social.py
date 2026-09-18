from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class AgentMessage:
    id: str
    sender: str
    recipient: str
    kind: str
    content: str
    created_at: str
    delivered: bool = False

class MessageBus:
    def __init__(self,path):
        self.path=Path(path); self.items=[]; self._load()

    def _load(self):
        if not self.path.exists(): return
        try:self.items=[AgentMessage(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception:self.items=[]

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-2000:]],indent=2,ensure_ascii=False),encoding="utf-8")

    def send(self,sender,recipient,content,kind="task"):
        m=AgentMessage(uuid.uuid4().hex[:12],sender,recipient,kind,content,datetime.now(timezone.utc).isoformat(),False)
        self.items.append(m); self._save(); return m

    def inbox(self,recipient,mark_delivered=False):
        out=[m for m in self.items if m.recipient==recipient and not m.delivered]
        if mark_delivered:
            for m in out:m.delivered=True
            self._save()
        return [asdict(m) for m in out]

    def broadcast(self,sender,recipients,content,kind="broadcast"):
        return [asdict(self.send(sender,r,content,kind)) for r in recipients]

    def snapshot(self): return [asdict(x) for x in self.items[-300:]]
