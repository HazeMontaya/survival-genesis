from dataclasses import dataclass
@dataclass(frozen=True)
class RevenueEvent:source:str;amount_eur:float;verified:bool=False
class Economy:
 def __init__(self,store,db=None):self.store=store;self.db=db
 def record_revenue(self,e):
  if e.amount_eur<=0 or not e.verified:raise ValueError("Only positive, verified revenue can enter the ledger.")
  l=self.store.load();l.cash_eur+=e.amount_eur;l.earned_eur+=e.amount_eur;l.revenue_events+=1;self.store.save(l)
  if self.db:self.db.event("revenue",{"source":e.source,"amount_eur":e.amount_eur})
  return l
