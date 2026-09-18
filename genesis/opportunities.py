from dataclasses import dataclass

@dataclass(frozen=True)
class Opportunity:
    name: str
    channel: str
    startup_cost_eur: float
    expected_margin_eur: float
    time_hours: float
    confidence: float
    repeatability: float = 0.5

    def score(self) -> float:
        cost = max(self.startup_cost_eur, 0.01)
        time = max(self.time_hours, 0.25)
        return (self.expected_margin_eur * self.confidence * (0.5 + self.repeatability)) / (cost * time)

def rank(opportunities: list[Opportunity]) -> list[Opportunity]:
    return sorted(opportunities, key=lambda x: x.score(), reverse=True)
