

import json
import os
import logging

class Persona:
    def __init__ (self, persona_file, debug=False):
        self.debug = debug
        self.logger = logging.getLogger("Persona")
        self.name = ""
        self.mood_tags = []
        self.greetings = []
        self.tone = ""
        self.guidelines = []
        self.limitations = []
        self.load_persona(persona_file)


    def load_persona_file(self, persona_file):
        # If absolute path, only try that path
        if os.path.isabs(persona_file):
            try:
                with open(persona_file, 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                raise FileNotFoundError(f"Persona file '{persona_file}' not found.")
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in persona file '{persona_file}'.")
        # Otherwise, try relative and fallback locations
        try:
            with open(persona_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            try:
                with open(f"./data/persona/{persona_file}", 'r') as file:
                    return json.load(file)
            except FileNotFoundError:
                try:
                    with open(f"./data/persona/{persona_file}.json", 'r') as file:
                        return json.load(file)
                except FileNotFoundError:
                    raise FileNotFoundError(f"Persona file '{persona_file}' not found in current or data directory.")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in persona file '{persona_file}'.")

    def load_persona(self, persona_file):
        self.persona_data = self.load_persona_file(persona_file)
        self.name = self.persona_data.get("name", "")
        self.mood_tags = self.persona_data.get("mood_tags", [])
        behavior = self.persona_data.get("behavior", {})
        self.greetings = behavior.get("greeting", [])
        self.tone = behavior.get("tone", "")
        self.guidelines = behavior.get("guidelines", [])
        self.limitations = behavior.get("limitations", [])
        if self.debug:
            self.logger.debug(f"Persona name: {self.name}")
            self.logger.debug(f"Mood tags: {self.mood_tags}")
            self.logger.debug(f"Greetings: {self.greetings}")
            self.logger.debug(f"Tone: {self.tone}")
            self.logger.debug(f"Guidelines: {self.guidelines}")
            self.logger.debug(f"Limitations: {self.limitations}")

    def __str__(self):
        return f"Persona(name={self.name}, mood_tags={self.mood_tags}, greetings={self.greetings}, tone={self.tone}, guidelines={self.guidelines})"