from dataclasses import asdict,dataclass
from datetime import datetime,timezone
from pathlib import Path
import json,uuid,math
@dataclass
class Entity:id:str;type:str;name:str;state:str="active";owner_id:str="";reason:str="";created_at:str="";room:str="core";activity:str="idle";x:float=0;y:float=0;size:float=1;metadata:dict=field(default_factory=dict)
@dataclass
class Relation:id:str;source:str;target:str;kind:str;created_at:str="";intensity:float=1.0;layer:str="neural";metadata:dict=field(default_factory=dict)
class WorldModel:
 def __init__(self,path):self.path=Path(path);self.entities=[];self.relations=[];self._load()
 def _load(self):
  if self.path.exists():
   try:r=json.loads(self.path.read_text());self.entities=[Entity(**{**x,"room":x.get("room","core"),"activity":x.get("activity","idle"),"x":x.get("x",0),"y":x.get("y",0),"size":x.get("size",1),"metadata":x.get("metadata",{})}) for x in r.get("entities",[])];self.relations=[Relation(**{**x,"intensity":x.get("intensity",1),"layer":x.get("layer","neural"),"metadata":x.get("metadata",{})}) for x in r.get("relations",[])]
   except Exception:pass
 def _save(self):self.path.parent.mkdir(parents=True,exist_ok=True);self.path.write_text(json.dumps({"entities":[asdict(x) for x in self.entities[-2000:]],"relations":[asdict(x) for x in self.relations[-4000:]]},indent=2,ensure_ascii=False))
 def ensure(self,i,t,n,owner_id="",reason="",state="active",room="core",activity="idle",metadata=None):
  x=next((e for e in self.entities if e.id==i),None)
  if not x:self.entities.append(Entity(i,t,n,state,owner_id,reason,datetime.now(timezone.utc).isoformat(),room,activity,0,0,1,metadata or {}))
  else:x.name=n;x.state=state;x.owner_id=owner_id;x.reason=reason;x.room=room;x.activity=activity;x.metadata.update(metadata or {})
 def relate(self,s,t,k,layer="neural",intensity=1.0,metadata=None):
  x=next((r for r in self.relations if r.source==s and r.target==t and r.kind==k),None)
  if x:x.intensity=float(intensity);x.layer=layer;x.metadata.update(metadata or {})
  else:self.relations.append(Relation(uuid.uuid4().hex[:10],s,t,k,datetime.now(timezone.utc).isoformat(),float(intensity),layer,metadata or {}))
 def sync(self,a):
  self.ensure("genesis-core","core","GENESIS")
  for x in a.agents.snapshot():self.ensure("agent:"+x["id"],"agent",x["name"],x["id"],x["purpose"]);self.relate("genesis-core","agent:"+x["id"],"contains")
  for x in a.capabilities.snapshot():self.ensure("cap:"+x["id"],"capability",x["name"],x.get("owner_agent",""),x["description"])
  for x in a.projects.snapshot():self.ensure("project:"+x["id"],"project",x["title"],x.get("owner_agent",""),x["goal"])
  for x in a.tasks.snapshot():self.ensure("task:"+x["id"],"task",x["title"],x.get("agent",""),x.get("error",""))
  for w in a.workflows.snapshot():
   self.ensure("workflow:"+w["id"],"workflow",w["title"],reason=w.get("goal",""))
   self.relate("genesis-core","workflow:"+w["id"],"production_line")
   for s in w.get("stages",[]):
    sid="stage:"+s["id"];self.ensure(sid,"stage",s["name"],s.get("agent_id",""),s.get("status",""))
    self.relate("workflow:"+w["id"],sid,"contains_stage")
    if s.get("task_id"):self.relate(sid,"task:"+s["task_id"],"executes")
  for x in a.evidence.snapshot():self.ensure("evidence:"+x["id"],"evidence",x["claim"][:48],x.get("subject",""),x.get("source",""),"verified" if x.get("verified") else "unverified","quality","complete" if x.get("verified") else "reviewing",{"verifier":x.get("verifier",""),"confidence":x.get("confidence",0)})
  for x in a.messages.snapshot():self.ensure("message:"+x["id"],"message",x["content"][:48],x["sender"],x["content"],"delivered" if x.get("delivered") else "unread","intelligence","collaborating",{"kind":x.get("kind","task")});self.relate("agent:"+x["sender"],"agent:"+x["recipient"],"communicates","neural",1,{"message_id":x["id"]})
  ledger=a.store.load();self.ensure("economy:cash","economy","CASH",state="active",room="economy",metadata={"cash_eur":ledger.cash_eur,"earned_eur":ledger.earned_eur,"spent_eur":ledger.spent_eur,"reserved_eur":ledger.reserved_eur,"net_cash":ledger.net_cash});self.ensure("economy:reserve","reserve","RESERVE",state="active",room="economy",metadata={"reserved_eur":ledger.reserved_eur})
  for x in a.commerce.snapshot()["offers"]:self.ensure("order:"+x["id"],"order","OFFER · "+x["name"],state=x.get("status","entwurf"),room="output",metadata={"price_eur":x.get("price_eur",0),"channel":x.get("channel","")})
  for x in a.artifacts.snapshot():self.ensure("artifact:"+x["id"],"artifact",x["title"],reason=x.get("status",""))
  for x in a.skills.snapshot():self.ensure("skill:"+x["id"],"skill",x["name"],reason=x["purpose"])
  for x in a.tools.snapshot():self.ensure("tool:"+x["id"],"tool",x["id"],reason=x["description"])
  self._place();self._save();return self.snapshot()
 def _place(self):
  rooms={"core":(0,0),"intelligence":(-430,-190),"production":(330,-210),"quality":(-250,270),"knowledge":(250,300),"output":(690,30),"economy":(690,300)};b={}
  for e in self.entities:
   if e.id=="genesis-core":e.x,e.y=0,0;continue
   b.setdefault(e.room,[]).append(e)
  for room,items in b.items():
   cx,cy=rooms.get(room,(0,0));n=len(items)
   for i,e in enumerate(items):
    if e.type=="agent":e.x=cx+(i-(n-1)/2)*78;e.y=cy
    else:a=2*math.pi*i/max(1,n);e.x=cx+math.cos(a)*105;e.y=cy+math.sin(a)*65
 def snapshot(self):return {"entities":[asdict(x) for x in self.entities[-1500:]],"relations":[asdict(x) for x in self.relations[-3000:]],"counts":{"entities":len(self.entities),"relations":len(self.relations),"agents":sum(x.type=="agent" for x in self.entities),"capabilities":sum(x.type=="capability" for x in self.entities),"projects":sum(x.type=="project" for x in self.entities),"tasks":sum(x.type=="task" for x in self.entities),"workflows":sum(x.type=="workflow" for x in self.entities) ,"stages":sum(x.type=="stage" for x in self.entities),"evidence":sum(x.type=="evidence" for x in self.entities),"messages":sum(x.type=="message" for x in self.entities),"orders":sum(x.type=="order" for x in self.entities),"economy":sum(x.type=="economy" for x in self.entities)}}
