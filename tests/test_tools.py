
import pytest
from src.tools import Tool, TimeTool
from datetime import datetime

def test_tool_abc_methods():
    # Tool is abstract, cannot instantiate directly
    with pytest.raises(TypeError):
        Tool()

def test_time_tool_prompt_and_metadata():
    tool = TimeTool()
    prompt = tool.get_tool_prompt()
    # The prompt should contain the current date and time (format check)
    now = datetime.now().strftime("%Y-%m-%d")
    assert now in prompt
    assert tool.get_name() == "time"
    assert "date and time" in tool.get_description().lower()

def test_time_tool_call_tool():
    tool = TimeTool()
    # call_tool returns None in current implementation
    assert tool.call_tool() is None
