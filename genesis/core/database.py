from contextlib import contextmanager
from pathlib import Path
import hashlib,json,sqlite3,threading,uuid
from datetime import datetime,timezone
class RuntimeDatabase:
 def __init__(self,path="workspace/runtime.db"):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self._lock=threading.RLock();self._init()
 def _connect(self):
  d=sqlite3.connect(self.path,timeout=30,isolation_level=None);d.row_factory=sqlite3.Row;d.execute("PRAGMA journal_mode=WAL");d.execute("PRAGMA foreign_keys=ON");d.execute("PRAGMA busy_timeout=30000");return d
 def _init(self):
  with self._connect() as d:d.executescript("""CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,ts TEXT NOT NULL,kind TEXT NOT NULL,actor TEXT NOT NULL,payload TEXT NOT NULL,prev_hash TEXT,hash TEXT NOT NULL);CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);CREATE TABLE IF NOT EXISTS policy_decisions(id TEXT PRIMARY KEY,ts TEXT NOT NULL,actor TEXT NOT NULL,tool TEXT NOT NULL,risk TEXT NOT NULL,decision TEXT NOT NULL,reason TEXT NOT NULL,input_hash TEXT NOT NULL);CREATE TABLE IF NOT EXISTS idempotency(scope TEXT NOT NULL,key TEXT NOT NULL,result TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY(scope,key));CREATE TABLE IF NOT EXISTS resource_reservations(id TEXT PRIMARY KEY,resource TEXT NOT NULL,amount REAL NOT NULL CHECK(amount>0),owner TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS financial_actions(id TEXT PRIMARY KEY,ts TEXT NOT NULL,action TEXT NOT NULL,mode TEXT NOT NULL,amount_eur REAL NOT NULL,status TEXT NOT NULL,evidence TEXT NOT NULL);""")
 @contextmanager
 def transaction(self):
  with self._lock:
   d=self._connect()
   try:d.execute("BEGIN IMMEDIATE");yield d;d.execute("COMMIT")
   except Exception:d.execute("ROLLBACK");raise
   finally:d.close()
 def event(self,kind,payload,actor="system"):
  body=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"));prev="";eid=uuid.uuid4().hex
  with self.transaction() as d:
   r=d.execute("SELECT hash FROM events ORDER BY rowid DESC LIMIT 1").fetchone();prev=r["hash"] if r else "";h=hashlib.sha256(f"{prev}|{kind}|{actor}|{body}".encode()).hexdigest();d.execute("INSERT INTO events VALUES(?,?,?,?,?,?,?)",(eid,datetime.now(timezone.utc).isoformat(),kind,actor,body,prev,h))
  return eid
 def events(self,limit=100):
  with self._connect() as d:
   rows=d.execute("SELECT id,ts,kind,actor,payload,hash FROM events ORDER BY rowid DESC LIMIT ?",(max(1,min(int(limit),500)),)).fetchall()
  return [{"id":r["id"],"ts":r["ts"],"kind":r["kind"],"actor":r["actor"],"payload":json.loads(r["payload"]),"hash":r["hash"]} for r in rows]
 def policy(self,actor,tool,risk,decision,reason,input_hash):
  with self.transaction() as d:d.execute("INSERT INTO policy_decisions VALUES(?,?,?,?,?,?,?,?)",(uuid.uuid4().hex,datetime.now(timezone.utc).isoformat(),actor,tool,risk,decision,reason,input_hash))
 def verify_chain(self):
  with self._connect() as d:rows=d.execute("SELECT * FROM events ORDER BY rowid").fetchall()
  prev=""
  for r in rows:
   h=hashlib.sha256(f"{prev}|{r['kind']}|{r['actor']}|{r['payload']}".encode()).hexdigest()
   if h!=r["hash"] or r["prev_hash"]!=prev:return False
   prev=r["hash"]
  return True
 def snapshot(self):
  with self._connect() as d:return {"events":d.execute("SELECT COUNT(*) n FROM events").fetchone()["n"],"policy_decisions":d.execute("SELECT COUNT(*) n FROM policy_decisions").fetchone()["n"],"financial_actions":d.execute("SELECT COUNT(*) n FROM financial_actions").fetchone()["n"],"path":str(self.path)}
