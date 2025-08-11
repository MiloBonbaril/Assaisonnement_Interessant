# AGENTS

These instructions apply to the entire repository unless a more specific `AGENTS.md` overrides them.

## Project Goals
- Build a multimodal AI assistant that users can interact with through text, audio, or visual inputs.
- The assistant can respond via the same channels and use tools such as home automation or other AI agents to assist with daily tasks.

## Development Guidelines
- Use Python 3.10 or newer.
- Follow PEP8 style conventions and keep lines under 88 characters.
- Provide type hints and docstrings for all public functions and classes.
- Keep code modular to ease adding new modalities or tools.
- Place implementation code inside `src/` and corresponding tests inside `tests/`.
- When changing code, update or add relevant tests and run `pytest` from the repository root before committing.

