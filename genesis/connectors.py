import os, json
from dataclasses import dataclass, asdict
from urllib.request import Request, urlopen

@dataclass
class Connector:
    id:str
    kind:str
    configured:bool
    enabled:bool
    description:str

class ConnectorRegistry:
    def __init__(self,store):
        self.store=store
        self.connectors=[
            Connector("webhook","generic_http_webhook",bool(os.getenv("GENESIS_WEBHOOK_URL")),bool(os.getenv("GENESIS_WEBHOOK_URL")),"Publish runtime events to an operator-configured HTTP endpoint"),
            Connector("revenue_webhook","verified_revenue_ingest",bool(os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET")),bool(os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET")),"Authenticated endpoint for verified revenue events"),
        ]

    def snapshot(self): return [asdict(x) for x in self.connectors]

    def publish(self,payload):
        url=os.getenv("GENESIS_WEBHOOK_URL")
        if not url: raise RuntimeError("GENESIS_WEBHOOK_URL is not configured")
        raw=json.dumps(payload).encode()
        req=Request(url,data=raw,headers={"Content-Type":"application/json"},method="POST")
        with urlopen(req,timeout=10) as response: return {"status":response.status}
