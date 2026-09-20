from dataclasses import dataclass
from typing import Callable

@dataclass
class Tool:
    name: str
    description: str
    fn: Callable
    side_effect: bool = False

class ToolDispatcher:
    def __init__(self, tools):
        self.tools = {tool.name: tool for tool in tools}

    def call(self, name, **kwargs):
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' is not allowed for this agent.")
        return self.tools[name].fn(**kwargs)

    def describe(self):
        return {k: v.description for k,v in self.tools.items()}
