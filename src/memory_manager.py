import json

class MemoryManager:
    """
    MemoryManager handles the loading and saving of memory data.
    It provides methods to load memory from a file and save memory to a file.
    """

    def __init__(self, memory_file: str, debug=False):
        self.memory_file = memory_file
        self.debug = debug
        self.memory = []
        self.create_memory_file()

    def load_memory(self):
        """
        Load memory from the specified file.
        """
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
            if self.debug:
                print(f"[MemoryManager] Memory loaded from {self.memory_file}")
        except FileNotFoundError:
            if self.debug:
                print(f"[MemoryManager] Memory file {self.memory_file} not found. Starting with empty memory.")
            self.memory = []
        except json.JSONDecodeError as e:
            if self.debug:
                print(f"[MemoryManager] Error decoding JSON from {self.memory_file}: {e}")
            self.memory = []

    def save_memory(self):
        """
        Save the current memory to the specified file.
        """
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)
        if self.debug:
            print(f"[MemoryManager] Memory saved to {self.memory_file}")

    def create_memory_file(self):
        """
        Create the memory file if it does not exist.
        """
        if self.memory_file and not self.memory_file.endswith('.json'):
            self.memory_file += '.json'

        if not self.memory_file:
            raise ValueError("Memory file path must be specified.")

        try:
            with open(self.memory_file, 'x') as f:
                json.dump([], f)  # Initialize with an empty JSON object
            if self.debug:
                print(f"[MemoryManager] Memory file created: {self.memory_file}")
        except FileExistsError:
            if self.debug:
                print(f"[MemoryManager] Memory file already exists: {self.memory_file}")
            self.load_memory()

    def add_memory_entry(self, message):
        """
        Add a new entry to the memory.
        """
        if isinstance(message, list):
            self.memory.extend(message)
        elif isinstance(message, dict):
            self.memory.append(message)
        if self.debug:
            print(f"[MemoryManager] Added memory entry: message={message}")
        self.save_memory()

    # DANGER ZONE
    def clear_memory(self):
        """
        DANGER ZONE:
        Clear the current memory.
        """
        self.memory = []
        if self.debug:
            print("[MemoryManager] Memory cleared.")
        self.save_memory()


if __name__ == "__main__":
    # Example usage
    memory_manager = MemoryManager(memory_file="./data/chats/test_memory.json", debug=True)
    memory_manager.clear_memory()
    memory_manager.add_memory_entry({"role": "system", "content": "test system message"})
    memory_manager.add_memory_entry([{"role": "user", "content": "test user message"}, {"role": "tool", "content": "test tool message"}, {"role": "assistant", "content": "test assistant message"}])
    print("Current memory:", memory_manager.memory)