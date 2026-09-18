from .economy import Economy
from .opportunities import Opportunity, rank
from .state import StateStore
from .survival import SurvivalPolicy
from .tasks import TaskBoard
from .memory import MemoryGraph
from .company import CompanyProfile
from .artifacts import ArtifactStore
from .signals import SignalEngine
from .commerce import CommerceEngine
from .connectors import ConnectorRegistry

DEFAULT_OPPORTUNITIES = [
    Opportunity("technical_microservice","service",0,120,3,.45,.65),
    Opportunity("digital_microproduct","digital_product",0,49,4,.35,.85),
    Opportunity("lead_generation","leads",0,100,4,.30,.75),
    Opportunity("open_source_sponsorship","open_source",0,25,2,.15,.90),
    Opportunity("affiliate_content","affiliate",0,60,5,.20,.70),
    Opportunity("print_on_demand","pod",0,35,5,.15,.55),
    Opportunity("dropship_test","dropshipping",0,80,8,.10,.45),
]

class GenesisAgent:
    def __init__(self, store=None, policy=None):
        self.store = store or StateStore()
        self.policy = policy or SurvivalPolicy()
        self.economy = Economy(self.store)
        root = self.store.path.parent
        self.company = CompanyProfile()
        self.tasks = TaskBoard(root/"tasks.json")
        self.memory = MemoryGraph(root/"memory.json")
        self.artifacts = ArtifactStore(root/"artifacts")
        self.signals = SignalEngine(self.store, self.memory)
        self.commerce = CommerceEngine(self.store, self.artifacts, self.memory)
        self.connectors = ConnectorRegistry(self.store)

    def snapshot(self):
        l = self.store.load()
        return {
            "mode": self.policy.mode(l),
            "company": self.company.snapshot(),
            "ledger": l.__dict__,
            "tasks": self.tasks.snapshot(),
            "memory": self.memory.snapshot(),
            "artifacts": self.artifacts.snapshot(),
            "signals": self.signals.snapshot(),
            "commerce": self.commerce.snapshot(),
            "connectors": self.connectors.snapshot(),
            "top_opportunities": [{"name":x.name,"channel":x.channel,"score":round(x.score(),3)} for x in rank(DEFAULT_OPPORTUNITIES)[:7]]
        }

    def select_next_experiment(self):
        l = self.store.load()
        choice = rank([x for x in DEFAULT_OPPORTUNITIES if x.startup_cost_eur == 0 or self.policy.may_spend(l,x.startup_cost_eur)])[0]
        l.experiments += 1
        self.store.save(l)
        self.store.event("experiment_selected", {"name":choice.name,"channel":choice.channel})
        self.memory.remember("decision", f"Selected {choice.name} as next experiment", choice.confidence)
        self.tasks.create("scout","research",f"Validate {choice.name}",90)
        self.tasks.create("analyst","research",f"Score evidence for {choice.name}",82)
        self.tasks.create("maker","forge",f"Build offer for {choice.name}",78)
        self.tasks.create("writer","growth",f"Prepare distribution copy for {choice.name}",65)
        self.tasks.create("seller","sales",f"Prepare lead workflow for {choice.name}",60)
        return choice

    def tick(self):
        o = self.select_next_experiment()
        signal = self.signals.scan(o)
        for agent_id in ("scout","analyst","maker","writer","seller"):
            t = self.tasks.start_next(agent_id)
            if not t: continue
            self.store.event("task_started", {"task_id":t.id,"agent":t.agent,"title":t.title})
            if agent_id == "scout":
                self.memory.remember("observation", signal["summary"], .75)
            elif agent_id == "analyst":
                self.memory.remember("analysis", f"Evidence score {signal['score']} for {o.name}", .75)
            elif agent_id == "maker":
                offer = self.commerce.create_offer(o)
                self.memory.remember("commerce", f"Offer prepared: {offer['name']}", .85)
            elif agent_id == "writer":
                self.commerce.create_distribution_asset(o)
            elif agent_id == "seller":
                self.commerce.create_lead_queue(o)
            self.tasks.complete(t.id)
        result = self.snapshot()
        result["selected"] = {"name":o.name,"channel":o.channel}
        result["signal"] = signal
        return result
