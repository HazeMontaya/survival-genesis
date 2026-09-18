from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, uuid

@dataclass(frozen=True)
class Evidence:
    id: str
    subject_id: str
    kind: str
    status: str
    summary: str
    fingerprint: str
    created_at: str
    source: str = ""

class EvidenceLedger:
    """Append-only evidence registry. Success claims require recorded evidence."""
    def __init__(self, path="workspace/evidence.json"):
        self.path=Path(path)
        self.items=self._load()

    def _load(self):
        if not self.path.exists(): return []
        try: return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return []

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(self.items[-5000:],indent=2,ensure_ascii=False),encoding="utf-8")

    def record(self, subject_id, kind, summary, payload=None, source="runtime"):
        raw=json.dumps(payload or {},sort_keys=True,default=str)
        item=Evidence(
            uuid.uuid4().hex[:12],str(subject_id),str(kind),"verified",str(summary),
            hashlib.sha256(raw.encode()).hexdigest(),datetime.now(timezone.utc).isoformat(),str(source)
        )
        self.items.append(asdict(item)); self._save(); return item

    def verify(self, evidence_id):
        return next((x for x in self.items if x["id"]==evidence_id and x["status"]=="verified"),None)

    def for_subject(self, subject_id):
        return [x for x in self.items if x["subject_id"]==str(subject_id)]

    def snapshot(self):
        return self.items[-500:]
