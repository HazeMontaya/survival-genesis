# Survival Genesis — Product & World Design System

## Product thesis

Survival Genesis is not a dashboard, admin console or game skin. It is a state projection of an autonomous economic organism.

The interface has one primary job: make current state, pressure, decisions, work, evidence and growth observable without inventing state.

The visual system is a complete rebuild. The previous UI vocabulary is not a design baseline.

## Experience model

The application is one continuous operating environment:

**WORLD → PRESSURE → WORK → EVIDENCE → ECONOMY → GROWTH**

The center is the world graph. Side regions expose only the information necessary to understand why the graph changes.

## Visual language

- asymmetric spatial composition
- graph-first canvas
- circular Genesis core
- agents as circles
- projects as rotated squares
- capabilities, tasks, resources and evidence as smaller nodes
- relationships as graph edges
- state represented through topology and restrained motion
- near-black base with thin structural separators
- one high-contrast signal color for active system pressure
- monospace for IDs, timestamps and machine facts
- sans-serif for descriptions

## World rules

The SVG is generated from runtime state.

The browser may position entities, draw relations, animate state, filter the projection and inspect entities.

The browser may not create customers, revenue, orders or verified evidence, mutate economic state, or infer success from visual appearance.

## Information hierarchy

### Survival
Cash, compute, inference budget, runtime state, active tasks and entity count remain visible.

### Bottleneck
The current blocking need is explicit: missing offer, publication, verified payment channel, fulfillment capability, resource shortage or policy denial.

### Work graph
Agents, capabilities, projects, tasks, artifacts, connectors and skills.

### Economic proof
Opportunities, evidence, offers, publications, leads, orders, payments and revenue.

### Lineage
Later versions expose parent/child agents, capability ownership, resource allocation and self-modification lineage.

## Interaction model

Primary modes are World, Agents, Work graph, Economy and Evidence. The world remains visible in every mode. Entity inspection is contextual and factual.

## State integrity

The frontend treats /api/state as a read model. Mutations go through explicit backend endpoints. The frontend never stores authoritative runtime state.

## Upgrade rule

Every feature must answer:

1. What real runtime state does it represent?
2. What evidence makes that state trustworthy?
3. Which capability owns or changes it?
4. What resource and policy boundary limits it?

If those questions cannot be answered, the feature is not authoritative UI.

## Concept alignment

The runtime is aligned with useful documented mechanisms from Conway Research's Automaton: continuous operation, ReAct-style cognition, centralized policy, persistent state, heartbeat, memory/skills, financial controls, auditability and controlled self-modification. Survival Genesis remains provider-neutral and zero-capital-first rather than copying the reference implementation.

## Forbidden regression

Do not reintroduce the previous HUD, toolbar, inspector styling, dashboard KPI grid, decorative simulated entities, hard-coded world objects, fake activity indicators or visual claims unsupported by backend state.
