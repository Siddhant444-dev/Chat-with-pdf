import logging
from typing import List, Dict, Any, Optional
from ..utils.document_processor import DocumentProcessor
from ..utils.vector_store import VectorStore
from ..utils.llm_client import LLMClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class RAGSystem:
    """Main RAG system that orchestrates document processing, vector storage, and LLM interactions"""
    
    def __init__(self):
        # Initialize components
        self.document_processor = DocumentProcessor(settings.SUPPORTED_FILE_TYPES)
        
        # Debug: Print environment variables
        logger.info(f"PINECONE_API_KEY: {'Set' if settings.PINECONE_API_KEY else 'Not set'}")
        logger.info(f"PINECONE_ENVIRONMENT: {'Set' if settings.PINECONE_ENVIRONMENT else 'Not set'}")
        logger.info(f"PERPLEXITY_API_KEY: {'Set' if settings.PERPLEXITY_API_KEY else 'Not set'}")
        
        # Initialize vector store if credentials are available
        if settings.PINECONE_API_KEY and settings.PINECONE_ENVIRONMENT:
            try:
                self.vector_store = VectorStore(
                    api_key=settings.PINECONE_API_KEY,
                    environment=settings.PINECONE_ENVIRONMENT,
                    index_name=settings.PINECONE_INDEX_NAME
                )
                logger.info("Vector store initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize vector store (this is normal if offline): {e}")
                self.vector_store = None
        else:
            logger.warning("Pinecone credentials not provided. Vector store functionality will be limited.")
            self.vector_store = None
        
        # Initialize LLM client (prioritize Perplexity if available)
        self.llm_client = LLMClient(
            openai_api_key=settings.OPENAI_API_KEY,
            perplexity_api_key=settings.PERPLEXITY_API_KEY
        )
    
    def process_and_index_document(self, document_url: str) -> Dict[str, Any]:
        """Process a document and add it to the vector store"""
        try:
            # Process document
            doc_info = self.document_processor.process_document(document_url)
            
            # Chunk the text
            chunks = self.document_processor.chunk_text(
                doc_info["text"], 
                chunk_size=settings.CHUNK_SIZE, 
                overlap=settings.CHUNK_OVERLAP
            )
            
            # Prepare documents for vector store
            documents = []
            for i, chunk in enumerate(chunks):
                documents.append({
                    "text": chunk,
                    "metadata": {
                        "document_url": document_url,
                        "file_type": doc_info["file_type"],
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "content_length": doc_info["content_length"]
                    }
                })
            
            # Add to vector store
            if self.vector_store:
                doc_ids = self.vector_store.add_documents(documents)
                logger.info(f"Indexed {len(documents)} chunks from document: {document_url}")
                return {
                    "success": True,
                    "document_url": document_url,
                    "chunks_processed": len(documents),
                    "document_ids": doc_ids
                }
            else:
                logger.warning("Vector store not available. Document not indexed.")
                return {
                    "success": False,
                    "error": "Vector store not available"
                }
                
        except Exception as e:
            logger.error(f"Error processing and indexing document: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def answer_question(self, question: str, document_url: Optional[str] = None) -> Dict[str, Any]:
        """Answer a question using RAG"""
        try:
            if not self.vector_store:
                return {
                    "success": False,
                    "error": "Vector store not available"
                }
            
            # Search for relevant context
            search_results = self.vector_store.search(
                query=question, 
                top_k=settings.TOP_K_RESULTS
            )
            
            if not search_results:
                return {
                    "success": False,
                    "error": "No relevant context found"
                }
            
            # Generate response using LLM
            try:
                answer = self.llm_client.generate_simple_response(question, search_results)
                
                return {
                    "success": True,
                    "answer": answer,
                    "context_used": len(search_results),
                    "search_results": search_results
                }
                
            except Exception as e:
                logger.error(f"Error generating LLM response: {e}")
                return {
                    "success": False,
                    "error": f"LLM error: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def answer_multiple_questions(self, questions: List[str], document_url: Optional[str] = None) -> Dict[str, Any]:
        """Answer multiple questions using RAG"""
        try:
            answers = []
            
            for question in questions:
                result = self.answer_question(question, document_url)
                if result["success"]:
                    answers.append(result["answer"])
                else:
                    answers.append(f"Error: {result.get('error', 'Unknown error')}")
            
            return {
                "success": True,
                "answers": answers
            }
            
        except Exception as e:
            logger.error(f"Error answering multiple questions: {e}")
            return {
                "success": False,
                "error": str(e),
                "answers": []
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health"""
        status = {
            "vector_store_available": self.vector_store is not None,
            "llm_client_available": (self.llm_client.client is not None or (self.llm_client.perplexity_api_key is not None and self.llm_client.perplexity_api_key != "your-perplexity-api-key")),
            "document_processor_available": True
        }
        
        # Test vector store if available
        if self.vector_store:
            try:
                # Try a simple search to test connectivity
                test_results = self.vector_store.search("test", top_k=1)
                status["vector_store_healthy"] = True
            except Exception as e:
                status["vector_store_healthy"] = False
                status["vector_store_error"] = str(e)
        
        # Test LLM client if available
        if (self.llm_client.client and self.llm_client.openai_api_key) or (self.llm_client.perplexity_api_key and self.llm_client.perplexity_api_key != "your-perplexity-api-key"):
            try:
                # Try a simple completion to test connectivity
                if self.llm_client.client and self.llm_client.openai_api_key:
                    response = self.llm_client.client.chat.completions.create(
                        model="sonar",
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                elif self.llm_client.perplexity_api_key:
                    # Test Perplexity API
                    import requests
                    test_url = "https://api.perplexity.ai/chat/completions"
                    test_payload = {
                        "model": "sonar",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    }
                    response = requests.post(
                        test_url,
                        headers=self.llm_client.perplexity_headers,
                        json=test_payload,
                        timeout=10
                    )
                    if response.status_code != 200:
                        raise Exception(f"Perplexity API test failed: {response.status_code}")
                
                status["llm_client_healthy"] = True
            except Exception as e:
                status["llm_client_healthy"] = False
                status["llm_client_error"] = str(e)
        
        return status 