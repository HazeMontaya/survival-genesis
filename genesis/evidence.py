"""Evidence ledger: external claims are facts only after explicit verification."""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, hashlib

@dataclass(frozen=True)
class Evidence:
    id: str
    kind: str
    subject: str
    source: str
    claim: str
    verified: bool
    confidence: float
    created_at: str
    fingerprint: str

class EvidenceLedger:
    def __init__(self,path):
        self.path=Path(path); self.items=self._load()
    def _load(self):
        if not self.path.exists(): return []
        return [Evidence(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-5000:]],indent=2,ensure_ascii=False),encoding="utf-8")
    def add(self,kind,subject,source,claim,verified=False,confidence=0.0):
        if not source or not claim: raise ValueError("source and claim are required")
        raw=f"{kind}|{subject}|{source}|{claim}|{verified}|{confidence:.4f}"
        item=Evidence(__import__("uuid").uuid4().hex[:12],str(kind),str(subject),str(source),str(claim),bool(verified),max(0.0,min(1.0,float(confidence))),datetime.now(timezone.utc).isoformat(),hashlib.sha256(raw.encode()).hexdigest())
        self.items.append(item); self._save(); return item
    def verified_for(self,subject):
        return [asdict(x) for x in self.items if x.subject==subject and x.verified]
    def snapshot(self): return [asdict(x) for x in self.items[-500:]]
