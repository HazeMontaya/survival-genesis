from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import json,uuid
@dataclass
class Project:id:str;title:str;goal:str;status:str="planned";owner_agent:str="";required_capabilities:list[str]=field(default_factory=list);task_ids:list[str]=field(default_factory=list);evidence:list[dict]=field(default_factory=list);created_at:str="";updated_at:str=""
class ProjectBoard:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():
   try:self.items=[Project(**x) for x in json.loads(self.path.read_text())]
   except Exception:self.items=[]
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False))
 def create(self,title,goal,owner_agent="",required_capabilities=None):
  now=datetime.now(timezone.utc).isoformat();x=Project(uuid.uuid4().hex[:10],title,goal,"planned",owner_agent,required_capabilities or [],[],[],now,now);self.items.append(x);self._save();return x
 def get(self,i):return next((x for x in self.items if x.id==i),None)
 def attach_task(self,p,t):x=self.get(p);x and t not in x.task_ids and (x.task_ids.append(t),self._save())
 def snapshot(self):return [asdict(x) for x in self.items[-300:]]
