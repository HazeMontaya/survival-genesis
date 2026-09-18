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
from .capabilities import CapabilityRegistry
from .projects import ProjectBoard
from .agents import AgentDirectory
from .social import MessageBus
from .tools import ToolRegistry
from .skills import SkillRegistry
from .soul import SoulStore
from .treasury import Treasury
from .resources import ResourceLedger

from .needs import NeedEngine
from .constitution import Constitution
from .policy import PolicyEngine
from .executor import CapabilityExecutor
from .catalog import DEFAULT_OPPORTUNITIES

class GenesisAgent:
    """A minimal seed agent that derives work from the mission and actual runtime state."""
    def __init__(self, store=None, policy=None):
        self.store=store or StateStore()
        self.policy=policy or SurvivalPolicy()
        self.constitution=Constitution()
        self.economy=Economy(self.store)
        root=self.store.path.parent
        self.company=CompanyProfile()
        self.tasks=TaskBoard(root/"tasks.json")
        self.memory=MemoryGraph(root/"memory.json")
        self.artifacts=ArtifactStore(root/"artifacts")
        self.signals=SignalEngine(self.store,self.memory)
        self.commerce=CommerceEngine(self.store,self.artifacts,self.memory)
        self.connectors=ConnectorRegistry(self.store)
        self.capabilities=CapabilityRegistry(root/"capabilities.json")
        self.projects=ProjectBoard(root/"projects.json")
        self.agents=AgentDirectory(root/"agents.json")
        self.agents.ensure_genesis()
        self.messages=MessageBus(root/"messages.json")
        self.tools=ToolRegistry(root,self.store,self.memory,self.messages)
        self.needs=NeedEngine(self)
        self.executor=CapabilityExecutor(self)
        self.treasury=Treasury(self.store)
        self.resources=ResourceLedger(root/"resources.json")
        self.execution_policy=PolicyEngine(self.store,self.constitution,self.treasury,self.resources)
        self.tools.policy=self.execution_policy
        self.skills=SkillRegistry(root/"skills.json")
        self.soul=SoulStore(root/"soul.json")
        self.soul.ensure(self.company.mission)
        self.world=WorldModel(root/"world.json")

    def snapshot(self):
        l=self.store.load()
        self.world.sync(self)
        return {
            "mode":self.policy.mode(l),
            "company":self.company.snapshot(),
            "ledger":l.__dict__,
            "tasks":self.tasks.snapshot(),
            "memory":self.memory.snapshot(),
            "artifacts":self.artifacts.snapshot(),
            "signals":self.signals.snapshot(),
            "commerce":self.commerce.snapshot(),
            "connectors":self.connectors.snapshot(),
            "capabilities":self.capabilities.snapshot(),
            "projects":self.projects.snapshot(),
            "agents":self.agents.snapshot(),
            "messages":self.messages.snapshot(),
            "tools":self.tools.snapshot(),
            "skills":self.skills.snapshot(),
            "soul":self.soul.snapshot(),
            "world":self.world.snapshot(self),
            "treasury":self.treasury.snapshot(),
            "resources":self.resources.snapshot(),
            "constitution":self.constitution.snapshot(),
            "policy_audit":str(self.execution_policy.audit_path),
            "top_opportunities":[{"name":x.name,"channel":x.channel,"score":round(x.score(),3)} for x in rank(DEFAULT_OPPORTUNITIES)]
        }

    def _capability(self,cid,name,description,owner="genesis-1",prerequisites=None):
        c=self.capabilities.ensure(cid,name,description,prerequisites,owner)
        if c.state=="entdeckt": self.capabilities.transition(cid,"geplant")
        return c

    def _project_for(self,cid,title,goal,owner="genesis-1"):
        existing=next((p for p in self.projects.items if p.status not in ("done","failed") and cid in p.required_capabilities),None)
        if existing:return existing
        return self.projects.create(title,goal,owner,[cid])

    def decide(self):
        """Select the highest-priority unsatisfied need from live state."""
        need=next(iter(self.needs.detect()),None)
        if not need:
            return None,None,None
        cid=need["capability"]
        genesis=self.agents.get("genesis-1")
        descriptions={
            "observe_environment":"Zustand, Ressourcen und externe Signale erfassen.",
            "goal_decomposition":"Aus der Mission konkrete Ziele und Abhängigkeiten ableiten.",
            "agent_creation":"Neue spezialisierte Agenten aus einem überprüfbaren Blueprint erzeugen.",
            "offer_creation":"Ein überprüfbares und lieferbares Ergebnis erzeugen.",
            "specialist_research":"Markt- und Evidenzsignale systematisch untersuchen.",
            "skill_creation":"Wiederverwendbare Verfahren aus verifizierter Arbeit extrahieren.",
            "self_testing":"Änderungen und Fähigkeiten durch reproduzierbare Tests prüfen.",
            "external_publishing":"Ein Angebot über einen konfigurierten externen Kanal veröffentlichen.",
        }
        title=cid.replace("_"," ").title()
        self._capability(cid,title,descriptions.get(cid,need["reason"]),genesis.id,need.get("prerequisites",[]))
        return cid,title,self._project_for(cid,title,need["reason"])

    def _execute(self,task):
        if task.capability_id:
            self.capabilities.transition(task.capability_id,"in_entwicklung")
        try:
            evidence=self.executor.execute(task)
            self.tasks.complete(task.id,evidence=evidence,result="verifiziert")
            if task.capability_id:
                self.capabilities.transition(task.capability_id,"getestet",evidence)
                self.capabilities.transition(task.capability_id,"verifiziert",evidence)
                self.capabilities.transition(task.capability_id,"aktiv",evidence)
                self.agents.assign_capability(task.agent,task.capability_id)
                self.soul.evolve(task.capability_id)
            if task.project_id:
                project=self.projects.get(task.project_id)
                all_done=bool(project and project.task_ids and all((self.tasks.get(tid) and self.tasks.get(tid).status=="done") for tid in project.task_ids))
                self.projects.transition(task.project_id,"done" if all_done else "active",evidence)
            return evidence
        except Exception as exc:
            self.tasks.fail(task.id,str(exc))
            if task.capability_id: self.capabilities.transition(task.capability_id,"fehlgeschlagen",{"error":str(exc)})
            if task.project_id: self.projects.transition(task.project_id,"blocked",{"error":str(exc)})
            self.store.event("task_failed",{"task_id":task.id,"error":str(exc)})
            return {"error":str(exc)}

    def tick(self):
        self.tasks.unblock()
        cid,title,project=self.decide()
        created=None
        if cid:
            task=self.tasks.create("genesis-1","genesis",title,95,cid,project.id)
            self.projects.attach_task(project.id,task.id)
            created=task
            self.store.event("genesis_decision",{"capability":cid,"title":title,"project_id":project.id})
        executed=[]
        for a in self.agents.snapshot():
            task=self.tasks.start_next(a["id"])
            if task:
                executed.append({"task_id":task.id,"agent":a["id"],"result":self._execute(task)})
        self.world.sync(self)
        result=self.snapshot()
        result["decision"]={"capability":cid,"title":title,"project_id":project.id if project else None}
        result["created_task"]=created.id if created else None
        result["execution"]=executed
        return result
