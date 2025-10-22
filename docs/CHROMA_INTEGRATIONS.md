# Chroma Integrations Guide

**Status:** ✅ Active Integrations  
**Project:** unified_orchestrator v2.1.0

## Overview

This guide documents how ChromaDB integrates with the unified_orchestrator's existing tech stack:
- **LangChain** - Framework integration
- **HuggingFace** - Embedding models (local + server)
- **Anthropic MCP** - Claude Desktop integration
- **CrewAI** - Agent memory system

## Current Setup

### 1. ChromaDB Vector Store
**Location:** `src/utils/vector_store.py`

```python
class VectorMemory:
    - PersistentClient (local storage: ./memory/)
    - Collection management
    - Semantic search with metadata filtering
    - Agent context storage
```

### 2. HuggingFace Embeddings (Local)
**Location:** `src/utils/hf_embeddings.py`

```python
class LocalHuggingFaceEmbeddings:
    - sentence-transformers/all-MiniLM-L6-v2 (default)
    - 100% local, no API calls
    - M3 Max GPU acceleration (MPS)
    - Free, unlimited usage
```

### 3. Configuration
**File:** `config.py`

```python
HF_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_TOKEN = os.getenv("HF_TOKEN", "")
```

## Integration 1: Anthropic MCP + Claude Desktop

