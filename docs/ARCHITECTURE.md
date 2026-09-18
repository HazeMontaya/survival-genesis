# Survival Genesis — Runtime Architecture v2

## 1. What the system is

Survival Genesis is a persistent autonomous operating runtime, not a chatbot and not a simulated economy. The runtime owns the state machine; the SVG world is only a projection of that state.

The seed starts with:
- one Genesis agent;
- zero cash/revenue;
- zero external provider authority;
- local execution only;
- persistent memory, tasks, capabilities, artifacts and audit events.

Everything else must be created because a real state transition requires it.

## 2. The control loop

**Observe → model state → detect needs → plan dependencies → acquire/verify capability → execute → verify evidence → account resources → learn → repeat.**

A need is not a task. A need is a missing prerequisite derived from state. A task is a concrete executable instance. A capability becomes active only after evidence-backed verification.

## 3. Authority boundary

All tool and external actions pass through one PolicyEngine before execution.

Authority levels:
1. owner/system
2. self
3. trusted agent
4. external

External input can provide information but cannot directly authorize dangerous actions.

Risk levels:
- safe
- caution
- dangerous
- forbidden

First-class policy checks cover protected paths, authority, risk and financial-action class. The policy decision is append-only audited.

## 4. Constitution

The Constitution is outside the self-modification surface. It defines:
- mission;
- non-deception / non-theft / authorization rules;
- evidence-before-claim rule;
- financial reserve boundary;
- uncertainty stop condition.

Self-modification can improve implementation, skills and strategies, but cannot rewrite the constitutional boundary.

## 5. Resource model

Every scarce resource is explicit:
- cash;
- reserved cash;
- compute credits;
- API/token budget;
- inference budget;
- energy/time budget;
- provider accounts and permissions.

Zero means unavailable. Missing credentials, accounts or authorization are resource gaps, never implicit capabilities.

## 6. Economic state machine

The real-world money path is:

**opportunity → evidence → offer → distribution → lead → order → verified payment → fulfillment → delivery → profit → reserve → reinvestment**

A local artifact is not a sale. A lead is not revenue. A webhook is not trusted until authenticated and replay-protected. Revenue enters the ledger only after provider-side evidence is verified.

## 7. External adapters

Core code contains provider-neutral contracts for:
- payments;
- marketplaces;
- exchanges.

Provider adapters are isolated from cognition. They receive explicit credentials from the host secret boundary and return evidence-backed execution results. If no adapter/credential exists, the capability is unavailable.

## 8. Trading

Trading is a separate capability, not a default survival mechanism.

Required progression:
**market data → strategy → backtest → paper orders → risk checks → explicit live authorization → live orders → reconciliation → P&L → learning**

Live trading must remain opt-in and independently gated. The agent cannot grant itself live authority by changing a prompt, skill, strategy or code path.

## 9. Self-improvement

Changes follow:
**hypothesis → patch → tests → evidence → version → deploy → observe → rollback if regression**

Protected policy/owner boundaries are never self-editable. Git is the implementation history; the runtime audit log records why a change was made and what evidence justified it.

## 10. Replication

Agents are created only when a real workload justifies specialization. A child receives:
- explicit purpose;
- minimum tools;
- explicit authority;
- task dependencies;
- lineage.

Replication is not free. It consumes resources and must be represented in the resource ledger.

## 11. World

The SVG world contains no prebuilt departments or decorative entities. Every visible node corresponds to persisted runtime state: agent, capability, project, task, artifact, connector, skill, tool, treasury/resource state, order/payment/position as those capabilities are implemented.

The world is therefore an operational graph, not a dashboard skin.

## 12. Reference implementation

The design deliberately adopts the useful architectural mechanisms documented by Conway-Research/automaton — continuous heartbeat, ReAct-style execution, centralized policy checks, financial limits, protected files, audit trails, versioned self-modification, skills, memory, replication and survival/resource states — while keeping Survival Genesis provider-neutral and independently implemented.

Reference: https://github.com/Conway-Research/automaton/blob/main/ARCHITECTURE.md
