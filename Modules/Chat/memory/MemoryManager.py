import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Modules.Chat.brain.ChatBrain import ChatBrain
import config
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

class MemoryManager:
    def __init__(self):
        self.brain = ChatBrain()
        self.path = config.CONVERSATION_MEMORY_PATH
        if os.path.exists(self.path):
            self.memory = []
            self.load()
        else:
            self.memory = []

    def load(self):
        with open(self.path, "r") as file:
            print("Loading memory...")
            load_data = json.load(file)
        for message in load_data:
            if message["type"] == "SystemMessage":
                self.memory.append(SystemMessage(message["content"]))
            elif message["type"] == "HumanMessage":
                self.memory.append(HumanMessage(message["content"]))
            elif message["type"] == "AIMessage":
                self.memory.append(AIMessage(message["content"]))

    def add_message_to_memory(self, message):
        if isinstance(message, list):
            print("Message is a list")
            for m in message:
                if isinstance(m, SystemMessage):
                    print("Message is a SystemMessage")
                    self.memory.append(m)
                elif isinstance(m, HumanMessage):
                    print("Message is a HumanMessage")
                    self.memory.append(m)
                elif isinstance(m, AIMessage):
                    print("Message is an AIMessage")
                    self.memory.append(m)
        else:
            if isinstance(message, SystemMessage):
                print("Message is a SystemMessage")
                self.memory.append(message)
            elif isinstance(message, HumanMessage):
                print("Message is a HumanMessage")
                self.memory.append(message)
            elif isinstance(message, AIMessage):
                print("Message is an AIMessage")
                self.memory.append(message)
        self.save()

    def save(self):
        save_data = []
        for message in self.memory:
            if isinstance(message, SystemMessage):
                save_data.append({"type": "SystemMessage", "content": message.content})
            elif isinstance(message, HumanMessage):
                save_data.append({"type": "HumanMessage", "content": message.content})
            elif isinstance(message, AIMessage):
                save_data.append({"type": "AIMessage", "content": message.content})
        with open(self.path, "w") as file:
            json.dump(save_data, file, indent=4)

    def send_message_without_adding_in_memory(self, message=None):
        messages = []
        for m in self.memory:
            messages.append(m)
        if message is not None:
            if isinstance(message, list):
                for m in message:
                    messages.append(m)
            else:
                messages.append(message)
        for chunk in self.brain.stream(messages):
            print(chunk.content, end="")
        print("\n\n--------------------//FULL TEXT//--------------------")
        full_message = self.brain.get_full()
        print(full_message)
        return full_message

    def send_message_with_memory(self, message):
        self.add_message_to_memory(message)
        full_message = self.send_message_without_adding_in_memory()
        self.add_message_to_memory(AIMessage(full_message))
        return full_message

    def reset_memory(self):
        self.memory = []
        self.save()

if __name__ == "__main__":
    memory = MemoryManager()
    # resetting the memory to test the memory
    memory.reset_memory()
    test_question = "how are you?"
    messages = [
        SystemMessage("You are Lilly, you act like a young woman. You will assist the user in their daily tasks, while keeping a conversation like a real human. Your answer should be short, just like a SMS."),
    ]
    memory.add_message_to_memory(messages)
    print(memory.memory)

    # sending a message without memory with my name so we can test the memory
    message = HumanMessage("Hey Lilly! my name is Milo.")
    memory.send_message_without_adding_in_memory(message)
    print(memory.memory)
    message = HumanMessage("What's my name?")
    memory.send_message_without_adding_in_memory(message)
    print(memory.memory)

    # sending a message with memory
    message = HumanMessage("Hey Lilly! my name is Milo.")
    memory.send_message_with_memory(message)
    print(memory.memory)
    message = HumanMessage("What's my name?")
    memory.send_message_with_memory(message)
    print(memory.memory)
