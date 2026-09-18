from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json
@dataclass
class Identity:purpose:str;principles:list[str];strategy:str;capabilities:list[str];version:int=1;updated_at:str=""
class IdentityStore:
 def __init__(self,path):self.path=Path(path);self.current=None;self._load()
 def _load(self):
  if self.path.exists():
   r=json.loads(self.path.read_text());self.current=Identity(**r["current"])
 def ensure(self,purpose):
  if self.current:return self.current
  self.current=Identity(purpose,["Keine erfundenen Ergebnisse","Jede Fähigkeit braucht Evidenz","Nur zielrelevante Arbeit"],"Beobachten → Entscheiden → Bauen → Prüfen → Lernen",[],1,datetime.now(timezone.utc).isoformat());self._save();return self.current
 def evolve(self,c):
  s=self.current
  if c not in s.capabilities:s.capabilities.append(c)
  s.version+=1;s.updated_at=datetime.now(timezone.utc).isoformat();self._save();return s
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps({"current":asdict(self.current)},indent=2,ensure_ascii=False))
 def snapshot(self):return asdict(self.current) if self.current else {}
