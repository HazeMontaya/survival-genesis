from dataclasses import dataclass, asdict
@dataclass(frozen=True)
class Need:
    id:str; capability:str; reason:str; urgency:int; prerequisites:tuple[str,...]=(); resource:str=''; amount:float=0.0
class NeedEngine:
    def __init__(self,agent): self.agent=agent
    def detect(self):
        a=self.agent; caps={x['id']:x for x in a.capabilities.snapshot()}; active=lambda c:caps.get(c,{}).get('state')=='aktiv'; needs=[]
        if not a.memory.snapshot(): return [asdict(Need('observe','observe_environment','Es fehlen reale Zustands-/Evidenzdaten.',100))]
        if not active('goal_decomposition'): needs.append(Need('decompose','goal_decomposition','Die Mission wurde noch nicht in überprüfbare Arbeit zerlegt.',95))
        if not active('self_testing'): needs.append(Need('verify','self_testing','Der Runtime-Zustand braucht reproduzierbare Verifikation.',90))
        if len(a.agents.snapshot())==1 and active('goal_decomposition'): needs.append(Need('specialize','agent_creation','Spezialisierung fehlt; der Seed ist alleiniger Ausführer.',85,('decompose',)))
        if not a.commerce.snapshot()['offers']: needs.append(Need('offer','offer_creation','Es existiert noch kein überprüfbares lieferbares Angebot.',80,('decompose',)))
        offers=a.commerce.snapshot()['offers']
        if offers and not any(x.get('published_url') for x in offers): needs.append(Need('distribution','external_publishing','Ein Angebot existiert, aber keine belegte externe Distribution.',75,('offer',)))
        return [asdict(x) for x in sorted(needs,key=lambda n:(-n.urgency,n.id))]
