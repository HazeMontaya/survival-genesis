# Survival Genesis

Zero-capital-first autonomous runtime. The repository is organized strictly by responsibility.

## Architecture

- `genesis/core/`: state, SQLite audit/control plane, policy, resource accounting, survival rules and identity.
- `genesis/domain/`: economy, commerce, treasury and opportunity model.
- `genesis/work/`: capabilities, projects and dependency-aware tasks.
- `genesis/agents/`: agent registry, lineage and messaging.
- `genesis/knowledge/`: memory, external signals and reusable skills.
- `genesis/platform/`: artifacts, connectors and policy-gated tools.
- `genesis/world/`: state-derived world graph.
- `genesis/runtime/`: Genesis seed, heartbeat and HTTP runtime.
- `world/`: SVG client only.
- `tests/`: behavior and security-boundary tests.

Runtime data is never stored in source folders; it belongs under `workspace/`, which is ignored by git.

## Control boundary

Genesis starts at zero cash. Revenue must be externally verified. Tool execution is centrally policy-gated. The SQLite journal is hash-chained and can be integrity-checked. Protected files, owner-only operations, reserves and financial limits are kept outside the autonomous decision surface.

Live payments, payouts and trading are provider-specific integrations and remain explicitly disabled until configured and authorized by the owner.

## Operating loop

**observe → derive need → satisfy prerequisites → execute → verify → learn → repeat**

The SVG world is a projection of runtime state, not a second source of truth.
