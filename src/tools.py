import abc
from datetime import datetime

class Tool(abc.ABC):
    @abc.abstractmethod
    def get_tool_prompt(self) -> str:
        """Return a string describing the tool for the system prompt."""
        pass

    @abc.abstractmethod
    def call_tool(self, args=None):
        """Call the tool with optional arguments."""
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass

class TimeTool(Tool):
    def get_tool_prompt(self) -> str:
        now = datetime.now()
        return now.strftime("The current date and time is %Y-%m-%d %H:%M:%S.")

    def call_tool(self, args=None):
        return None

    def get_name(self) -> str:
        return "time"

    def get_description(self) -> str:
        return "Returns the current date and time."