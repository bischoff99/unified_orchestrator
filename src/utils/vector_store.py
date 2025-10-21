"""Chroma Vector Store for Agent Memory"""
import chromadb
import os
from typing import Dict, List, Optional

class VectorMemory:
    """
    Persistent vector memory using ChromaDB for agent context storage.

    Enables agents to store and retrieve context using semantic search,
    allowing for better context awareness across tasks.
    """

    def __init__(self, collection_name: str = "orchestrator", persist_dir: str = "./memory"):
        """
        Initialize vector memory with ChromaDB persistent storage.

        Args:
            collection_name: Name of the collection for this orchestrator instance
            persist_dir: Directory for persistent storage (default: ./memory)
        """
        # Create persist directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)

        # Use PersistentClient for data persistence across runs
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)
        self.collection_name = collection_name
        self.persist_dir = persist_dir
    
    def save(self, key: str, content: str, metadata: Optional[Dict] = None):
        """
        Store content with embedding for semantic search.
        
        Args:
            key: Unique identifier for this content
            content: Text content to store
            metadata: Optional metadata dict (e.g., {"agent": "fullstack", "phase": "impl"})
        """
        self.collection.upsert(
            ids=[key],
            documents=[content],
            metadatas=[metadata or {}]
        )
    
    def load(self, key: str) -> Optional[str]:
        """
        Retrieve content by exact key.
        
        Args:
            key: Unique identifier to retrieve
        
        Returns:
            Stored content or None if not found
        """
        result = self.collection.get(ids=[key])
        if result['documents']:
            return result['documents'][0]
        return None
    
    def query(self, text: str, k: int = 3, filter_metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Semantic search for similar content.
        
        Args:
            text: Query text to search for
            k: Number of results to return
            filter_metadata: Optional metadata filter (e.g., {"agent": "fullstack"})
        
        Returns:
            List of dicts with keys: id, document, metadata, distance
        """
        query_params = {
            "query_texts": [text],
            "n_results": k
        }
        
        if filter_metadata:
            query_params["where"] = filter_metadata
        
        results = self.collection.query(**query_params)
        
        # Format results
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results.get('distances') else None
            })
        
        return formatted
    
    def clear(self):
        """Clear all memory in this collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(self.collection_name)
    
    def count(self) -> int:
        """Get count of stored items"""
        return self.collection.count()
    
    def __repr__(self):
        return f"VectorMemory(collection='{self.collection_name}', persist_dir='{self.persist_dir}', count={self.count()})"

