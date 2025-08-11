from src.argparser import get_args
from src.persona import Persona
from src.ollama_interface import OllamaInterface
from src.prompt_manager import PromptManager
from src.memory_manager import MemoryManager
from src.tools import TimeTool
import logging

def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("main")
    logger.info(f"Arguments received: {args}")
    if not args.llm_model:
        args.llm_model = "qwen3:4b"
    ollama_interface = OllamaInterface(model_name=args.llm_model, debug=args.debug)
    persona = Persona(args.persona, debug=args.debug)
    tools = [TimeTool()]
    prompt_manager = PromptManager(persona, tools, debug=args.debug)
    memory_manager = MemoryManager(args.memory_file, tools, debug=args.debug)
    system_prompt = prompt_manager.get_system_prompt()
    if memory_manager.is_new_memory:
        greeting_messages = memory_manager.get_memory() + [system_prompt, {"role": "system", "content": f"It is the first time you meet the user. Greet them appropriately. You must introduce yourself as {persona.name}."}]
    else:
        greeting_messages = memory_manager.get_memory() + [system_prompt, {"role": "system", "content": "The user has entered the chat. Greet them appropriately."}]
    response = ""
    for chunk in ollama_interface.stream_response(messages=greeting_messages, think=True):
        print(f"{chunk}", end='', flush=True)
        response += chunk
    if args.debug:
        logger.debug("\n")
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
        if args.debug:
            logger.debug("\n")
        memory_manager.add_memory_entry({"role": "assistant", "content": response})
        print('\n')

if __name__ == "__main__":
    main()