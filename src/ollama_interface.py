
import ollama
import logging

class OllamaInterface:
    def __init__(self, model_name, tools=None, debug=False):
        self.model_name = model_name
        self.debug = debug
        self.attemps = 3
        self.tools = tools if tools is not None else []
        self.logger = logging.getLogger("OllamaInterface")

    def generate_response(self, messages=None, think=False):
        if self.debug:
            self.logger.debug(f"Generating response for prompt: {messages[-1]} using model: {self.model_name}")

        for attempt in range(self.attemps):
            try:
                response = ollama.chat(model=self.model_name, messages=messages, think=think)
                if self.debug:
                    self.logger.debug(f"Response received: {response}")
                break
            except Exception as e:
                if self.debug:
                    self.logger.debug(f"Attempt {attempt + 1} failed with error: {e}")
                if attempt == self.attemps - 1:
                    raise e

        return response['message']['content']

    def stream_response(self, messages=None, think=False):
        if self.debug:
            self.logger.debug(f"Streaming response for prompt: {messages[-1]} using model: {self.model_name}")

        ollama_tools = []
        for tool in self.tools:
            ollama_tools.append({
                "name": tool.get_name(),
                "description": tool.get_description()
            })

        stream = ollama.chat(model=self.model_name, messages=messages, stream=True, think=think)

        for chunk in stream:
            yield chunk['message']['content']

if __name__ == "__main__":
    # Example usage
    import logging
    logging.basicConfig(level=logging.DEBUG)
    ollama_interface = OllamaInterface(model_name="qwen3:4b", debug=True)
    messages = [{"role": "user", "content": "Hello, I'm Milo, nice to meet you!"}]
    for chunk in ollama_interface.stream_response(messages=messages, think=False):
        print(f"{chunk}", end='', flush=True)
    print("\n\nGenerating response with thinking...\n")
    for chunk in ollama_interface.stream_response(messages=messages, think=True):
        print(f"{chunk}", end='', flush=True)