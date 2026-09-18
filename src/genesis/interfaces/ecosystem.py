from datetime import datetime, timezone

def ecosystem_snapshot(agent):
    ledger=agent.store.load()
    tasks=agent.tasks.snapshot()
    agents=agent.agents.snapshot()
    active={t["agent"]:t for t in tasks if t["status"]=="active"}
    return {
        "company":agent.company.snapshot(),
        "agents":[{
            **a,
            "status":"arbeitet" if a["id"] in active else a["state"],
            "task":active[a["id"]]["title"] if a["id"] in active else "keine aktive Aufgabe"
        } for a in agents],
        "rooms":[],
        "tasks":tasks,
        "memory":agent.memory.snapshot(),
        "clock":datetime.now(timezone.utc).isoformat(),
        "ledger":ledger.__dict__,
        "capabilities":agent.capabilities.snapshot(),
        "projects":agent.projects.snapshot(),
        "world":agent.world.snapshot(agent),
    }
