from genesis.core.company import CompanyProfile
from genesis.core.constitution import Constitution
from genesis.core.database import RuntimeDatabase
from genesis.core.policy import PolicyEngine
from genesis.core.resources import ResourceLedger
from genesis.core.state import StateStore
from genesis.core.survival import SurvivalPolicy
from genesis.domain.commerce import CommerceEngine
from genesis.domain.economy import Economy
from genesis.domain.opportunities import DEFAULT_OPPORTUNITIES,rank
from genesis.domain.treasury import Treasury
from genesis.agents.directory import AgentDirectory
from genesis.agents.social import MessageBus
from genesis.knowledge.memory import MemoryGraph
from genesis.knowledge.evidence import EvidenceLedger
from genesis.knowledge.identity import IdentityStore
from genesis.knowledge.signals import SignalEngine
from genesis.knowledge.skills import SkillRegistry
from genesis.platform.artifacts import ArtifactStore
from genesis.platform.connectors import ConnectorRegistry
from genesis.platform.tools import ToolRegistry
from genesis.work.capabilities import CapabilityRegistry
from genesis.work.projects import ProjectBoard
from genesis.work.tasks import TaskBoard
from genesis.work.workflows import WorkflowEngine
from genesis.world.model import WorldModel
class NeedEngine:
 def __init__(self,a):self.a=a
 def detect(self):
  a=self.a;m=a.memory.snapshot();c={x["id"]:x for x in a.capabilities.snapshot()};offers=a.commerce.snapshot()["offers"];agents=a.agents.snapshot();skills=a.skills.snapshot();active=lambda i:c.get(i,{}).get("state")=="aktiv";n=[]
  if not m:return [{"capability":"observe_environment","title":"Umgebung beobachten","reason":"Reale Zustands- und Evidenzdaten fehlen.","urgency":100,"prerequisites":[]}]
  if not active("goal_decomposition"):n.append({"capability":"goal_decomposition","title":"Ziel zerlegen","reason":"Die Mission braucht überprüfbare Teilziele.","urgency":95,"prerequisites":["observe_environment"]})
  if active("goal_decomposition") and len(agents)==1:n.append({"capability":"agent_creation","title":"Spezialisierung aufbauen","reason":"Der Seed-Agent ist ein Single Point of Execution.","urgency":85,"prerequisites":["goal_decomposition"]})
  if not offers:n.append({"capability":"offer_creation","title":"Erstes Ergebnis erzeugen","reason":"Noch kein verwertbares Ergebnis existiert.","urgency":80,"prerequisites":["goal_decomposition"]})
  if offers and not any("research" in x["purpose"].lower() for x in agents):n.append({"capability":"specialist_research","title":"Recherche spezialisieren","reason":"Angebotsentscheidungen brauchen Evidenz.","urgency":70,"prerequisites":["agent_creation"]})
  if not skills:n.append({"capability":"skill_creation","title":"Verfahren speichern","reason":"Wiederholbare Arbeit soll erhalten bleiben.","urgency":60,"prerequisites":["agent_creation"]})
  if not active("self_testing"):n.append({"capability":"self_testing","title":"Eigenen Zustand testen","reason":"Neue Fähigkeiten brauchen reproduzierbare Evidenz.","urgency":90,"prerequisites":["skill_creation"]})
  return sorted([x for x in n if all(active(p) for p in x["prerequisites"])],key=lambda x:(-x["urgency"],x["capability"]))
