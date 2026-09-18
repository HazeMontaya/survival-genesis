from .economy import Economy
from .opportunities import Opportunity,rank
from .state import StateStore
from .survival import SurvivalPolicy
from .tasks import TaskBoard
from .memory import MemoryGraph
from .company import CompanyProfile
from .artifacts import ArtifactStore
DEFAULT_OPPORTUNITIES=[
Opportunity("digital_microproduct","digital_product",0,49,4,.35,.85),
Opportunity("technical_microservice","service",0,120,3,.45,.65),
Opportunity("open_source_sponsorship","open_source",0,25,2,.15,.90),
Opportunity("affiliate_content","affiliate",0,60,5,.20,.70),
Opportunity("print_on_demand","pod",0,35,5,.15,.55),
Opportunity("dropship_test","dropshipping",0,80,8,.10,.45),
Opportunity("lead_generation","leads",0,100,4,.30,.75)]
class GenesisAgent:
    def __init__(self,store=None,policy=None):
        self.store=store or StateStore(); self.policy=policy or SurvivalPolicy(); self.economy=Economy(self.store)
        root=self.store.path.parent; self.company=CompanyProfile(); self.tasks=TaskBoard(root/"tasks.json"); self.memory=MemoryGraph(root/"memory.json"); self.artifacts=ArtifactStore(root/"artifacts")
    def snapshot(self):
        l=self.store.load()
        return {"mode":self.policy.mode(l),"company":self.company.snapshot(),"ledger":l.__dict__,"tasks":self.tasks.snapshot(),"memory":self.memory.snapshot(),"artifacts":self.artifacts.snapshot(),"top_opportunities":[{"name":x.name,"channel":x.channel,"score":round(x.score(),3)} for x in rank(DEFAULT_OPPORTUNITIES)[:5]]}
    def select_next_experiment(self):
        l=self.store.load(); choice=rank([x for x in DEFAULT_OPPORTUNITIES if x.startup_cost_eur==0 or self.policy.may_spend(l,x.startup_cost_eur)])[0]
        l.experiments+=1; self.store.save(l); self.store.event("experiment_selected",{"name":choice.name,"channel":choice.channel})
        self.memory.remember("decision",f"Selected {choice.name} as next zero-capital experiment",choice.confidence)
        self.tasks.create("scout","research",f"Validate {choice.name} opportunity",85); self.tasks.create("forge","forge",f"Prepare first artifact for {choice.name}",70); return choice
    def build_local_artifact(self,o):
        body=f"""# {o.name.replace("_"," ").title()}
## Objective
Validate this zero-capital opportunity with a concrete, useful deliverable.
## Channel
{o.channel}
## Constraints
- Startup cash: €0
- Paid execution: {self.policy.paid_execution_enabled}
- Financial execution: {self.policy.financial_execution_enabled}
- No fabricated revenue, accounts, credits or credentials.
## Validation
1. Define customer and painful problem.
2. Produce the smallest useful artifact.
3. Publish only through an explicitly configured connector.
4. Measure real responses or transactions.
5. Recognize revenue only after verification.
## Status
Local artifact ready for operator review.
"""
        return self.artifacts.create_markdown(o.name,body,o.channel)
    def tick(self):
        o=self.select_next_experiment()
        for agent in ("scout","forge"):
            t=self.tasks.start_next(agent)
            if t:
                self.store.event("task_started",{"task_id":t.id,"agent":t.agent,"title":t.title})
                if agent=="scout": self.memory.remember("observation",f"Completed local scouting task: {t.title}",.8)
                else:
                    a=self.build_local_artifact(o); self.store.event("artifact_ready",{"artifact_id":a.id,"path":a.path}); self.memory.remember("artifact",f"Created local artifact {a.title}",.9)
                self.tasks.complete(t.id)
        r=self.snapshot(); r["selected"]={"name":o.name,"channel":o.channel}; return r
