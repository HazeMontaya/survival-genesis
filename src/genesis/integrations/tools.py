from dataclasses import asdict, dataclass
from pathlib import Path
import os, subprocess

@dataclass
class ToolSpec:
    id: str
    description: str
    risk: str = "safe"
    enabled: bool = True

class ToolRegistry:
    """Local zero-cost tool layer with explicit, auditable handlers."""
    def __init__(self,root,store,memory=None,messages=None):
        self.root=Path(root).resolve()
        self.store=store
        self.memory=memory
        self.messages=messages
        self.specs=[
            ToolSpec("read_file","Read a project file","safe"),
            ToolSpec("write_file","Write a project file inside the workspace","caution"),
            ToolSpec("list_files","List files inside the project","safe"),
            ToolSpec("run_tests","Run the repository test suite","caution"),
            ToolSpec("run_python","Run a Python module/script from the project","caution"),
            ToolSpec("remember","Persist a verified observation","safe"),
            ToolSpec("send_message","Send a message to another agent","safe"),
        ]

    def snapshot(self): return [asdict(x) for x in self.specs]

    def _path(self,relative):
        p=(self.root/relative).resolve()
        if self.root not in p.parents and p != self.root:
            raise PermissionError("path escapes project root")
        return p

    def call(self,tool_id,**kwargs):
        spec=next((x for x in self.specs if x.id==tool_id),None)
        if not spec or not spec.enabled: raise RuntimeError(f"tool unavailable: {tool_id}")
        if tool_id=="read_file":
            p=self._path(kwargs["path"]); result=p.read_text(encoding="utf-8")
        elif tool_id=="write_file":
            p=self._path(kwargs["path"]); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(kwargs["content"],encoding="utf-8"); result={"path":str(p)}
        elif tool_id=="list_files":
            base=self._path(kwargs.get("path","."))
            result=[str(x.relative_to(self.root)) for x in base.rglob("*") if x.is_file()][:500]
        elif tool_id=="run_tests":
            python=os.fspath(self.root/".venv/Scripts/python.exe") if (self.root/".venv/Scripts/python.exe").exists() else "python"
            proc=subprocess.run([python,"-m","pytest","-q"],cwd=self.root,text=True,capture_output=True,timeout=120)
            result={"returncode":proc.returncode,"stdout":proc.stdout[-12000:],"stderr":proc.stderr[-12000:]}
        elif tool_id=="run_python":
            module=kwargs["module"]
            if any(x in module for x in ("..","/","\\",";")): raise ValueError("invalid module")
            proc=subprocess.run(["python","-m",module],cwd=self.root,text=True,capture_output=True,timeout=120)
            result={"returncode":proc.returncode,"stdout":proc.stdout[-12000:],"stderr":proc.stderr[-12000:]}
        elif tool_id=="remember":
            if not self.memory: raise RuntimeError("memory handler unavailable")
            kind=str(kwargs.get("kind","observation"))
            content=str(kwargs["content"])
            confidence=float(kwargs.get("confidence",0.8))
            self.memory.remember(kind,content,confidence)
            result={"remembered":True,"kind":kind,"content":content,"confidence":confidence}
        elif tool_id=="send_message":
            if not self.messages: raise RuntimeError("message handler unavailable")
            message=self.messages.send(
                str(kwargs["sender"]),
                str(kwargs["recipient"]),
                str(kwargs["content"]),
                str(kwargs.get("kind","task")),
            )
            result={"sent":True,"message_id":message.id}
        self.store.event("tool_called",{"tool":tool_id,"risk":spec.risk,"ok":True})
        return result
