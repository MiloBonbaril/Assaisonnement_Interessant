from Modules.Chat.memory.MemoryManager import MemoryManager
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

memory_manager = MemoryManager()

welcome_message = [
    SystemMessage("Lilly, you are now Online! Please welcome the user."),
    HumanMessage("Heyyy Lilly, welcome back!")
]

final_message = memory_manager.send_message_without_adding_in_memory(welcome_message)
print("Lilly: " + final_message)

# Set a loop to keep the program running
while True:
    # Get the user input
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "bye", "goodbye", "stop"]:
        break

    user_input = HumanMessage(user_input)
    # Add the user input to the memory
    final_message = memory_manager.send_message_with_memory(user_input)
    # Print the response
    print("Lilly: " + final_message)