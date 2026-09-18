from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import json
import os

@dataclass
class TreasuryPolicy:
    enabled: bool = False
    collect_enabled: bool = False
    payout_enabled: bool = False
    trading_enabled: bool = False
    trading_mode: str = "paper"
    max_payout_eur: float = 0.0
    require_human_approval_above_eur: float = 0.0
    daily_payout_limit_eur: float = 0.0
    daily_trade_notional_eur: float = 0.0
    minimum_cash_reserve_eur: float = 0.0
    allowed_payout_hashes: list[str] = field(default_factory=list)

@dataclass
class TreasuryAccount:
    provider: str
    account_ref_hash: str
    owner_label: str
    verified: bool = False
    created_at: str = ""
    processed_event_ids: list[str] = field(default_factory=list)

class Treasury:
    """Provider-neutral money boundary. Secrets never enter the repository or ledger."""
    def __init__(self, store):
        self.store=store
        self.path=Path(os.getenv("GENESIS_TREASURY_STATE",str(Path(store.path).parent/"treasury.json")))
        self.policy=TreasuryPolicy(
            enabled=os.getenv("GENESIS_TREASURY_ENABLED","0")=="1",
            collect_enabled=os.getenv("GENESIS_TREASURY_COLLECT","0")=="1",
            payout_enabled=os.getenv("GENESIS_TREASURY_PAYOUT","0")=="1",
            trading_enabled=os.getenv("GENESIS_TRADING_ENABLED","0")=="1",
            trading_mode=os.getenv("GENESIS_TRADING_MODE","paper"),
            max_payout_eur=float(os.getenv("GENESIS_MAX_PAYOUT_EUR","0")),
            require_human_approval_above_eur=float(os.getenv("GENESIS_HUMAN_APPROVAL_EUR","0")),
            daily_payout_limit_eur=float(os.getenv("GENESIS_DAILY_PAYOUT_LIMIT_EUR","0")),
            daily_trade_notional_eur=float(os.getenv("GENESIS_DAILY_TRADE_NOTIONAL_EUR","0")),
            minimum_cash_reserve_eur=float(os.getenv("GENESIS_MIN_CASH_RESERVE_EUR","0")),
            allowed_payout_hashes=[x for x in os.getenv("GENESIS_ALLOWED_PAYOUT_HASHES","").split(",") if x],
        )
        if self.policy.trading_mode not in ("paper","live"):
            raise ValueError("GENESIS_TRADING_MODE must be paper or live")
        self.account=self._load()

    def _load(self):
        if not self.path.exists(): return None
        raw=json.loads(self.path.read_text(encoding="utf-8"))
        raw.setdefault("processed_event_ids",[])
        return TreasuryAccount(**raw)

    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps(asdict(self.account),indent=2),encoding="utf-8")

    @staticmethod
    def fingerprint(provider,account_ref):
        return hashlib.sha256(f"{provider}:{account_ref}".encode()).hexdigest()[:20]

    def bind_owner_account(self,provider,account_ref,owner_label,verification_token):
        expected=os.getenv("GENESIS_OWNER_BIND_TOKEN","")
        if not expected or not hmac.compare_digest(str(verification_token),expected):
            raise PermissionError("owner verification failed")
        if not provider or not account_ref or not owner_label:
            raise ValueError("provider, account_ref and owner_label are required")
        self.account=TreasuryAccount(
            provider=str(provider),account_ref_hash=self.fingerprint(str(provider),str(account_ref)),
            owner_label=str(owner_label),verified=True,created_at=datetime.now(timezone.utc).isoformat())
        self._save()
        self.store.event("treasury_account_bound",{"provider":self.account.provider,"account_ref_hash":self.account.account_ref_hash,"owner_label":self.account.owner_label,"verified":True})
        return self.snapshot()

    def can_collect(self):
        return bool(self.policy.enabled and self.policy.collect_enabled and self.account and self.account.verified)

    def accept_signed_revenue(self,event_id,source,amount_eur,signature):
        secret=os.getenv("GENESIS_REVENUE_WEBHOOK_SECRET","")
        if not secret: raise PermissionError("revenue webhook secret is not configured")
        if not event_id or event_id in (self.account.processed_event_ids if self.account else []): raise ValueError("missing or replayed event")
        body=f"{event_id}|{source}|{amount_eur:.2f}".encode()
        expected=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature or "",expected): raise PermissionError("invalid revenue signature")
        if not self.can_collect(): raise PermissionError("treasury collection is not enabled and verified")
        from .economy import RevenueEvent
        ledger=self.store.load()
        from .economy import Economy
        ledger=Economy(self.store).record_revenue(RevenueEvent(str(source),float(amount_eur),True))
        self.account.processed_event_ids.append(str(event_id))
        self.account.processed_event_ids=self.account.processed_event_ids[-5000:]
        self._save()
        self.store.event("treasury_revenue_verified",{"event_id":event_id,"source":source,"amount_eur":amount_eur})
        return ledger

    def payout_destination_allowed(self,destination):
        return bool(destination and self.policy.allowed_payout_hashes and self.fingerprint(self.account.provider if self.account else "",str(destination)) in self.policy.allowed_payout_hashes)

    def can_payout(self,amount_eur,human_approved=False,destination=None,current_cash_eur=0.0,today_payout_eur=0.0):
        if amount_eur<=0 or not self.policy.enabled or not self.policy.payout_enabled: return False
        if not self.account or not self.account.verified: return False
        if self.policy.max_payout_eur<=0 or amount_eur>self.policy.max_payout_eur: return False
        if self.policy.daily_payout_limit_eur<=0 or today_payout_eur+amount_eur>self.policy.daily_payout_limit_eur: return False
        if current_cash_eur-amount_eur<self.policy.minimum_cash_reserve_eur: return False
        if not self.payout_destination_allowed(destination): return False
        if amount_eur>self.policy.require_human_approval_above_eur and not human_approved: return False
        return True

    def can_trade(self,notional_eur=0.0,today_notional_eur=0.0,current_cash_eur=0.0):
        if not (self.policy.enabled and self.policy.trading_enabled and self.account and self.account.verified and self.policy.trading_mode=="live"): return False
        if notional_eur<=0 or self.policy.daily_trade_notional_eur<=0: return False
        if today_notional_eur+notional_eur>self.policy.daily_trade_notional_eur: return False
        return current_cash_eur>=self.policy.minimum_cash_reserve_eur+notional_eur

    def snapshot(self):
        return {"policy":asdict(self.policy),"account":asdict(self.account) if self.account else None,"secret_material_stored":False}
