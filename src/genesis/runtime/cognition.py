from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class CognitionResult:
    status:str
    turns:int
    mutations:int
    observations:list[dict]
    reason:str=""

class CognitionLoop:
    """Bounded ReAct-style execution boundary. The planner is never an authority bypass."""
    def __init__(self, policy, tools, max_turns=8):
        self.policy=policy; self.tools=tools; self.max_turns=max(1,int(max_turns))

    def run(self, planner, initial_context=None, actor="genesis-1", authority="self"):
        context=dict(initial_context or {})
        observations=[]; mutations=0; patterns={}
        for turn in range(1,self.max_turns+1):
            proposal=planner(context,tuple(observations))
            if not proposal:
                return CognitionResult("sleep",turn-1,mutations,observations,"planner returned no action")
            tool=proposal.get("tool")
            args=dict(proposal.get("args") or {})
            key=(tool,tuple(sorted((str(k),str(v)) for k,v in args.items())))
            patterns[key]=patterns.get(key,0)+1
            if patterns[key]>=3:
                return CognitionResult("loop_detected",turn-1,mutations,observations,"repeated identical action")
            args["_actor"]=actor; args["_authority"]=authority
            result=self.tools.call(tool,**args)
            observations.append({"turn":turn,"tool":tool,"result":result})
            if tool not in {"read_file","list_files","remember"}:
                mutations+=1
            context["last_result"]=result
            context["turn"]=turn
        return CognitionResult("budget_exhausted",self.max_turns,mutations,observations,"turn budget exhausted")
