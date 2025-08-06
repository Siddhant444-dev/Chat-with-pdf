import os
import uuid
from typing import List, Dict, Any, Optional
import pinecone
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Handles vector storage and retrieval using Pinecone"""
    
    def __init__(self, api_key: str, environment: str, index_name: str):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        
        # Initialize Pinecone (newer version)
        try:
            from pinecone import Pinecone
            self.pc = Pinecone(api_key=api_key)
        except ImportError:
            # Fallback to older version
            pinecone.init(api_key=api_key, environment=environment)
            self.pc = None
        
        # Get or create index
        self._ensure_index_exists()
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists"""
        try:
            if self.pc:
                # Newer Pinecone version
                if self.index_name not in self.pc.list_indexes().names():
                    # Create index with appropriate dimensions
                    self.pc.create_index(
                        name=self.index_name,
                        dimension=384,  # Dimension for all-MiniLM-L6-v2
                        metric="cosine"
                    )
                    logger.info(f"Created Pinecone index: {self.index_name}")
                
                self.index = self.pc.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name}")
            else:
                # Older Pinecone version
                if self.index_name not in pinecone.list_indexes():
                    # Create index with appropriate dimensions
                    pinecone.create_index(
                        name=self.index_name,
                        dimension=384,  # Dimension for all-MiniLM-L6-v2
                        metric="cosine"
                    )
                    logger.info(f"Created Pinecone index: {self.index_name}")
                
                self.index = pinecone.Index(self.index_name)
                logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        try:
            # Simple TF-IDF-like embedding for demo purposes
            # In production, use a proper embedding model
            embeddings = []
            for text in texts:
                # Create a simple hash-based embedding
                words = text.lower().split()
                embedding = np.zeros(384)  # 384 dimensions
                for word in words:
                    # Simple hash-based word embedding
                    hash_val = hash(word) % 384
                    embedding[hash_val] += 1
                # Normalize
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                embeddings.append(embedding.tolist())
            return embeddings
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store"""
        try:
            # Extract texts and metadata
            texts = [doc["text"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            
            # Create embeddings
            embeddings = self.create_embeddings(texts)
            
            # Generate IDs
            ids = [str(uuid.uuid4()) for _ in documents]
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (embedding, metadata) in enumerate(zip(embeddings, metadatas)):
                vectors.append({
                    "id": ids[i],
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "text": texts[i][:1000]  # Store truncated text in metadata
                    }
                })
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
            logger.info(f"Added {len(documents)} documents to vector store")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            # Create embedding for query
            query_embedding = self.create_embeddings([query])[0]
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": match.metadata.get("text", ""),
                    "metadata": match.metadata
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    def delete_documents(self, ids: List[str]):
        """Delete documents from the vector store"""
        try:
            self.index.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents from vector store")
        except Exception as e:
            logger.error(f"Error deleting documents from vector store: {e}")
            raise
    
    def clear_index(self):
        """Clear all documents from the index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all documents from vector store")
        except Exception as e:
            logger.error(f"Error clearing vector store: {e}")
            raise 