
from src.persona import Persona
import logging

class PromptManager:

    def __init__(self, persona:Persona, tools=None, debug=False):
        self.persona = persona
        self.debug = debug
        self.tools = tools if tools is not None else []
        self.logger = logging.getLogger("PromptManager")

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
        # Add limitations if present
        limitations = getattr(persona, "limitations", [])
        if limitations:
            prompt_lines.append("Your limitations are:")
            for l in limitations:
                prompt_lines.append(f"- {l}")
        if persona.greetings:
            joined = '", "'.join(persona.greetings)
            prompt_lines.append(f'Sample greetings: "{joined}"')
        # Add tools if available
        for tool in self.tools:
            tool_prompt = tool.get_tool_prompt()
            if tool_prompt:
                prompt_lines.append(tool_prompt)
        system_prompt = "\n".join(prompt_lines)
        if self.debug:
            self.logger.debug("System prompt generated:")
            self.logger.debug(system_prompt)
        return {"role": "system", "content": system_prompt}

if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(level=logging.DEBUG)
    persona = Persona("Lilly.json", debug=True)
    prompt_manager = PromptManager(persona, debug=True)
    system_prompt = prompt_manager.get_system_prompt()