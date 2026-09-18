from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

@dataclass
class TreasuryPolicy:
    enabled: bool = False
    collect_enabled: bool = False
    payout_enabled: bool = False
    trading_enabled: bool = False
    max_payout_eur: float = 0.0
    require_human_approval_above_eur: float = 0.0

@dataclass
class TreasuryAccount:
    provider: str
    account_ref_hash: str
    owner_label: str
    verified: bool = False
    created_at: str = ""

class Treasury:
    """Provider-neutral money boundary. Secrets never enter the repository or ledger."""
    def __init__(self, store):
        self.store = store
        self.path = Path(os.getenv("GENESIS_TREASURY_STATE", "workspace/treasury.json"))
        self.policy = TreasuryPolicy(
            enabled=os.getenv("GENESIS_TREASURY_ENABLED","0")=="1",
            collect_enabled=os.getenv("GENESIS_TREASURY_COLLECT","0")=="1",
            payout_enabled=os.getenv("GENESIS_TREASURY_PAYOUT","0")=="1",
            trading_enabled=False,
            max_payout_eur=float(os.getenv("GENESIS_MAX_PAYOUT_EUR","0")),
            require_human_approval_above_eur=float(os.getenv("GENESIS_HUMAN_APPROVAL_EUR","0")),
        )
        self.account = self._load()

    def _load(self):
        if not self.path.exists():
            return None
        return TreasuryAccount(**json.loads(self.path.read_text(encoding="utf-8")))

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(self.account), indent=2), encoding="utf-8")

    @staticmethod
    def fingerprint(provider, account_ref):
        raw=f"{provider}:{account_ref}".encode()
        return hashlib.sha256(raw).hexdigest()[:20]

    def bind_owner_account(self, provider, account_ref, owner_label, verified=False):
        if not provider or not account_ref or not owner_label:
            raise ValueError("provider, account_ref and owner_label are required")
        self.account=TreasuryAccount(
            provider=str(provider),
            account_ref_hash=self.fingerprint(str(provider), str(account_ref)),
            owner_label=str(owner_label),
            verified=bool(verified),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._save()
        self.store.event("treasury_account_bound", {
            "provider": self.account.provider,
            "account_ref_hash": self.account.account_ref_hash,
            "owner_label": self.account.owner_label,
            "verified": self.account.verified,
        })
        return self.snapshot()

    def can_collect(self):
        return bool(self.policy.enabled and self.policy.collect_enabled and self.account and self.account.verified)

    def can_payout(self, amount_eur, human_approved=False):
        if amount_eur <= 0 or not self.policy.enabled or not self.policy.payout_enabled:
            return False
        if not self.account or not self.account.verified:
            return False
        if self.policy.max_payout_eur <= 0 or amount_eur > self.policy.max_payout_eur:
            return False
        if amount_eur > self.policy.require_human_approval_above_eur and not human_approved:
            return False
        return True

    def snapshot(self):
        return {
            "policy": asdict(self.policy),
            "account": asdict(self.account) if self.account else None,
            "secret_material_stored": False,
        }
