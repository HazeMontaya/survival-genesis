# Survival Genesis

A zero-capital-first autonomous economic agent runtime.

Survival Genesis is inspired by the architecture of Conway Research's Automaton, but changes the bootstrap assumption: the system starts with **€0, no paid API, no subscription and no pre-funded wallet** and attempts to create measurable value using only resources actually available to its runtime.

## Core loop

`observe → discover → build → publish → distribute → measure → earn → reinvest → improve`

The runtime is deliberately **revenue-driven, cost-aware, auditable and conservative around irreversible financial actions**.

### Revenue surfaces

The engine can evaluate and operate workflows for:

- digital products
- software/tools
- services
- affiliate programs
- print-on-demand
- dropshipping
- lead generation
- content/media
- open-source sponsorship
- marketplaces
- data/research products
- licensing
- later-stage investing

No revenue is assumed. Every opportunity must pass validation and unit-economics checks.

## Zero-capital invariant

At bootstrap:

- cash balance = 0
- paid API budget = 0
- subscriptions = 0
- trading enabled = false
- external financial execution = false

The system may use free/local resources that are actually available. It must never fabricate credits or pretend a payment account exists.

## Safety

External publishing and financial execution are separated. The default runtime is simulation/dry-run. Real payment, marketplace, advertising, brokerage or wallet adapters require explicit configuration and provider authorization.

The system must not spam, impersonate, defraud, evade platform controls, manipulate markets, or perform unauthorized access.

## Status

Genesis MVP: resource ledger, opportunity scoring, experiment engine, revenue ledger, policy gates, persistence, CLI and tests.

Inspired by [Conway-Research/automaton](https://github.com/Conway-Research/automaton).
