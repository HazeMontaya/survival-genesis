from dataclasses import asdict, dataclass
from pathlib import Path
import json, os, subprocess, shlex

@dataclass
class ToolSpec:
    id: str
    description: str
    risk: str = "safe"
    enabled: bool = True

class ToolRegistry:
    """Local zero-cost tool layer. Dangerous capabilities are explicit and audited."""
    def __init__(self,root,store):
        self.root=Path(root).resolve()
        self.store=store
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
            base=self._path(kwargs.get("path",".")); result=[str(x.relative_to(self.root)) for x in base.rglob("*") if x.is_file()][:500]
        elif tool_id=="run_tests":
            result=subprocess.run([os.fspath(self.root/".venv/Scripts/python.exe") if (self.root/".venv/Scripts/python.exe").exists() else "python","-m","pytest","-q"],cwd=self.root,text=True,capture_output=True,timeout=120)
            result={"returncode":result.returncode,"stdout":result.stdout[-12000:],"stderr":result.stderr[-12000:]}
        elif tool_id=="run_python":
            module=kwargs["module"]
            if any(x in module for x in ("..","/","\\",";")): raise ValueError("invalid module")
            result=subprocess.run(["python","-m",module],cwd=self.root,text=True,capture_output=True,timeout=120)
            result={"returncode":result.returncode,"stdout":result.stdout[-12000:],"stderr":result.stderr[-12000:]}
        else:
            result=kwargs
        self.store.event("tool_called",{"tool":tool_id,"risk":spec.risk,"ok":True})
        return result
