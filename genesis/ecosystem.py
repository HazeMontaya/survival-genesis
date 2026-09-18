from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Room:
    id: str
    name: str
    subtitle: str
    color: str
    status: str = "online"
    load: int = 0

ROOMS = [
    Room("command","Genesis-Zentrale","Strategie · Gedächtnis · Steuerung","violet"),
    Room("research","Forschungslabor","Signale · Belege · Chancen","cyan"),
    Room("forge","Produktwerkstatt","Produkte · Angebote · Vermögenswerte","orange"),
    Room("growth","Wachstumsstudio","Inhalte · Vertrieb · Verteilung","pink"),
    Room("sales","Umsatzzentrale","Interessenten · Abschluss","green"),
    Room("treasury","Finanzkasse","Buchhaltung · Rücklagen · Reinvestition","gold"),
    Room("operations","Betrieb","Erfüllung · Qualität · Automatisierung","blue"),
    Room("evolution","Entwicklungslabor","Experimente · Lernen · Ausbau","purple"),
]

AGENT_DEFS = [
    ("ceo","Genesis","Geschäftsleitung","command"),
    ("scout","Scout","Marktaufklärung","research"),
    ("analyst","Atlas","Chancenanalyse","research"),
    ("maker","Forge","Produktentwicklung","forge"),
    ("writer","Muse","Inhalt und Marke","growth"),
    ("seller","Closer","Vertrieb","sales"),
    ("ledger","Ledger","Finanzsteuerung","treasury"),
    ("operator","Ops","Betrieb und Erfüllung","operations"),
    ("evolver","Evo","Experimententwicklung","evolution"),
]

def ecosystem_snapshot(agent):
    ledger = agent.store.load()
    tasks = agent.tasks.snapshot()
    active = {t["agent"]: t for t in tasks if t["status"] == "active"}
    rooms = []
    for r in ROOMS:
        queued = [t for t in tasks if t["room"] == r.id and t["status"] in ("queued","active")]
        rooms.append({
            **asdict(r),
            "load": len(queued),
            "queued": sum(t["status"] == "queued" for t in queued),
            "active": sum(t["status"] == "active" for t in queued),
        })
    agents = []
    for aid, name, role, room in AGENT_DEFS:
        task = active.get(aid)
        agents.append({
            "id": aid, "name": name, "role": role, "room": room,
            "status": "arbeitet" if task else "bereit",
            "task": task["title"] if task else "Keine aktive Aufgabe",
            "energy": 100,
        })
    return {
        "company": agent.company.snapshot(),
        "rooms": rooms,
        "agents": agents,
        "tasks": tasks,
        "memory": agent.memory.snapshot(),
        "clock": datetime.now(timezone.utc).isoformat(),
        "ledger": ledger.__dict__,
        "world": agent.world.snapshot(agent),
    }
