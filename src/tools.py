import abc
from datetime import datetime

class Tool(abc.ABC):
    @abc.abstractmethod
    def get_tool_prompt(self) -> str:
        """Return a string from the tool for the system prompt."""
        pass

    @abc.abstractmethod
    def get_tool_memory(self) -> str:
        """Return a string from the tool for the memory prompt."""
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
    def __init__(self):
        # Initialize the tool with the current date and time
        self.now = datetime.now()

    def get_tool_prompt(self) -> str:
        self.now = datetime.now()
        return self.now.strftime("The current date and time is %Y-%m-%d %H:%M:%S.")

    def get_tool_memory(self) -> str:
        self.now = datetime.now()
        return self.now.strftime("Current date and time: %Y-%m-%d %H:%M:%S.")

    def call_tool(self, args=None):
        return None

    def get_name(self) -> str:
        return "time"

    def get_description(self) -> str:
        return "Returns the current date and time."