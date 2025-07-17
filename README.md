## Assaisonnement Interessant

### Project Overview

**Assaisonnement Interessant** is a Python 1.13.1 project with the ambitious goal of creating a 'virtual friend'—an interactive character designed for augmented reality (AR) environments, such as Meta Quest or Apple Vision Pro. The ultimate vision is to have this character interact with your home (e.g., controlling lights like Alexa or Google Home) and, most importantly, engage in real-time conversations via voice and/or text.

---

### Key Features

- **Augmented Reality Character**: Designed for AR headsets, providing an immersive, interactive experience.
- **Home Automation Integration**: Control smart home devices (e.g., lights) locally, similar to Alexa/Google Home.
- **Real-Time Chat**: Converse with the character using both voice and text, with a focus on low-latency, natural interaction.
- **Modular Architecture**: Highly modular and extensible codebase, organized into modules and sub-modules for easy maintenance and scalability.
- **Local-First Approach**: Prioritizes local execution for privacy and performance. Only databases and code hosting (GitHub) are remote.

---

### Project Structure

- `main.py`: Entry point for the application.
- `src/`: Contains core modules and sub-modules (e.g., argument parsing, interaction logic, device control, chat engine, etc.).

---

### Goals

1. **Immersive AR Experience**: Bring a virtual friend to life in your living space.
2. **Smart Home Interaction**: Enable the character to control and respond to home devices.
3. **Conversational AI**: Support seamless, real-time voice and text chat.
4. **Performance & Modularity**: Ensure the project is highly optimized and easy to extend.
5. **Local-First**: Minimize cloud dependencies for privacy and speed.

---

### Getting Started

1. **Clone the repository:**
   ```powershell
   git clone <your-github-repo-url>
   cd Assaisonnement_Interessant
   ```
2. **Set up your Python environment (Python 1.13.1):**
   ```powershell
   # Example using venv
   python -m venv venv
   .\venv\Scripts\Activate
   pip install -r requirements.txt
   ```
3. **Run the project:**
   ```powershell
   python main.py
   ```

---

### Contributing

Contributions are welcome! Please ensure your code is modular, well-documented, and tested. Open issues or pull requests on GitHub.

---

### License

This project is licensed under the MIT License.
