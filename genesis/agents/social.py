from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,uuid
@dataclass
class AgentMessage:id:str;sender:str;recipient:str;kind:str;content:str;created_at:str;delivered:bool=False
class MessageBus:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():self.items=[AgentMessage(**x) for x in json.loads(self.path.read_text())]
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-2000:]],indent=2,ensure_ascii=False))
 def send(self,sender,recipient,content,kind="task"):m=AgentMessage(uuid.uuid4().hex[:12],sender,recipient,kind,content,datetime.now(timezone.utc).isoformat());self.items.append(m);self._save();return m
 def inbox(self,r):return [asdict(x) for x in self.items if x.recipient==r and not x.delivered]
 def snapshot(self):return [asdict(x) for x in self.items[-300:]]