**Reference:** [Chroma Docs - Anthropic MCP](https://docs.trychroma.com/integrations/frameworks/anthropic-mcp)

### Setup

Add to your Claude Desktop config (`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "chroma-orchestrator": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
      ]
    }
  }
}
```

### Available MCP Tools

Once configured, Claude can use these tools with your existing vector memory:

**Collection Management:**
- `chroma_list_collections` - List all collections
- `chroma_create_collection` - Create new collection
- `chroma_get_collection_info` - Get stats and metadata
- `chroma_delete_collection` - Remove collection

**Document Operations:**
- `chroma_add_documents` - Store documents with metadata
- `chroma_query_documents` - Semantic search
- `chroma_get_documents` - Retrieve by ID or filter
- `chroma_update_documents` - Modify existing documents
- `chroma_delete_documents` - Remove documents

### Usage Examples

**Query Agent Memory:**
```
You: "What did the architect agent store in memory?"
Claude: *uses chroma_list_collections, then chroma_query_documents*
```

**Debug Context:**
```
You: "Show me all documents in the 'orchestrator' collection"
Claude: *uses chroma_get_collection_info, then chroma_get_documents*
```

**Store Project Knowledge:**
```
You: "Store this API design in memory"
Claude: *uses chroma_add_documents with metadata*
```

## Integration 2: LangChain Framework

**Reference:** [Chroma Docs - LangChain](https://docs.trychroma.com/integrations/frameworks/langchain)

### Current Usage
**Location:** `src/tools/langchain_tools.py`

Your project already uses LangChain. Here's how to enhance with Chroma:

### Enhanced Vector Store with LangChain

```python
# src/utils/langchain_chroma.py (NEW)
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pathlib import Path

class LangChainChromaStore:
    """
    LangChain-integrated Chroma vector store.
    
    Benefits:
    - LangChain ecosystem integration
    - Document loaders, text splitters
    - Retrieval chains, agents
    - Compatible with existing VectorMemory
    """
    
    def __init__(
        self,
        collection_name: str = "orchestrator",
        persist_directory: str = "./memory"
    ):
        # Use same HF embeddings as existing setup
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Initialize Chroma with LangChain wrapper
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
    
    def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        """Add texts with optional metadata"""
        return self.vectorstore.add_texts(texts, metadatas=metadatas)
    
    def similarity_search(self, query: str, k: int = 3, filter: dict = None):
        """Semantic search with optional metadata filter"""
        return self.vectorstore.similarity_search(
            query, k=k, filter=filter
        )
    
    def as_retriever(self, search_kwargs: dict = None):
        """Return as LangChain retriever for chains"""
        return self.vectorstore.as_retriever(
            search_kwargs=search_kwargs or {"k": 3}
        )
```

### LangChain Retrieval Chain Example

```python
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from src.utils.langchain_chroma import LangChainChromaStore

# Initialize components
memory = LangChainChromaStore(collection_name="agent_knowledge")
llm = Ollama(model="llama3.1:8b-instruct-q5_K_M")

# Create retrieval chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=memory.as_retriever(
        search_kwargs={"k": 5, "filter": {"agent": "architect"}}
    )
)

# Query with context from vector memory
result = qa_chain.run("What patterns did the architect use for FastAPI?")
```

### Document Loaders + Chroma

```python
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load generated code files
loader = DirectoryLoader(
    "src/generated/",
    glob="**/*.py",
    loader_cls=TextLoader
)
documents = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

# Store in Chroma
memory = LangChainChromaStore(collection_name="generated_code")
memory.vectorstore.add_documents(chunks)

# Now searchable: "Find FastAPI authentication examples"
```

## Integration 3: HuggingFace Embeddings

**Reference:** [Chroma Docs - HuggingFace](https://docs.trychroma.com/integrations/embedding-models/hugging-face)

### Current: Local Sentence-Transformers ✅

Your setup already uses the recommended approach:

```python
# src/utils/hf_embeddings.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = model.encode(texts)
```

**Benefits:**
- ✅ 100% local (no API calls)
- ✅ Free, unlimited usage
- ✅ Fast with M3 Max GPU
- ✅ Works offline

### Alternative: HuggingFace API Embeddings

For cloud-based embeddings with more model choices:

```python
# src/utils/hf_api_embeddings.py (OPTIONAL)
import chromadb.utils.embedding_functions as embedding_functions

# Requires HF_TOKEN environment variable
huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
    api_key=os.getenv("HF_TOKEN"),
    model_name="sentence-transformers/all-mpnet-base-v2"
)

# Use with Chroma
collection = client.create_collection(
    name="api_embeddings",
    embedding_function=huggingface_ef
)
```

**When to use API:**
- Need specific models not available locally
- Want 768-dim embeddings (mpnet)
- Don't want to download model weights
- Have HF Pro subscription

### Model Comparison

| Model | Dims | Size | Speed | Quality | Local |
|-------|------|------|-------|---------|-------|
| **all-MiniLM-L6-v2** (current) | 384 | 80MB | Fast | Good | ✅ |
| all-mpnet-base-v2 | 768 | 420MB | Medium | Best | ✅ |
| paraphrase-MiniLM-L3-v2 | 384 | 61MB | Fastest | Basic | ✅ |
| text-embedding-ada-002 (OpenAI) | 1536 | API | Fast | Excellent | ❌ |

**Recommendation:** Stick with all-MiniLM-L6-v2 for local development, consider all-mpnet-base-v2 for production if quality matters more than speed.

## Integration 4: HuggingFace Inference Server

**Reference:** [Chroma Docs - HF Server](https://docs.trychroma.com/integrations/embedding-models/hugging-face-server)

### For Self-Hosted HuggingFace Inference

If deploying your own HF inference server:

```python
import chromadb.utils.embedding_functions as embedding_functions

# Connect to self-hosted HF inference endpoint
hf_server_ef = embedding_functions.HuggingFaceEmbeddingServer(
    url="https://your-hf-inference.com/embed"
)

collection = client.create_collection(
    name="server_embeddings",
    embedding_function=hf_server_ef
)
```

### Use Cases

1. **Team Deployment:** Shared embedding service for multiple developers
2. **GPU Server:** Centralized GPU for faster embeddings
3. **Cost Control:** Self-host instead of API calls
4. **Custom Models:** Deploy fine-tuned embedding models

### Existing HF Pro Integration

Your project already has HuggingFace Pro integration:

**Files:**
- `src/utils/hf_inference_client.py` - HF Pro inference client
- `src/utils/hf_cost_monitor.py` - Budget tracking (£3.33/day)

**Current Usage:** Text generation, not embeddings  
**Opportunity:** Add HF Pro embeddings for highest quality

```python
# Potential: Use HF Pro for embeddings too
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.getenv("HF_TOKEN"))

# Feature Extraction API (embeddings)
embeddings = client.feature_extraction(
    text="Your text here",
    model="sentence-transformers/all-mpnet-base-v2"
)
```

## Integration Matrix

| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| **ChromaDB Vector Store** | ✅ Active | `src/utils/vector_store.py` | PersistentClient |
| **Local HF Embeddings** | ✅ Active | `src/utils/hf_embeddings.py` | sentence-transformers |
| **LangChain Tools** | ✅ Active | `src/tools/langchain_tools.py` | Existing tools |
| **Anthropic MCP** | 🎯 Planned | Claude Desktop config | Phase 1 ready |
| **LangChain + Chroma** | 🎯 Enhancement | New wrapper needed | Retrieval chains |
| **HF API Embeddings** | ⏸️ Optional | Alternative approach | If needed |
| **HF Inference Server** | ⏸️ Optional | For team deployment | Future |

## Recommended Next Steps

### Phase 1: Anthropic MCP (Immediate - 5 min)

1. **Add MCP Server to Claude**
```bash
# Edit ~/.config/Claude/claude_desktop_config.json
# Add chroma-orchestrator config (see above)
```

2. **Test from Claude Desktop**
```
"List all Chroma collections"
"Query the orchestrator collection for FastAPI patterns"
"Show me agent memory statistics"
```

### Phase 2: LangChain Integration (1 hour)

1. **Create LangChain wrapper**
```bash
# Create src/utils/langchain_chroma.py
# Implement LangChainChromaStore class
```

2. **Add retrieval chains**
```python
# Enable context-aware agent queries
# Implement RAG patterns
# Connect to existing agents
```

3. **Test with document loaders**
```python
# Index generated code
# Search across projects
# Semantic code retrieval
```

### Phase 3: Enhanced Embeddings (Optional)

1. **Evaluate quality needs**
```python
# Benchmark all-MiniLM-L6-v2 vs all-mpnet-base-v2
# Test on real queries
# Measure quality improvement vs size cost
```

2. **Consider HF Pro embeddings**
```python
# If quality is critical
# Already have HF Pro infrastructure
# Add to cost monitoring
```

## Configuration Summary

### Environment Variables (.env)

```bash
# Current (Local Embeddings)
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HF_TOKEN=hf_...  # For HF Pro inference (optional for embeddings)

# ChromaDB
CHROMA_DATA_DIR=./memory

# Optional: MCP Server
CHROMA_CLIENT_TYPE=persistent
CHROMA_DOTENV_PATH=/full/path/to/.env
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "chroma-orchestrator": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
      ]
    }
  }
}
```

## Best Practices

### 1. **Embedding Consistency**
- Use same embedding model for indexing and retrieval
- Model is persisted with collection (Chroma v1.0+)
- Don't mix embedding models in same collection

### 2. **Metadata Strategy**
```python
# Good metadata for filtering
metadata = {
    "agent": "architect",
    "phase": "design",
    "project": "notes_api",
    "timestamp": "2025-10-22T16:00:00",
    "run_id": "job_abc123"
}
```

### 3. **Collection Organization**
```python
# Separate collections for different purposes
- "orchestrator" - Agent shared memory
- "generated_code" - Code search
- "agent_knowledge" - Best practices per agent
- "project_context" - Project-specific data
```

### 4. **Query Optimization**
```python
# Use metadata filters to reduce search space
results = memory.query(
    text="FastAPI authentication",
    k=3,
    filter_metadata={"agent": "architect", "phase": "design"}
)
```

## Monitoring and Observability

### Metrics to Track

```python
# Add to existing Prometheus metrics
chroma_collections_total = Gauge('chroma_collections', 'Total collections')
chroma_documents_total = Gauge('chroma_documents', 'Total documents')
chroma_query_latency_ms = Histogram('chroma_query_latency_ms', 'Query latency')
chroma_embedding_dimension = Gauge('chroma_embedding_dims', 'Embedding dimensions')
```

### Integration with Existing Stack

```python
# src/mcp/continuous_monitor.py - Add Chroma monitoring
from src.utils.vector_store import VectorMemory

def monitor_chroma():
    memory = VectorMemory()
    collections = memory.client.list_collections()
    
    for collection in collections:
        count = collection.count()
        chroma_documents_total.labels(collection=collection.name).set(count)
```

## Troubleshooting

### Issue: "Collection not found"
**Solution:** Collections are created on first use. Check `./memory/chroma.sqlite3` exists.

### Issue: "Embedding dimension mismatch"
**Solution:** Don't mix embedding models. Delete collection and recreate with consistent model.

### Issue: "Slow queries on large collections"
**Solution:** 
- Add metadata filters to reduce search space
- Tune HNSW parameters (ef_search, ef_construction)
- Consider splitting into smaller collections

### Issue: "MCP server not connecting"
**Solution:**
- Verify path in Claude config is absolute
- Check `memory/` directory exists and is writable
- Restart Claude Desktop after config changes

## References

### Official Documentation
- **Chroma Anthropic MCP:** https://docs.trychroma.com/integrations/frameworks/anthropic-mcp
- **Chroma LangChain:** https://docs.trychroma.com/integrations/frameworks/langchain
- **Chroma HuggingFace:** https://docs.trychroma.com/integrations/embedding-models/hugging-face
- **Chroma HF Server:** https://docs.trychroma.com/integrations/embedding-models/hugging-face-server

### Project Files
- **Vector Store:** `src/utils/vector_store.py`
- **HF Embeddings:** `src/utils/hf_embeddings.py`
- **LangChain Tools:** `src/tools/langchain_tools.py`
- **Configuration:** `config.py`

## Conclusion

**Current State:** ✅ Solid foundation with local embeddings and ChromaDB

**Recommended Path:**
1. ✅ **Phase 1:** Add Anthropic MCP (5 min, high value)
2. 🎯 **Phase 2:** LangChain integration for retrieval chains (1 hour)
3. ⏸️ **Phase 3:** Enhanced embeddings if needed (optional)

Your existing setup is production-ready. The integrations above add:
- **MCP:** AI assistant access to vector memory
- **LangChain:** Retrieval chains and document loaders
- **Enhanced Embeddings:** Quality improvements (if needed)

All integrations are **additive** - no breaking changes to existing code.

---

**Status:** Ready for Phase 1 (MCP) implementation  
**Compatibility:** All integrations work with current setup  
**Risk:** Low (side-by-side deployment)
