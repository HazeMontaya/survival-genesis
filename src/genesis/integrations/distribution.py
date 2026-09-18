from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class Publication:
    id:str
    offer_id:str
    channel:str
    content:str
    status:str
    evidence_id:str
    created_at:str

class DistributionEngine:
    """Local-first publication queue. External publishing is only performed by configured adapters."""
    def __init__(self,path="workspace/publications.json"):
        self.path=Path(path); self.items=self._load()
    def _load(self):
        if not self.path.exists(): return []
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return []
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(self.items[-2000:],indent=2,ensure_ascii=False),encoding="utf-8")
    def queue(self,offer_id,channel,content,evidence_id):
        if not offer_id or not content or not evidence_id: raise ValueError("publication requires offer, content and evidence")
        item=Publication(uuid.uuid4().hex[:12],str(offer_id),str(channel),str(content),"queued",str(evidence_id),datetime.now(timezone.utc).isoformat())
        self.items.append(item.__dict__); self._save(); return item
    def mark_published(self,publication_id,evidence_id,external_ref):
        item=next((x for x in self.items if x["id"]==publication_id),None)
        if not item: raise KeyError(publication_id)
        if not evidence_id or not external_ref: raise ValueError("published state requires external evidence")
        item.update(status="published",evidence_id=str(evidence_id),external_ref=str(external_ref))
        self._save(); return item
    def snapshot(self): return self.items[-500:]
