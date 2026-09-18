from dataclasses import dataclass,asdict,field
from datetime import datetime,timezone
from pathlib import Path
import json, uuid
@dataclass
class Memory:
    id:str; kind:str; content:str; confidence:float=1.0; created_at:str=""; uses:int=0; links:list[str]=field(default_factory=list); status:str="alive"
class MemoryGraph:
    def __init__(self,path="workspace/memory.json"):
        self.path=Path(path); self.items=[]; self._load()
    def _load(self):
        if self.path.exists():
            raw=json.loads(self.path.read_text())
            self.items=[Memory(x.get("id",uuid.uuid4().hex[:10]),x["kind"],x["content"],x.get("confidence",1.0),x.get("created_at",""),x.get("uses",0),x.get("links") or [],x.get("status","alive")) for x in raw]
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2))
    def remember(self,kind,content,confidence=1.0,links=None):
        m=Memory(uuid.uuid4().hex[:10],kind,content,float(confidence),datetime.now(timezone.utc).isoformat(),0,links or [],"alive"); self.items.append(m); self._save(); return m
    def use(self,memory_id):
        m=next((x for x in self.items if x.id==memory_id),None)
        if not m: raise KeyError(memory_id)
        m.uses+=1; self._save(); return m
    def link(self,source_id,target_id):
        source=next((x for x in self.items if x.id==source_id),None)
        if not source: raise KeyError(source_id)
        if target_id not in source.links: source.links.append(target_id); self._save()
    def age(self,days=30):
        cutoff=datetime.now(timezone.utc).timestamp()-days*86400
        for m in self.items:
            if m.created_at and datetime.fromisoformat(m.created_at).timestamp()<cutoff and m.uses==0: m.status="stale"
        self._save()
    def snapshot(self): return [asdict(x) for x in self.items[-200:]]
