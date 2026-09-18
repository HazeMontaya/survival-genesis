from genesis.runtime.agent import GenesisAgent
from genesis.domain.economy import Economy, RevenueEvent
from genesis.core.state import StateStore
from genesis.core.survival import SurvivalPolicy

def test_bootstrap_is_zero_cost(tmp_path):
    store=StateStore(str(tmp_path/"state.json")); agent=GenesisAgent(store=store); assert store.load().cash_eur==0; assert agent.snapshot()["mode"]=="bootstrap"
def test_unverified_revenue_is_rejected(tmp_path):
    store=StateStore(str(tmp_path/"state.json")); economy=Economy(store)
    try: economy.record_revenue(RevenueEvent("test",10,verified=False))
    except ValueError: pass
    else: raise AssertionError("unverified revenue must be rejected")
def test_verified_revenue_increases_cash(tmp_path):
    store=StateStore(str(tmp_path/"state.json")); economy=Economy(store); ledger=economy.record_revenue(RevenueEvent("test",10,verified=True)); assert ledger.cash_eur==10
def test_trading_is_off_by_default(): assert SurvivalPolicy().may_trade() is False
