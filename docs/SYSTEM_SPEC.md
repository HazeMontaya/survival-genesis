# Survival Genesis — System Specification

## 1. Zweck

Survival Genesis ist ein autonomer, zustandsgetriebener Agenten-/Unternehmensruntime.

Mission:

> Verstehe dein Ziel, sichere deine Existenz und baue selbstständig alles auf, was zur Erreichung des Ziels benötigt wird.

Leitprozess:

**Wahrnehmen → Verstehen → Entscheiden → Bauen → Prüfen → Lernen → Weiterbauen**

Der Startzustand ist absichtlich extrem klein: ein Genesis-Seed, keine künstlichen Einnahmen, keine vorausgesetzten API-Tokens, kein vorausgesetztes Kapital und keine automatisch aktivierten Finanzoperationen.

## 2. Source of Truth

GitHub `main` ist die kanonische Quelle. Lokale Checkouts sind Downstream-Kopien.

Erlaubter Synchronisationsfluss:

**GitHub main → lokale Kopie → lokaler Runtime-Betrieb**

Lokale Runtime-Daten gehören nicht in Git.

## 3. Weltmodell

Die Weboberfläche ist eine SVG-Projektion des tatsächlichen Systemzustands, kein separates Dashboard.

Die Welt soll dynamisch wachsen mit:

- Genesis und Tochteragenten
- Fähigkeiten
- Aufgaben und Projekte
- Memory und Soul
- Skills
- Opportunities
- Offers
- Orders
- Evidence
- Ressourcen
- Treasury
- Zahlungen
- Risiken
- externe Anschlüsse
- später Positionen/Trading-Zustände

Die UI darf keine erfundenen Zustände erzeugen. Sie projiziert nur persistierten Runtime-State.

## 4. Genesis-Lifecycle

1. Bootstrap
2. Umwelt beobachten
3. Mission zerlegen
4. fehlende Fähigkeit identifizieren
5. Capability planen
6. Task erzeugen
7. Agent/Tool führt Task aus
8. Ergebnis mit Evidence belegen
9. Capability testen/verifizieren/aktivieren
10. Memory/Soul aktualisieren
11. World-State aktualisieren
12. nächsten Engpass bestimmen

Kein Schritt darf Erfolg allein aus einer behaupteten Variable ableiten.

## 5. Ressourcenmodell

Ressourcen sind endlich und explizit:

- EUR-Cash
- reserviertes Cash
- Compute Credits
- API Tokens
- Inference Budget
- Energy Budget
- später Zeit-/Rate-Limits und externe Kontingente

`0` bedeutet nicht "unbegrenzt", sondern "nicht verfügbar".

Cash darf nur durch verifizierte Revenue-Ereignisse steigen.

## 6. Evidence Ledger

Jede consequentiale Behauptung benötigt Evidence.

Evidence besitzt:

- ID
- Subject
- Typ
- Status
- Zusammenfassung
- Fingerprint
- Quelle
- Timestamp

Revenue, Ausgaben, Order-Transitions und Capability-Erfolg dürfen nicht auf bloßen Behauptungen basieren.

## 7. Ökonomischer Funnel

Der Zielpfad ist:

**Opportunity → Evidence → Offer → Publication → Lead → Quote → Acceptance → Payment → Fulfillment → Delivery → Completion → Profit → Reserve → Reinvestment**

Im Bootstrap-Modus werden nur lokale/kostenlose Schritte ausgeführt.

Externe Aktionen benötigen einen konfigurierten Provider und passieren durch die Policy-Grenze.

## 8. Commerce

Commerce bleibt provider-neutral.

Ein Offer beschreibt:

- Problem
- Zielkunde
- Leistung
- Preis/Zielwert
- Lieferweg
- Integritätsstatus

Orders besitzen eine kontrollierte State Machine:

`lead → quoted → accepted → paid → fulfilling → delivered → completed`

Alternative Endzustände:

`cancelled`, `refunded`

Jeder Übergang benötigt Evidence.

## 9. Treasury

Treasury ist eine Sicherheitsgrenze zwischen Runtime und echtem Geld.

Standard:

- deaktiviert
- keine Auszahlung
- kein Live-Trading
- keine ungeprüfte Kontoidentität
- keine Speicherung von Private Keys
- Allowlist für Ziele
- Tages-/Einzelgrenzen
- Mindestreserve
- Owner-Bindung
- Human Approval für konfigurierbare Schwellen

Das System darf nie behaupten, dass Geld dem Benutzer gehört, solange Provider-/Rechts-/Kontodaten das nicht belegen.

## 10. Trading

Trading ist ein späterer Capability-Pfad:

**Market Data → Strategy → Backtest → Paper Trading → Risk Gate → Explicit Live Authorization → Live → Reconciliation → P&L → Learning**

