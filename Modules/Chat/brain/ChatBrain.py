import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import config
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import sys

class ChatBrain:
    def __init__(self):
        self.llm = ChatOllama(
            model = config.MODEL_NAME,
            temperature = 0.6,
            top_k=35,
            top_p=0.92,
            repeat_penalty=1.1,
            seed=42,
            # other params ...
        )
        self.full = ""

    def stream(self, messages):
        print("--------------------//DEBUG//--------------------")
        print(messages)
        print("--------------------//DEBUG//--------------------")
        for chunk in self.llm.stream(messages):
            self.full += chunk.content
            yield chunk

    def get_full(self):
        return_message = self.full
        self.reset()
        return return_message

    def reset(self):
        self.full = ""

if __name__ == "__main__":
    brain = ChatBrain()
    # testing the brain with a few messages

    messages = [
        SystemMessage("You are Lilly, you act like a young woman. You will assist the user in their daily tasks, while keeping a conversation like a real human. Your answer should be short, just like a SMS."),
        HumanMessage("Hey Lilly, how are you?"),
    ]
    for chunk in brain.stream(messages):
        print(chunk.content, end="")

    print("\n\n--------------------//FULL TEXT//--------------------")
    print(brain.get_full())