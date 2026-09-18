from genesis.runtime.agent import GenesisAgent
from genesis.core.state import StateStore
from genesis.domain.economy import RevenueEvent, Economy
from genesis.domain.evidence import EvidenceLedger
from genesis.domain.orders import OrderEngine


def test_evidence_is_required_for_revenue(tmp_path):
    store=StateStore(tmp_path/"state.json")
    evidence=EvidenceLedger(tmp_path/"evidence.json")
    economy=Economy(store,evidence)
    try:
        economy.record_revenue(RevenueEvent("test",10,True,"missing"))
        assert False
    except ValueError:
        pass
    ev=evidence.record("order-1","payment","verified payment",{"provider_event_id":"evt-1"},"provider")
    ledger=economy.record_revenue(RevenueEvent("test",10,True,ev.id))
    assert ledger.cash_eur==10


def test_order_lifecycle_requires_evidence(tmp_path):
    orders=OrderEngine(tmp_path/"orders.json")
    ev="evidence-1"
    order=orders.create("offer-1","customer-hash",25,ev)
    assert order.status=="lead"
    order=orders.transition(order.id,"quoted",ev)
    order=orders.transition(order.id,"accepted",ev)
    order=orders.transition(order.id,"paid",ev)
    assert order["status"]=="paid"
    try:
        orders.transition(order["id"],"completed","")
        assert False
    except ValueError:
        pass


def test_bootstrap_has_no_resources_or_fake_revenue(tmp_path):
    agent=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    for _ in range(6):
        agent.tick()
    snap=agent.snapshot()
    assert snap["ledger"]["cash_eur"]==0
    assert snap["ledger"]["earned_eur"]==0
    assert snap["resources"]["cash_eur"]==0
    assert snap["evidence"]


def test_runtime_audit_chain_survives_normal_operation(tmp_path):
    agent=GenesisAgent(store=StateStore(tmp_path/"state.json"))
    agent.tick()
    assert agent.runtime_db.verify_event_chain()
