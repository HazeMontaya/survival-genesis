from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json, uuid

@dataclass
class EvolutionProposal:
    id:str
    target:str
    hypothesis:str
    patch_hash:str
    status:str
    created_at:str
    evidence_id:str=""

class EvolutionManager:
    """Self-improvement registry. Proposal != deployment; deployment requires tests and evidence."""
    def __init__(self,path="workspace/evolution.json",evidence=None):
        self.path=Path(path); self.items=self._load(); self.evidence=evidence
    def _load(self):
        if not self.path.exists(): return []
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return []
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(self.items[-1000:],indent=2),encoding="utf-8")
    def propose(self,target,hypothesis,patch_text):
        if not target or not hypothesis: raise ValueError("target and hypothesis required")
        digest=hashlib.sha256(str(patch_text).encode()).hexdigest()
        item=EvolutionProposal(uuid.uuid4().hex[:12],target,hypothesis,digest,"proposed",datetime.now(timezone.utc).isoformat())
        self.items.append(asdict(item)); self._save(); return item
    def verify(self,proposal_id,evidence_id):
        item=next((x for x in self.items if x["id"]==proposal_id),None)
        if not item: raise KeyError(proposal_id)
        if not evidence_id: raise ValueError("evidence required")
        if self.evidence:
            try: self.evidence.require_verified(evidence_id)
            except (KeyError,ValueError) as exc: raise ValueError("evolution verification requires verified evidence") from exc
        item["status"]="verified"; item["evidence_id"]=str(evidence_id); self._save(); return item
    def mark_deployed(self,proposal_id, deployment_evidence_id=""):
        if self.evidence:
            if not deployment_evidence_id:
                raise ValueError("deployment requires evidence")
            try: self.evidence.require_verified(deployment_evidence_id)
            except (KeyError,ValueError) as exc: raise ValueError("deployment requires verified evidence") from exc
        item=next((x for x in self.items if x["id"]==proposal_id),None)
        if not item or item["status"]!="verified": raise ValueError("proposal must be verified before deployment")
        item["status"]="deployed"; self._save(); return item
    def snapshot(self): return self.items[-200:]
