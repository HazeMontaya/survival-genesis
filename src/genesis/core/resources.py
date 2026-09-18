from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json

@dataclass
class ResourceSnapshot:
    cash_eur:float=0.0
    reserved_eur:float=0.0
    compute_credits:float=0.0
    api_tokens:float=0.0
    inference_budget_eur:float=0.0
    energy_budget:float=0.0
    updated_at:str=""

class ResourceLedger:
    """Scarce-resource inventory. No resource is assumed to exist unless recorded."""
    def __init__(self,path="workspace/resources.json"):
        self.path=Path(path); self.state=self._load()
    def _load(self):
        if not self.path.exists(): return ResourceSnapshot(updated_at=datetime.now(timezone.utc).isoformat())
        return ResourceSnapshot(**json.loads(self.path.read_text(encoding="utf-8")))
    def save(self):
        self.state.updated_at=datetime.now(timezone.utc).isoformat(); self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(asdict(self.state),indent=2),encoding="utf-8")
    def set(self,**values):
        for k,v in values.items():
            if not hasattr(self.state,k): raise KeyError(k)
            if float(v)<0: raise ValueError("resource balances cannot be negative")
            setattr(self.state,k,float(v))
        self.save(); return self.snapshot()
    def sync_cash(self,amount):
        amount=float(amount)
        if amount<0: raise ValueError("cash cannot be negative")
        self.state.cash_eur=amount
        self.save()

    def credit_cash(self,amount):
        if amount<0: raise ValueError("amount must be positive")
        self.state.cash_eur+=float(amount); self.save()
    def debit_cash(self,amount):
        amount=float(amount)
        if amount<0 or self.available_cash()<amount: raise ValueError("insufficient available cash")
        self.state.cash_eur-=amount; self.save()
    def reserve_cash(self,amount):
        amount=float(amount)
        if amount<0 or self.available_cash()<amount:return False
        self.state.reserved_eur+=amount; self.save(); return True
    def release_cash(self,amount):
        amount=float(amount)
        if amount<0 or amount>self.state.reserved_eur:return False
        self.state.reserved_eur-=amount; self.save(); return True
    def consume(self,resource,amount):
        amount=float(amount)
        if amount < 0: raise ValueError("resource consumption cannot be negative")
        if not hasattr(self.state,resource): raise KeyError(resource)
        current=float(getattr(self.state,resource))
        if current < amount: return False
        setattr(self.state,resource,current-amount); self.save(); return True

    def available_cash(self): return max(0.0,self.state.cash_eur-self.state.reserved_eur)
    def snapshot(self): return asdict(self.state)
