from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Event, Thread
import json

from .agent import GenesisAgent
from .ecosystem import ecosystem_snapshot

ROOT=Path(__file__).resolve().parent.parent
DASHBOARD=ROOT/"dashboard"/"index.html"

class Runtime:
    def __init__(self):
        self.agent=GenesisAgent()
        self.running=False
        self.stop_event=Event()
        self.thread=None
        self.lock=None
    def tick(self):
        result=self.agent.tick()
        if self.agent.tasks.items:
            self.agent.tasks.start_next()
        return result
    def loop(self):
        while not self.stop_event.wait(8):
            if self.running:
                try:self.tick()
                except Exception as exc:self.agent.store.event("runtime_error",{"error":str(exc)})
    def start(self):
        self.running=True; self.stop_event.clear()
        if not self.thread or not self.thread.is_alive():
            self.thread=Thread(target=self.loop,daemon=True); self.thread.start()
    def stop(self):
        self.running=False; self.stop_event.set()

runtime=Runtime()

class Handler(BaseHTTPRequestHandler):
    def send_json(self,payload,code=200):
        raw=json.dumps(payload).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(raw)))
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/state":
            snap=ecosystem_snapshot(runtime.agent); snap["runtime"]={"running":runtime.running,"tick_interval_seconds":8}
            self.send_json(snap); return
        if self.path in ("/","/index.html"):
            raw=DASHBOARD.read_bytes(); self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw)))
            self.end_headers(); self.wfile.write(raw); return
        self.send_json({"error":"not_found"},404)
    def do_POST(self):
        if self.path=="/api/tick": self.send_json(runtime.tick()); return
        if self.path=="/api/runtime/start": runtime.start(); self.send_json({"running":True}); return
        if self.path=="/api/runtime/stop": runtime.stop(); self.send_json({"running":False}); return
        self.send_json({"error":"not_found"},404)
    def log_message(self,*_): return

def serve(host="127.0.0.1",port=8765):
    print(f"Survival Genesis control center: http://{host}:{port}")
    ThreadingHTTPServer((host,port),Handler).serve_forever()
