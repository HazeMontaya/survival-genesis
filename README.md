# Survival Genesis

A zero-capital-first autonomous company operating system.

Survival Genesis is an auditable agent ecosystem: a company shell, organizational topology, economic ledger, opportunity engine and live control center. It is designed to grow capabilities from **verified value**, not simulated money.

## Live enterprise control center

Run the local runtime:

```bash
pip install -e .
survival-genesis serve
```

Then open **http://127.0.0.1:8765**.

The control center visualizes:

- **Genesis Command** — strategy, memory and governance
- **Research Lab** — signals, markets and opportunity discovery
- **Product Forge** — products, code, packaging and QA
- **Growth Studio** — brand, content and distribution
- **Revenue Floor** — offers, leads and conversion
- **Treasury** — verified revenue, reserves and reinvestment
- **Operations** — fulfillment and execution queues
- **Evolution Lab** — experiments and learning

The dashboard is intentionally not a decorative animation. Its state is read from the runtime API and persisted ledger. The operator can start/stop the autonomous cycle, trigger a decision cycle, inspect agents, export state and observe the event surface.

## Architecture

```
                    ┌─────────────────────────────┐
                    │       GENESIS COMMAND       │
                    │ strategy · memory · policy  │
                    └──────────────┬──────────────┘
                                   │
       ┌──────────────┬────────────┼────────────┬──────────────┐
       ▼              ▼            ▼            ▼              ▼
  RESEARCH        PRODUCT        GROWTH       REVENUE       TREASURY
  LAB             FORGE         STUDIO        FLOOR          LEDGER
       │              │            │            │              │
       └──────────────┴────────────┴────────────┴──────────────┘
                                   │
                           OPERATIONS / EVOLUTION
                                   │
                         verified outcomes only
```

The current runtime uses Python's standard library for the live server, so the control center does not require a paid SaaS backend or a third-party web framework.

## Core loop

`observe → discover → build → publish → distribute → measure → earn → reinvest → improve`

The runtime is revenue-driven, cost-aware, auditable and conservative around irreversible actions.

## Zero-capital invariant

At bootstrap:

- cash balance = €0
- paid API budget = €0
- subscriptions = €0
- trading enabled = false
- external financial execution = false

The system may use free/local resources that are actually available. It must never fabricate credits, balances, credentials or payment accounts.

## Execution gates

The architecture separates **decision-making** from **external side effects**. Real payment, marketplace, advertising, brokerage, wallet or publishing adapters must be explicitly configured and authorized.

The system must not spam, impersonate, defraud, evade platform controls, manipulate markets, or perform unauthorized access.

## Status

Current build: economic kernel + persistent ledger + opportunity engine + company/room/agent topology + live local control server + immersive enterprise dashboard + tests.

Next engineering layers are provider adapters, authenticated operator controls, task queues, artifact storage, real opportunity connectors, publishing workflows, verified payment ingestion and policy-scoped automation. These should be added as real integrations rather than fake dashboard activity.

Inspired by Conway Research's Automaton architecture.
