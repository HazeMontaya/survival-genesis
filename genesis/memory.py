from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Memory:
    kind: str
    content: str
    confidence: float = 1.0
    created_at: str = ""

class MemoryGraph:
    def __init__(self):
        self.items=[]

    def remember(self, kind, content, confidence=1.0):
        m=Memory(kind,content,confidence,datetime.now(timezone.utc).isoformat())
        self.items.append(m)
        return m

    def snapshot(self):
        return [asdict(x) for x in self.items[-200:]]
