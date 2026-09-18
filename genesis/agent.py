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

class NeedEngine:
    """Derives the next missing capability from persistent runtime state."""
    def __init__(self, agent):
        self.agent=agent
    def detect(self):
        a=self.agent
        memories=a.memory.snapshot()
        caps={x["id"]:x for x in a.capabilities.snapshot()}
        offers=a.commerce.snapshot()["offers"]
        agents=a.agents.snapshot()
        skills=a.skills.snapshot()
        active=lambda cid: caps.get(cid,{}).get("state")=="aktiv"
        needs=[]
        if not memories:
            return [{"capability":"observe_environment","title":"Umgebung beobachten","reason":"Reale Zustands- und Evidenzdaten fehlen.","urgency":100,"prerequisites":[]}]
        if not active("goal_decomposition"):
            needs.append({"capability":"goal_decomposition","title":"Ziel in ausführbare Schritte zerlegen","reason":"Die Mission benötigt eine überprüfbare nächste Handlung.","urgency":95,"prerequisites":["observe_environment"]})
        if active("goal_decomposition") and len(agents)==1 and not active("agent_creation"):
            needs.append({"capability":"agent_creation","title":"Arbeitsfähigkeit durch Spezialisierung erweitern","reason":"Der Seed-Agent ist ein Single Point of Execution.","urgency":85,"prerequisites":["goal_decomposition"]})
        if not offers:
            needs.append({"capability":"offer_creation","title":"Erstes lieferbares Ergebnis erzeugen","reason":"Noch kein verwertbares Ergebnis existiert.","urgency":80,"prerequisites":["goal_decomposition"]})
        if offers and not any("research" in x["purpose"].lower() for x in agents):
            needs.append({"capability":"specialist_research","title":"Evidenz- und Marktbeobachtung spezialisieren","reason":"Angebotsentscheidungen brauchen externe Evidenz.","urgency":70,"prerequisites":["agent_creation"]})
        if not skills:
            needs.append({"capability":"skill_creation","title":"Verifiziertes Verfahren als Skill speichern","reason":"Wiederholbare Arbeit sollte als prozedurales Wissen erhalten bleiben.","urgency":60,"prerequisites":["agent_creation"]})
        if not active("self_testing"):
            needs.append({"capability":"self_testing","title":"Eigenen Zustand reproduzierbar prüfen","reason":"Neue Fähigkeiten benötigen ausführbare Evidenz.","urgency":90,"prerequisites":["skill_creation"]})
        if offers and any(x.get("configured") for x in a.connectors.snapshot()) and not any(x.get("published_url") for x in offers):
            needs.append({"capability":"external_publishing","title":"Angebot über echten Anschluss veröffentlichen","reason":"Ein konfigurierter externer Kanal existiert.","urgency":75,"prerequisites":["offer_creation"]})
        return sorted(needs,key=lambda x:(-x["urgency"],x["capability"]))

DEFAULT_OPPORTUNITIES = [
    Opportunity("technical_microservice","service",0,120,3,.45,.65),
    Opportunity("digital_microproduct","digital_product",0,49,4,.35,.85),
    Opportunity("lead_generation","leads",0,100,4,.30,.75),
    Opportunity("open_source_sponsorship","open_source",0,25,2,.15,.90),
    Opportunity("affiliate_content","affiliate",0,60,5,.20,.70),
    Opportunity("print_on_demand","pod",0,35,5,.15,.55),
]

class GenesisAgent:
    """A minimal seed agent that derives work from the mission and actual runtime state."""
    def __init__(self, store=None, policy=None):
        self.store=store or StateStore()
        self.policy=policy or SurvivalPolicy()
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
        self._capability(cid,need["title"],descriptions.get(cid,need["reason"]),genesis.id,need.get("prerequisites",[]))
        return cid,need["title"],self._project_for(cid,need["title"],need["reason"])

    def _execute(self,task):
        if task.capability_id:
            self.capabilities.transition(task.capability_id,"in_entwicklung")
        try:
            if task.capability_id=="observe_environment":
                signal=self.signals.scan(DEFAULT_OPPORTUNITIES[0])
                self.memory.remember("observation",f"Startbeobachtung: {signal['summary']}",.8)
                evidence={"type":"observation","signal":signal}
            elif task.capability_id=="goal_decomposition":
                self.memory.remember("goal","Mission in überprüfbare Teilziele zerlegen.",.9)
                evidence={"type":"goal_decomposition","verified":True}
            elif task.capability_id=="agent_creation":
                child=self.agents.spawn("Researcher","Untersuche Belege, Chancen und externe Signale.",task.agent,[],["read_file","list_files","run_tests","remember","send_message"])
                self.messages.send(task.agent,child.id,"Willkommen. Untersuche externe Signale und liefere belegte Beobachtungen.", "onboarding")
                self.memory.remember("agent",f"Neuer Agent erzeugt: {child.name}",.9)
                self._capability("research_observation","Recherche beobachten","Externe Signale erfassen und als Evidenz speichern.",child.id)
                child_task=self.tasks.create(child.id,"research","Führe eine Recherchebeobachtung durch",70,"research_observation","")
                self.messages.send(task.agent,child.id,"Arbeitsauftrag: Führe die Recherchebeobachtung aus und melde Evidenz.","task")
                evidence={"type":"agent_created","agent_id":child.id,"task_id":child_task.id}
            elif task.capability_id=="research_observation":
                signal=self.signals.scan(DEFAULT_OPPORTUNITIES[0])
                self.memory.remember("research",signal["summary"],signal["score"])
                self.messages.send(task.agent,"genesis-1",signal["summary"],"result")
                evidence={"type":"research_observation","signal":signal}
            elif task.capability_id=="offer_creation":
                choice=rank(DEFAULT_OPPORTUNITIES)[0]
                offer=self.commerce.create_offer(choice)
                evidence={"type":"artifact_created","artifact_id":offer["artifact_id"],"offer_id":offer["id"]}
            elif task.capability_id=="specialist_research":
                child=self.agents.spawn("Researcher","Untersuche Markt- und Evidenzsignale und liefere belegte Beobachtungen.",task.agent,["specialist_research"],["read_file","list_files","run_tests","remember","send_message"])
                self.messages.send(task.agent,child.id,"Arbeite als spezialisierter Recherche-Agent und dokumentiere Evidenz.", "onboarding")
                evidence={"type":"agent_created","agent_id":child.id}
            elif task.capability_id=="skill_creation":
                skill=self.skills.create("research_basics","Recherche-Grundlagen","Belege und Signale strukturiert untersuchen.","Quelle erfassen → Signal prüfen → Unsicherheit markieren → Ergebnis speichern.")
                evidence={"type":"skill_created","skill_id":skill.id}
            elif task.capability_id=="self_testing":
                result=self.tools.call("run_tests")
                if result["returncode"]!=0: raise RuntimeError(result["stderr"] or result["stdout"])
                evidence={"type":"test_run","returncode":result["returncode"],"stdout":result["stdout"][-3000:]}
            elif task.capability_id=="external_publishing":
                configured=any(c["id"]=="webhook" and c["configured"] for c in self.connectors.snapshot())
                if not configured: raise RuntimeError("Kein externer Veröffentlichungsanschluss konfiguriert")
                evidence={"type":"connector_ready","verified":True}
            else:
                evidence={"type":"capability_step","verified":True}
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