Live-Trading wird nicht automatisch aus Paper-Trading aktiviert.

Keine Strategie darf ohne Daten-/Order-/Fill-Evidence einen Gewinn behaupten.

## 11. Runtime Control Plane

Jeder Tool-Aufruf durchläuft:

**Agent → Policy → Audit → Execution → Result**

Policy berücksichtigt:

- Authority
- Risk
- Kill Switch
- Protected Paths
- Secret Access
- Command Safety
- Finanzgrenzen
- später Rate Limits und Resource Budgets

Die Runtime-Datenbank enthält eine prüfbare Audit-Chain.

## 12. Memory

Das System entwickelt Wissen über:

- Working/aktuellen Zustand
- Episoden
- Fakten
- Verfahren
- Beziehungen

Memory ist kein unkontrollierter Prompt-Speicher. Externe Inhalte bleiben untrusted input.

## 13. Skills

Ein Skill ist reproduzierbares Verfahren.

Lebenszyklus:

**entdecken → erzeugen → testen → verifizieren → aktivieren → beobachten → verbessern/deaktivieren**

## 14. Selbstmodifikation

Späterer kontrollierter Pfad:

**Hypothese → Patch → Tests → Evidence → Version → Deploy → Observe → Rollback**

Geschützte Identität, Treasury, Credentials, Runtime-Datenbank und Sicherheitsregeln dürfen nicht durch gewöhnliche Agenten-Tools überschrieben werden.

## 15. Replikation

Kinder entstehen nur bei nachweisbarem Arbeitsbedarf.

Ein Child erhält:

- minimale benötigte Fähigkeiten
- minimale Autorität
- begrenzte Ressourcen
- Parent-/Lineage-ID
- Aufgaben
- Sicherheitsregeln

Lebenszyklus:

**spawn → configure → start → healthy → unhealthy → recover/dead → cleanup**

## 16. Heartbeat

Der Runtime-Heartbeat hält autonome Prozesse am Leben.

Geplante Aufgaben werden später u.a.:

- Health Checks
- Opportunity Scans
- Inbox
- Memory Maintenance
- Model/Provider Refresh
- Child Health
- Metrics
- Risk Checks
- Wake Events

Nicht jede Heartbeat-Aufgabe darf externe Aktionen auslösen.

## 17. Cognition

Die vollständige Cognition-Schicht soll später einen ReAct-Zyklus implementieren:

**Context → Reason → Tool Call → Policy → Observation → Memory → Next Decision**

Zusätzlich:

- Token-/Inference-Budget
- Low-compute-Modus
- Loop Detection
- Idle Detection
- Retry/Backoff
- Modell-Routing
- Kostenmessung

## 18. Sicherheit

Mehrschichtige Verteidigung:

1. unveränderliche Grundregeln
2. zentrale Policy
3. Injection Defense
4. Pfadschutz
5. Command Safety
6. Finanzlimits
7. Authority Hierarchy
8. Audit
9. Kill Switch
10. Rollback/Recovery

Die Sicherheitsprinzipien werden an dokumentierte Mechanismen aus Conway Automaton angelehnt, aber provider- und kapitalneutral umgesetzt. Conway Automaton beschreibt u.a. zentrale Policy-Gates, Auditierung, Finanzlimits, Pfadschutz, ReAct-Loop, Heartbeat, Memory, Self-Modification und Replication als getrennte Runtime-Schichten. Siehe die Referenzarchitektur: https://github.com/Conway-Research/automaton/blob/main/ARCHITECTURE.md

## 19. Kein Fake-Economy-State

Unzulässig:

- erfundene Kunden
- erfundene Zahlungen
- erfundene Umsätze
- erfundene Kontostände
- erfundene API-Zugänge
- erfundene Provider-Bestätigungen
- erfundene Trading-Fills
- erfundene Profit-Zahlen

Der Runtime-State darf nur durch lokale Fakten oder verifizierte externe Evidence fortgeschrieben werden.

## 20. Endzustand

Das Zielsystem ist kein statisches Dashboard und kein einzelner Chatbot.

Es ist ein persistentes autonomes System mit:

- eigener Identität
- Mission
- Ressourcenmodell
- Capability-Graph
- Task-/Projekt-System
- Evidence Ledger
- Economy
- Commerce
- Treasury
- Memory
- Soul
- Skills
- Agenten-Lineage
- Policy
- Audit
- Heartbeat
- World Graph
- externer Integrationsschicht
- später Cognition
- später kontrollierter Replikation
- später optionalem Echtgeld-/Trading-Betrieb

Autonomie bedeutet dabei nicht unbeschränkte Autorität. Jede zusätzliche reale Wirkung muss durch einen expliziten Capability-, Policy-, Ressourcen- und Evidence-Pfad freigeschaltet werden.
