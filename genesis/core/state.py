from dataclasses import asdict,dataclass
from pathlib import Path
import json
@dataclass
class Ledger:
 cash_eur:float=0.0; earned_eur:float=0.0; spent_eur:float=0.0; reserved_eur:float=0.0; compute_cost_eur:float=0.0; revenue_events:int=0; experiments:int=0
 @property
 def net_cash(self): return self.cash_eur-self.reserved_eur
 @property
 def surplus(self): return self.earned_eur-self.spent_eur-self.reserved_eur
class StateStore:
 def __init__(self,path="workspace/state.json"):self.path=Path(path)
 def load(self):return Ledger(**json.loads(self.path.read_text(encoding="utf-8"))) if self.path.exists() else Ledger()
 def save(self,ledger):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(asdict(ledger),indent=2,ensure_ascii=False),encoding="utf-8")
