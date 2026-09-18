from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Lock
from pathlib import Path
import json
from genesis.runtime.agent import GenesisAgent
from genesis.runtime.heartbeat import HeartbeatDaemon
ROOT=Path(__file__).resolve().parents[2];WORLD=ROOT/"world"/"index.html"
class Runtime:
 def __init__(self):self.agent=GenesisAgent();self.running=False;self.lock=Lock();self.heartbeat=HeartbeatDaemon(self.agent)
 def tick(self):
  with self.lock:return self.agent.tick()
 def start(self):self.running=True;self.heartbeat.start()
 def stop(self):self.running=False;self.heartbeat.stop()
runtime=Runtime()
class Handler(BaseHTTPRequestHandler):
 def send_json(self,x,code=200):
  b=json.dumps(x,ensure_ascii=False).encode();self.send_response(code);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path=="/api/state":s=runtime.agent.snapshot();s["runtime"]={"running":runtime.running,"heartbeat":runtime.heartbeat.snapshot()};return self.send_json(s)
  if self.path in ("/","/index.html"):b=WORLD.read_bytes();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b);return
  self.send_json({"error":"not_found"},404)
 def do_POST(self):
  if self.path=="/api/tick":return self.send_json(runtime.tick())
  if self.path=="/api/runtime/start":runtime.start();return self.send_json({"running":True})
  if self.path=="/api/runtime/stop":runtime.stop();return self.send_json({"running":False})
  self.send_json({"error":"not_found"},404)
 def log_message(self,*a):pass
def serve(host="127.0.0.1",port=8765):ThreadingHTTPServer((host,port),Handler).serve_forever()
