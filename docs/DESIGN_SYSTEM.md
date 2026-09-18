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

## Agent World v2

The product experience now uses two synchronized visual layers.

### Physical layer

The world is spatially organized into runtime-derived rooms:
- **Core** — Genesis and orchestration.
- **Intelligence** — research, scouting and analysis.
- **Knowledge** — memory, skills and evidence.
- **Production** — artifacts, projects and outputs.
- **Quality** — review and verification.
- **Factory** — executable tools and workflows.
- **Gateway** — configured external connectors.
- **Commerce** — offers and real orders.

Agents have runtime-derived visual states such as `idle`, `searching`, `working` and `reviewing`. These are projections of active tasks and capabilities, not cosmetic character traits.

Tasks are rendered as work objects. A task exists visually only when it exists in the persisted task board.

### Neural layer

Pressing **N** switches between the physical world and a relationship-oriented neural projection.

The neural layer exposes persisted relations and their intensity. It is not a fabricated neural network. A stronger line means the runtime has recorded a stronger relation; it does not imply intelligence or quality.

### Knowledge garden

Evidence and skills live in the Knowledge room. Evidence status is rendered from the evidence ledger (`observed`, `verified`, `rejected`). Verification is a runtime trust boundary.

### Temporal/audit principle

The runtime journal remains the source for factual history. Future timeline controls must replay recorded events rather than regenerate a simulated past.

### Animation rule

Animation communicates state transitions or active work. Idle entities remain visually quiet. Decorative motion must not imply work, revenue, communication or success that the runtime did not record.

### Control rule

The browser remains a projection layer. Commands that can change runtime state must cross the backend policy boundary. Source-code evolution is a controlled change-management operation, not an unrestricted browser file write.
