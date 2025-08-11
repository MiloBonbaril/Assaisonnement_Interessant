import argparse


def get_args():
    parser = argparse.ArgumentParser(description="Assaisonnement Interessant CLI")
    parser.add_argument('--llm-model', type=str, default=None,
                        help='Name of the LLM model to use (optional)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (optional)')
    parser.add_argument('--persona', type=str, required=True,
                        help='Persona to load (required)')
    parser.add_argument('--memory_file', type=str,
                        default='./data/chats/{persona}.json',
                        help='Path to the memory file (optional, '
                             'default: ./data/chats/{persona}.json)')
    parser.add_argument('--audio', action='store_true',
                        help='Enable audio output (optional)')
    parser.add_argument('--voice', type=str, default='default',
                        help='Voice to use for audio output (optional)')
    # format the memory file path to include the persona name
    args = parser.parse_args()
    args.memory_file = args.memory_file.format(persona=args.persona)
    return args
