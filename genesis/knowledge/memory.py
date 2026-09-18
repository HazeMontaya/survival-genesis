from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json
@dataclass
class Memory:kind:str;content:str;confidence:float=1.0;created_at:str=""
class MemoryGraph:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():self.items=[Memory(**x) for x in json.loads(self.path.read_text())]
 def remember(self,kind,content,confidence=1):
  x=Memory(kind,content,confidence,datetime.now(timezone.utc).isoformat());self.items.append(x);self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(y) for y in self.items[-500:]],indent=2,ensure_ascii=False));return x
 def snapshot(self):return [asdict(x) for x in self.items[-200:]]
