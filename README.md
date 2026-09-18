# Survival Genesis

A zero-capital-first autonomous company operating system.

## Windows quick start

From **Command Prompt (cmd.exe)**:

    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install -e .
    survival-genesis serve

If PowerShell is being used instead:

    .\.venv\Scripts\Activate.ps1

If Windows blocks PowerShell scripts, use Command Prompt as shown above; no execution-policy change is required.

Then open **http://127.0.0.1:8765**.

To run without activating the environment:

    .venv\Scripts\python.exe -m pip install -e .
    .venv\Scripts\survival-genesis.exe serve

## Operational state

The interactive Genesis world is backed by the actual Python runtime. The initial world is intentionally minimal: one Genesis agent and the runtime substrate. Organizational structures are not pre-created; they emerge from decisions and verified work. The SVG world is a projection of persisted runtime state, not a separate simulation. The runtime persists the economic ledger, append-only events, task queue, memory graph and locally generated artifacts under `workspace/`.

Implemented:
- persistent economic ledger and audit event log
- persistent agent-owned task queue with completion state
- persistent memory graph
- local artifact factory producing reviewable Markdown assets
- zero-capital opportunity ranking and experiment loop
- live state API and autonomous 8-second runtime
- seed-agent Genesis runtime that derives goals, creates capabilities, projects and child agents from actual state\n- dependency-aware task lifecycle with retries and verification\n- persistent emergent scene graph: the world starts with only the Genesis core and grows from real entities and relations
- SVG Genesis world with no prebuilt departments: agents, projects, capabilities, tasks, artifacts and connectors become visible only after they exist in runtime state
- manual cycle, start and stop controls
- honest revenue accounting: unverified revenue is rejected
- financial execution and trading disabled by default

## First autonomous cycle

A cycle selects a zero-cost opportunity, records an experiment, creates research/build tasks, completes local work, writes a concrete artifact and stores the result in memory. It never claims that an artifact was sold or that revenue exists.

Operating loop: observe -> discover -> select -> execute locally -> verify -> learn -> repeat.

## External execution

Publishing, payments, advertising, brokerage, wallets and marketplace actions are not silently enabled. They require explicit provider adapters, credentials and policy gates. No credentials, balances, accounts or transactions are fabricated.

The system must not spam, impersonate, defraud, evade platform controls, manipulate markets or access systems without authorization.

## Repository status

The project contains the economic kernel, persistent operating state, seed-agent runtime, emergent capability/project/agent graph, dependency-aware task execution, artifact pipeline, live control server, immersive SVG world and tests. Real provider integrations are the next external-execution layer and are deliberately gated rather than faked.


## Money, ownership and security boundary

Survival Genesis treats money as a capability with explicit custody and policy, not as an unrestricted AI resource. The safest deployment is an account held by the human owner or their legal company, with the runtime receiving only the minimum provider permissions required to collect or operate. Never put private keys, banking passwords, exchange API secrets or recovery phrases in git, source files, prompts, skills or agent-visible memory.

The treasury boundary supports:
- owner verification before an external account can be bound
- hashed account references rather than storing the raw account identifier in the treasury record
- replay protection for verified revenue events
- explicit collection, payout and live-trading gates
- payout destination allowlisting
- maximum single payout, daily payout and minimum-reserve limits
- separate live versus paper trading mode
- daily trade-notional limits
- an independent resource ledger for cash, reserves, compute credits, inference budget and other scarce resources

**Important:** enabling a financial gate does not create money, a bank account, an exchange account, legal ownership, or market access. Those must be established with the provider under the owner's identity and terms. The runtime must never bypass KYC, platform restrictions, withdrawal controls or authorization requirements.

## Recommended zero-capital activation path

1. Run the system locally with every financial gate off.
2. Create a dedicated account/wallet owned by you or your legal company; do not reuse a personal password or expose its recovery material to the agent.
3. Create provider credentials with the narrowest permissions possible. Prefer read/receive permissions first; add trading only after the non-trading path is audited.
4. Store secrets outside the repository using the host secret store/environment and restrict file permissions. GitHub secret scanning and push protection should remain enabled.
5. Bind the account through the owner-verification boundary. The runtime records only a fingerprint and verification state.
6. Configure a non-zero reserve and strict payout/trading caps. Use paper trading first; live trading is an explicit separate mode.
7. Start with real revenue collection and fulfillment. Only after independently verified revenue exists should the runtime gain authority to spend part of it.
8. Keep owner withdrawal destinations allowlisted. Do not give the agent permission to change its own withdrawal destination.

The target resource loop is: **opportunity → evidence → free/local build → distribution → lead → order → verified payment → fulfillment → delivery → profit → reserve → reinvestment → capability growth**. A missing provider, credential, balance or authorization is represented as a resource gap; it is never treated as if it already exists.
