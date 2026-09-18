from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Event, Thread, Lock

@dataclass
class Heartbeat:
    name: str
    interval_seconds: int
    enabled: bool = True
    last_run: str = ""
    runs: int = 0
    failures: int = 0

class HeartbeatDaemon:
    def __init__(self,agent,interval_seconds=8):
        self.agent=agent
        self.items=[Heartbeat("world_cycle",interval_seconds),Heartbeat("maintenance",max(30,interval_seconds*4)),Heartbeat("audit",max(60,interval_seconds*8))]
        self.stop_event=Event(); self.thread=None; self.lock=Lock()

    def snapshot(self): return [asdict(x) for x in self.items]

    def start(self):
        if self.thread and self.thread.is_alive(): return
        self.stop_event.clear()
        self.thread=Thread(target=self._loop,daemon=True); self.thread.start()

    def stop(self): self.stop_event.set()

    def _loop(self):
        while not self.stop_event.wait(self.items[0].interval_seconds):
            hb=self.items[0]
            if not hb.enabled: continue
            try:
                with self.lock:
                    self.agent.tick()
                    self.agent.memory.age()
                    if self.agent.runtime_db.verify_event_chain() is False:
                        raise RuntimeError("runtime event chain verification failed")
                hb.last_run=datetime.now(timezone.utc).isoformat(); hb.runs+=1
            except Exception as exc:
                hb.failures+=1
                self.agent.store.event("heartbeat_error",{"error":str(exc)})
                self.agent.runtime_db.event("heartbeat_error",{"error":str(exc)},actor="heartbeat")
