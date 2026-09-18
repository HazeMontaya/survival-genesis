from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json, re, uuid

@dataclass
class Artifact:
    id: str
    kind: str
    title: str
    path: str
    status: str = "draft"
    created_at: str = ""
    updated_at: str = ""

class ArtifactStore:
    def __init__(self, root="workspace/artifacts"):
        self.root=Path(root); self.index=self.root/"index.json"; self.items=[]; self._load()
    def _load(self):
        if self.index.exists(): self.items=[Artifact(**x) for x in json.loads(self.index.read_text())]
    def _save(self):
        self.root.mkdir(parents=True,exist_ok=True)
        self.index.write_text(json.dumps([asdict(x) for x in self.items[-500:]],indent=2))
    def create_markdown(self,title,body,kind="product"):
        slug=re.sub(r"[^a-z0-9]+","-",title.lower()).strip("-")[:60] or uuid.uuid4().hex[:8]
        now=datetime.now(timezone.utc).isoformat(); p=self.root/f"{slug}.md"
        self.root.mkdir(parents=True,exist_ok=True)
        p.write_text(body,encoding="utf-8")
        a=Artifact(uuid.uuid4().hex[:10],kind,title,str(p),"ready",now,now)
        self.items.append(a); self._save(); return a
    def snapshot(self): return [asdict(x) for x in self.items[-100:]]
