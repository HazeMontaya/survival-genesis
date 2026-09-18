from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Event, Thread, Lock
from pathlib import Path
import json
from genesis.runtime.agent import GenesisAgent
from genesis.interfaces.ecosystem import ecosystem_snapshot
from genesis.runtime.heartbeat import HeartbeatDaemon

ROOT=Path(__file__).resolve().parents[2]
WORLD=ROOT/"web"/"index.html"

class Runtime:
    def __init__(self):
        self.agent=GenesisAgent(); self.running=False; self.stop_event=Event(); self.thread=None; self.lock=Lock(); self.heartbeat=HeartbeatDaemon(self.agent,8); self.last_result=None; self.last_error=None
    def tick(self):
        with self.lock:
            try:self.last_result=self.agent.tick(); self.last_error=None; return self.last_result
            except Exception as exc:self.last_error=str(exc); self.agent.store.event("runtime_error",{"error":self.last_error}); raise
    def loop(self): self.heartbeat.start(); self.stop_event.wait(); self.heartbeat.stop()
    def start(self):
        self.running=True; self.stop_event.clear()
        if not self.thread or not self.thread.is_alive(): self.thread=Thread(target=self.loop,daemon=True); self.thread.start()
    def stop(self): self.running=False; self.stop_event.set(); self.heartbeat.stop()

runtime=Runtime()

class Handler(BaseHTTPRequestHandler):
    def send_json(self,payload,code=200):
        raw=json.dumps(payload,ensure_ascii=False).encode(); self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def body(self):
        n=int(self.headers.get("Content-Length","0")); return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        if self.path=="/api/state":
            s=ecosystem_snapshot(runtime.agent); s.update({"artifacts":runtime.agent.artifacts.snapshot(),"signals":runtime.agent.signals.snapshot(),"commerce":runtime.agent.commerce.snapshot(),"connectors":runtime.agent.connectors.snapshot(),"events":runtime.agent.store.events()[-100:],"runtime":{"running":runtime.running,"tick_interval_seconds":8,"last_tick":runtime.last_result is not None,"last_error":runtime.last_error,"heartbeat":runtime.heartbeat.snapshot()}}); self.send_json(s); return
        if self.path in ("/","/index.html"):
            raw=WORLD.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        self.send_json({"error":"not_found"},404)
    def do_POST(self):
        try:
            if self.path=="/api/tick": self.send_json(runtime.tick()); return
            if self.path=="/api/runtime/start": runtime.start(); self.send_json({"running":True}); return
            if self.path=="/api/runtime/stop": runtime.stop(); self.send_json({"running":False}); return
            if self.path=="/api/revenue/verified":
                data=self.body(); ledger=runtime.agent.treasury.accept_signed_revenue(str(data["event_id"]),str(data.get("source","webhook")),float(data["amount_eur"]),self.headers.get("X-Genesis-Signature","")); self.send_json({"accepted":True,"ledger":ledger.__dict__}); return
        except Exception as exc:self.send_json({"error":str(exc)},500); return
        self.send_json({"error":"not_found"},404)
    def log_message(self,*_): return

def serve(host="127.0.0.1",port=8765):
    print(f"Survival Genesis Welt: http://{host}:{port}"); ThreadingHTTPServer((host,port),Handler).serve_forever()
