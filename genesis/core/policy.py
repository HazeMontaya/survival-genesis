from dataclasses import dataclass
from pathlib import Path
import hashlib,json,os
@dataclass(frozen=True)
class PolicyDecision:allowed:bool;reason:str;risk:str
@dataclass(frozen=True)
class ToolRule:risk:str;min_authority:str="self"
class PolicyEngine:
 AUTHORITY={"external":0,"peer":1,"self":2,"owner":3}
 DEFAULTS={"read_file":ToolRule("safe"),"list_files":ToolRule("safe"),"remember":ToolRule("safe"),"send_message":ToolRule("caution"),"run_tests":ToolRule("caution"),"run_python":ToolRule("caution"),"write_file":ToolRule("caution"),"publish":ToolRule("dangerous","owner"),"payout":ToolRule("dangerous","owner"),"trade_live":ToolRule("dangerous","owner"),"modify_policy":ToolRule("forbidden","owner"),"read_secret":ToolRule("forbidden","owner")}
 PROTECTED={"constitution.md","owner.json","treasury.json","runtime.db",".env","wallet.json","credentials.json","secrets.json"};SECRET=("private_key","secret","password","credential","api_key","token")
 def __init__(self,db,root):self.db=db;self.root=Path(root).resolve();self.refresh()
 def refresh(self):self.kill_switch=os.getenv("GENESIS_KILL_SWITCH","0")=="1"
 def evaluate(self,tool,args=None,actor="genesis-1",authority="self"):
  args=args or {};r=self.DEFAULTS.get(tool,ToolRule("forbidden"));ok=True;reason="allowed by baseline policy"
  if self.kill_switch and r.risk in ("dangerous","forbidden"):ok=False;reason="global kill switch is active"
  elif self.AUTHORITY.get(authority,-1)<self.AUTHORITY[r.min_authority]:ok=False;reason="insufficient authority"
  elif r.risk=="forbidden":ok=False;reason="tool is forbidden by policy"
  elif tool in {"read_file","write_file","list_files"}:
   p=(self.root/str(args.get("path","."))).resolve()
   if self.root not in p.parents and p!=self.root:ok=False;reason="path escapes workspace"
   elif any(x.lower() in self.PROTECTED for x in p.parts) or any(x in p.name.lower() for x in self.SECRET):
    if authority!="owner":ok=False;reason="protected or secret path"
  self.db.policy(actor,tool,r.risk,"allow" if ok else "deny",reason,hashlib.sha256(json.dumps(args,sort_keys=True,default=str).encode()).hexdigest());return PolicyDecision(ok,reason,r.risk)
