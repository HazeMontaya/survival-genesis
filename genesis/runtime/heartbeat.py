from threading import Event,Thread,Lock
from dataclasses import asdict,dataclass
from datetime import datetime,timezone
@dataclass
class Heartbeat:name:str;interval_seconds:int;enabled:bool=True;last_run:str="";runs:int=0;failures:int=0
class HeartbeatDaemon:
 def __init__(self,agent,interval_seconds=8):self.agent=agent;self.item=Heartbeat("world_cycle",interval_seconds);self.stop_event=Event();self.thread=None;self.lock=Lock()
 def snapshot(self):return [asdict(self.item)]
 def start(self):
  if self.thread and self.thread.is_alive():return
  self.stop_event.clear();self.thread=Thread(target=self._loop,daemon=True);self.thread.start()
 def stop(self):self.stop_event.set()
 def _loop(self):
  while not self.stop_event.wait(self.item.interval_seconds):
   try:
    with self.lock:self.agent.tick()
    self.item.last_run=datetime.now(timezone.utc).isoformat();self.item.runs+=1
   except Exception as e:self.item.failures+=1;self.agent.db.event("heartbeat_error",{"error":str(e)})
