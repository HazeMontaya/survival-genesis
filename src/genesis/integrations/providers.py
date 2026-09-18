from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class ProviderEvidence:
    provider: str
    event_id: str
    status: str
    amount_eur: float = 0.0
    reference: str = ""

class PaymentProvider(Protocol):
    def verify_payment(self, external_event_id: str) -> ProviderEvidence: ...

class MarketplaceProvider(Protocol):
    def publish_offer(self, offer: dict) -> ProviderEvidence: ...
    def fetch_orders(self) -> list[dict]: ...

class ExchangeProvider(Protocol):
    def market_data(self, symbol: str) -> dict: ...
    def submit_paper_order(self, symbol: str, side: str, quantity: float, price: float) -> ProviderEvidence: ...

class DisabledProvider:
    """Explicit no-op provider. It never claims that an external action happened."""
    def __init__(self,name): self.name=name
    def __getattr__(self,name):
        def disabled(*args,**kwargs):
            raise RuntimeError(f"provider disabled: {self.name}:{name}")
        return disabled

class PaperExchange:
    """Deterministic local exchange boundary for testing strategies without real money."""
    def __init__(self):
        self.orders=[]
    def market_data(self,symbol):
        return {"symbol":symbol,"mode":"paper","available":False,"reason":"No external market data configured"}
    def submit_paper_order(self,symbol,side,quantity,price):
        if side not in {"buy","sell"} or quantity<=0 or price<=0:
            raise ValueError("invalid paper order")
        event_id=f"paper-{len(self.orders)+1}"
        self.orders.append({"event_id":event_id,"symbol":symbol,"side":side,"quantity":quantity,"price":price})
        return ProviderEvidence("paper",event_id,"simulated",quantity*price,symbol)
