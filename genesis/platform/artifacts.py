from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,re,uuid
@dataclass
class Artifact:id:str;kind:str;title:str;path:str;status:str="draft";created_at:str="";updated_at:str=""
class ArtifactStore:
 def __init__(self,root):self.root=Path(root);self.index=self.root/"index.json";self.items=[];self._load()
 def _load(self):
  if self.index.exists():self.items=[Artifact(**x) for x in json.loads(self.index.read_text())]
 def create_markdown(self,title,body,kind="product"):
  slug=re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")[:60] or uuid.uuid4().hex[:8];self.root.mkdir(parents=True,exist_ok=True);p=self.root/f"{slug}.md";p.write_text(body,encoding="utf-8");now=datetime.now(timezone.utc).isoformat();x=Artifact(uuid.uuid4().hex[:10],kind,title,str(p),"ready",now,now);self.items.append(x);self.index.write_text(json.dumps([asdict(y) for y in self.items[-500:]],indent=2,ensure_ascii=False));return x
 def snapshot(self):return [asdict(x) for x in self.items[-100:]]
