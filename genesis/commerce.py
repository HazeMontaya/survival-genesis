from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json, re, uuid

@dataclass
class Offer:
    id: str
    name: str
    channel: str
    price_eur: float
    status: str
    artifact_id: str
    created_at: str
    published_url: str = ""

class CommerceEngine:
    def __init__(self, store, artifacts, memory):
        self.store,self.artifacts,self.memory=store,artifacts,memory
        self.path=store.path.parent/"commerce.json"
        self.offers=self._load("offers"); self.leads=self._load("leads"); self.assets=self._load("assets")

    def _load(self,key):
        if not self.path.exists(): return []
        try: return json.loads(self.path.read_text(encoding="utf-8")).get(key,[])
        except Exception: return []

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps({"offers":self.offers[-500:],"leads":self.leads[-1000:],"assets":self.assets[-500:]},indent=2),encoding="utf-8")

    def create_offer(self,opportunity):
        now=datetime.now(timezone.utc).isoformat()
        body=f"""# {opportunity.name.replace("_"," ").title()}

## Offer
A narrowly scoped {opportunity.channel} offer.

## Customer
Define the target customer and painful problem before publishing.

## Deliverable
Produce the smallest useful result that can be delivered without paid infrastructure.

## Target transaction value
€{opportunity.expected_margin_eur:.2f}

## Fulfillment
Local/manual fulfillment is supported. Automated fulfillment requires a configured connector.

## Integrity
No fabricated customers, reviews, revenue, accounts, credentials, or transactions.
"""
        artifact=self.artifacts.create_markdown(opportunity.name.replace("_"," ")+" offer",body,"offer")
        offer=asdict(Offer(uuid.uuid4().hex[:10],opportunity.name.replace("_"," ").title(),opportunity.channel,float(opportunity.expected_margin_eur),"draft",artifact.id,now))
        self.offers.append(offer); self._save(); self.store.event("offer_created",offer); return offer

    def create_distribution_asset(self,opportunity):
        asset={"id":uuid.uuid4().hex[:10],"type":"distribution_copy","opportunity":opportunity.name,
               "content":f"Problem-led offer: {opportunity.name.replace('_',' ')}. Reply for scope and delivery details.",
               "status":"ready","created_at":datetime.now(timezone.utc).isoformat()}
        self.assets.append(asset); self._save(); self.store.event("distribution_asset_ready",asset); return asset

    def create_lead_queue(self,opportunity):
        lead={"id":uuid.uuid4().hex[:10],"source":opportunity.channel,"status":"uncontacted",
              "next_action":"Acquire an opt-in or inbound lead","created_at":datetime.now(timezone.utc).isoformat()}
        self.leads.append(lead); self._save(); self.store.event("lead_queue_ready",lead); return lead

    def snapshot(self):
        return {"offers":self.offers[-100:],"leads":self.leads[-100:],"assets":self.assets[-100:]}
