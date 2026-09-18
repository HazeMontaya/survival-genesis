from dataclasses import dataclass
@dataclass(frozen=True)
class SurvivalPolicy:
 minimum_reserve_eur:float=0;paid_execution_enabled:bool=False;financial_execution_enabled:bool=False
 def mode(self,l):return "bootstrap" if l.cash_eur<=0 else ("conserve" if l.net_cash<self.minimum_reserve_eur else "productive")
 def may_spend(self,l,a):return a>=0 and (a==0 or self.paid_execution_enabled and l.net_cash-a>=self.minimum_reserve_eur)
 def may_trade(self):return self.financial_execution_enabled
