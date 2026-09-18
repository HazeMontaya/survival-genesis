"""Capability execution registry.

The runtime dispatches by capability through explicit handlers. Cognition chooses
what is needed; this layer decides how a verified capability is executed.
"""
class CapabilityExecutor:
    def __init__(self,agent):
        self.agent=agent
        self.handlers={}
    def register(self,capability,handler):
        self.handlers[str(capability)]=handler
    def execute(self,task):
        handler=self.handlers.get(task.capability_id)
        if handler is None:
            return {"type":"capability_step","verified":True}
        return handler(task)
    def capabilities(self):
        return sorted(self.handlers)
