from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    risk: str


@dataclass(frozen=True)
class ToolRule:
    risk: str
    min_authority: str = "self"


class PolicyEngine:
    """Pre-execution policy gate. No tool bypasses this boundary."""

    AUTHORITY = {"external": 0, "peer": 1, "self": 2, "owner": 3}
    RISK = {"safe": 0, "caution": 1, "dangerous": 2, "forbidden": 3}

    DEFAULTS = {
        "read_file": ToolRule("safe"),
        "list_files": ToolRule("safe"),
        "remember": ToolRule("safe"),
        "send_message": ToolRule("caution"),
        "run_tests": ToolRule("caution"),
        "run_python": ToolRule("caution"),
        "write_file": ToolRule("caution"),
        "publish": ToolRule("dangerous", "owner"),
        "payout": ToolRule("dangerous", "owner"),
        "trade_live": ToolRule("dangerous", "owner"),
        "modify_policy": ToolRule("forbidden", "owner"),
        "read_secret": ToolRule("forbidden", "owner"),
    }

    PROTECTED_NAMES = {
        "constitution.md", "owner.json", "treasury.json", "runtime.db",
        ".env", "wallet.json", "credentials.json", "secrets.json"
    }
    SECRET_MARKERS = ("private_key", "secret", "password", "credential", "api_key", "token")

    def __init__(self, database, root: str | Path):
        self.db = database
        self.root = Path(root).resolve()
        self.kill_switch = self._read_kill_switch()

    def _read_kill_switch(self) -> bool:
        return os.getenv("GENESIS_KILL_SWITCH", "0") == "1"

    def refresh(self):
        self.kill_switch = self._read_kill_switch()

    def _hash_input(self, args: dict) -> str:
        return hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()

    def _protected_path(self, path: str) -> bool:
        p = Path(path)
        parts = {x.lower() for x in p.parts}
        if any(part in self.PROTECTED_NAMES for part in parts):
            return True
        return any(marker in p.name.lower() for marker in self.SECRET_MARKERS)

    def evaluate(self, tool: str, args: dict | None = None, actor: str = "genesis-1", authority: str = "self") -> PolicyDecision:
        args = args or {}
        rule = self.DEFAULTS.get(tool, ToolRule("forbidden"))
        reason = "allowed by baseline policy"
        allowed = True

        if self.kill_switch and rule.risk in ("dangerous", "forbidden"):
            allowed, reason = False, "global kill switch is active"
        elif self.AUTHORITY.get(authority, -1) < self.AUTHORITY[rule.min_authority]:
            allowed, reason = False, f"authority {authority} below required {rule.min_authority}"
        elif rule.risk == "forbidden":
            allowed, reason = False, "tool is forbidden by policy"
        elif tool in {"write_file", "read_file", "list_files"}:
            path = str(args.get("path", "."))
            resolved = (self.root / path).resolve()
            if self.root not in resolved.parents and resolved != self.root:
                allowed, reason = False, "path escapes workspace"
            elif self._protected_path(path) and authority != "owner":
                allowed, reason = False, "protected or secret path"

        decision = PolicyDecision(allowed, reason, rule.risk)
        self.db.policy(actor, tool, rule.risk, "allow" if allowed else "deny", reason, self._hash_input(args))
        return decision
