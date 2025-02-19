import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from Modules.Chat.brain.ChatBrain import ChatBrain
import config
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import gettext

class MemoryManager:
    def __init__(self, translation=None):
        if translation is not None:
            self._ = translation
        else:
            self._ = lambda x: x
        self.brain = ChatBrain()
        self.path = config.CONVERSATION_MEMORY_PATH
        if os.path.exists(self.path):
            self.memory = []
            self.load()
        else:
            self.memory = []
            self.init_memory()
        self.memo_id = 0

    def init_memory(self):
        messages = [
            SystemMessage(self._("You are Lilly, you act like a young woman. You will assist the user in their daily tasks, while keeping a conversation like a real human. Your answer should be short, just like a SMS."))
        ]
        if config.DEBUG:
            print("Memory file does not exist. Creating a new one...")
        self.add_message_to_memory(messages)

    def load(self):
        with open(self.path, "r") as file:
            if config.DEBUG:
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
            if config.DEBUG:
                print("Message is a list")
            for m in message:
                if isinstance(m, SystemMessage):
                    if config.DEBUG:
                        print("Message is a SystemMessage")
                    self.memory.append(m)
                elif isinstance(m, HumanMessage):
                    if config.DEBUG:
                        print("Message is a HumanMessage")
                    self.memory.append(m)
                elif isinstance(m, AIMessage):
                    if config.DEBUG:
                        print("Message is an AIMessage")
                    self.memory.append(m)
        else:
            if isinstance(message, SystemMessage):
                if config.DEBUG:
                    print("Message is a SystemMessage")
                self.memory.append(message)
            elif isinstance(message, HumanMessage):
                if config.DEBUG:
                    print("Message is a HumanMessage")
                self.memory.append(message)
            elif isinstance(message, AIMessage):
                if config.DEBUG:
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
        if config.DEBUG:
            print("Saving memory...")
        with open(self.path, "w") as file:
            json.dump(save_data, file, indent=4)

    def send_message_without_adding_in_memory(self, message=None, include_memory=True):
        messages = []
        if include_memory:
            for m in self.memory:
                messages.append(m)
        if message is not None:
            if isinstance(message, list):
                for m in message:
                    messages.append(m)
            else:
                messages.append(message)
        for chunk in self.brain.stream(messages):
            if config.DEBUG:
                print(chunk.content, end="")
            else:
                continue
        full_message = self.brain.get_full()
        if config.DEBUG:
            print("\n\n--------------------//FULL TEXT//--------------------")
            print(full_message)
        return full_message

    def send_message_with_memory(self, message):
        memory_status = self.check_memory()
        if memory_status:
            print("Memmory has been summarized. Please consider to take a look.")
            return
        self.add_message_to_memory(message)
        full_message = self.send_message_without_adding_in_memory()
        self.add_message_to_memory(AIMessage(full_message))
        return full_message

    def get_memory_id(self):
        # check inside a 'data' folder how many files are there and return the number of files + 1
        os.makedirs("data", exist_ok=True)
        files = os.listdir("data")
        return len(files) + 1

    def soft_reset_memory(self):
        # save the memory in a file inside 'data' folder, following the id and reset the memory
        self.memo_id = self.get_memory_id()
        if config.DEBUG:
            print(f"Saving memory in data/conv_{self.memo_id}.json")
        with open(f"data/conv_{self.memo_id}.json", "w") as file:
            save_data = []
            for message in self.memory:
                if isinstance(message, SystemMessage):
                    save_data.append({"type": "SystemMessage", "content": message.content})
                elif isinstance(message, HumanMessage):
                    save_data.append({"type": "HumanMessage", "content": message.content})
                elif isinstance(message, AIMessage):
                    save_data.append({"type": "AIMessage", "content": message.content})
            json.dump(save_data, file, indent=4)
        self.reset_memory()

    def reset_memory(self):
        self.memory = []
        self.save()

    def count_token_in_memory(self):
        count = 0
        for message in self.memory:
            count += len(message.content.split())
        return count

    def verify_memory_length(self):
        print("Memory length:", self.count_token_in_memory())
        if self.count_token_in_memory() > config.MAX_TOKEN_LENGTH:
            return True
        return False

    def summarize_memory(self):
        # take all the memory and summarize it with the AI using a complex system prompt
        print("Summarizing memory...")
        prompt = self.memory + [
            SystemMessage(self._("You are Lilly, you act like a young woman. Your goal now is to summarize the conversation you had with the user, just like you tell your future self what you did and what you tell to the user. You should keep the conversation short and to the point, while keeping as much as possible personnal information about yourself and the user. AND of course KEEP major events!")),
            HumanMessage(self._("Can you summarize the conversation we had?")),
        ]
        summary = self.send_message_without_adding_in_memory(prompt, include_memory=False)
        # ask the user if the summary is good
        print("--------------------//SUMMARY//--------------------")
        print("Summary:", summary)
        print("--------------------//SUMMARY//--------------------")
        print("Is the summary good?")
        user_response = input()
        if user_response.lower() in ["yes", "y", "ok", "sure", "fine", "good"]:
            print("Ok, I will reset the memory.")
            self.soft_reset_memory()
            messages = [
                SystemMessage(self._("The conversation was summarized by the AI and the user confirmed it was good. The following message is the summary of the conversation.")),
                AIMessage(summary),
                SystemMessage(self._("You can now act normal. You are Lilly, you act like a young woman. You will assist the user in their daily tasks, while keeping a conversation like a real human. Your answer should be short, just like a SMS."))
            ]
            self.add_message_to_memory(messages)
        else:
            print("Ok, I will keep the memory as it is.")

    def check_memory(self, force_summarize=False):
        if self.verify_memory_length() or force_summarize:
            self.summarize_memory()
            return True
        return False

    def __str__(self):
        # return the memory in a string format, and listed properly
        string = ""
        for message in self.memory:
            if isinstance(message, SystemMessage):
                string += f"System: {message.content}\n"
            elif isinstance(message, HumanMessage):
                string += f"Human: {message.content}\n"
            elif isinstance(message, AIMessage):
                string += f"AI: {message.content}\n"
        return string

if __name__ == "__main__":
    memory = MemoryManager()
    print("Memory:", memory)
    """ 
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
    print(memory.memory) """
    #print(memory.check_memory(force_summarize=True))