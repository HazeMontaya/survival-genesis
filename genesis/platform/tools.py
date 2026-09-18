from dataclasses import asdict,dataclass
from pathlib import Path
import os,subprocess
@dataclass
class ToolSpec:id:str;description:str;risk:str="safe";enabled:bool=True
class ToolRegistry:
 def __init__(self,root,store,memory,messages,policy):self.root=Path(root).resolve();self.store=store;self.memory=memory;self.messages=messages;self.policy=policy;self.specs=[ToolSpec("read_file","Read a project file"),ToolSpec("write_file","Write a project file","caution"),ToolSpec("list_files","List project files"),ToolSpec("run_tests","Run tests","caution"),ToolSpec("run_python","Run a Python module","caution"),ToolSpec("remember","Persist an observation"),ToolSpec("send_message","Send a message","caution")]
 def snapshot(self):return [asdict(x) for x in self.specs]
 def _path(self,r):
  p=(self.root/r).resolve()
  if self.root not in p.parents and p!=self.root:raise PermissionError("path escapes project root")
  return p
 def call(self,i,actor="genesis-1",authority="self",**k):
  if not any(x.id==i and x.enabled for x in self.specs):raise RuntimeError(f"tool unavailable: {i}")
  d=self.policy.evaluate(i,k,actor,authority)
  if not d.allowed:raise PermissionError(d.reason)
  if i=="read_file":r=self._path(k["path"]).read_text(encoding="utf-8")
  elif i=="write_file":p=self._path(k["path"]);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(k["content"],encoding="utf-8");r={"path":str(p)}
  elif i=="list_files":r=[str(x.relative_to(self.root)) for x in self._path(k.get("path",".")).rglob("*") if x.is_file()][:500]
  elif i=="run_tests":
   py=os.fspath(self.root/".venv/Scripts/python.exe") if (self.root/".venv/Scripts/python.exe").exists() else "python";p=subprocess.run([py,"-m","pytest","-q"],cwd=self.root,text=True,capture_output=True,timeout=120);r={"returncode":p.returncode,"stdout":p.stdout[-12000:],"stderr":p.stderr[-12000:]}
  elif i=="run_python":
   m=k["module"]
   if any(x in m for x in ("..","/","\\",";")):raise ValueError("invalid module")
   p=subprocess.run(["python","-m",m],cwd=self.root,text=True,capture_output=True,timeout=120);r={"returncode":p.returncode,"stdout":p.stdout[-12000:],"stderr":p.stderr[-12000:]}
  elif i=="remember":self.memory.remember(str(k.get("kind","observation")),str(k["content"]),float(k.get("confidence",.8)));r={"remembered":True}
  else:r={"sent":True,"message_id":self.messages.send(str(k["sender"]),str(k["recipient"]),str(k["content"]),str(k.get("kind","task"))).id}
  self.store.save(self.store.load());self.store_event(i,actor,d.risk);return r
 def store_event(self,i,a,r):self.db_event(i,a,r)
 def db_event(self,i,a,r):self.policy.db.event("tool_called",{"tool":i,"risk":r,"ok":True},a)
