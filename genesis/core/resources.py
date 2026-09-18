from dataclasses import asdict,dataclass
from pathlib import Path
import json
@dataclass
class ResourceState:cash_eur:float=0;reserved_eur:float=0;compute_credits:float=0;api_tokens:float=0;inference_budget_eur:float=0;energy_budget:float=0
class ResourceLedger:
 def __init__(self,path):self.path=Path(path);self.state=ResourceState(**json.loads(self.path.read_text())) if self.path.exists() else ResourceState()
 def save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(asdict(self.state),indent=2))
 def set(self,**v):
  for k,x in v.items():
   if not hasattr(self.state,k) or float(x)<0:raise ValueError("invalid resource")
   setattr(self.state,k,float(x))
  self.save();return self.snapshot()
 def available_cash(self):return max(0,self.state.cash_eur-self.state.reserved_eur)
 def snapshot(self):return asdict(self.state)
