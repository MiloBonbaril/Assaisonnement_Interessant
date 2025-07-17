import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Assaisonnement Interessant CLI")
    parser.add_argument('--llm-model', type=str, default=None, help='Name of the LLM model to use (optional)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode (optional)')
    parser.add_argument('--persona', type=str, required=True, help='Persona to load (required)')
    return parser.parse_args()
