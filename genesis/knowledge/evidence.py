from dataclasses import asdict,dataclass
from datetime import datetime,timezone
import hashlib,json
@dataclass(frozen=True)
class Evidence:id:str;kind:str;subject:str;source:str;claim:str;verified:bool=False;confidence:float=0.0;created_at:str="";fingerprint:str="";verifier:str=""
class EvidenceLedger:
 def __init__(self,path):self.path=path;self.items=[];self._load()
 def _load(self):
  if self.path.exists():self.items=[Evidence(**{**x,"verifier":x.get("verifier","")}) for x in json.loads(self.path.read_text())]
 def add(self,kind,subject,source,claim,verified=False,confidence=0,verifier=""):
  if verified and not verifier:raise PermissionError("verified evidence requires verifier identity")
  now=datetime.now(timezone.utc).isoformat();fp=hashlib.sha256(f"{kind}|{subject}|{source}|{claim}".encode()).hexdigest();e=Evidence(fp[:12],kind,subject,source,claim,verified,confidence,now,fp,verifier);self.items.append(e);self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps([asdict(x) for x in self.items[-5000:]],indent=2,ensure_ascii=False));return e
 def verify(self,evidence_id,verifier):
  if not verifier:raise PermissionError("verifier identity required")
  for i,x in enumerate(self.items):
   if x.id==evidence_id:self.items[i]=Evidence(x.id,x.kind,x.subject,x.source,x.claim,True,x.confidence,x.created_at,x.fingerprint,str(verifier));self.path.write_text(json.dumps([asdict(y) for y in self.items[-5000:]],indent=2,ensure_ascii=False));return self.items[i]
  raise KeyError(evidence_id)
 def verified_for(self,subject):return [asdict(x) for x in self.items if x.subject==subject and x.verified]
 def snapshot(self):return [asdict(x) for x in self.items[-500:]]
