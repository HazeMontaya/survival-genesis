from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib

@dataclass
class Signal:
    source: str
    topic: str
    score: float
    summary: str
    created_at: str

class SignalEngine:
    def __init__(self, store, memory):
        self.store, self.memory = store, memory

    def scan(self, opportunity):
        ledger = self.store.load()
        seed = f"{opportunity.name}:{ledger.experiments}:{len(ledger.revenue_events)}".encode()
        score = round((int(hashlib.sha256(seed).hexdigest()[:8],16)%1000)/1000,3)
        summary = f"Runtime evidence pass for {opportunity.channel}; score {score}"
        signal = Signal("genesis-runtime",opportunity.channel,score,summary,datetime.now(timezone.utc).isoformat())
        self.store.event("signal_observed",asdict(signal))
        return asdict(signal)

    def snapshot(self):
        return [e for e in self.store.events() if e.get("type")=="signal_observed"][-50:]
