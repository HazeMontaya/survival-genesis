from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.parse import quote
import os, re, xml.etree.ElementTree as ET

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

    def _feeds(self, opportunity):
        configured = [x.strip() for x in os.getenv("GENESIS_SIGNAL_URLS","").split(",") if x.strip()]
        if configured:
            return configured
        q = quote(opportunity.channel)
        return [f"https://hnrss.org/newest?q={q}"]

    def _fetch(self, url):
        req = Request(url, headers={"User-Agent":"SurvivalGenesis/0.2"})
        with urlopen(req, timeout=8) as r:
            return r.read(512000)

    def scan(self, opportunity):
        hits, errors = [], []
        for url in self._feeds(opportunity)[:5]:
            try:
                raw = self._fetch(url)
                root = ET.fromstring(raw)
                texts = [re.sub(r"\s+", " ", (x.text or "")).strip() for x in root.iter() if x.text]
                joined = " ".join(texts)
                hits.append({"source":url, "items":max(0, joined.lower().count(opportunity.channel.lower()))})
            except Exception as exc:
                errors.append(f"{url}: {exc}")

        if hits:
            total = sum(x["items"] for x in hits)
            score = round(min(1.0, total / 10), 3)
            summary = f"{len(hits)} Live-Quelle(n) abgerufen; {total} passende Signalnennungen"
            source = ",".join(x["source"] for x in hits)
        else:
            score = 0.0
            summary = "Keine externe Signalquelle erreichbar; Ausführung bleibt nachweisgebunden"
            source = "nicht_verfügbar"

        signal = Signal(source, opportunity.channel, score, summary, datetime.now(timezone.utc).isoformat())
        self.store.event("signal_beobachtet", asdict(signal))
        if errors:
            self.store.event("signal_fehler", {"fehler": errors})
        return asdict(signal)

    def snapshot(self):
        return [e for e in self.store.events() if e.get("type") == "signal_beobachtet"][-50:]
