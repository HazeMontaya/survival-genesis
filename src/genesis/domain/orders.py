from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

STATES=("lead","quoted","accepted","paid","fulfilling","delivered","completed","cancelled","refunded")

@dataclass
class Order:
    id:str
    offer_id:str
    customer_ref:str
    amount_eur:float
    status:str
    evidence_id:str
    created_at:str
    updated_at:str

class OrderEngine:
    """Provider-neutral commercial lifecycle. External money is never fabricated."""
    
    @staticmethod
    def _order(item):
        return Order(**item)

    def __init__(self,path="workspace/orders.json",evidence=None):
        self.path=Path(path); self.orders=self._load(); self.evidence=evidence
    def _load(self):
        if not self.path.exists(): return []
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError):return []
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(self.orders[-2000:],indent=2),encoding="utf-8")
    def create(self,offer_id,customer_ref,amount_eur,evidence_id):
        if amount_eur<=0: raise ValueError("order amount must be positive")
        now=datetime.now(timezone.utc).isoformat()
        o=Order(uuid.uuid4().hex[:12],str(offer_id),str(customer_ref),float(amount_eur),"lead",str(evidence_id),now,now)
        self.orders.append(asdict(o)); self._save(); return o
    def transition(self,order_id,target,evidence_id):
        if target not in STATES: raise ValueError("invalid order state")
        item=next((x for x in self.orders if x["id"]==order_id),None)
        if not item: raise KeyError(order_id)
        current=item["status"]
        allowed={"lead":{"quoted","cancelled"},"quoted":{"accepted","cancelled"},"accepted":{"paid","cancelled"},"paid":{"fulfilling","refunded"},"fulfilling":{"delivered","cancelled"},"delivered":{"completed","refunded"},"completed":set(),"cancelled":set(),"refunded":set()}
        if target not in allowed[current]: raise ValueError(f"invalid transition {current}->{target}")
        if not evidence_id: raise ValueError("state transitions require evidence")
        if self.evidence:
            try: self.evidence.require_verified(evidence_id)
            except (KeyError,ValueError) as exc: raise ValueError("state transition requires verified evidence") from exc
        item["status"]=target; item["evidence_id"]=str(evidence_id); item["updated_at"]=datetime.now(timezone.utc).isoformat(); self._save(); return self._order(item)
    def snapshot(self): return self.orders[-500:]
