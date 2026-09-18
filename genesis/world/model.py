from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,uuid
@dataclass
class Entity:id:str;type:str;name:str;state:str="active";owner_id:str="";reason:str="";created_at:str=""
@dataclass
class Relation:id:str;source:str;target:str;kind:str;created_at:str=""
class WorldModel:
 def __init__(self,path):self.path=Path(path);self.entities=[];self.relations=[];self._load()
 def _load(self):
  if self.path.exists():
   try:r=json.loads(self.path.read_text());self.entities=[Entity(**x) for x in r.get("entities",[])];self.relations=[Relation(**x) for x in r.get("relations",[])]
   except Exception:pass
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps({"entities":[asdict(x) for x in self.entities[-2000:]],"relations":[asdict(x) for x in self.relations[-4000:]]},indent=2,ensure_ascii=False))
 def ensure(self,i,t,n,owner_id="",reason=""):
  if not any(x.id==i for x in self.entities):self.entities.append(Entity(i,t,n,"active",owner_id,reason,datetime.now(timezone.utc).isoformat()))
 def relate(self,s,t,k):
  if not any(x.source==s and x.target==t and x.kind==k for x in self.relations):self.relations.append(Relation(uuid.uuid4().hex[:10],s,t,k,datetime.now(timezone.utc).isoformat()))
 def sync(self,a):
  self.ensure("genesis-core","core","GENESIS")
  for x in a.agents.snapshot():self.ensure("agent:"+x["id"],"agent",x["name"],x["id"],x["purpose"]);self.relate("genesis-core","agent:"+x["id"],"contains")
  for x in a.capabilities.snapshot():self.ensure("cap:"+x["id"],"capability",x["name"],x.get("owner_agent",""),x["description"])
  for x in a.projects.snapshot():self.ensure("project:"+x["id"],"project",x["title"],x.get("owner_agent",""),x["goal"])
  for x in a.tasks.snapshot():self.ensure("task:"+x["id"],"task",x["title"],x.get("agent",""),x.get("error",""))
  for x in a.artifacts.snapshot():self.ensure("artifact:"+x["id"],"artifact",x["title"],reason=x.get("status",""))
  for x in a.skills.snapshot():self.ensure("skill:"+x["id"],"skill",x["name"],reason=x["purpose"])
  for x in a.tools.snapshot():self.ensure("tool:"+x["id"],"tool",x["id"],reason=x["description"])
  self._save();return self.snapshot()
 def snapshot(self):return {"entities":[asdict(x) for x in self.entities[-1500:]],"relations":[asdict(x) for x in self.relations[-3000:]],"counts":{"entities":len(self.entities),"relations":len(self.relations),"agents":sum(x.type=="agent" for x in self.entities),"capabilities":sum(x.type=="capability" for x in self.entities),"projects":sum(x.type=="project" for x in self.entities),"tasks":sum(x.type=="task" for x in self.entities)}}
