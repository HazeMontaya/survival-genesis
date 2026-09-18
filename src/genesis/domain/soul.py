from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class Soul:
    purpose: str
    principles: list[str]
    strategy: str
    capabilities: list[str]
    version: int = 1
    updated_at: str = ""

class SoulStore:
    def __init__(self,path):
        self.path=Path(path); self.current=None; self.history=[]; self._load()
    def _load(self):
        if not self.path.exists(): return
        try:
            raw=json.loads(self.path.read_text(encoding="utf-8"))
            self.current=Soul(**raw["current"]); self.history=raw.get("history",[])
        except Exception:self.current=None
    def ensure(self,purpose):
        if self.current:return self.current
        self.current=Soul(purpose,["Keine erfundenen Ergebnisse","Jede Fähigkeit braucht Evidenz","Baue nur was zum Ziel beiträgt"],"Beobachten → Entscheiden → Bauen → Prüfen → Lernen",[],1,datetime.now(timezone.utc).isoformat())
        self._save(); return self.current
    def evolve(self,capability):
        s=self.current or self.ensure("")
        if capability not in s.capabilities:s.capabilities.append(capability)
        s.version+=1;s.updated_at=datetime.now(timezone.utc).isoformat();self._save();return s
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps({"current":asdict(self.current),"history":self.history[-100:]},indent=2,ensure_ascii=False),encoding="utf-8")
    def snapshot(self): return asdict(self.current) if self.current else {}
