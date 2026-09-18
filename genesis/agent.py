from .economy import Economy
from .opportunities import Opportunity, rank
from .state import StateStore
from .survival import SurvivalPolicy
from .tasks import TaskBoard
from .memory import MemoryGraph
from .company import CompanyProfile

DEFAULT_OPPORTUNITIES = [
    Opportunity("digital_microproduct","digital_product",0,49,4,.35,.85),
    Opportunity("technical_microservice","service",0,120,3,.45,.65),
    Opportunity("open_source_sponsorship","open_source",0,25,2,.15,.90),
    Opportunity("affiliate_content","affiliate",0,60,5,.20,.70),
    Opportunity("print_on_demand","pod",0,35,5,.15,.55),
    Opportunity("dropship_test","dropshipping",0,80,8,.10,.45),
    Opportunity("lead_generation","leads",0,100,4,.30,.75),
]

class GenesisAgent:
    def __init__(self, store=None, policy=None):
        self.store=store or StateStore()
        self.policy=policy or SurvivalPolicy()
        self.economy=Economy(self.store)
        self.company=CompanyProfile()
        self.tasks=TaskBoard()
        self.memory=MemoryGraph()

    def snapshot(self):
        ledger=self.store.load()
        return {
            "mode":self.policy.mode(ledger),
            "company":self.company.snapshot(),
            "ledger":ledger.__dict__,
            "tasks":self.tasks.snapshot(),
            "memory":self.memory.snapshot(),
            "top_opportunities":[{"name":x.name,"channel":x.channel,"score":round(x.score(),3)} for x in rank(DEFAULT_OPPORTUNITIES)[:5]]
        }

    def select_next_experiment(self):
        ledger=self.store.load()
        candidates=[x for x in DEFAULT_OPPORTUNITIES if x.startup_cost_eur==0 or self.policy.may_spend(ledger,x.startup_cost_eur)]
        choice=rank(candidates)[0]
        ledger.experiments+=1
        self.store.save(ledger)
        self.store.event("experiment_selected",{"name":choice.name,"channel":choice.channel})
        self.memory.remember("decision",f"Selected {choice.name} as next zero-capital experiment",choice.confidence)
        self.tasks.create("scout","research",f"Validate {choice.name} opportunity",85)
        self.tasks.create("forge","forge",f"Prepare first artifact for {choice.name}",70)
        return choice

    def tick(self):
        opportunity=self.select_next_experiment()
        result=self.snapshot()
        result["selected"]={"name":opportunity.name,"channel":opportunity.channel}
        return result
