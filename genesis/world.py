from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, uuid

@dataclass
class WorldNode:
    id: str
    kind: str
    name: str
    room: str
    status: str = "aktiv"
    reason: str = ""
    created_at: str = ""

class WorldModel:
    """Persistent topology of the company. The topology is derived from real runtime state
    and grows only when a concrete capability or workflow gap is detected."""
    def __init__(self, path):
        self.path = Path(path)
        self.nodes = []
        self.events = []
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.nodes = [WorldNode(**x) for x in raw.get("nodes", [])]
            self.events = raw.get("events", [])
        except Exception:
            self.nodes, self.events = [], []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "nodes": [asdict(x) for x in self.nodes[-500:]],
            "events": self.events[-500:],
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    def has(self, node_id):
        return any(n.id == node_id for n in self.nodes)

    def ensure(self, node_id, kind, name, room, reason):
        if self.has(node_id):
            return None
        now = datetime.now(timezone.utc).isoformat()
        node = WorldNode(node_id, kind, name, room, "aktiv", reason, now)
        self.nodes.append(node)
        event = {"id": uuid.uuid4().hex[:10], "type": "welt_erweitert",
                 "node": asdict(node), "timestamp": now}
        self.events.append(event)
        self._save()
        return node

    def assess(self, agent):
        """Inspect actual state and return concrete missing capabilities."""
        gaps = []
        connectors = agent.connectors.snapshot()
        configured = {c["id"]: c for c in connectors}
        offers = agent.commerce.snapshot()["offers"]
        leads = agent.commerce.snapshot()["leads"]
        ledger = agent.store.load()
        tasks = agent.tasks.snapshot()

        if not offers:
            gaps.append(("cap_offer_factory", "Fähigkeit: Angebotsfabrik", "forge",
                         "Es existiert noch kein Angebot."))
        if offers and not any(x.get("published_url") for x in offers):
            gaps.append(("cap_publishing", "Fähigkeit: Veröffentlichungsweg", "growth",
                         "Angebote existieren lokal, aber kein bestätigter Veröffentlichungsanschluss."))
        if not leads:
            gaps.append(("cap_inbound_leads", "Fähigkeit: Interessenten-Eingang", "sales",
                         "Es wurde noch kein eingehender Interessentenfluss erfasst."))
        if not configured.get("revenue_webhook", {}).get("configured"):
            gaps.append(("cap_verified_revenue", "Fähigkeit: Verifizierter Zahlungseingang", "treasury",
                         "Kein authentifizierter Umsatzanschluss ist konfiguriert."))
        if not any(t["agent"] == "operator" for t in tasks):
            gaps.append(("cap_fulfillment", "Fähigkeit: Auftragserfüllung", "operations",
                         "Kein Betriebsauftrag ist im Task-System vorhanden."))
        if not any(t["agent"] == "evolver" for t in tasks):
            gaps.append(("cap_learning", "Fähigkeit: Lernschleife", "evolution",
                         "Kein Entwicklungsauftrag ist im Task-System vorhanden."))
        if ledger.earned_eur > 0 and ledger.experiments > 0:
            gaps.append(("cap_unit_economics", "Fähigkeit: Wirtschaftsauswertung", "treasury",
                         "Verifizierter Umsatz erfordert laufende Margen- und Wiederholungsanalyse."))
        return gaps

    def grow_from_gaps(self, agent):
        created = []
        for node_id, name, room, reason in self.assess(agent):
            node = self.ensure(node_id, "faehigkeit", name, room, reason)
            if node:
                created.append(asdict(node))
                agent.store.event("faehigkeit_entdeckt", {
                    "node_id": node_id, "name": name, "room": room, "reason": reason
                })
        return created

    def snapshot(self, agent):
        gaps = self.assess(agent)
        return {
            "nodes": [asdict(x) for x in self.nodes[-300:]],
            "growth_events": self.events[-100:],
            "gaps": [{"id": x[0], "name": x[1], "room": x[2], "reason": x[3]} for x in gaps],
            "counts": {
                "nodes": len(self.nodes),
                "capabilities": sum(x.kind == "faehigkeit" for x in self.nodes),
                "growth_events": len(self.events),
            },
        }
