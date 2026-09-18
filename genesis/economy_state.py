"""Evidence-backed commerce state machine."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

STATES=("draft","published","lead","ordered","payment_pending","paid","fulfilling","delivered","completed","refunded","disputed","cancelled")
TRANSITIONS={
"draft":{"published"},
"published":{"lead","ordered","cancelled"},
"lead":{"ordered","cancelled"},
"ordered":{"payment_pending","cancelled"},
"payment_pending":{"paid","cancelled","disputed"},
"paid":{"fulfilling","refunded","disputed"},
"fulfilling":{"delivered","disputed"},
"delivered":{"completed","disputed"},
"completed":set(),
"refunded":set(),
"disputed":{"refunded","completed"},
"cancelled":set(),
}

@dataclass
class CommerceOrder:
    id:str
    offer_id:str
    status:str
    amount_eur:float
    customer_ref:str
    created_at:str
    updated_at:str
    payment_ref:str=""
    delivery_ref:str=""

class CommerceState:
    def __init__(self,path):
        self.path=Path(path); self.orders=self._load()
    def _load(self):
        if not self.path.exists(): return []
        return [CommerceOrder(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.orders[-5000:]],indent=2,ensure_ascii=False),encoding="utf-8")
    def create_order(self,offer_id,amount_eur,customer_ref):
        now=datetime.now(timezone.utc).isoformat()
        o=CommerceOrder(uuid.uuid4().hex[:12],str(offer_id),"draft",float(amount_eur),str(customer_ref),now,now)
        self.orders.append(o); self._save(); return o
    def transition(self,order_id,new_status,evidence=None):
        o=next((x for x in self.orders if x.id==order_id),None)
        if not o: raise KeyError(order_id)
        if new_status not in STATES or new_status not in TRANSITIONS[o.status]:
            raise ValueError(f"invalid commerce transition: {o.status} -> {new_status}")
        if new_status in ("paid","delivered","completed") and not evidence:
            raise ValueError("external completion states require evidence")
        o.status=new_status; o.updated_at=datetime.now(timezone.utc).isoformat()
        if isinstance(evidence,dict):
            if new_status=="paid": o.payment_ref=str(evidence.get("external_id",""))
            if new_status=="delivered": o.delivery_ref=str(evidence.get("external_id",""))
        self._save(); return o
    def snapshot(self): return [asdict(x) for x in self.orders[-500:]]
