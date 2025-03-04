import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import config
import json

class RagManager:
    def __init__(self, chat_brain=None, translation=None):
        if translation is not None:
            self._ = translation
        else:
            self._ = lambda x: x
            
        if config.DEBUG:
            print(self._("RagManager: Loading HuggingFaceEmbeddings"))
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        if config.DEBUG:
            print(self._("RagManager: HuggingFaceEmbeddings loaded"))

        self.chat_brain = chat_brain
        self.create_vector_db()

    def create_vector_db(self):
        """
        Create a vector database from a list of messages
        """
        if config.DEBUG:
            print(self._("RagManager: Creating vector database"))
        self.vector_store = Chroma(embedding_function=self.embeddings, collection_name="conversation", persist_directory="data/rag/main_db")
        if config.DEBUG:
            print(self._("RagManager: Vector database created"))

    def retroactively_add_conversation(self, documents):
        """
        Add a conversation to the vector database
        """
        if config.DEBUG:
            print(self._("RagManager: Adding conversation to vector database"))
        self.vector_store.add_documents(documents)
        if config.DEBUG:
            print(self._("RagManager: Conversation added to vector database"))

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

    def similarity_search(self, query, k=5):
        """
        Perform a similarity search on the vector database

        Args:
            query: Query string
            k: Number of results to return

        Returns:
            List of LangChain Document objects
        """
        return self.vector_store.similarity_search_with_score(query, k)

    def is_retrieval_relevant(self, query):
        """
        Use the LLM to determine if retrieval would be helpful for this query.
        
        Args:
            query: The user query
            
        Returns:
            Boolean indicating if retrieval should be performed
        """
        if not self.chat_brain:
            # Fallback to keyword-based approach if no LLM is available
            retrieval_keywords = ["previous", "before", "earlier", "last time", "remember", "mentioned", "said"]
            return any(keyword in query.lower() for keyword in retrieval_keywords)
        
        # LLM-based approach
        prompt = [
            SystemMessage(content=self._("Determine if this query requires retrieving information from past conversations.\nReply with ONLY 'Yes' or 'No'.\nSay 'Yes' if the query explicitly or implicitly refers to past conversations or previously discussed information.\nSay 'No' if the query can be answered without reference to past conversations.")),
            HumanMessage(content=self._("Query: {0}").format(query))
        ]
        
        response = self.chat_brain.get_response(prompt)
        if config.DEBUG:
            print("RagManager: Retrieval relevance response:")
            print(response)
        return any(keyword in response.lower() for keyword in ["yes", "oui", 'si', 'yeah', 'yep', 'yup', 'ouai', 'ok', 'okay'])

    def evaluate_document_relevance(self, query, documents, k=3):
        """
        Use the LLM to evaluate and rank the relevance of documents for the query.
        
        Args:
            query: The user query
            documents: List of candidate documents
            k: Number of documents to return
            
        Returns:
            List of the most relevant Document objects
        """
        if not self.chat_brain or not documents:
            return documents[:k]  # Simple truncation if no LLM or documents
        
        # Prepare document evaluation prompt
        doc_texts = []
        for i, doc in enumerate(documents):
            doc_texts.append(f"Document {i+1}:\n{doc.page_content}")
        
        evaluation_prompt = [
            SystemMessage(content=self._("Evaluate each document's relevance to the query on a scale of 1-10.\nReturn ONLY a JSON array with the relevance scores: [score1, score2, ...]\nHigher scores mean more relevant.")),
            HumanMessage(content=self._("Query: {0}\n\n{1}").format(query, chr(10).join(doc_texts)))
        ]
        
        try:
            # Get relevance scores from LLM
            response = self.chat_brain.get_response(evaluation_prompt)
            if config.DEBUG:
                print("RagManager: LLM document relevance scores:")
                print(response)
            scores = json.loads(response)
            
            # Pair documents with scores and sort by relevance
            doc_scores = list(zip(documents, scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top k relevant documents
            return [doc for doc, _ in doc_scores[:k]]
        except:
            # Fallback if LLM response parsing fails
            if config.DEBUG:
                print(self._("RagManager: Failed to parse LLM document relevance scores"))
            return documents[:k]

    def generate_rag_prompt(self, query, documents, max_context_docs=3):
        """
        Generate a system prompt enriched with relevant context from documents.
        
        Args:
            query: The user query
            documents: List of relevant Document objects
            max_context_docs: Maximum number of documents to include
            
        Returns:
            String containing the RAG-enhanced system prompt
        """
        # Limit the number of documents to avoid context overflow
        documents = documents[:max_context_docs]
        
        # Create context from documents
        context_parts = []
        for i, doc in enumerate(documents):
            context_parts.append(f"Context {i+1}:\n{doc.page_content}\n")
        
        context_text = "\n".join(context_parts)
        
        # Create the RAG prompt
        rag_prompt = self._("You have access to previous conversation history that might be relevant to the current query.\nUse this information when appropriate to provide contextual and informed responses.\n\nPREVIOUS CONVERSATION CONTEXT:\n{0}\n\nWhen responding:\n1. Use the provided context when it's directly relevant to the query\n2. Don't explicitly mention you're using \"context\" or \"previous conversations\"\n3. Answer naturally as if you remember the conversation\n4. If the context isn't helpful, rely on your general knowledge").format(context_text)
        
        return rag_prompt

    def process_query_with_rag(self, query):
        """
        Process a query using the RAG workflow with LLM for relevance decisions.
        
        Args:
            query: The user query
            
        Returns:
            Dictionary with RAG results including prompt and relevance info
        """
        if config.DEBUG:
            print(self._("RagManager: Processing query with RAG: {0}").format(query))
            
        # Step 1: Check if retrieval is relevant
        retrieval_relevant = self.is_retrieval_relevant(query)
        
        # Initialize result dictionary
        result = {
            "query": query,
            "retrieval_performed": False,
            "documents_found": 0,
            "rag_prompt": None
        }
        
        # Step 2: If relevant, retrieve documents
        if retrieval_relevant:
            if config.DEBUG:
                print(self._("RagManager: Query requires retrieval, fetching documents"))
                
            # Get initial candidate documents
            candidate_docs = [doc for doc, _ in self.similarity_search(query, k=8)]
            
            # Further filter for relevance using LLM
            documents = self.evaluate_document_relevance(query, candidate_docs)
            
            result["retrieval_performed"] = True
            result["documents_found"] = len(documents)
            
            # Step 3: Generate RAG prompt if relevant documents were found
            if documents:
                if config.DEBUG:
                    print(self._("RagManager: Found {0} relevant documents").format(len(documents)))
                result["rag_prompt"] = self.generate_rag_prompt(query, documents)
            elif config.DEBUG:
                print(self._("RagManager: No relevant documents found"))
        elif config.DEBUG:
            print(self._("RagManager: Query does not require retrieval"))
        
        return result

if __name__ == "__main__":
    from Modules.Chat.brain.ChatBrain import ChatBrain

    import gettext
    # Select the language you need
    lang = 'fr'  # For French, for example

    # Set up the translation. 'messages' is the domain name, and 'locale' is the directory
    translation = gettext.translation('prompts', localedir='locale', languages=[lang])
    translation.install()
    _ = translation.gettext  # Alias for easier usage
    
    # Test the RAG system
    print("Initializing ChatBrain and RagManager...")
    chat_brain = ChatBrain()
    rag_manager = RagManager(chat_brain=chat_brain, translation=_)
    
    # First ensure we have documents in the vector store
    documents = rag_manager.conversation_memory_to_documents()
    
    # Check if documents need to be added
    doc_count = len(rag_manager.vector_store.get()['documents'])
    if doc_count == 0:
        print(f"No documents found in vector store. Adding {len(documents)} documents...")
        rag_manager.retroactively_add_conversation(documents)
        print("Documents added to vector store.")
    else:
        print(f"Vector store already contains {doc_count} documents.")
    
    # Test the RAG workflow with a sample query
    def test_rag_query(query):
        print(f"\n--- Testing RAG with query: '{query}' ---")
        
        # Check if retrieval is deemed relevant
        is_relevant = rag_manager.is_retrieval_relevant(query)
        print(rag_manager._("Is retrieval relevant? {0}").format("Yes" if is_relevant else "No"))
        
        # Process the query with RAG
        result = rag_manager.process_query_with_rag(query)
        
        print(rag_manager._("Retrieval performed: {0}").format(result['retrieval_performed']))
        print(rag_manager._("Documents found: {0}").format(result['documents_found']))
        
        if result['rag_prompt']:
            print("\n" + rag_manager._("Generated RAG Prompt:"))
            print("=" * 50)
            print(result['rag_prompt'])
            print("=" * 50)
        else:
            print(rag_manager._("No RAG prompt generated."))
        
        return result
    
    # Test with a query that likely needs retrieval
    test_rag_query(rag_manager._("What did we talk about yesterday?"))
    
    # Test with a query that likely doesn't need retrieval
    test_rag_query(rag_manager._("What's the weather like today?"))
    
    # Interactive mode for testing
    print("\n--- " + rag_manager._("Interactive RAG Testing Mode") + " ---")
    print(rag_manager._("Type queries to test or 'exit' to quit"))
    
    while True:
        user_query = input("\n" + rag_manager._("Enter a query: "))
        if user_query.lower() in ['exit', 'quit', 'q']:
            break
            
        result = test_rag_query(user_query)

