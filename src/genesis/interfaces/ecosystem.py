from datetime import datetime, timezone

def ecosystem_snapshot(agent):
    state = agent.snapshot()
    world = state["world"]
    return {
        "schema": "agent-world/1",
        "clock": datetime.now(timezone.utc).isoformat(),
        "mission": state["company"]["mission"],
        "survival": {
            "mode": state["mode"],
            "cash_eur": state["ledger"]["cash_eur"],
            "reserved_eur": state["ledger"]["reserved_eur"],
            "compute_cost_eur": state["ledger"]["compute_cost_eur"],
        },
        "world": world,
        "agents": state["agents"],
        "tasks": state["tasks"],
        "projects": state["projects"],
        "workflows": state["workflows"],
        "capabilities": state["capabilities"],
        "memory": state["memory"],
        "evidence": state["evidence"],
        "commerce": state["commerce"],
        "orders": state["orders"],
        "treasury": state["treasury"],
        "resources": state["resources"],
        "runtime": state["runtime"],
        "events": agent.runtime_db.recent_events(120),
        "top_opportunities": state["top_opportunities"],
    }
