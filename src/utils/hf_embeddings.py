"""HuggingFace Embeddings for CrewAI Memory - LOCAL sentence-transformers"""
from sentence_transformers import SentenceTransformer
import os


class LocalHuggingFaceEmbeddings:
    """
    Local HuggingFace embedding function using sentence-transformers.
    Runs entirely on-device with M3 Max GPU acceleration (MPS).
    No API calls or internet required after model download.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize local sentence-transformers model.

        Args:
            model_name: HuggingFace model identifier (default: all-MiniLM-L6-v2)
                       - all-MiniLM-L6-v2: 384 dims, 80MB, fast
                       - all-mpnet-base-v2: 768 dims, 420MB, best quality
                       - paraphrase-MiniLM-L3-v2: 384 dims, 61MB, fastest
        """
        self.model_name = model_name
        print(f"Loading {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded on device: {self.model.device}")

    def __call__(self, input: list[str]) -> list[list[float]]:
        """
        Generate embeddings for input texts.

        Args:
            input: List of texts to embed

        Returns:
            List of embedding vectors (floats)
        """
        embeddings = self.model.encode(input, convert_to_numpy=True)
        return embeddings.tolist()


def get_hf_embedding_function():
    """
    Get LOCAL HuggingFace embedding function for CrewAI memory.

    Benefits:
    - 100% local, no API calls
    - Free, unlimited usage
    - Fast with M3 Max GPU acceleration
    - Works offline after first download

    Returns:
        LocalHuggingFaceEmbeddings instance
    """
    model_name = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return LocalHuggingFaceEmbeddings(model_name=model_name)
