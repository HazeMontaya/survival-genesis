from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json, re

@dataclass
class Skill:
    id: str
    name: str
    purpose: str
    instructions: str
    version: int = 1
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""

class SkillRegistry:
    def __init__(self,path):
        self.path=Path(path); self.items=[]; self._load()
    def _load(self):
        if not self.path.exists(): return
        try:self.items=[Skill(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception:self.items=[]
    def _save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.path.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2,ensure_ascii=False),encoding="utf-8")
    def get(self,skill_id): return next((x for x in self.items if x.id==skill_id),None)
    def create(self,skill_id,name,purpose,instructions):
        if self.get(skill_id): return self.get(skill_id)
        now=datetime.now(timezone.utc).isoformat()
        safe=re.sub(r"[^a-zA-Z0-9_-]","_",skill_id)
        s=Skill(safe,name,purpose,instructions,1,"active",now,now)
        self.items.append(s); self._save(); return s
    def snapshot(self): return [asdict(x) for x in self.items[-300:]]
