from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from pathlib import Path
import json,uuid

STAGE_STATES={"queued","active","done","failed","blocked"}

@dataclass
class WorkflowStage:
 id:str
 name:str
 kind:str
 task_id:str=""
 status:str="queued"
 agent_id:str=""
 evidence:dict=field(default_factory=dict)
 created_at:str=""
 updated_at:str=""

@dataclass
class Workflow:
 id:str
 title:str
 goal:str
 project_id:str=""
 status:str="queued"
 stages:list[dict]=field(default_factory=list)
 created_at:str=""
 updated_at:str=""

class WorkflowEngine:
 """Production-line projection: existing tasks become an observable input→work→verify→output chain."""
 def __init__(self,path):
  self.path=Path(path);self.items=[];self._load()
 def _load(self):
  if not self.path.exists(): return
  try:self.items=[Workflow(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
  except Exception:self.items=[]
 def _save(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  self.path.write_text(json.dumps([asdict(x) for x in self.items[-300:]],indent=2,ensure_ascii=False),encoding="utf-8")
 def get(self,workflow_id):
  return next((x for x in self.items if x.id==workflow_id),None)
 def for_project(self,project_id):
  return next((x for x in self.items if x.project_id==project_id),None)
 def ensure_for_project(self,project,task_snapshot):
  existing=self.for_project(project.id)
  tasks={x["id"]:x for x in task_snapshot}
  ordered=[tasks[i] for i in project.task_ids if i in tasks]
  if not ordered:return existing
  now=datetime.now(timezone.utc).isoformat()
  if existing is None:
   existing=Workflow(uuid.uuid4().hex[:10],project.title,project.goal,project.id,"queued",[],now,now)
   self.items.append(existing)
  known={x["task_id"]:x for x in existing.stages}
  for t in ordered:
   if t["id"] in known:continue
   existing.stages.append(asdict(WorkflowStage(
    uuid.uuid4().hex[:10],t["title"],t.get("capability_id","work"),t["id"],
    self._stage_state(t),t.get("agent",""),{"items":t.get("evidence",[])},
    now,now)))
  self._sync_workflow(existing,tasks)
  self._save()
  return existing
 def _stage_state(self,t):
  return {"queued":"queued","active":"active","done":"done","failed":"failed","blocked":"blocked"}.get(t.get("status"),"queued")
 def _sync_workflow(self,w,tasks):
  now=datetime.now(timezone.utc).isoformat()
  for s in w.stages:
   t=tasks.get(s["task_id"])
   if not t:continue
   s["status"]=self._stage_state(t);s["agent_id"]=t.get("agent","");s["evidence"]={"items":t.get("evidence",[])};s["updated_at"]=now
  states=[s["status"] for s in w.stages]
  if states and all(x=="done" for x in states):w.status="done"
  elif any(x=="failed" for x in states):w.status="failed"
  elif any(x=="active" for x in states):w.status="active"
  elif any(x=="blocked" for x in states):w.status="blocked"
  else:w.status="queued"
  w.updated_at=now
 def sync(self,projects,tasks):
  for p in projects:
   self.ensure_for_project(p,tasks)
  return self.snapshot()
 def snapshot(self):
  return [asdict(x) for x in self.items[-300:]]
