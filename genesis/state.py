from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time

@dataclass
class Ledger:
    cash_eur: float = 0.0
    earned_eur: float = 0.0
    spent_eur: float = 0.0
    reserved_eur: float = 0.0
    compute_cost_eur: float = 0.0
    revenue_events: int = 0
    experiments: int = 0

    @property
    def net_cash(self) -> float:
        return self.cash_eur - self.reserved_eur

    @property
    def surplus(self) -> float:
        return self.earned_eur - self.spent_eur - self.reserved_eur

class StateStore:
    def __init__(self, path: str = "workspace/state.json"):
        self.path = Path(path)

    def load(self) -> Ledger:
        if not self.path.exists():
            return Ledger()
        return Ledger(**json.loads(self.path.read_text()))

    def save(self, ledger: Ledger) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(ledger), indent=2))

    def event(self, kind: str, data: dict) -> None:
        p = self.path.parent / "events.jsonl"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "kind": kind, "data": data}) + "\n")
