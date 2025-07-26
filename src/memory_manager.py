import json
import logging
import numpy as np
import os
import faiss
from src.ollama_interface import OllamaInterface

class MemoryManager:
    """
    MemoryManager handles the loading and saving of memory data.
    It provides methods to load memory from a file and save memory to a file.
    """

    def __init__(self, memory_file: str, debug=False):
        self.memory_file = memory_file
        self.debug = debug
        self.memory = []
        self.is_new_memory = False
        self.logger = logging.getLogger("MemoryManager")
        self.rag_db_path = memory_file.replace('.json', '_rag.index')
        self.rag_meta_path = memory_file.replace('.json', '_rag_meta.json')
        self.embedding_model_name = "all-MiniLM-L6-v2"
        self.embedding_model = None
        self.rag_index = None
        self.rag_meta = []
        self.create_memory_file()
        self.create_rag_db()
        if self.memory == []:
            self.is_new_memory = True
            if self.debug:
                self.logger.debug("No existing memory found. Starting with new memory.")

    def create_rag_db(self):
        """
        Create the RAG database (FAISS index) if it does not exist.
        """
        if not os.path.exists(self.rag_db_path):
            # Create a new FAISS index (L2 distance, 384 dims for MiniLM)
            self.rag_index = faiss.IndexFlatL2(384)
            faiss.write_index(self.rag_index, self.rag_db_path)
            with open(self.rag_meta_path, 'w') as f:
                json.dump([], f)
            if self.debug:
                self.logger.debug(f"RAG DB created: {self.rag_db_path}")
        else:
            self.load_rag_db()

    def load_rag_db(self):
        """
        Load the RAG database and metadata.
        """
        if os.path.exists(self.rag_db_path):
            self.rag_index = faiss.read_index(self.rag_db_path)
        else:
            self.rag_index = faiss.IndexFlatL2(384)
        if os.path.exists(self.rag_meta_path):
            with open(self.rag_meta_path, 'r') as f:
                self.rag_meta = json.load(f)
        else:
            self.rag_meta = []

    def embed_text(self, text):
        """
        Embed text using sentence-transformers.
        """
        if self.embedding_model is None:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
        return self.embedding_model.encode([text])[0]

    def load_memory(self):
        """
        Load memory from the specified file.
        """
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
            if self.debug:
                self.logger.debug(f"Memory loaded from {self.memory_file}")
        except FileNotFoundError:
            if self.debug:
                self.logger.debug(f"Memory file {self.memory_file} not found. Starting with empty memory.")
            self.memory = []
        except json.JSONDecodeError as e:
            if self.debug:
                self.logger.debug(f"Error decoding JSON from {self.memory_file}: {e}")
            self.memory = []

    def save_memory(self):
        """
        Save the current memory to the specified file.
        """
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)
        if self.debug:
            self.logger.debug(f"Memory saved to {self.memory_file}")

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
                self.logger.debug(f"Memory file created: {self.memory_file}")
        except FileExistsError:
            if self.debug:
                self.logger.debug(f"Memory file already exists: {self.memory_file}")
            self.load_memory()

    def add_memory_entry(self, message):
        """
        Add a new entry to the memory. If token count exceeds 10000, embed user-assistant pairs and store in RAG DB.
        """
        if isinstance(message, list):
            self.memory.extend(message)
        elif isinstance(message, dict):
            self.memory.append(message)
        if self.debug:
            self.logger.debug(f"Added memory entry: message={message}")
        if self.get_token_count() > 10000:
            if self.debug:
                self.logger.debug("Memory token count exceeded 10000. Starting RAG transformation.")
            self.transform_memory_to_rag()
        self.save_memory()

    def transform_memory_to_rag(self):
        """
        Transform user-assistant pairs to embeddings and store in RAG DB.
        """
        # Find user-assistant pairs
        pairs = []
        i = 0
        while i < len(self.memory) - 3:
            user = self.memory[i]
            assistant = self.memory[i+1]
            if user.get('role') == 'user' and assistant.get('role') == 'assistant':
                pairs.append((user, assistant))
                i += 2
            else:
                i += 1
        # Embed and add to RAG DB
        new_vectors = []
        new_meta = []
        for user, assistant in pairs:
            text = "user:" + user['content'] + "\n" + "assistant:" + assistant['content']
            vector = self.embed_text(text)
            new_vectors.append(vector)
            new_meta.append({"user": user['content'], "assistant": assistant['content']})
        if new_vectors:
            self.load_rag_db()
            self.rag_index.add(np.array(new_vectors, dtype='float32'))
            self.rag_meta.extend(new_meta)
            faiss.write_index(self.rag_index, self.rag_db_path)
            with open(self.rag_meta_path, 'w') as f:
                json.dump(self.rag_meta, f, indent=4)
            ollama = OllamaInterface(model_name="qwen3:4b", debug=self.debug)
            summary_prompt = "Summarize the following conversation:\n" + "\n".join(
                [f"user: {meta['user']}\nassistant: {meta['assistant']}" for meta in new_meta]
            )
            summary = ollama.ask(summary_prompt)
            self.memory = self.memory[:len(self.memory) - 2 * len(pairs)]  # Remove old user-assistant pairs
            self.memory.append({"role": "system", "content": f"Summary of previous conversation: {summary}"})
            self.save_memory()
            if self.debug:
                self.logger.debug(f"Added {len(new_vectors)} pairs to RAG DB.")

    def query_rag(self, query, top_k=5):
        """
        Query the RAG DB for similar user-assistant pairs.
        """
        self.load_rag_db()
        query_vec = self.embed_text(query)
        D, I = self.rag_index.search(np.array([query_vec], dtype='float32'), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.rag_meta):
                results.append(self.rag_meta[idx])
        return results

    def get_token_count(self):
        """
        Return the total token count in the memory.
        Assumes each entry in memory is a dict with a 'content' field (string).
        Token count is estimated by splitting content on whitespace.
        """
        token_count = 0
        for entry in self.memory:
            if isinstance(entry, dict) and 'content' in entry and isinstance(entry['content'], str):
                token_count += len(entry['content'].split())
        return token_count

    def get_memory(self):
        """
        Get the current memory.
        """
        if not self.memory:
            self.load_memory()
        return self.memory

    # DANGER ZONE
    def clear_memory(self):
        """
        DANGER ZONE:
        Clear the current memory.
        """
        self.memory = []
        if self.debug:
            self.logger.debug("Memory cleared.")
        self.save_memory()


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.DEBUG)
    memory_manager = MemoryManager(memory_file="./data/chats/test_memory.json", debug=True)
    memory_manager.clear_memory()
    memory_manager.add_memory_entry({"role": "system", "content": "test system message"})
    memory_manager.add_memory_entry([{"role": "user", "content": "test user message"}, {"role": "tool", "content": "test tool message"}, {"role": "assistant", "content": "test assistant message"}])
    print("Current memory:", memory_manager.memory)