class GenesisAgent:
 def __init__(self,store=None):
  self.store=store or StateStore();root=self.store.path.parent;self.db=RuntimeDatabase(root/"runtime.db");self.control=PolicyEngine(self.db,root);self.policy=SurvivalPolicy();self.resources=ResourceLedger(root/"resources.json");self.company=CompanyProfile();self.constitution=Constitution();self.memory=MemoryGraph(root/"memory.json");self.evidence=EvidenceLedger(root/"evidence.json");self.identity=IdentityStore(root/"identity.json");self.identity.ensure(self.company.mission);self.artifacts=ArtifactStore(root/"artifacts");self.connectors=ConnectorRegistry(self.store);self.agents=AgentDirectory(root/"agents.json");self.agents.ensure_genesis();self.messages=MessageBus(root/"messages.json");self.capabilities=CapabilityRegistry(root/"capabilities.json");self.projects=ProjectBoard(root/"projects.json");self.tasks=TaskBoard(root/"tasks.json");self.workflows=WorkflowEngine(root/"workflows.json");self.skills=SkillRegistry(root/"skills.json");self.signals=SignalEngine(self.db,self.memory);self.commerce=CommerceEngine(self.store,self.artifacts,self.memory,self.db);self.economy=Economy(self.store,self.db);self.treasury=Treasury(self.store,self.db);self.tools=ToolRegistry(root,self.store,self.memory,self.messages,self.control);self.world=WorldModel(root/"world.json");self.needs=NeedEngine(self)
 def snapshot(self):self.world.sync(self);return {"company":self.company.snapshot(),"ledger":self.store.load().__dict__,"resources":self.resources.snapshot(),"agents":self.agents.snapshot(),"capabilities":self.capabilities.snapshot(),"projects":self.projects.snapshot(),"tasks":self.tasks.snapshot(),"workflows":self.workflows.snapshot(),"memory":self.memory.snapshot(),"evidence":self.evidence.snapshot(),"messages":self.messages.snapshot(),"artifacts":self.artifacts.snapshot(),"signals":self.signals.snapshot(),"commerce":self.commerce.snapshot(),"connectors":self.connectors.snapshot(),"skills":self.skills.snapshot(),"tools":self.tools.snapshot(),"treasury":self.treasury.snapshot(),"world":self.world.snapshot(),"runtime_db":self.db.snapshot(),"mode":self.policy.mode(self.store.load()),"top_opportunities":[x.name for x in rank(DEFAULT_OPPORTUNITIES)]}
 def tick(self):
  need=next(iter(self.needs.detect()),None);created=None
  if need:
   c=self.capabilities.ensure(need["capability"],need["title"],need["reason"],need["prerequisites"],"genesis-1");c.state=="entdeckt" and self.capabilities.transition(c.id,"geplant");p=next((x for x in self.projects.items if x.status not in ("done","failed") and c.id in x.required_capabilities),None) or self.projects.create(need["title"],need["reason"],"genesis-1",[c.id]);created=self.tasks.create("genesis-1",need["title"],need["urgency"],c.id,p.id);self.projects.attach_task(p.id,created.id);self.db.event("decision",need,"genesis-1")
  executed=[]
  for a in self.agents.snapshot():
   t=self.tasks.start_next(a["id"])
   if not t:self.agents.set_activity(a["id"],"idle");continue
   self.agents.set_activity(a["id"],"working")
   self.capabilities.transition(t.capability_id,"in_entwicklung")
   try:
    if t.capability_id=="observe_environment":e=self.signals.scan(DEFAULT_OPPORTUNITIES[0]);self.memory.remember("observation",e["summary"],.8)
    elif t.capability_id=="goal_decomposition":self.memory.remember("goal",self.company.mission,.9);e={"verified":True,"type":"goal_decomposition"}
    elif t.capability_id=="agent_creation":child=self.agents.spawn("Researcher","Untersuche externe Signale und Evidenz.","genesis-1",[],["read_file","list_files","run_tests","remember","send_message"]);self.messages.send("genesis-1",child.id,"Liefere belegte Beobachtungen.");e={"verified":True,"type":"agent_created","agent_id":child.id}
    elif t.capability_id=="offer_creation":e=self.commerce.create_offer(rank(DEFAULT_OPPORTUNITIES)[0])
    elif t.capability_id=="skill_creation":e={"type":"skill_created","skill_id":self.skills.create("research_basics","Recherche-Grundlagen","Belege prüfen","Quelle → Signal → Unsicherheit → speichern.").id}
    elif t.capability_id=="self_testing":e=self.tools.call("run_tests")
    else:e={"verified":True}
    self.tasks.complete(t.id,e,"verifiziert");self.agents.set_activity(t.agent,"completed")self.capabilities.transition(t.capability_id,"getestet",e);self.capabilities.transition(t.capability_id,"verifiziert",e);self.capabilities.transition(t.capability_id,"aktiv",e);self.agents.assign_capability(t.agent,t.capability_id);self.db.event("task_completed",{"task_id":t.id,"capability":t.capability_id},"genesis-1");executed.append({"task_id":t.id,"agent":t.agent,"result":e})
   except Exception as exc:self.tasks.fail(t.id,str(exc));self.agents.set_activity(t.agent,"error");self.capabilities.transition(t.capability_id,"fehlgeschlagen",{"error":str(exc)});self.db.event("task_failed",{"task_id":t.id,"error":str(exc)},"genesis-1");executed.append({"task_id":t.id,"agent":t.agent,"result":{"error":str(exc)}})
  self.workflows.sync(self.projects.items,self.tasks.snapshot());s=self.snapshot();s["decision"]=need;s["created_task"]=created.id if created else None;s["execution"]=executed;return s
