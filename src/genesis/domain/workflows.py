from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

STAGE_STATES = ("queued", "active", "blocked", "done", "failed")

@dataclass
class WorkflowStage:
    id: str
    name: str
    kind: str
    task_id: str = ""
    status: str = "queued"
    agent_id: str = ""
    evidence: list[dict] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

@dataclass
class Workflow:
    id: str
    title: str
    goal: str
    project_id: str = ""
    status: str = "queued"
    stages: list[WorkflowStage] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

class WorkflowEngine:
    """Persistent execution graph derived from projects/tasks, never invented by the UI."""
    def __init__(self, path="workspace/workflows.json"):
        self.path = Path(path)
        self.items: list[Workflow] = []
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.items = []
            for item in raw:
                stages = [WorkflowStage(**{**{"task_id":"","status":"queued","agent_id":"","evidence":[],"created_at":"","updated_at":""}, **s}) for s in item.get("stages", [])]
                self.items.append(Workflow(**{**item, "stages": stages}))
        except (OSError, json.JSONDecodeError, TypeError):
            self.items = []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]], indent=2, ensure_ascii=False), encoding="utf-8")

    def get(self, workflow_id):
        return next((x for x in self.items if x.id == workflow_id), None)

    def for_project(self, project_id):
        return next((x for x in self.items if x.project_id == project_id and x.status not in ("done", "failed")), None)

    def ensure_for_project(self, project, tasks):
        workflow = self.for_project(project.id)
        if workflow:
            return self.sync(workflow.id, tasks)
        now = datetime.now(timezone.utc).isoformat()
        workflow = Workflow(uuid.uuid4().hex[:10], project.title, project.goal, project.id, "queued", [], now, now)
        self.items.append(workflow)
        self._save()
        return self.sync(workflow.id, tasks)

    def sync(self, workflow_id, tasks):
        workflow = self.get(workflow_id)
        if not workflow:
            raise KeyError(workflow_id)
        now = datetime.now(timezone.utc).isoformat()
        by_task = {t["id"]: t for t in tasks}
        for task_id in [*workflow_task_ids(workflow)]:
            if task_id not in by_task:
                continue
        existing = {s.task_id: s for s in workflow.stages if s.task_id}
        ordered = [t for t in tasks if t.get("project_id") == workflow.project_id]
        for task in ordered:
            stage = existing.get(task["id"])
            status = task.get("status", "queued")
            if stage is None:
                stage = WorkflowStage(uuid.uuid4().hex[:10], task.get("title","Task"), task.get("capability_id","task"), task["id"], status, task.get("agent",""), task.get("evidence",[]), task.get("created_at",""), now)
                workflow.stages.append(stage)
            else:
                stage.name = task.get("title", stage.name)
                stage.kind = task.get("capability_id", stage.kind)
                stage.status = status if status in STAGE_STATES else "queued"
                stage.agent_id = task.get("agent","")
                stage.evidence = task.get("evidence", [])
                stage.updated_at = now
        statuses = [s.status for s in workflow.stages]
        if not statuses:
            workflow.status = "queued"
        elif any(s == "failed" for s in statuses):
            workflow.status = "failed"
        elif all(s == "done" for s in statuses):
            workflow.status = "done"
        elif any(s == "active" for s in statuses):
            workflow.status = "active"
        elif any(s == "blocked" for s in statuses):
            workflow.status = "blocked"
        else:
            workflow.status = "queued"
        workflow.updated_at = now
        self._save()
        return workflow

    def snapshot(self):
        return [asdict(x) for x in self.items[-300:]]

def workflow_task_ids(workflow):
    return [stage.task_id for stage in workflow.stages if stage.task_id]
