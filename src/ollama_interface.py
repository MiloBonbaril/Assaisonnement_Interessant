import ollama

class OllamaInterface:
    def __init__(self, model_name, debug=False):
        self.model_name = model_name
        self.debug = debug

    def generate_response(self, messages=None, think=False):
        if self.debug:
            print(f"Generating response for prompt: {messages[-1]} using model: {self.model_name}")

        response = ollama.chat(model=self.model_name, messages=messages, think=think)

        return response['message']['content']

    def stream_response(self, messages=None, think=False):
        if self.debug:
            print(f"Streaming response for prompt: {messages[-1]} using model: {self.model_name}")

        stream = ollama.chat(model=self.model_name, messages=messages, stream=True, think=think)

        for chunk in stream:
            yield chunk['message']['content']



if __name__ == "__main__":
    # Example usage
    ollama_interface = OllamaInterface(model_name="qwen3:4b", debug=True)
    messages = [{"role": "user", "content": "Hello, I'm Milo, nice to meet you!"}]
    for chunk in ollama_interface.stream_response(messages=messages, think=False):
        print(f"{chunk}", end='', flush=True)
    print("\n\nGenerating response with thinking...\n")
    for chunk in ollama_interface.stream_response(messages=messages, think=True):
        print(f"{chunk}", end='', flush=True)