from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import json,uuid
@dataclass
class AgentRecord:id:str;name:str;purpose:str;parent_id:str="";state:str="alive";capabilities:list[str]=field(default_factory=list);tool_ids:list[str]=field(default_factory=list);lineage_depth:int=0;created_at:str="";updated_at:str=""
class AgentDirectory:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():
   try:self.items=[AgentRecord(**x) for x in json.loads(self.path.read_text())]
   except Exception:self.items=[]
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False))
 def ensure_genesis(self):
  if self.items:return self.items[0]
  now=datetime.now(timezone.utc).isoformat();x=AgentRecord("genesis-1","Genesis","Verstehe das Ziel, sichere die eigene Existenz und baue die fehlende Umgebung auf.","","alive",[],["read_file","write_file","list_files","run_tests","run_python","remember","send_message"],0,now,now);self.items.append(x);self._save();return x
 def get(self,i):return next((x for x in self.items if x.id==i),None)
 def spawn(self,name,purpose,parent_id,capabilities=None,tool_ids=None):
  p=self.get(parent_id);now=datetime.now(timezone.utc).isoformat();x=AgentRecord(uuid.uuid4().hex[:12],name,purpose,parent_id,"alive",capabilities or [],tool_ids or [],p.lineage_depth+1 if p else 0,now,now);self.items.append(x);self._save();return x
 def assign_capability(self,i,c):
  x=self.get(i)
  if x and c not in x.capabilities:x.capabilities.append(c);x.updated_at=datetime.now(timezone.utc).isoformat();self._save()
 def snapshot(self):return [asdict(x) for x in self.items[-300:]]
