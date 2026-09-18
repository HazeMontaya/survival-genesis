import os,json
from dataclasses import asdict,dataclass
from urllib.request import Request,urlopen
@dataclass
class Connector:id:str;kind:str;configured:bool;enabled:bool;description:str
class ConnectorRegistry:
 def __init__(self,store):self.store=store;u=bool(os.getenv("GENESIS_WEBHOOK_URL"));self.connectors=[Connector("webhook","generic_http_webhook",u,u,"Operator-configured HTTP endpoint"),Connector("revenue_webhook","verified_revenue_ingest",bool(os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET")),bool(os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET")),"Authenticated revenue ingress")]
 def snapshot(self):return [asdict(x) for x in self.connectors]
 def publish(self,payload):
  u=os.getenv("GENESIS_WEBHOOK_URL")
  if not u:raise RuntimeError("GENESIS_WEBHOOK_URL is not configured")
  with urlopen(Request(u,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST"),timeout=10) as r:return {"status":r.status}
