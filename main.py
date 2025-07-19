from src.argparser import get_args
from src.persona import Persona
from src.ollama_interface import OllamaInterface
from src.prompt_manager import PromptManager
from src.memory_manager import MemoryManager

def main():
    args = get_args()
    print(f"Arguments received: {args}")
    if not args.llm_model:
        args.llm_model = "qwen3:4b"
    ollama_interface = OllamaInterface(model_name=args.llm_model, debug=args.debug)
    persona = Persona(args.persona, debug=args.debug)
    prompt_manager = PromptManager(persona, debug=args.debug)
    memory_manager = MemoryManager("./data/chats/memory.json", debug=args.debug)
    system_prompt = prompt_manager.get_system_prompt()
    greeting_messages = memory_manager.get_memory() + [system_prompt, {"role": "system", "content": "The user has entered the chat. Greet them appropriately."}]
    response = ""
    for chunk in ollama_interface.stream_response(messages=greeting_messages, think=True):
        print(f"{chunk}", end='', flush=True)
        response += chunk
    memory_manager.add_memory_entry({"role": "assistant", "content": response})
    print('\n')
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat.")
            break

        messages = memory_manager.get_memory() + [system_prompt, {"role": "user", "content": user_input}]
        memory_manager.add_memory_entry({"role": "user", "content": user_input})

        response = ""
        print(f"Assistant: ", end='', flush=True)
        for chunk in ollama_interface.stream_response(messages=messages, think=True):
            print(f"{chunk}", end='', flush=True)
            response += chunk

        memory_manager.add_memory_entry({"role": "assistant", "content": response})
        print('\n')

if __name__ == "__main__":
    main()