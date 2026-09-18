from dataclasses import dataclass
from genesis.core.state import Ledger

@dataclass(frozen=True)
class SurvivalPolicy:
    minimum_reserve_eur: float = 0.0
    paid_execution_enabled: bool = False
    financial_execution_enabled: bool = False
    def mode(self, ledger: Ledger) -> str:
        if ledger.cash_eur <= 0: return "bootstrap"
        if ledger.net_cash < self.minimum_reserve_eur: return "conserve"
        return "productive"
    def may_spend(self, ledger: Ledger, amount: float) -> bool:
        if amount < 0: return False
        if amount == 0: return True
        return self.paid_execution_enabled and ledger.net_cash-amount >= self.minimum_reserve_eur
    def may_trade(self) -> bool: return self.financial_execution_enabled
