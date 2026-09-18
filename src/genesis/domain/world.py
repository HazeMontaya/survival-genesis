from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import math
from typing import Any

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
    """Pure presentation projection: domain state in, Agent World state out.

    The browser is never allowed to invent an entity, task, message, result,
    financial value or relationship. Positions are deterministic decoration.
    """

    ROOMS = {
        "core": (50, 50),
        "intelligence": (28, 27),
        "production": (72, 28),
        "quality": (72, 72),
        "knowledge": (30, 72),
        "output": (50, 88),
    }

    def __init__(self, path=None):
        self.path = path
        self.entities: list[WorldEntity] = []
        self.relations: list[WorldRelation] = []
        self.events: list[dict] = []
        self.generated_at = ""

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
        p = purpose.lower()
        if any(x in p for x in ("research", "signal", "markt", "scout")):
            return "intelligence"
        if any(x in p for x in ("prüf", "critic", "quality", "test")):
            return "quality"
        if any(x in p for x in ("write", "content", "design", "production")):
            return "production"
        return "core"

    @staticmethod
    def _agent_visual(agent_id: str, tasks: list[dict]) -> str:
        active = next((t for t in tasks if t.get("agent") == agent_id and t.get("status") == "active"), None)
        if not active:
            return "idle"
        cap = active.get("capability_id", "").lower()
        if "research" in cap or "observe" in cap:
            return "searching"
        if "test" in cap or "critic" in cap:
            return "reviewing"
        return "working"

    def project(self, agent) -> dict:
        tasks = agent.tasks.snapshot()
        agents = agent.agents.snapshot()
        projects = agent.projects.snapshot()
        capabilities = agent.capabilities.snapshot()
        evidence = agent.evidence.snapshot()
        orders = agent.orders.snapshot()
        messages = agent.messages.snapshot()
        offers = agent.commerce.snapshot().get("offers", [])
        entities: list[WorldEntity] = []
        relations: list[WorldRelation] = []

        def add(e: WorldEntity):
            entities.append(e)

        add(WorldEntity("core:genesis", "core", "GENESIS", room="core",
                        visual_state="running", x=50, y=50, size=2.2,
                        reason=agent.company.mission, created_at=""))

        for i, a in enumerate(agents):
            room = self._room(a.get("purpose", ""))
            x, y = self._pos(a["id"], room, i, len(agents))
            aid = f"agent:{a['id']}"
            add(WorldEntity(aid, "agent", a["name"], parent_id="core:genesis",
                            owner_id=a["id"], room=room,
                            visual_state=self._agent_visual(a["id"], tasks),
                            x=x, y=y, size=1.25, reason=a["purpose"],
                            created_at=a.get("created_at", "")))
            relations.append(WorldRelation(f"spawn:{a['id']}", f"agent:{a['parent_id']}",
                                            aid, "spawned", 1.5) if a.get("parent_id") else
                             WorldRelation(f"core:{a['id']}", "core:genesis", aid, "coordinates", 0.8))

        for i, t in enumerate(tasks):
            x, y = self._pos(t["id"], task_room if "task_room" in locals() else "production", i, max(1, len(tasks)))
            state = {"active": "working", "done": "complete", "blocked": "blocked",
                     "failed": "error", "verifying": "reviewing"}.get(t.get("status"), "queued")
            tid = f"task:{t['id']}"
            add(WorldEntity(tid, "task", t["title"], owner_id=t.get("agent", ""),
                            room="production", visual_state=state, x=x, y=y,
                            size=0.7, reason=t.get("result") or t.get("error", "")))
            if t.get("agent"):
                relations.append(WorldRelation(f"owns:{t['id']}", f"agent:{t['agent']}", tid, "carries", 1.0))
            if t.get("project_id"):
                relations.append(WorldRelation(f"contains:{t['id']}", f"project:{t['project_id']}", tid, "contains", 0.7))

        for p in projects:
            pid = f"project:{p['id']}"
            add(WorldEntity(pid, "project", p["title"], owner_id=p.get("owner_agent", ""),
                            room="production", visual_state="working" if p.get("status") == "active" else "idle",
                            x=72, y=28, size=1.0, reason=p.get("goal", "")))
        for c in capabilities:
            cid = f"cap:{c['id']}"
            add(WorldEntity(cid, "capability", c["name"], owner_id=c.get("owner_agent", ""),
                            room="intelligence", visual_state="working" if c.get("state") == "in_entwicklung" else "idle",
                            x=28, y=27, size=0.65, reason=c.get("description", "")))
        for o in offers:
            oid = f"offer:{o['id']}"
            add(WorldEntity(oid, "output", o.get("title", "Offer"), room="output",
                            visual_state="ready", x=50, y=88, size=0.9, reason=o.get("description", "")))
        for e in evidence[-80:]:
            eid = f"evidence:{e['id']}"
            add(WorldEntity(eid, "evidence", e["kind"], owner_id=e.get("subject_id", ""),
                            room="knowledge", visual_state=e.get("status", "observed"),
                            x=30, y=72, size=0.45, reason=e.get("summary", ""),
                            created_at=e.get("created_at", "")))
        for o in orders[-40:]:
            oid = f"order:{o['id']}"
            add(WorldEntity(oid, "order", o.get("title", "Order"), room="output",
                            visual_state=o.get("status", "queued"), x=50, y=88, size=0.5,
                            reason=o.get("result", "")))

        for m in messages[-120:]:
            if m.get("sender") and m.get("recipient"):
                relations.append(WorldRelation(
                    f"msg:{m.get('id', hashlib.sha1(str(m).encode()).hexdigest()[:10])}",
                    f"agent:{m['sender']}", f"agent:{m['recipient']}", "communicates",
                    min(5.0, 1.0 + len(m.get("content", "")) / 500)
                ))

        self.entities = entities
        self.relations = [r for r in relations if r.source != r.target]
        self.generated_at = datetime.now(timezone.utc).isoformat()
        self.events = [{
            "type": "projection",
            "timestamp": self.generated_at,
            "entities": len(self.entities),
            "relations": len(self.relations),
        }]
        return self.snapshot(agent)

    def sync(self, agent):
        return self.project(agent)

    def snapshot(self, agent=None) -> dict:
        counts = {}
        for e in self.entities:
            counts[e.type] = counts.get(e.type, 0) + 1
        return {
            "generated_at": self.generated_at,
            "entities": [asdict(e) for e in self.entities],
            "relations": [asdict(r) for r in self.relations],
            "events": self.events[-50:],
            "counts": counts,
            "rooms": [{"id": k, "x": v[0], "y": v[1]} for k, v in self.ROOMS.items()],
            "layers": {"physical": True, "neural": True, "economic": True},
        }
