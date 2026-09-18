from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from urllib.parse import quote
from urllib.request import Request,urlopen
import os,re,xml.etree.ElementTree as ET,json
@dataclass
class Signal:source:str;topic:str;score:float;summary:str;created_at:str
class SignalEngine:
 def __init__(self,db,memory):self.db=db;self.memory=memory
 def scan(self,o):
  urls=[x.strip() for x in os.getenv("GENESIS_SIGNAL_URLS","").split(",") if x.strip()] or [f"https://hnrss.org/newest?q={quote(o.channel)}"];hits=[]
  for u in urls[:5]:
   try:root=ET.fromstring(urlopen(Request(u,headers={"User-Agent":"SurvivalGenesis/0.2"}),timeout=8).read(512000));text=" ".join(re.sub(r"\\s+"," ",(x.text or "")).strip() for x in root.iter() if x.text);hits.append((u,text.lower().count(o.channel.lower())))
   except Exception:pass
  total=sum(x[1] for x in hits);s=Signal(",".join(x[0] for x in hits) or "nicht_verfügbar",o.channel,round(min(1,total/10),3),f"{len(hits)} Live-Quelle(n) abgerufen; {total} passende Signalnennungen",datetime.now(timezone.utc).isoformat());self.db.event("signal_observed",asdict(s));return asdict(s)
 def snapshot(self):
  with self.db._connect() as d:r=d.execute("SELECT payload FROM events WHERE kind='signal_observed' ORDER BY rowid DESC LIMIT 50").fetchall()
  return [json.loads(x["payload"]) for x in r][::-1]
