from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,re
@dataclass
class Skill:id:str;name:str;purpose:str;instructions:str;version:int=1;status:str="active";created_at:str="";updated_at:str=""
class SkillRegistry:
 def __init__(self,path):self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if self.path.exists():self.items=[Skill(**x) for x in json.loads(self.path.read_text())]
 def create(self,i,n,p,ins):
  old=next((x for x in self.items if x.id==i),None)
  if old:return old
  now=datetime.now(timezone.utc).isoformat();x=Skill(re.sub(r"[^a-zA-Z0-9_-]","_",i),n,p,ins,1,"active",now,now);self.items.append(x);self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(y) for y in self.items[-500:]],indent=2,ensure_ascii=False));return x
 def snapshot(self):return [asdict(x) for x in self.items[-300:]]
