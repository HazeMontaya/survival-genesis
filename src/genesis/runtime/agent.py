from genesis.domain.economy import Economy
from genesis.domain.evidence import EvidenceLedger
from genesis.domain.orders import OrderEngine
from genesis.core.opportunities import Opportunity, rank
from genesis.core.state import StateStore
from genesis.core.survival import SurvivalPolicy
from genesis.domain.tasks import TaskBoard
from genesis.domain.memory import MemoryGraph
from genesis.core.company import CompanyProfile
from genesis.domain.artifacts import ArtifactStore
from genesis.integrations.signals import SignalEngine
from genesis.domain.commerce import CommerceEngine
from genesis.integrations.connectors import ConnectorRegistry
from genesis.domain.world import WorldModel
from genesis.domain.capabilities import CapabilityRegistry
from genesis.domain.projects import ProjectBoard
from genesis.domain.agents import AgentDirectory
from genesis.domain.social import MessageBus
from genesis.integrations.tools import ToolRegistry
from genesis.domain.skills import SkillRegistry
from genesis.domain.soul import SoulStore
from genesis.integrations.treasury import Treasury
from genesis.runtime.database import RuntimeDatabase
from genesis.runtime.policy import PolicyEngine
from genesis.runtime.evolution import EvolutionManager
from genesis.core.resources import ResourceLedger
from genesis.domain.workflows import WorkflowEngine

DEFAULT_OPPORTUNITIES = [
    Opportunity("technical_microservice", "service", 0, 120, 3, .45, .65),
    Opportunity("digital_microproduct", "digital_product", 0, 49, 4, .35, .85),
    Opportunity("lead_generation", "leads", 0, 100, 4, .30, .75),
    Opportunity("open_source_sponsorship", "open_source", 0, 25, 2, .15, .90),
]

class NeedEngine:
    def __init__(self, agent):
        self.agent = agent

    def detect(self):
        a = self.agent
        memories = a.memory.snapshot()
        caps = {x["id"]: x for x in a.capabilities.snapshot()}
        agents = a.agents.snapshot()
        offers = a.commerce.snapshot().get("offers", [])
        skills = a.skills.snapshot()
        active = lambda cid: caps.get(cid, {}).get("state") in {"aktiv", "verifiziert", "getestet"}
        needs = []
        if not memories:
            needs.append(("observe_environment", "Umgebung beobachten", 100, []))
        if memories and not active("goal_decomposition"):
            needs.append(("goal_decomposition", "Mission zerlegen", 95, ["observe_environment"]))
        if active("goal_decomposition") and len(agents) == 1 and not active("agent_creation"):
            needs.append(("agent_creation", "Spezialisierung erzeugen", 90, ["goal_decomposition"]))
        if not offers:
            needs.append(("offer_creation", "Erstes lieferbares Ergebnis erzeugen", 80, ["goal_decomposition"]))
        if not skills and len(agents) > 1:
            needs.append(("skill_creation", "Verifiziertes Verfahren speichern", 60, ["agent_creation"]))
        if not active("self_testing"):
            needs.append(("self_testing", "Eigenen Zustand prüfen", 85, ["skill_creation"]))
        return [
            {"capability": c, "title": t, "urgency": u, "prerequisites": p}
            for c, t, u, p in sorted(needs, key=lambda x: (-x[2], x[0]))
            if all(active(prereq) for prereq in p)
        ]

