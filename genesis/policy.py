from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json

RISK_ORDER={'safe':0,'caution':1,'dangerous':2,'forbidden':3}
AUTH_ORDER={'system':4,'owner':4,'self':3,'trusted_agent':2,'external':1}
@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool; tool: str; risk: str; authority: str; reason: str; timestamp: str
class PolicyEngine:
    def __init__(self,store,constitution,treasury=None,resources=None):
        self.store=store; self.constitution=constitution; self.treasury=treasury; self.resources=resources; self.audit_path=Path(store.path).parent/'policy.jsonl'
    def _audit(self,d):
        self.audit_path.parent.mkdir(parents=True,exist_ok=True)
        with self.audit_path.open('a',encoding='utf-8') as f: f.write(json.dumps(asdict(d),ensure_ascii=False)+'\n')
        self.store.event('policy_decision',asdict(d))
    def evaluate(self,tool,risk='safe',authority='self',params=None):
        params=params or {}; allowed=True; reason='allowed'
        if risk not in RISK_ORDER: allowed=False; reason='unknown risk level'
        elif risk=='forbidden': allowed=False; reason='tool is forbidden'
        elif authority not in AUTH_ORDER: allowed=False; reason='unknown authority'
        elif authority=='external' and risk in ('dangerous','forbidden'): allowed=False; reason='external authority cannot invoke dangerous actions'
        path=str(params.get('path','')).replace('\\\\','/').lstrip('/')
        if path and any(path==p or path.startswith(p.rstrip('/')+'/') for p in self.constitution.protected_paths) and tool in ('write_file','edit_own_file','delete_file','self_modify'): allowed=False; reason='protected path'
        if tool in ('payout','live_trade','transfer') and risk!='dangerous': allowed=False; reason='financial action must be dangerous'
        d=PolicyDecision(allowed,tool,risk,authority,reason,datetime.now(timezone.utc).isoformat()); self._audit(d); return d
    def require(self,tool,risk='safe',authority='self',params=None):
        d=self.evaluate(tool,risk,authority,params)
        if not d.allowed: raise PermissionError(f'policy denied {tool}: {d.reason}')
        return d
