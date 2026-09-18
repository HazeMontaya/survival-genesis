from datetime import datetime,timezone
def snapshot(agent):
 active={x["agent"]:x for x in agent.tasks.snapshot() if x["status"]=="active"}
 return {"company":agent.company.snapshot(),"clock":datetime.now(timezone.utc).isoformat(),"agents":[{**x,"status":"arbeitet" if x["id"] in active else x["state"],"task":active[x["id"]]["title"] if x["id"] in active else "keine aktive Aufgabe"} for x in agent.agents.snapshot()],"tasks":agent.tasks.snapshot(),"memory":agent.memory.snapshot(),"ledger":agent.store.load().__dict__,"capabilities":agent.capabilities.snapshot(),"projects":agent.projects.snapshot(),"world":agent.world.snapshot()}
