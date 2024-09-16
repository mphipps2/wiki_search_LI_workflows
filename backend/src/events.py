from llama_index.core.workflow import Event
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import ToolSelection, ToolOutput
from typing import List

class PrepEvent(Event):
    pass

class InputEvent(Event):
    input: List[ChatMessage]

class ToolCallEvent(Event):
    tool_calls: List[ToolSelection]

class FunctionOutputEvent(Event):
    output: ToolOutput
