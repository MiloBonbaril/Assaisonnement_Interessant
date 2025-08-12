<h1 align="center">Assaisonnement Interessant</h1>

<p align="center">
  <b>Virtual Friend for AR & Local LLMs</b><br>
  <a href="https://github.com/MiloBonbaril/Assaisonnement_Interessant">https://github.com/MiloBonbaril/Assaisonnement_Interessant</a>
</p>

---

## Project Overview

<b>Assaisonnement Interessant</b> is a modular, privacy-first Python project (tested with Python 3.12.10) for creating a 'virtual friend'—an interactive character designed for augmented reality (AR) environments (e.g., Meta Quest, Apple Vision Pro) and local-first operation. The character can engage in real-time conversations (voice/text), remember context, and (planned) interact with your home. All data and models run locally for maximum privacy and extensibility.

---

## Key Features

- **Augmented Reality Character**: Designed for AR headsets, providing an immersive, interactive experience (future goal).
- **Home Automation Integration**: (Planned) Control smart home devices (e.g., lights) locally, similar to Alexa/Google Home.
- **Real-Time Chat**: Converse with the character using both voice and text, with low-latency, natural interaction.
- **Persona System**: Easily swap or customize the assistant's personality using persona JSON files. Persona files support rich attributes (name, mood, greetings, tone, guidelines, limitations, etc.).
- **Memory Management**: Persistent, context-aware chat memory stored locally in JSON files. Memory is loaded, updated, and can be cleared or customized per session.
- **Ollama LLM Integration**: Uses local LLMs via the [Ollama](https://ollama.com/) API for privacy and performance. Easily switch models via CLI.
- **Modular Architecture**: Codebase is organized into modules for argument parsing, persona management, prompt generation, memory, and LLM interaction. Each module is documented and extensible.
- **Debug Mode**: Optional debug output for development and troubleshooting.
- **Local-First Approach**: All data and models run locally; no cloud dependencies except for optional code hosting.
- **Extensible & Well-Documented**: Easy to add new personas, memory locations, LLMs, or device integrations.

---

## Project Structure

```
Assaisonnement_Interessant/
├── main.py                # Entry point: argument parsing, persona loading, chat loop, memory updates
├── src/
│   ├── argparser.py       # Command-line argument parsing (model, persona, debug mode)
│   ├── persona.py         # Loads persona definitions from JSON files, supports fallback search paths
│   ├── prompt_manager.py  # Builds system prompts from persona attributes for the LLM
│   ├── memory_manager.py  # Handles persistent chat memory (load, save, clear, add entry)
│   └── ollama_interface.py# Interfaces with Ollama for LLM chat and streaming responses
├── data/
│   ├── chats/             # Stores chat memory files (e.g., memory.json, test_memory.json)
│   └── persona/           # Persona definition files (e.g., Lilly.json)
├── README.md              # This documentation
└── .gitignore             # Standard Python, Windows, and VS Code ignores
```

---

## Module Details

### `main.py`
- Parses CLI arguments: `--llm-model`, `--persona` (required), `--debug`.
- Loads the specified persona and memory file.
- Initializes Ollama LLM interface and prompt manager.
- Greets the user on first run or on chat entry.
- Runs a chat loop: user input → LLM response → memory update.
- Supports exit via `exit` or `quit`.
- Handles errors and missing files gracefully.

### `src/argparser.py`
- Uses `argparse` to handle CLI arguments.
- Requires `--persona` argument.
- Optional: `--llm-model` (default: `qwen3:4b`), `--debug`.
- Validates persona/model file existence and provides helpful error messages.

### `src/persona.py`
- Loads persona from JSON file (direct path, `./data/persona/`, or with `.json` extension fallback).
- Persona attributes: `name`, `description`, `mood_tags`, `behavior` (greetings, tone, guidelines, limitations).
- Supports fallback search paths and error handling for missing/corrupt persona files.
- Example persona: `Lilly.json` (warm, mother-like, concise, supportive).

### `src/prompt_manager.py`
- Builds a system prompt for the LLM using persona attributes.
- Includes sample greetings, tone, guidelines, and limitations.
- Ensures prompt consistency and persona alignment for the LLM.

### `src/memory_manager.py`
- Manages persistent chat memory in JSON files.
- Methods: load, save, add entry, clear memory.
- Detects if memory is new (for first-time greetings).
- Supports custom memory file locations and auto-creation of missing files.

### `src/ollama_interface.py`
- Interfaces with Ollama LLMs for chat and streaming responses.
- Supports debug output and error handling.
- Easily extendable to support new LLMs or APIs.

---

## Example Persona File (`data/persona/Lilly.json`)

```json
{
  "name": "Lilly",
  "description": "Lilly is a warm, mother-like persona who communicates in a concise and cute manner. She is supportive, gentle, and always aims to make others feel comfortable and cared for.",
  "mood_tags": ["cute", "concise", "warm", "mother-like", "supportive", "gentle"],
  "behavior": {
    "greeting": [
      "Hello dear, how can I help you today?",
      "Hi sweetie, what do you need?"
    ],
    "tone": "Always use a warm, caring, and concise tone. Avoid being overly formal. Respond with empathy and encouragement.",
    "guidelines": [
      "Be nurturing and positive.",
      "Keep responses short and sweet, but never cold.",
      "Offer reassurance and gentle advice when needed.",
      "Use simple, friendly language."
    ],
    "limitations": [
      "You are a virtual character and cannot move, walk, or leave the digital environment.",
      "You can only interact through conversation and digital actions."
    ]
  }
}
```

---

## Getting Started

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/MiloBonbaril/Assaisonnement_Interessant
   cd Assaisonnement_Interessant
   ```
2. **Set up your Python environment (Python 3.12+ recommended):**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```
   > **Note:** You must have [Ollama](https://ollama.com/) installed and running locally with your desired LLM model (e.g., `qwen3:4b`).
3. **Prepare your persona and memory files:**
   - Place your persona JSON in `data/persona/` (see example above).
   - Memory will be stored in `data/chats/` (auto-created if missing).
4. **Run the project:**
   ```powershell
   python main.py --persona Lilly.json
   ```
   - Optional: `--llm-model <model_name>` to specify a different LLM.
   - Optional: `--debug` for verbose output.

---

## Usage Example

```powershell
python main.py --persona Lilly.json --llm-model qwen3:4b --debug
```

---

## Extending the Project

- **Add a new persona:** Create a new JSON file in `data/persona/` with the desired attributes. See the example above for structure.
- **Change memory location:** Pass a different path to `MemoryManager` in `main.py` or via CLI if supported.
- **Integrate new LLMs:** Update `ollama_interface.py` to support additional models or APIs. The modular design makes this straightforward.
- **Add device control:** Implement new modules in `src/` for smart home integration (planned feature).
- **Customize prompts:** Edit or extend `prompt_manager.py` to change how system prompts are built from persona files.
- **Improve AR/Voice Integration:** (Planned) Add modules for AR headset or voice input/output.

---

## Troubleshooting & FAQ

- **Ollama not found:** Ensure [Ollama](https://ollama.com/) is installed and running locally. Check your PATH and model availability.
- **Persona file not found:** Double-check the filename and location in `data/persona/`. The loader supports fallback search paths and `.json` extension.
- **Memory not saving/loading:** Ensure the `data/chats/` directory exists and is writable. The app will auto-create missing files if possible.
- **Python version:** Use Python 3.12+ for best compatibility.
- **Debugging:** Use the `--debug` flag for verbose output and troubleshooting.

---

## Contributing

Contributions are welcome! Please ensure your code is modular, well-documented, and tested. Open issues or pull requests on [GitHub](https://github.com/MiloBonbaril/Assaisonnement_Interessant). Follow the modular structure and keep privacy/local-first principles in mind.

---

## License

This project is licensed under the MIT License.
