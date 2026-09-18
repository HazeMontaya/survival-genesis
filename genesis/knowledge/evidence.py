from dataclasses import asdict,dataclass
from datetime import datetime,timezone
import hashlib,json
@dataclass(frozen=True)
class Evidence:id:str;kind:str;subject:str;source:str;claim:str;verified:bool=False;confidence:float=0.0;created_at:str="";fingerprint:str=""
class EvidenceLedger:
 def __init__(self,path):self.path=path;self.items=[];self._load()
 def _load(self):
  if self.path.exists():self.items=[Evidence(**x) for x in json.loads(self.path.read_text())]
 def add(self,kind,subject,source,claim,verified=False,confidence=0):
  now=datetime.now(timezone.utc).isoformat();fp=hashlib.sha256(f"{kind}|{subject}|{source}|{claim}".encode()).hexdigest();e=Evidence(fp[:12],kind,subject,source,claim,verified,confidence,now,fp);self.items.append(e);self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-5000:]],indent=2,ensure_ascii=False));return e
 def verified_for(self,subject):return [asdict(x) for x in self.items if x.subject==subject and x.verified]
 def snapshot(self):return [asdict(x) for x in self.items[-500:]]