class GenesisAgent:
    """Runtime brain. It owns decisions; the browser only observes/projects them."""

    def __init__(self, store=None, policy=None):
        self.store = store or StateStore()
        self.policy = policy or SurvivalPolicy()
        root = self.store.path.parent
        self.evidence = EvidenceLedger(root / "evidence.json")
        self.orders = OrderEngine(root / "orders.json", self.evidence)
        self.resources = ResourceLedger(root / "resources.json")
        self.economy = Economy(self.store, self.evidence, self.resources)
        self.company = CompanyProfile()
        self.tasks = TaskBoard(root / "tasks.json")
        self.memory = MemoryGraph(root / "memory.json")
        self.artifacts = ArtifactStore(root / "artifacts")
        self.signals = SignalEngine(self.store, self.memory)
        self.commerce = CommerceEngine(self.store, self.artifacts, self.memory)
        self.connectors = ConnectorRegistry(self.store)
        self.capabilities = CapabilityRegistry(root / "capabilities.json")
        self.projects = ProjectBoard(root / "projects.json")
        self.agents = AgentDirectory(root / "agents.json")
        self.agents.ensure_genesis()
        self.messages = MessageBus(root / "messages.json")
        self.runtime_db = RuntimeDatabase(root / "runtime.db")
        self.runtime_policy = PolicyEngine(self.runtime_db, root)
        self.evolution = EvolutionManager(root / "evolution.json", self.evidence)
        self.tools = ToolRegistry(root, self.store, self.memory, self.messages, self.runtime_policy)
        self.needs = NeedEngine(self)
        self.treasury = Treasury(self.store)
        self.skills = SkillRegistry(root / "skills.json")
        self.soul = SoulStore(root / "soul.json")
        self.soul.ensure(self.company.mission)
        self.world = WorldModel()
        self.workflows = WorkflowEngine(root / "workflows.json")

    def snapshot(self):
        ledger = self.store.load()
        self.world.project(self)
        return {
            "mode": self.policy.mode(ledger),
            "company": self.company.snapshot(),
            "ledger": ledger.__dict__,
            "tasks": self.tasks.snapshot(),
            "memory": self.memory.snapshot(),
            "artifacts": self.artifacts.snapshot(),
            "signals": self.signals.snapshot(),
            "commerce": self.commerce.snapshot(),
            "connectors": self.connectors.snapshot(),
            "capabilities": self.capabilities.snapshot(),
            "projects": self.projects.snapshot(),
            "agents": self.agents.snapshot(),
            "messages": self.messages.snapshot(),
            "tools": self.tools.snapshot(),
            "skills": self.skills.snapshot(),
            "soul": self.soul.snapshot(),
            "world": self.world.snapshot(self),
            "treasury": self.treasury.snapshot(),
            "resources": self.resources.snapshot(),
            "evidence": self.evidence.snapshot(),
            "orders": self.orders.snapshot(),
            "workflows": self.workflows.snapshot(),
            "evolution": self.evolution.snapshot(),
            "runtime": self.runtime_db.snapshot(),
            "top_opportunities": [{"name": x.name, "channel": x.channel, "score": round(x.score(), 3)} for x in rank(DEFAULT_OPPORTUNITIES)],
        }

    def _capability(self, cid, name, description, owner="genesis-1", prerequisites=None):
        c = self.capabilities.ensure(cid, name, description, prerequisites or [], owner)
        if c.state == "entdeckt":
            self.capabilities.transition(cid, "geplant")
        return c

    def _project(self, cid, title, goal):
        p = next((x for x in self.projects.items if x.status not in ("done", "failed") and cid in x.required_capabilities), None)
        return p or self.projects.create(title, goal, "genesis-1", [cid])

    def command(self, text: str, actor="human"):
        text = str(text).strip()
        if not text:
            raise ValueError("command is empty")
        project = self.projects.create("Command", text, "genesis-1", []) if not any(p.title == "Command" and p.status == "active" for p in self.projects.items) else next(p for p in self.projects.items if p.title == "Command" and p.status == "active")
        task = self.tasks.create("genesis-1", "command", text, 100, "human_command", project.id)
        self.projects.attach_task(project.id, task.id)
        self.runtime_db.event("command_received", {"task_id": task.id, "text": text}, actor=actor)
        return {"task_id": task.id, "accepted": True}

    def decide(self):
        need = next(iter(self.needs.detect()), None)
        if not need:
            return None
        cid, title, _, prereq = need["capability"], need["title"], need["urgency"], need["prerequisites"]
        self._capability(cid, title, f"Runtime capability: {title}", prerequisites=prereq)
        project = self._project(cid, title, f"Capability zur Erfüllung der Mission: {title}")
        task = self.tasks.create("genesis-1", "genesis", title, 95, cid, project.id)
        self.projects.attach_task(project.id, task.id)
        self.workflows.ensure_for_project(project, self.tasks.snapshot())
        self.runtime_db.event("decision", {"capability": cid, "task_id": task.id}, actor="genesis-1")
        return task

    def _verified(self, subject, kind, summary, payload=None, source="runtime"):
        ev = self.evidence.record(subject, kind, summary, payload, source, status="observed")
        self.evidence.verify(ev.id, verifier="runtime")
        return ev

    def execute(self, task):
        if task.capability_id:
            self.capabilities.transition(task.capability_id, "in_entwicklung")
        try:
            if task.capability_id in {"observe_environment", "research_observation"}:
                signal = self.signals.scan(DEFAULT_OPPORTUNITIES[0])
                self.memory.remember("observation", signal["summary"], signal["score"])
                ev = self._verified(task.id, task.capability_id, signal["summary"], signal, "signal-engine")
                result = {"evidence_id": ev.id, "signal": signal}
            elif task.capability_id == "goal_decomposition":
                self.memory.remember("goal", self.company.mission, .9)
                ev = self._verified(task.id, "goal", "Mission als überprüfbarer Arbeitsgegenstand gespeichert", {"mission": self.company.mission})
                result = {"evidence_id": ev.id}
            elif task.capability_id == "agent_creation":
                child = self.agents.spawn("Researcher", "Research, Evidenz und Marktbeobachtung", "genesis-1",
                                          ["research_observation"], ["read_file", "list_files", "run_tests", "remember", "send_message"])
                self.messages.send("genesis-1", child.id, "Arbeite nur mit belegbaren Beobachtungen.", "onboarding")
                ev = self._verified(task.id, "agent_created", "Researcher erzeugt", {"agent_id": child.id})
                result = {"evidence_id": ev.id, "agent_id": child.id}
            elif task.capability_id == "offer_creation":
                choice = rank(DEFAULT_OPPORTUNITIES)[0]
                offer = self.commerce.create_offer(choice)
                ev = self._verified(offer["id"], "offer_created", "Angebot als internes Artefakt erzeugt", offer, "commerce")
                result = {"evidence_id": ev.id, "offer_id": offer["id"]}
            elif task.capability_id == "skill_creation":
                skill = self.skills.create("research_basics", "Recherche-Grundlagen",
                                           "Quelle erfassen → Signal prüfen → Unsicherheit markieren → Ergebnis speichern.")
                ev = self._verified(task.id, "skill_created", "Skill gespeichert", {"skill_id": skill.id})
                result = {"evidence_id": ev.id}
            elif task.capability_id == "self_testing":
                test = self.tools.call("run_tests")
                if test.get("returncode", 1) != 0:
                    raise RuntimeError(test.get("stderr") or test.get("stdout") or "tests failed")
                ev = self._verified(task.id, "test_run", "Tests erfolgreich ausgeführt", test)
                result = {"evidence_id": ev.id, "returncode": 0}
            elif task.capability_id == "human_command":
                ev = self._verified(task.id, "command_received", task.title, {"command": task.title}, "human")
                result = {"evidence_id": ev.id, "status": "queued_for_planning"}
            else:
                ev = self._verified(task.id, "capability_step", task.title, {"task_id": task.id})
                result = {"evidence_id": ev.id}
            self.tasks.complete(task.id, evidence=result, result="verified")
            if task.capability_id:
                for state in ("getestet", "verifiziert", "aktiv"):
                    self.capabilities.transition(task.capability_id, state, result)
                self.agents.assign_capability(task.agent, task.capability_id)
                self.soul.evolve(task.capability_id)
            return result
        except Exception as exc:
            self.tasks.fail(task.id, str(exc))
            self.runtime_db.event("task_failed", {"task_id": task.id, "error": str(exc)}, actor=task.agent)
            return {"error": str(exc)}

    def tick(self):
        self.tasks.unblock()
        decision = self.decide()
        executed = []
        for a in self.agents.snapshot():
            task = self.tasks.start_next(a["id"])
            if task:
                self.agents.set_activity(a["id"], "walking", task.room)
                self.runtime_db.event("agent_moved", {"agent_id": a["id"], "room": task.room, "task_id": task.id}, actor=a["id"])
                self.agents.set_activity(a["id"], "processing", task.room)
                self.runtime_db.event("task_started", {"task_id": task.id, "agent_id": a["id"], "room": task.room}, actor=a["id"])
                result = self.execute(task)
                inbox = self.messages.inbox(a["id"], mark_delivered=True)
                if inbox:
                    self.agents.set_activity(a["id"], "collaborating", task.room)
                    self.runtime_db.event("messages_delivered", {"agent_id": a["id"], "count": len(inbox), "message_ids": [m["id"] for m in inbox]}, actor=a["id"])
                final_activity = "completed" if "error" not in result else "error"
                self.agents.set_activity(a["id"], final_activity, task.room)
                self.runtime_db.event("task_completed" if final_activity == "completed" else "task_failed", {"task_id": task.id, "agent_id": a["id"], "evidence_id": result.get("evidence_id", "")}, actor=a["id"])
                self.agents.set_activity(a["id"], "idle", "core")
                executed.append({"task_id": task.id, "agent": a["id"], "result": result})
        for workflow in self.workflows.snapshot():
            self.workflows.sync(workflow["id"], self.tasks.snapshot())
        self.world.project(self)
        self.runtime_db.event("world_tick", {"entities": len(self.world.entities), "relations": len(self.world.relations)}, actor="system")
        result = self.snapshot()
        result["decision"] = {"task_id": decision.id if decision else None}
        result["execution"] = executed
        return result
