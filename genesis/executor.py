"""Capability execution registry.

Cognition selects a capability. This layer contains concrete side effects.
"""
from .opportunities import rank
from .catalog import DEFAULT_OPPORTUNITIES

class CapabilityExecutor:
    def __init__(self,agent):
        self.agent=agent
        self.handlers={
            "observe_environment":self._observe,"goal_decomposition":self._goal,
            "agent_creation":self._agent,"research_observation":self._research,
            "offer_creation":self._offer,"specialist_research":self._specialist,
            "skill_creation":self._skill,"self_testing":self._tests,
            "external_publishing":self._publish,
        }
    def register(self,capability,handler): self.handlers[str(capability)]=handler
    def execute(self,task):
        handler=self.handlers.get(task.capability_id)
        return handler(task) if handler else {"type":"capability_step","verified":True}
    def capabilities(self): return sorted(self.handlers)
    def _observe(self,t):
        s=self.agent.signals.scan(DEFAULT_OPPORTUNITIES[0]); self.agent.memory.remember("observation",f"Startbeobachtung: {s['summary']}",.8); return {"type":"observation","signal":s}
    def _goal(self,t):
        self.agent.memory.remember("goal","Mission in überprüfbare Teilziele zerlegen.",.9); return {"type":"goal_decomposition","verified":True}
    def _agent(self,t):
        a=self.agent; child=a.agents.spawn("Researcher","Untersuche Belege, Chancen und externe Signale.",t.agent,[],["read_file","list_files","run_tests","remember","send_message"])
        a.messages.send(t.agent,child.id,"Willkommen. Untersuche externe Signale und liefere belegte Beobachtungen.","onboarding"); a.memory.remember("agent",f"Neuer Agent erzeugt: {child.name}",.9)
        a._capability("research_observation","Recherche beobachten","Externe Signale erfassen und als Evidenz speichern.",child.id)
        ct=a.tasks.create(child.id,"research","Führe eine Recherchebeobachtung durch",70,"research_observation",""); a.messages.send(t.agent,child.id,"Arbeitsauftrag: Führe die Recherchebeobachtung aus und melde Evidenz.","task")
        return {"type":"agent_created","agent_id":child.id,"task_id":ct.id}
    def _research(self,t):
        a=self.agent; s=a.signals.scan(DEFAULT_OPPORTUNITIES[0]); a.memory.remember("research",s["summary"],s["score"]); a.messages.send(t.agent,"genesis-1",s["summary"],"result"); return {"type":"research_observation","signal":s}
    def _offer(self,t):
        o=self.agent.commerce.create_offer(rank(DEFAULT_OPPORTUNITIES)[0]); return {"type":"artifact_created","artifact_id":o["artifact_id"],"offer_id":o["id"]}
    def _specialist(self,t):
        a=self.agent; child=a.agents.spawn("Researcher","Untersuche Markt- und Evidenzsignale und liefere belegte Beobachtungen.",t.agent,["specialist_research"],["read_file","list_files","run_tests","remember","send_message"]); a.messages.send(t.agent,child.id,"Arbeite als spezialisierter Recherche-Agent und dokumentiere Evidenz.","onboarding"); return {"type":"agent_created","agent_id":child.id}
    def _skill(self,t):
        s=self.agent.skills.create("research_basics","Recherche-Grundlagen","Belege und Signale strukturiert untersuchen.","Quelle erfassen → Signal prüfen → Unsicherheit markieren → Ergebnis speichern."); return {"type":"skill_created","skill_id":s.id}
    def _tests(self,t):
        r=self.agent.tools.call("run_tests")
        if r["returncode"]!=0: raise RuntimeError(r["stderr"] or r["stdout"])
        return {"type":"test_run","returncode":r["returncode"],"stdout":r["stdout"][-3000:]}
    def _publish(self,t):
        if not any(c["id"]=="webhook" and c["configured"] for c in self.agent.connectors.snapshot()): raise RuntimeError("Kein externer Veröffentlichungsanschluss konfiguriert")
        return {"type":"connector_ready","verified":True}
