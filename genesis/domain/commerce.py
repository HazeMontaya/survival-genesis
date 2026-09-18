from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,re,uuid
@dataclass
class Offer:id:str;name:str;channel:str;price_eur:float;status:str;artifact_id:str;created_at:str;published_url:str=""
class CommerceEngine:
 def __init__(self,store,artifacts,memory,db=None):self.store=store;self.artifacts=artifacts;self.memory=memory;self.db=db;self.path=store.path.parent/"commerce.json";self.offers=self._load("offers");self.leads=self._load("leads");self.assets=self._load("assets")
 def _load(self,k):
  if not self.path.exists():return []
  try:return json.loads(self.path.read_text()).get(k,[])
  except Exception:return []
 def create_offer(self,o):
  title=o.name.replace("_"," ").title();a=self.artifacts.create_markdown(title+" Angebot",f"# {title}\n\nEin klar abgegrenztes {o.channel}-Angebot.\n\nNachfrage muss vor Veröffentlichung belegt werden.\n\nKeine erfundenen Kunden, Bewertungen, Umsätze oder Konten.\n","angebot");x=asdict(Offer(uuid.uuid4().hex[:10],title,o.channel,float(o.expected_margin_eur),"entwurf",a.id,datetime.now(timezone.utc).isoformat()));self.offers.append(x);self._save();self.db and self.db.event("offer_created",x);return x
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps({"offers":self.offers[-500:],"leads":self.leads[-1000:],"assets":self.assets[-500:]},indent=2,ensure_ascii=False))
 def snapshot(self):return {"offers":self.offers[-100:],"leads":self.leads[-100:],"assets":self.assets[-100:]}
