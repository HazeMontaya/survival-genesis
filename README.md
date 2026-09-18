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

The local control center is backed by the actual Python runtime. The runtime persists the economic ledger, append-only events, task queue, memory graph and locally generated artifacts under `workspace/`.

Implemented:
- persistent economic ledger and audit event log
- persistent agent-owned task queue with completion state
- persistent memory graph
- local artifact factory producing reviewable Markdown assets
- zero-capital opportunity ranking and experiment loop
- live state API and autonomous 8-second runtime
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

The project contains the economic kernel, persistent operating state, company/room/agent topology, autonomous local execution loop, artifact pipeline, live control server, immersive dashboard and tests. Real provider integrations are the next external-execution layer and are deliberately gated rather than faked.
