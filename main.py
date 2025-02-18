from Modules.Chat.memory.MemoryManager import MemoryManager
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from datetime import datetime

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
    # adding a system message right before the user input to tell the date and hour of the conversation
    current_date = datetime.now()
    system_message = SystemMessage(f"Today is {current_date.strftime('%d/%m/%Y')} and the time is {current_date.strftime('%H:%M:%S')}")
    # Send the system message
    memory_manager.add_message_to_memory(system_message)
    # Add the user input to the memory
    final_message = memory_manager.send_message_with_memory(user_input)
    # Print the response
    print("Lilly: " + final_message)