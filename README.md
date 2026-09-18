# Survival Genesis

A zero-capital-first autonomous company/runtime built around a persistent seed agent and an emergent SVG world.

## Canonical repository

GitHub main is the source of truth. Local copies are downstream.

Use this direction only:

GitHub main → local checkout → local runtime

Do not treat local runtime files, experiments or generated workspace/ state as a source for GitHub.

## Repository structure

.
├── .github/workflows/       # CI only
├── docs/                    # architecture and operating rules
├── src/genesis/
│   ├── core/                # state, identity, resources, survival, opportunities
│   ├── domain/              # agents, tasks, projects, commerce, memory, world
│   ├── runtime/             # seed-agent orchestration, heartbeat, policy, DB
│   ├── integrations/        # tools, connectors, signals, treasury
│   └── interfaces/          # CLI, HTTP API, SVG state projection
├── tests/                   # automated tests
├── web/                     # full-screen SVG world
├── pyproject.toml
└── README.md

Generated runtime state lives in workspace/ and is ignored by Git.

## Windows quick start

From Command Prompt:

    git clone https://github.com/HazeMontaya/survival-genesis.git
    cd survival-genesis
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -e ".[test]"
    survival-genesis serve

Open http://127.0.0.1:8765.

## Runtime model

The world starts with one Genesis agent and only the runtime substrate. Missing capabilities are derived from persisted state. Work is dependency-aware; capabilities are activated only after execution and evidence. The SVG is a projection of actual runtime entities, not a prebuilt simulation.

Operating loop: observe → understand → decide → build → verify → learn → continue.

## Financial boundary

Revenue is accepted only when externally verified. Payments, payouts and live trading are disabled by default. The treasury stores account fingerprints rather than raw account references and never stores secret material. Real provider access requires explicit owner verification, provider credentials and policy limits.

The system must not fabricate customers, revenue, accounts, credentials or transactions, and must not bypass KYC, platform controls or authorization requirements.

## Design reference

The architecture adapts general mechanisms documented by Conway Research's Automaton — continuous runtime/heartbeat, a centralized policy gate, persistent state, memory/skills, and explicit financial controls — without treating the reference implementation as the source of truth for this repository.
