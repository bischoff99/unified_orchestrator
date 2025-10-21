"""FAISS Vector Store - High-performance alternative for large-scale vector search"""
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Optional, Any
from sentence_transformers import SentenceTransformer


class FAISSVectorStore:
    """
    FAISS-based vector store for high-performance semantic search.

    Use this when:
    - You have >10,000 vectors (50-250x faster than ChromaDB)
    - Speed is critical (milliseconds matter)
    - You don't need complex metadata filtering

    Use ChromaDB when:
    - You have <10,000 vectors
    - You need metadata filtering
    - You want simpler integration with CrewAI
    """

    def __init__(
        self,
        dimension: int = 384,
        index_path: str = "./faiss_index",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
            index_path: Directory to save/load index
            model_name: Sentence transformer model for embeddings
        """
        self.dimension = dimension
        self.index_path = index_path
        self.model_name = model_name

        # Create FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(dimension)

        # Store metadata separately (FAISS doesn't support metadata)
        self.metadata: List[Dict[str, Any]] = []
        self.documents: List[str] = []
        self.ids: List[str] = []

        # Load embedding model
        self.encoder = SentenceTransformer(model_name)

        # Load existing index if available
        self._load_index()

    def add(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the index.

        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            ids: Optional IDs (auto-generated if not provided)
        """
        if not documents:
            return

        # Generate embeddings
        embeddings = self.encoder.encode(documents, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')

        # Add to FAISS index
        self.index.add(embeddings)

        # Store documents
        self.documents.extend(documents)

        # Store metadata
        if metadatas is None:
            metadatas = [{}] * len(documents)
        self.metadata.extend(metadatas)

        # Store or generate IDs
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]
        self.ids.extend(ids)

    def search(
        self,
        query: str,
        k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            k: Number of results
            metadata_filter: Optional metadata filter (applied post-search)

        Returns:
            List of results with document, metadata, distance, id
        """
        if self.index.ntotal == 0:
            return []

        # Generate query embedding
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        query_embedding = query_embedding.astype('float32')

        # Search FAISS index (get more if filtering)
        search_k = k * 10 if metadata_filter else k
        distances, indices = self.index.search(query_embedding, min(search_k, self.index.ntotal))

        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):  # Valid index
                metadata = self.metadata[idx]

                # Apply metadata filter
                if metadata_filter:
                    if not all(metadata.get(key) == value for key, value in metadata_filter.items()):
                        continue

                results.append({
                    'document': self.documents[idx],
                    'metadata': metadata,
                    'distance': float(dist),
                    'id': self.ids[idx]
                })

                if len(results) >= k:
                    break

        return results

    def count(self) -> int:
        """Get number of vectors in index"""
        return self.index.ntotal

    def save(self):
        """Save index and metadata to disk"""
        os.makedirs(self.index_path, exist_ok=True)

        # Save FAISS index
        index_file = os.path.join(self.index_path, "index.faiss")
        faiss.write_index(self.index, index_file)

        # Save metadata and documents
        metadata_file = os.path.join(self.index_path, "metadata.pkl")
        with open(metadata_file, 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'ids': self.ids
            }, f)

        print(f"✅ FAISS index saved to {self.index_path}")

    def _load_index(self):
        """Load index and metadata from disk"""
        index_file = os.path.join(self.index_path, "index.faiss")
        metadata_file = os.path.join(self.index_path, "metadata.pkl")

        if os.path.exists(index_file) and os.path.exists(metadata_file):
            # Load FAISS index
            self.index = faiss.read_index(index_file)

            # Load metadata
            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
                self.ids = data['ids']

            print(f"✅ Loaded FAISS index from {self.index_path} ({self.count()} vectors)")

    def clear(self):
        """Clear all data"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        self.ids = []

    def __repr__(self):
        return f"FAISSVectorStore(dimension={self.dimension}, count={self.count()}, path={self.index_path})"


# Performance comparison example
if __name__ == "__main__":
    import time

    print("🚀 FAISS Vector Store Performance Test\n")

    # Create store
    store = FAISSVectorStore(index_path="./faiss_test")

    # Add test documents
    print("Adding 1000 test documents...")
    test_docs = [
        f"This is test document number {i} about machine learning and AI"
        for i in range(1000)
    ]
    test_metadata = [{"id": i, "type": "test"} for i in range(1000)]

    start = time.time()
    store.add(test_docs, test_metadata)
    add_time = time.time() - start
    print(f"✅ Added {store.count()} documents in {add_time:.3f}s")

    # Search test
    print("\nSearching for 'machine learning'...")
    start = time.time()
    results = store.search("machine learning", k=5)
    search_time = time.time() - start
    print(f"✅ Search completed in {search_time*1000:.2f}ms")

    print("\nTop results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Distance: {result['distance']:.3f}")
        print(f"   {result['document'][:60]}...")

    # Save test
    print("\nSaving index...")
    store.save()

    # Cleanup
    import shutil
    if os.path.exists("./faiss_test"):
        shutil.rmtree("./faiss_test")
        print("✅ Test cleanup complete")

    print(f"\n📊 Performance Summary:")
    print(f"   Add 1000 docs: {add_time:.3f}s ({1000/add_time:.0f} docs/sec)")
    print(f"   Search: {search_time*1000:.2f}ms")
    print(f"\n💡 FAISS is ~50-250x faster than ChromaDB for large datasets")
