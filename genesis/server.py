from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from threading import Event,Thread,Lock
import json
from .agent import GenesisAgent
from .ecosystem import ecosystem_snapshot
ROOT=Path(__file__).resolve().parent.parent; DASHBOARD=ROOT/"dashboard"/"index.html"
class Runtime:
    def __init__(self):
        self.agent=GenesisAgent(); self.running=False; self.stop_event=Event(); self.thread=None; self.lock=Lock(); self.last_result=None
    def tick(self):
        with self.lock: self.last_result=self.agent.tick(); return self.last_result
    def loop(self):
        while not self.stop_event.wait(8):
            if self.running:
                try:self.tick()
                except Exception as exc:self.agent.store.event("runtime_error",{"error":str(exc)})
    def start(self):
        self.running=True; self.stop_event.clear()
        if not self.thread or not self.thread.is_alive(): self.thread=Thread(target=self.loop,daemon=True); self.thread.start()
    def stop(self): self.running=False; self.stop_event.set()
runtime=Runtime()
class Handler(BaseHTTPRequestHandler):
    def send_json(self,payload,code=200):
        raw=json.dumps(payload).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/state":
            s=ecosystem_snapshot(runtime.agent); s["artifacts"]=runtime.agent.artifacts.snapshot(); s["runtime"]={"running":runtime.running,"tick_interval_seconds":8,"last_tick":runtime.last_result is not None}; self.send_json(s); return
        if self.path in ("/","/index.html"):
            raw=DASHBOARD.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw); return
        self.send_json({"error":"not_found"},404)
    def do_POST(self):
        if self.path=="/api/tick":
            try:self.send_json(runtime.tick())
            except Exception as e:self.send_json({"error":str(e)},500)
            return
        if self.path=="/api/runtime/start":runtime.start(); self.send_json({"running":True}); return
        if self.path=="/api/runtime/stop":runtime.stop(); self.send_json({"running":False}); return
        self.send_json({"error":"not_found"},404)
    def log_message(self,*_):return
def serve(host="127.0.0.1",port=8765):
    print(f"Survival Genesis control center: http://{host}:{port}"); ThreadingHTTPServer((host,port),Handler).serve_forever()
