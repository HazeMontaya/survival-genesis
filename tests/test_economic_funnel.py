from genesis.domain.opportunities import OpportunityLedger
from genesis.integrations.distribution import DistributionEngine

def test_opportunity_requires_evidence(tmp_path):
    ledger=OpportunityLedger(tmp_path/"opportunities.json")
    try:
        ledger.record("x","service",.5,[])
        assert False
    except ValueError:
        pass
    item=ledger.record("x","service",.5,["ev-1"])
    assert item.status=="observed"

def test_distribution_requires_external_publication_evidence(tmp_path):
    d=DistributionEngine(tmp_path/"publications.json")
    p=d.queue("offer-1","local","offer content","ev-1")
    assert p.status=="queued"
    try:
        d.mark_published(p.id,"","")
        assert False
    except ValueError:
        pass
    assert d.mark_published(p.id,"ev-2","external-123")["status"]=="published"
