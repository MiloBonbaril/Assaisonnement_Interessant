import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from datetime import datetime
import config
import json

class RagManager:
    def __init__(self):
        if config.DEBUG:
            print("RagManager: Loading HuggingFaceEmbeddings")
        self.embeddings =  HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        if config.DEBUG:
            print("RagManager: HuggingFaceEmbeddings loaded")

        self.create_vector_db()

    def create_vector_db(self):
        """
        Create a vector database from a list of messages
        """
        if config.DEBUG:
            print("RagManager: Creating vector database")
        self.vector_store = Chroma(embedding_function=self.embeddings, collection_name="conversation", persist_directory="data/rag/main_db")
        if config.DEBUG:
            print("RagManager: Vector database created")

    def retroactively_add_conversation(self, documents):
        """
        Add a conversation to the vector database
        """
        if config.DEBUG:
            print("RagManager: Adding conversation to vector database")
        self.vector_store.add_documents(documents)
        if config.DEBUG:
            print("RagManager: Conversation added to vector database")

    def conversation_memory_to_documents(self, chunk_size=1000, chunk_overlap=200):
        """
        Process conversation memory from config path into LangChain Documents.

        Args:
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks

        Returns:
            List of LangChain Document objects
        """
        # Read the conversation memory file
        with open(config.CONVERSATION_MEMORY_PATH, 'r', encoding='utf-8') as file:
            text = file.read()
        # Clean the text by removing any leading or trailing whitespace and removing '{' and '}' characters and removing tabs
        text = text.strip().replace("{", "").replace("}", "").replace("\t", "").replace("        ", "").replace("    ,\n", "")

        # Create a text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        # Split the text into chunks
        chunks = text_splitter.split_text(text)

        # Convert chunks to Documents
        documents = [Document(page_content=chunk, metadata={"save_date": f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"}) for chunk in chunks]

        return documents

if __name__ == "__main__":
    rag_manager = RagManager()
    documents = rag_manager.conversation_memory_to_documents()
    #rag_manager.retroactively_add_conversation(documents)
    for doc in rag_manager.vector_store.similarity_search_with_score("amélioration", 5):
        print(doc)