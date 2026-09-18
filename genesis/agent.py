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
from .world import WorldModel

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
        self.world = WorldModel(root/"world.json")

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
            "world": self.world.snapshot(self),
            "top_opportunities": [{"name":x.name,"channel":x.channel,"score":round(x.score(),3)} for x in rank(DEFAULT_OPPORTUNITIES)[:7]]
        }

    def select_next_experiment(self):
        l = self.store.load()
        choice = rank([x for x in DEFAULT_OPPORTUNITIES if x.startup_cost_eur == 0 or self.policy.may_spend(l,x.startup_cost_eur)])[0]
        l.experiments += 1
        self.store.save(l)
        self.store.event("experiment_selected", {"name":choice.name,"channel":choice.channel})
        self.memory.remember("decision", f"Nächstes Experiment: {choice.name}", choice.confidence)
        self.tasks.create("scout","research",f"Validiere {choice.name}",90)
        self.tasks.create("analyst","research",f"Bewerte Belege für {choice.name}",82)
        self.tasks.create("maker","forge",f"Erstelle Angebot für {choice.name}",78)
        self.tasks.create("writer","growth",f"Bereite Vertriebsmaterial für {choice.name} vor",65)
        self.tasks.create("seller","sales",f"Bereite Interessentenprozess für {choice.name} vor",60)
        return choice

    def _build_improvement_task(self):
        gaps = self.world.assess(self)
        if not gaps:
            return None
        node_id, name, room, reason = gaps[0]
        agent_map = {
            "research":"analyst", "forge":"maker", "growth":"writer", "sales":"seller",
            "treasury":"ledger", "operations":"operator", "evolution":"evolver"
        }
        agent_id = agent_map.get(room, "evolver")
        existing = [t for t in self.tasks.snapshot()
                    if t["status"] in ("queued","active") and t["title"].startswith("Verbessere: "+name)]
        if existing:
            return None
        task = self.tasks.create(agent_id, room, "Verbessere: "+name, 88)
        self.store.event("selbstverbesserung_geplant", {
            "task_id": task.id, "faehigkeit": name, "grund": reason, "agent": agent_id
        })
        self.memory.remember("improvement", f"{name}: {reason}", .9)
        return task

    def tick(self):
        # First inspect the real system, then grow its persistent topology.
        new_nodes = self.world.grow_from_gaps(self)
        improvement = self._build_improvement_task()

        o = self.select_next_experiment()
        signal = self.signals.scan(o)
        for agent_id in ("scout","analyst","maker","writer","seller"):
            t = self.tasks.start_next(agent_id)
            if not t:
                continue
            self.store.event("task_started", {"task_id":t.id,"agent":t.agent,"title":t.title})
            if agent_id == "scout":
                self.memory.remember("observation", signal["summary"], .75)
            elif agent_id == "analyst":
                self.memory.remember("analysis", f"Belegscore {signal['score']} für {o.name}", .75)
            elif agent_id == "maker":
                offer = self.commerce.create_offer(o)
                self.memory.remember("commerce", f"Angebot vorbereitet: {offer['name']}", .85)
            elif agent_id == "writer":
                self.commerce.create_distribution_asset(o)
            elif agent_id == "seller":
                self.commerce.create_lead_queue(o)
            self.tasks.complete(t.id)

        # Re-evaluate after execution: the next world state reflects what really exists.
        result = self.snapshot()
        result["selected"] = {"name":o.name,"channel":o.channel}
        result["signal"] = signal
        result["world_growth"] = new_nodes
        result["improvement_task"] = improvement.id if improvement else None
        return result
