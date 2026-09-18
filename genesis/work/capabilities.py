from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import json
STATES=("entdeckt","geplant","in_entwicklung","implementiert","getestet","verifiziert","aktiv","fehlgeschlagen")
@dataclass
class Capability:id:str;name:str;description:str;owner_agent:str="";prerequisites:list[str]=field(default_factory=list);state:str="entdeckt";version:int=1;evidence:list[dict]=field(default_factory=list);created_at:str="";updated_at:str=""
class CapabilityRegistry:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():
   try:self.items=[Capability(**x) for x in json.loads(self.path.read_text())]
   except Exception:self.items=[]
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-1000:]],indent=2,ensure_ascii=False))
 def get(self,c):return next((x for x in self.items if x.id==c),None)
 def ensure(self,c,n,d,p=None,o=""):
  if (x:=self.get(c)):return x
  now=datetime.now(timezone.utc).isoformat();x=Capability(c,n,d,o,p or [],"entdeckt",1,[],now,now);self.items.append(x);self._save();return x
 def transition(self,c,state,e=None):
  if state not in STATES:raise ValueError(state)
  x=self.get(c);x.state=state;x.updated_at=datetime.now(timezone.utc).isoformat();e and x.evidence.append(e);self._save();return x
 def snapshot(self):return [asdict(x) for x in self.items[-500:]]
