# AGENTS

These instructions apply to the `src/` directory.

## Code Style
- Write Python modules with clear separation of concerns.
- Use snake_case for functions and variables; use PascalCase for classes.
- Include type hints and docstrings for all public objects.
- Avoid hard-coded paths; accept configuration through parameters or environment variables.

## Design Notes
- Implement features to support text, audio, and visual interaction modes.
- Structure code so new tools and modalities can be integrated easily.
- Keep functions reasonably short (under ~50 lines) and focused on a single task.

