from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class RuntimeDatabase:
    """Durable runtime journal and control-plane store.

    SQLite is the authoritative audit/control plane. Domain modules may keep
    projections for compatibility, but every consequential runtime action is
    journaled here before it is exposed as successful.
    """

    def __init__(self, path: str | Path = "workspace/runtime.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                kind TEXT NOT NULL,
                actor TEXT NOT NULL,
                payload TEXT NOT NULL,
                prev_hash TEXT,
                hash TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
            CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);

            CREATE TABLE IF NOT EXISTS policy_decisions (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actor TEXT NOT NULL,
                tool TEXT NOT NULL,
                risk TEXT NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                input_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS idempotency (
                scope TEXT NOT NULL,
                key TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(scope, key)
            );

            CREATE TABLE IF NOT EXISTS resource_reservations (
                id TEXT PRIMARY KEY,
                resource TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                owner TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS financial_actions (
                id TEXT PRIMARY KEY,
                ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                mode TEXT NOT NULL,
                amount_eur REAL NOT NULL,
                status TEXT NOT NULL,
                evidence TEXT NOT NULL
            );
            """)

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            db = self._connect()
            try:
                db.execute("BEGIN IMMEDIATE")
                yield db
                db.execute("COMMIT")
            except Exception:
                db.execute("ROLLBACK")
                raise
            finally:
                db.close()

    def event(self, kind: str, payload: dict, actor: str = "system") -> str:
        import hashlib
        import time

        event_id = uuid.uuid4().hex
        body = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        with self.transaction() as db:
            row = db.execute("SELECT hash FROM events ORDER BY rowid DESC LIMIT 1").fetchone()
            prev = row["hash"] if row else ""
            digest = hashlib.sha256(f"{prev}|{kind}|{actor}|{body}".encode()).hexdigest()
            db.execute(
                "INSERT INTO events(id,ts,kind,actor,payload,prev_hash,hash) VALUES(?,?,?,?,?,?,?)",
                (event_id, str(time.time()), kind, actor, body, prev, digest),
            )
        return event_id

    def policy(self, actor: str, tool: str, risk: str, decision: str, reason: str, input_hash: str) -> str:
        decision_id = uuid.uuid4().hex
        with self.transaction() as db:
            db.execute(
                "INSERT INTO policy_decisions(id,actor,tool,risk,decision,reason,input_hash) VALUES(?,?,?,?,?,?,?)",
                (decision_id, actor, tool, risk, decision, reason, input_hash),
            )
        return decision_id

    def once(self, scope: str, key: str, result: dict | None = None):
        with self.transaction() as db:
            row = db.execute(
                "SELECT result FROM idempotency WHERE scope=? AND key=?", (scope, key)
            ).fetchone()
            if row:
                return json.loads(row["result"])
            if result is None:
                return None
            db.execute(
                "INSERT INTO idempotency(scope,key,result) VALUES(?,?,?)",
                (scope, key, json.dumps(result, ensure_ascii=False, sort_keys=True)),
            )
            return result

    def financial_action(self, action: str, mode: str, amount_eur: float, status: str, evidence: dict):
        self.event("financial_action", {
            "action": action, "mode": mode, "amount_eur": amount_eur,
            "status": status, "evidence": evidence
        }, actor="treasury")
        with self.transaction() as db:
            db.execute(
                "INSERT INTO financial_actions(id,action,mode,amount_eur,status,evidence) VALUES(?,?,?,?,?,?)",
                (uuid.uuid4().hex, action, mode, amount_eur, status,
                 json.dumps(evidence, ensure_ascii=False, sort_keys=True)),
            )

    def verify_event_chain(self) -> bool:
        import hashlib
        with self._connect() as db:
            rows = db.execute("SELECT kind, actor, payload, prev_hash, hash FROM events ORDER BY rowid ASC").fetchall()
        previous = ""
        for row in rows:
            expected = hashlib.sha256(f"{previous}|{row['kind']}|{row['actor']}|{row['payload']}".encode()).hexdigest()
            if row["prev_hash"] != previous or row["hash"] != expected:
                return False
            previous = row["hash"]
        return True

    def snapshot(self) -> dict:
        with self._connect() as db:
            events = db.execute("SELECT COUNT(*) n FROM events").fetchone()["n"]
            policies = db.execute("SELECT COUNT(*) n FROM policy_decisions").fetchone()["n"]
            financial = db.execute("SELECT COUNT(*) n FROM financial_actions").fetchone()["n"]
        return {"events": events, "policy_decisions": policies, "financial_actions": financial, "path": str(self.path)}
