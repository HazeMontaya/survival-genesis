# Survival Genesis — Repository Architecture

## Source of truth

GitHub main is the canonical source repository. Local checkouts are disposable working copies. The normal synchronization direction is GitHub to local. Local runtime state under workspace/ is never source material and must never be pushed back into the repository.

## Layout

src/genesis/ contains importable application code:

- core/ — identity, resource/state primitives, opportunity ranking and survival policy.
- domain/ — agents, tasks, projects, capabilities, memory, skills, commerce, economy and world model.
- runtime/ — Genesis orchestration, heartbeat and the runtime control-plane database/policy.
- integrations/ — external I/O boundaries and local tool execution: connectors, signals, tools and treasury.
- interfaces/ — CLI, HTTP server and state projection for the world UI.
- web/ — the SVG world only; it contains no runtime state.
- tests/ — tests only; tests import the installed genesis package.
- docs/ — architecture and operational documentation only.
- workspace/ — generated runtime state, local only, ignored by Git.

## Dependency direction

interfaces → runtime → domain/core
runtime → integrations
domain → core

core must not import domain, runtime, integrations or interfaces.

integrations may depend on core/domain contracts, but must not own application orchestration.

This keeps the seed-agent loop in one place and prevents provider/network code from leaking into domain models.

## Persistence rule

Runtime JSON files and SQLite belong to workspace/. They are projections of runtime state, not repository configuration. Secrets and financial account material are never stored in Git.

## Runtime flow

GenesisAgent → NeedEngine → TaskBoard → capability execution → verification → state projection → SVG world

Consequential external operations must additionally pass the runtime policy boundary before provider execution.

## Security boundary

Protected configuration, credentials, treasury state and runtime database files are outside the self-modification surface. Financial operations remain disabled by default and require explicit owner/provider configuration.

The structure follows the same architectural principle seen in Conway Research's Automaton: a dedicated runtime, centralized policy boundary, persistent state, heartbeat, skills/memory and explicit financial controls. It is an adaptation of the architectural pattern, not a copy of its implementation.
