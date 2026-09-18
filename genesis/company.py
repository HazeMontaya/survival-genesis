from dataclasses import dataclass, asdict

@dataclass
class CompanyProfile:
    name: str = "SURVIVAL GENESIS"
    product: str = ""
    mission: str = "Verstehe dein Ziel, sichere deine Existenz und baue selbstständig alles auf, was zur Erreichung des Ziels benötigt wird."
    operating_principle: str = "Wahrnehmen → Verstehen → Entscheiden → Bauen → Prüfen → Lernen → Weiterbauen"
    stage: str = "GENESIS"
    external_execution: str = "GESPERRT BIS KONFIGURIERT"

    def snapshot(self):
        return asdict(self)
