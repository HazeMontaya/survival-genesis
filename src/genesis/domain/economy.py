from dataclasses import dataclass
from genesis.core.state import Ledger, StateStore

@dataclass(frozen=True)
class RevenueEvent:
    source: str
    amount_eur: float
    verified: bool = False
    evidence_id: str = ""

class Economy:
    def __init__(self, store: StateStore, evidence=None, resources=None):
        self.store=store; self.evidence=evidence; self.resources=resources
    def record_revenue(self,event:RevenueEvent)->Ledger:
        if event.amount_eur<=0 or not event.verified or not event.evidence_id: raise ValueError("Revenue requires positive amount, verification and evidence.")
        if self.evidence:
            try: self.evidence.require_verified(event.evidence_id)
            except (KeyError,ValueError) as exc: raise ValueError("Revenue evidence is missing or unverified.") from exc
        ledger=self.store.load(); ledger.cash_eur+=event.amount_eur; ledger.earned_eur+=event.amount_eur; ledger.revenue_events+=1; self.store.save(ledger)
        if self.resources: self.resources.sync_cash(ledger.cash_eur)
        self.store.event("revenue",{"source":event.source,"amount_eur":event.amount_eur,"evidence_id":event.evidence_id}); return ledger
    def record_spend(self,amount_eur,reason,evidence_id="")->Ledger:
        if amount_eur<=0 or not evidence_id: raise ValueError("Spend requires positive amount and evidence.")
        if self.evidence:
            try: self.evidence.require_verified(evidence_id)
            except (KeyError,ValueError) as exc: raise ValueError("Spend evidence is missing or unverified.") from exc
        ledger=self.store.load()
        if ledger.net_cash<amount_eur: raise ValueError("insufficient available cash")
        ledger.cash_eur-=amount_eur; ledger.spent_eur+=amount_eur; self.store.save(ledger)
        if self.resources: self.resources.sync_cash(ledger.cash_eur)
        self.store.event("spend",{"reason":reason,"amount_eur":amount_eur,"evidence_id":evidence_id}); return ledger
