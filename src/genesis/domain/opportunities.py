from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class OpportunityRecord:
    id:str
    name:str
    channel:str
    evidence_ids:list[str]
    score:float
    status:str
    created_at:str

class OpportunityLedger:
    """Turns observed signals into traceable opportunity records; it never invents demand."""
    def __init__(self,path="workspace/opportunities.json"):
        self.path=Path(path); self.items=self._load()
    def _load(self):
        if not self.path.exists(): return []
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return []
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.items[-2000:],indent=2,ensure_ascii=False),encoding="utf-8")
    def record(self,name,channel,score,evidence_ids):
        if not evidence_ids: raise ValueError("opportunity requires evidence")
        item=OpportunityRecord(uuid.uuid4().hex[:12],str(name),str(channel),list(evidence_ids),max(0.0,min(1.0,float(score))),"observed",datetime.now(timezone.utc).isoformat())
        self.items.append(asdict(item)); self._save(); return item
    def snapshot(self): return self.items[-500:]
