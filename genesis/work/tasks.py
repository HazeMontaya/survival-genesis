from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import json,uuid
@dataclass
class Task:id:str;agent:str;title:str;priority:int=50;status:str="queued";capability_id:str="";project_id:str="";dependencies:list[str]=field(default_factory=list);attempts:int=0;max_retries:int=2;error:str="";result:str="";evidence:list[dict]=field(default_factory=list);created_at:str="";updated_at:str=""
class TaskBoard:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():
   try:self.items=[Task(**x) for x in json.loads(self.path.read_text())]
   except Exception:self.items=[]
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-1000:]],indent=2,ensure_ascii=False))
 def create(self,agent,title,priority=50,capability_id="",project_id="",dependencies=None,max_retries=2):
  for x in self.items:
   if x.status in ("queued","active","blocked") and x.agent==agent and x.title==title:return x
  now=datetime.now(timezone.utc).isoformat();x=Task(uuid.uuid4().hex[:10],agent,title,priority,"queued",capability_id,project_id,dependencies or [],0,max_retries,"","",[],now,now);self.items.append(x);self._save();return x
 def get(self,i):return next((x for x in self.items if x.id==i),None)
 def _done(self,t):return all(self.get(d) and self.get(d).status=="done" for d in t.dependencies)
 def start_next(self,agent=None):
  for x in self.items:
   if x.status=="blocked" and self._done(x):x.status="queued"
  c=[x for x in self.items if x.status=="queued" and (agent is None or x.agent==agent)]
  for x in c:
   if not self._done(x):x.status="blocked"
  c=[x for x in c if x.status=="queued"]
  if not c:self._save();return None
  x=max(c,key=lambda t:t.priority);x.status="active";x.attempts+=1;x.updated_at=datetime.now(timezone.utc).isoformat();self._save();return x
 def complete(self,i,e,r=""):x=self.get(i);x.status="done";x.result=r;x.evidence.append(e);self._save();return x
 def fail(self,i,e):x=self.get(i);x.error=str(e);x.status="queued" if x.attempts<=x.max_retries else "failed";self._save();return x
 def snapshot(self):return [asdict(x) for x in self.items[-300:]]
