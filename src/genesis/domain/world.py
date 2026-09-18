from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import math

@dataclass(frozen=True)
class WorldEntity:
    id: str
    type: str
    name: str
    state: str = "active"
    parent_id: str = ""
    owner_id: str = ""
    room: str = "core"
    visual_state: str = "idle"
    x: float = 0.0
    y: float = 0.0
    size: float = 1.0
    reason: str = ""
    created_at: str = ""

@dataclass(frozen=True)
class WorldRelation:
    id: str
    source: str
    target: str
    kind: str
    intensity: float = 1.0
    state: str = "active"

class WorldModel:
    """Deterministic read-model of persisted runtime state."""
    ROOMS = {
        "core": (50, 50),
        "intelligence": (28, 27),
        "production": (72, 28),
        "quality": (72, 72),
        "knowledge": (30, 72),
        "output": (50, 88),
        "factory": (50, 18),
        "gateway": (12, 58),
        "commerce": (88, 55),
    }

    def __init__(self, path=None):
        self.path = path
        self.entities: list[WorldEntity] = []
        self.relations: list[WorldRelation] = []
        self.events: list[dict] = []
        self.generated_at = ""
        self.gaps: list[dict] = []

    @staticmethod
    def _pos(entity_id: str, room: str, index: int, total: int) -> tuple[float, float]:
        cx, cy = WorldModel.ROOMS.get(room, WorldModel.ROOMS["core"])
        if total <= 1:
            return cx, cy
        digest = hashlib.sha256(entity_id.encode()).digest()
        angle = (int.from_bytes(digest[:2], "big") / 65535) * math.tau
        radius = 7 + (digest[2] / 255) * 7
        return cx + math.cos(angle) * radius, cy + math.sin(angle) * radius

    @staticmethod
    def _room(purpose: str) -> str:
        p = str(purpose).lower()
        if any(x in p for x in ("research", "signal", "markt", "scout")): return "intelligence"
        if any(x in p for x in ("prüf", "critic", "quality", "test", "review")): return "quality"
        if any(x in p for x in ("write", "content", "design", "production")): return "production"
        if any(x in p for x in ("memory", "knowledge")): return "knowledge"
        return "core"

    @staticmethod
    def _agent_visual(agent_id: str, tasks: list[dict]) -> str:
        active = next((t for t in tasks if t.get("agent") == agent_id and t.get("status") == "active"), None)
        if not active: return "idle"
        cap = str(active.get("capability_id", "")).lower()
        if "research" in cap or "observe" in cap: return "searching"
        if "test" in cap or "critic" in cap or "review" in cap: return "reviewing"
        return "working"

    @staticmethod
    def _task_visual(status: str) -> str:
        return {"active":"working","done":"complete","blocked":"blocked","failed":"error","verifying":"reviewing"}.get(status, "queued")

    def project(self, agent) -> dict:
        tasks = agent.tasks.snapshot()
        agents = agent.agents.snapshot()
        projects = agent.projects.snapshot()
        capabilities = agent.capabilities.snapshot()
        evidence = agent.evidence.snapshot()
        orders = agent.orders.snapshot()
        messages = agent.messages.snapshot()
        memories = agent.memory.snapshot()
        offers = agent.commerce.snapshot().get("offers", [])
        workflows = agent.workflows.snapshot()
        entities: list[WorldEntity] = []
        relations: list[WorldRelation] = []

        def add(e): entities.append(e)

        add(WorldEntity("core:genesis", "core", "GENESIS", room="core", visual_state="running",
                        x=50, y=50, size=2.2, reason=agent.company.mission))

        for i, a in enumerate(agents):
            room = a.get("location") or self._room(a.get("purpose", ""))
            x, y = self._pos(a["id"], room, i, len(agents))
            aid = f"agent:{a['id']}"
            add(WorldEntity(aid, "agent", a["name"], parent_id="core:genesis", owner_id=a["id"],
                            room=room, visual_state=a.get("activity") or self._agent_visual(a["id"], tasks),
                            x=x, y=y, size=1.25, reason=a["purpose"], created_at=a.get("created_at","")))
            parent = a.get("parent_id")
            relations.append(WorldRelation(f"spawn:{a['id']}", f"agent:{parent}", aid, "spawned", 1.5)
                             if parent else WorldRelation(f"core:{a['id']}", "core:genesis", aid, "coordinates", .8))

        task_map = {t["id"]: t for t in tasks}
        for i, t in enumerate(tasks):
            room = t.get("room") or "production"
            x, y = self._pos(t["id"], room, i, max(1, len(tasks)))
            tid = f"task:{t['id']}"
            add(WorldEntity(tid, "task", t["title"], owner_id=t.get("agent",""), room=room,
                            visual_state=self._task_visual(t.get("status","")), x=x, y=y, size=.7,
                            reason=t.get("result") or t.get("error",""), created_at=t.get("created_at","")))
            if t.get("agent"): relations.append(WorldRelation(f"owns:{t['id']}", f"agent:{t['agent']}", tid, "carries", 1))
            if t.get("project_id"): relations.append(WorldRelation(f"contains:{t['id']}", f"project:{t['project_id']}", tid, "contains", .7))

        for p in projects:
            pid = f"project:{p['id']}"
            visual = "working" if p.get("status") == "active" else ("complete" if p.get("status") == "done" else "idle")
            add(WorldEntity(pid, "project", p["title"], owner_id=p.get("owner_agent",""), room="production",
                            visual_state=visual, x=72, y=28, size=1, reason=p.get("goal",""), created_at=p.get("created_at","")))

        for w in workflows:
            wid = f"workflow:{w['id']}"
            visual = {"active":"working","done":"complete","blocked":"blocked","failed":"error"}.get(w.get("status"), "queued")
            add(WorldEntity(wid, "workflow", w["title"], owner_id="", room="factory",
                            visual_state=visual, x=50, y=18, size=1.0, reason=w.get("goal",""), created_at=w.get("created_at","")))
            if w.get("project_id"): relations.append(WorldRelation(f"production:{w['id']}", f"project:{w['project_id']}", wid, "production_line", 1.2))
            for j, s in enumerate(w.get("stages", [])):
                sid = f"stage:{s['id']}"
                add(WorldEntity(sid, "stage", s["name"], owner_id=s.get("agent_id",""), room="factory",
                                visual_state=self._task_visual(s.get("status","queued")), x=50 + (j % 5 - 2) * 9,
                                y=18 + (j // 5) * 7, size=.55, reason=s.get("kind",""), created_at=s.get("created_at","")))
                relations.append(WorldRelation(f"stage-of:{s['id']}", wid, sid, "contains_stage", 1))
                if s.get("task_id") and s["task_id"] in task_map:
                    relations.append(WorldRelation(f"executes:{s['id']}", sid, f"task:{s['task_id']}", "executes", 1.3))

        for c in capabilities:
            cid = f"cap:{c['id']}"
            state = c.get("state")
            add(WorldEntity(cid, "capability", c["name"], owner_id=c.get("owner_agent",""), room="intelligence",
                            visual_state="working" if state == "in_entwicklung" else ("complete" if state == "aktiv" else "idle"),
                            x=28, y=27, size=.65, reason=c.get("description",""), created_at=c.get("created_at","")))

        for o in offers:
            oid = f"offer:{o['id']}"
            add(WorldEntity(oid, "output", o.get("title","Offer"), room="commerce", visual_state="ready",
                            x=88, y=55, size=.9, reason=o.get("description","")))

        for m in memories[-100:]:
            mid = "memory:" + m["id"]
            idx = max(0, len(memories) - 100) + memories[-100:].index(m)
            x, y = self._pos(mid, "knowledge", idx, max(1, min(100, len(memories))))
            add(WorldEntity(mid, "memory", m["kind"], room="knowledge", visual_state=m.get("status","alive"),
                            x=x, y=y, size=min(1.1, .45 + min(8, m.get("uses",0))*.08),
                            reason=m.get("content",""), created_at=m.get("created_at","")))
            for target in m.get("links", []):
                if any(item["id"] == target for item in memories):
                    relations.append(WorldRelation(f"memory-link:{m['id']}:{target}", mid, f"memory:{target}",
                                                    "knowledge_link", min(4, 1 + m.get("uses",0)/3)))

        for e in evidence[-80:]:
            eid = f"evidence:{e['id']}"
            add(WorldEntity(eid, "evidence", e["kind"], owner_id=e.get("subject_id",""), room="knowledge",
                            visual_state=e.get("status","observed"), x=30, y=72, size=.45,
                            reason=e.get("summary",""), created_at=e.get("created_at","")))

        for o in orders[-40:]:
            oid = f"order:{o['id']}"
            add(WorldEntity(oid, "order", o.get("title","Order"), room="commerce", visual_state=o.get("status","queued"),
                            x=88, y=55, size=.5, reason=o.get("result","")))

        for m in messages[-120:]:
            if m.get("sender") and m.get("recipient"):
                relations.append(WorldRelation(f"msg:{m.get('id', hashlib.sha1(str(m).encode()).hexdigest()[:10])}",
                                                f"agent:{m['sender']}", f"agent:{m['recipient']}", "communicates",
                                                min(5, 1 + len(m.get("content",""))/500)))

        self.entities = entities
        self.relations = [r for r in relations if r.source != r.target]
        self.generated_at = datetime.now(timezone.utc).isoformat()
        self.events = [{"type":"projection","timestamp":self.generated_at,"entities":len(entities),"relations":len(self.relations)}]
        self.gaps = []
        if not memories: self.gaps.append({"name":"Knowledge Garden empty","reason":"No persistent observations or memories exist yet."})
        if len(agents) == 1: self.gaps.append({"name":"Genesis alone","reason":"No specialist agent has been created."})
        if not offers: self.gaps.append({"name":"No output","reason":"No deliverable offer exists yet."})
        if not workflows: self.gaps.append({"name":"No workflow","reason":"No executable production workflow has been derived yet."})
        return self.snapshot(agent)

    def sync(self, agent):
        return self.project(agent)

    def snapshot(self, agent=None) -> dict:
        counts = {}
        for e in self.entities: counts[e.type] = counts.get(e.type, 0) + 1
        return {
            "generated_at": self.generated_at,
            "entities": [asdict(e) for e in self.entities],
            "relations": [asdict(r) for r in self.relations],
            "events": self.events[-50:],
            "counts": counts,
            "rooms": [{"id":k,"x":v[0],"y":v[1]} for k,v in self.ROOMS.items()],
            "layers": {"physical":True,"neural":True,"economic":True,"knowledge":True,"workflow":True},
            "gaps": self.gaps,
        }
