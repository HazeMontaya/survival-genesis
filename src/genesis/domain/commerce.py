from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json, uuid

@dataclass
class Offer:
    id: str
    name: str
    channel: str
    price_eur: float
    status: str
    artifact_id: str
    created_at: str
    published_url: str = ""

class CommerceEngine:
    def __init__(self, store, artifacts, memory):
        self.store, self.artifacts, self.memory = store, artifacts, memory
        self.path = store.path.parent / "commerce.json"
        self.offers = self._load("offers")
        self.leads = self._load("leads")
        self.assets = self._load("assets")

    def _load(self, key):
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8")).get(key, [])
        except Exception:
            return []

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "offers": self.offers[-500:],
            "leads": self.leads[-1000:],
            "assets": self.assets[-500:]
        }, indent=2, ensure_ascii=False), encoding="utf-8")

    def create_offer(self, opportunity):
        now = datetime.now(timezone.utc).isoformat()
        body = f"""# {opportunity.name.replace("_"," ").title()}

## Angebot
Ein klar abgegrenztes {opportunity.channel}-Angebot.

## Zielkunde
Zielkunden und konkretes Problem müssen vor einer Veröffentlichung belegt werden.

## Leistung
Das kleinstmögliche nützliche Ergebnis, das ohne kostenpflichtige Infrastruktur geliefert werden kann.

## Zielwert
€{opportunity.expected_margin_eur:.2f}

## Erfüllung
Lokale/manuelle Erfüllung ist möglich. Automatisierte Erfüllung benötigt einen eingerichteten Anschluss.

## Integrität
Keine erfundenen Kunden, Bewertungen, Umsätze, Konten, Zugangsdaten oder Transaktionen.
"""
        artifact = self.artifacts.create_markdown(
            opportunity.name.replace("_", " ") + " Angebot", body, "angebot"
        )
        offer = asdict(Offer(
            uuid.uuid4().hex[:10],
            opportunity.name.replace("_", " ").title(),
            opportunity.channel,
            float(opportunity.expected_margin_eur),
            "entwurf",
            artifact.id,
            now
        ))
        self.offers.append(offer)
        self._save()
        self.store.event("angebot_erstellt", offer)
        return offer

    def create_distribution_asset(self, opportunity):
        asset = {
            "id": uuid.uuid4().hex[:10],
            "type": "vertriebsinhalt",
            "opportunity": opportunity.name,
            "content": f"Problembasiertes Angebot: {opportunity.name.replace('_',' ')}. Für Umfang und Lieferdetails anfragen.",
            "status": "bereit",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.assets.append(asset)
        self._save()
        self.store.event("vertriebsinhalt_bereit", asset)
        return asset

    def create_lead_queue(self, opportunity):
        lead = {
            "id": uuid.uuid4().hex[:10],
            "source": opportunity.channel,
            "status": "unbearbeitet",
            "next_action": "Einwilligungsbasierten oder eingehenden Interessenten erfassen",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        self.leads.append(lead)
        self._save()
        self.store.event("interessenten_warteschlange_bereit", lead)
        return lead

    def snapshot(self):
        return {"offers": self.offers[-100:], "leads": self.leads[-100:], "assets": self.assets[-100:]}
