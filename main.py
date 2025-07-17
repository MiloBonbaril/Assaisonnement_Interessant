from src.argparser import get_args
from src.persona import Persona
from src.ollama_interface import OllamaInterface
from src.prompt_manager import PromptManager

def main():
    args = get_args()
    print(f"Arguments received: {args}")
    if not args.llm_model:
        args.llm_model = "qwen3:4b"
    ollama_interface = OllamaInterface(model_name=args.llm_model, debug=args.debug)
    persona = Persona(args.persona, debug=args.debug)
    prompt_manager = PromptManager(persona, debug=args.debug)

if __name__ == "__main__":
    main()