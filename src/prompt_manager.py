from persona import Persona

class PromptManager:

    def __init__(self, persona:Persona, debug=False):
        self.persona = persona
        self.debug = debug

    def get_system_prompt(self):
        """
        Returns a system prompt as an Ollama message dict, constructed from the persona config.
        """
        persona = self.persona
        # Compose the system prompt string from persona attributes
        prompt_lines = []
        if persona.name and persona.mood_tags:
            prompt_lines.append(f"You are {persona.name}, a {', '.join(persona.mood_tags)} assistant.")
        elif persona.name:
            prompt_lines.append(f"You are {persona.name}, an assistant.")
        if persona.tone:
            prompt_lines.append(f"Your tone is: {persona.tone}.")
        if persona.guidelines:
            prompt_lines.append("Your guidelines are:")
            for g in persona.guidelines:
                prompt_lines.append(f"- {g}")
        if persona.greetings:
            prompt_lines.append(f"""Sample greetings: "{'", "'.join(persona.greetings)}\"""")
        system_prompt = "\n".join(prompt_lines)
        if self.debug:
            print("[PromptManager] System prompt generated:")
            print(system_prompt)
        return {"role": "system", "content": system_prompt}

if __name__ == "__main__":
    # Example usage
    persona = Persona("Lilly.json", debug=True)
    prompt_manager = PromptManager(persona, debug=True)
    system_prompt = prompt_manager.get_system_prompt()