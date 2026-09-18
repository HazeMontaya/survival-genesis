from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from pathlib import Path
import json
@dataclass
class Memory:
    kind:str; content:str; confidence:float=1.0; created_at:str=""
class MemoryGraph:
    def __init__(self,path="workspace/memory.json"):
        self.path=Path(path); self.items=[]; self._load()
    def _load(self):
        if self.path.exists(): self.items=[Memory(**x) for x in json.loads(self.path.read_text())]
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2))
    def remember(self,kind,content,confidence=1.0):
        m=Memory(kind,content,confidence,datetime.now(timezone.utc).isoformat()); self.items.append(m); self._save(); return m
    def snapshot(self): return [asdict(x) for x in self.items[-200:]]
