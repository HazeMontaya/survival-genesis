from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from threading import Event, Thread, Lock
import time

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

    def _run_item(self, item):
        if item.name == "world_cycle":
            self.agent.tick()
        elif item.name == "maintenance":
            self.agent.memory.age()
            self.agent.world.sync(self.agent)
        elif item.name == "audit":
            if self.agent.runtime_db.verify_event_chain() is False:
                raise RuntimeError("runtime event chain verification failed")
        item.last_run=datetime.now(timezone.utc).isoformat()
        item.runs += 1

    def _loop(self):
        next_due = {item.name: time.monotonic() + item.interval_seconds for item in self.items}
        while not self.stop_event.wait(1.0):
            now = time.monotonic()
            for item in self.items:
                if not item.enabled or now < next_due[item.name]:
                    continue
                try:
                    with self.lock:
                        self._run_item(item)
                except Exception as exc:
                    item.failures += 1
                    self.agent.store.event("heartbeat_error", {"heartbeat": item.name, "error": str(exc)})
                    self.agent.runtime_db.event("heartbeat_error", {"heartbeat": item.name, "error": str(exc)}, actor="heartbeat")
                finally:
                    next_due[item.name] = now + item.interval_seconds
