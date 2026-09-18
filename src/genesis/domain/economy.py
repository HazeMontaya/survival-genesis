from dataclasses import dataclass
from genesis.core.state import Ledger, StateStore

@dataclass(frozen=True)
class RevenueEvent:
    source: str
    amount_eur: float
    verified: bool = False

class Economy:
    def __init__(self, store: StateStore): self.store = store
    def record_revenue(self, event: RevenueEvent) -> Ledger:
        if event.amount_eur <= 0 or not event.verified: raise ValueError("Only positive, verified revenue can enter the economic ledger.")
        ledger=self.store.load(); ledger.cash_eur+=event.amount_eur; ledger.earned_eur+=event.amount_eur; ledger.revenue_events+=1; self.store.save(ledger); self.store.event("revenue",{"source":event.source,"amount_eur":event.amount_eur}); return ledger
    def record_spend(self, amount_eur: float, reason: str) -> Ledger:
        if amount_eur <= 0: raise ValueError("Spend must be positive.")
        ledger=self.store.load(); ledger.cash_eur-=amount_eur; ledger.spent_eur+=amount_eur; self.store.save(ledger); self.store.event("spend",{"reason":reason,"amount_eur":amount_eur}); return ledger
