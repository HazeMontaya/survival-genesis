from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import hashlib,hmac,json,os
@dataclass
class TreasuryPolicy:
 enabled:bool=False;collect_enabled:bool=False;payout_enabled:bool=False;trading_enabled:bool=False;trading_mode:str="paper";max_payout_eur:float=0;require_human_approval_above_eur:float=0;daily_payout_limit_eur:float=0;daily_trade_notional_eur:float=0;minimum_cash_reserve_eur:float=0;allowed_payout_hashes:list[str]=field(default_factory=list)
@dataclass
class TreasuryAccount:provider:str;account_ref_hash:str;owner_label:str;verified:bool=False;created_at:str="";processed_event_ids:list[str]=field(default_factory=list)
class Treasury:
 def __init__(self,store,db=None):
  self.store=store;self.db=db;self.path=Path(os.getenv("GENESIS_TREASURY_STATE",str(Path(store.path).parent/"treasury.json")));self.policy=TreasuryPolicy(enabled=os.getenv("GENESIS_TREASURY_ENABLED")=="1",collect_enabled=os.getenv("GENESIS_TREASURY_COLLECT")=="1",payout_enabled=os.getenv("GENESIS_TREASURY_PAYOUT")=="1",trading_enabled=os.getenv("GENESIS_TRADING_ENABLED")=="1",trading_mode=os.getenv("GENESIS_TRADING_MODE","paper"),max_payout_eur=float(os.getenv("GENESIS_MAX_PAYOUT_EUR","0")),require_human_approval_above_eur=float(os.getenv("GENESIS_HUMAN_APPROVAL_EUR","0")),daily_payout_limit_eur=float(os.getenv("GENESIS_DAILY_PAYOUT_LIMIT_EUR","0")),daily_trade_notional_eur=float(os.getenv("GENESIS_DAILY_TRADE_NOTIONAL_EUR","0")),minimum_cash_reserve_eur=float(os.getenv("GENESIS_MIN_CASH_RESERVE_EUR","0")),allowed_payout_hashes=[x for x in os.getenv("GENESIS_ALLOWED_PAYOUT_HASHES","").split(",") if x]);self.account=self._load()
  if self.policy.trading_mode not in ("paper","live"):raise ValueError("trading mode must be paper or live")
 def _load(self):
  if not self.path.exists():return None
  r=json.loads(self.path.read_text());r.setdefault("processed_event_ids",[]);return TreasuryAccount(**r)
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps(asdict(self.account),indent=2))
 @staticmethod
 def fingerprint(provider,ref):return hashlib.sha256(f"{provider}:{ref}".encode()).hexdigest()[:20]
 def bind_owner_account(self,provider,account_ref,owner_label,verification_token):
  expected=os.getenv("GENESIS_OWNER_BIND_TOKEN","")
  if not expected or not hmac.compare_digest(str(verification_token),expected):raise PermissionError("owner verification failed")
  self.account=TreasuryAccount(str(provider),self.fingerprint(str(provider),str(account_ref)),str(owner_label),True,datetime.now(timezone.utc).isoformat());self._save();self.db and self.db.event("treasury_account_bound",{"provider":provider,"account_ref_hash":self.account.account_ref_hash,"owner_label":owner_label},"owner");return self.snapshot()
 def can_collect(self):return bool(self.policy.enabled and self.policy.collect_enabled and self.account and self.account.verified)
 def accept_signed_revenue(self,event_id,source,amount_eur,signature):
  secret=os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET","")
  if not secret or not self.account or event_id in self.account.processed_event_ids:raise PermissionError("revenue verification unavailable")
  expected=hmac.new(secret.encode(),f"{event_id}|{source}|{amount_eur:.2f}".encode(),hashlib.sha256).hexdigest()
  if not hmac.compare_digest(signature or "",expected):raise PermissionError("invalid revenue signature")
  if not self.can_collect():raise PermissionError("treasury collection is not enabled and verified")
  from .economy import Economy,RevenueEvent
  l=Economy(self.store,self.db).record_revenue(RevenueEvent(str(source),float(amount_eur),True));self.account.processed_event_ids.append(str(event_id));self._save();return l
 def snapshot(self):return {"policy":asdict(self.policy),"account":asdict(self.account) if self.account else None,"secret_material_stored":False}
