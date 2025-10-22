# Chroma MCP Server Integration Plan

**Repository:** https://github.com/chroma-core/chroma-mcp  
**Status:** 🎯 Planned Integration  
**Priority:** Medium (Enhancement)

## Overview

The Chroma MCP server provides a Model Context Protocol interface to ChromaDB, enabling AI assistants (like Claude) to interact with our existing vector memory system through standardized MCP tools.

## Current State

**Existing ChromaDB Integration:**
- Location: `src/utils/vector_store.py`
- Client: PersistentClient (local file storage)
- Features: Semantic search, metadata filtering, collection management
- Storage: `./memory/` directory
- Used by: Agent context storage, cross-session memory

## Benefits of MCP Integration

### 1. **Standardized AI Assistant Access**
- Claude Desktop can directly query/update vector memory
- No custom tool implementation needed
- Follows Model Context Protocol standard

### 2. **Enhanced Capabilities**
- 14 standardized MCP tools for collection/document operations
- Advanced filtering (metadata + full-text search)
- Multiple embedding functions (Cohere, OpenAI, Jina, etc.)
- Pagination support for large collections
- HNSW parameter configuration for optimized search

### 3. **Flexible Deployment Options**
- **Ephemeral** - Testing and development
- **Persistent** - Current local setup (compatible with existing)
- **HTTP** - Self-hosted Chroma instance
- **Cloud** - Chroma Cloud integration

### 4. **Improved Developer Experience**
- Query vector memory from Claude Desktop
- Debug agent memory interactively
- Inspect collection statistics
- Test semantic search queries manually

## Integration Options

### Option A: Side-by-Side (Recommended)

**Keep existing VectorMemory class, add MCP server separately**

**Pros:**
- No breaking changes to existing code
- MCP provides external access layer
- Existing code continues to work
- Gradual migration path

**Implementation:**
```bash
# Add to Claude Desktop config
"chroma-orchestrator": {
    "command": "uvx",
    "args": [
        "chroma-mcp",
        "--client-type", "persistent",
        "--data-dir", "/full/path/to/unified_orchestrator/memory"
    ]
}
```

### Option B: Full Migration

**Replace VectorMemory with Chroma MCP client**

**Pros:**
- Single source of truth
- Leverage all MCP features
- Standardized interface

**Cons:**
- Breaking changes to existing code
- Need to refactor agents
- More complex deployment

## Implementation Steps

### Phase 1: External Access (Quick Win)

1. **Add Chroma MCP to Claude Desktop config**
   ```json
   {
     "chroma-orchestrator": {
       "command": "uvx",
       "args": [
         "chroma-mcp",
         "--client-type", "persistent",
         "--data-dir", "/Users/andrejsp/Developer/projects/unified_orchestrator/memory"
       ]
     }
   }
   ```

2. **Test MCP tools from Claude**
   - List collections: `chroma_list_collections`
   - Query memory: `chroma_query_documents`
   - Inspect agent context: `chroma_get_collection_info`

3. **Document usage patterns**
   - How to query agent memory
   - How to debug context issues
   - Best practices for metadata filtering

### Phase 2: Enhanced Embedding Functions (Optional)

1. **Evaluate embedding options**
   - Current: ChromaDB default embeddings
   - Options: OpenAI, Cohere, Jina, VoyageAI
   - Consider: Cost, quality, speed

2. **Configure API keys**
   ```bash
   # Add to .env
   CHROMA_OPENAI_API_KEY="sk-..."
   CHROMA_COHERE_API_KEY="..."
   ```

3. **Create collections with specific embeddings**
   ```python
   # Example: OpenAI embeddings for high-quality semantic search
   chroma_create_collection(
       name="agent_memory_v2",
       embedding_function="openai"
   )
   ```

### Phase 3: HTTP Client (Production Deployment)

1. **Deploy self-hosted Chroma instance**
   - Docker: `docker run -p 8000:8000 chromadb/chroma`
   - Kubernetes: Use Chroma Helm charts
   - Cloud: Deploy to AWS/GCP/Azure

2. **Update MCP config for HTTP client**
   ```json
   {
     "chroma-orchestrator": {
       "command": "uvx",
       "args": [
         "chroma-mcp",
         "--client-type", "http",
         "--host", "chroma.yourdomain.com",
         "--port", "8000",
         "--ssl", "true"
       ]
     }
   }
   ```

3. **Enable authentication**
   - Set up custom auth credentials
   - Configure SSL certificates
   - Implement access controls

### Phase 4: Chroma Cloud (Optional)

**For managed ChromaDB with zero infrastructure**

1. **Sign up for Chroma Cloud**
   - Visit: https://www.trychroma.com/cloud

2. **Configure cloud client**
   ```json
   {
     "chroma-orchestrator": {
       "command": "uvx",
       "args": [
         "chroma-mcp",
         "--client-type", "cloud",
         "--tenant", "your-tenant-id",
         "--database", "unified-orchestrator",
         "--api-key", "your-api-key"
       ]
     }
   }
   ```

## Use Cases

### 1. **Interactive Memory Debugging**
Ask Claude:
- "Show me what the architect agent stored in memory"
- "Query the vector memory for 'FastAPI authentication'"
- "List all collections and their document counts"

### 2. **Cross-Session Context**
- Store project requirements in ChromaDB
- Agents query memory for architectural decisions
- Preserve context across multiple runs

### 3. **Semantic Code Search**
- Index generated code in ChromaDB
- Search by semantic meaning, not exact text
- Find similar implementations across projects

### 4. **Agent Knowledge Base**
- Store best practices per agent type
- Query relevant patterns during execution
- Learn from past successful runs

## Migration Path (if needed)

### Current VectorMemory API → Chroma MCP

```python
# Current API
memory = VectorMemory(collection_name="orchestrator")
memory.save(key="arch_design", content="...")
memory.query(text="FastAPI patterns", k=3)

# MCP equivalent (via Claude Desktop)
# Ask Claude: "Store this architecture design in memory"
# Ask Claude: "Find patterns related to FastAPI"
```

### Keep Compatibility

```python
# Wrapper to maintain existing API
class VectorMemory:
    def __init__(self, collection_name, persist_dir="./memory"):
        # Use same directory as MCP server
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)
    
    # ... existing methods unchanged
```

## Configuration

### Environment Variables

```bash
# .env
CHROMA_CLIENT_TYPE=persistent
CHROMA_DATA_DIR=/full/path/to/unified_orchestrator/memory

# Optional: Enhanced embeddings
CHROMA_OPENAI_API_KEY=sk-...
CHROMA_COHERE_API_KEY=...

# Optional: HTTP client
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_SSL=false

# Optional: Cloud client
CHROMA_TENANT=your-tenant-id
CHROMA_DATABASE=unified-orchestrator
CHROMA_API_KEY=your-cloud-api-key
```

### Claude Desktop Config

```json
{
  "mcpServers": {
    "chroma-orchestrator": {
      "command": "uvx",
      "args": [
        "chroma-mcp",
        "--dotenv-path",
        "/Users/andrejsp/Developer/projects/unified_orchestrator/.env"
      ]
    }
  }
}
```

## Testing Plan

### 1. **Basic MCP Tools**
```bash
# From Claude Desktop, test:
- chroma_list_collections
- chroma_create_collection(name="test_collection")
- chroma_add_documents(collection="test_collection", docs=["test"])
- chroma_query_documents(collection="test_collection", query="test")
- chroma_delete_collection(name="test_collection")
```

### 2. **Existing Data Compatibility**
```bash
# Verify MCP can read existing vector memory
- List existing collections (should see "orchestrator")
- Query existing agent context
- Verify document counts match
```

### 3. **Performance**
```bash
# Benchmark queries
- Query 1K documents: < 100ms
- Query 10K documents: < 500ms
- Bulk insert 1K documents: < 2s
```

## Security Considerations

### 1. **API Key Management**
- Store keys in `.env` (not in config files)
- Use `--dotenv-path` flag for custom location
- Never commit keys to git
- Rotate keys regularly

### 2. **Access Control**
- MCP server runs locally (no network exposure by default)
- For HTTP client: implement authentication
- For Cloud: use Chroma Cloud's built-in auth

### 3. **Data Privacy**
- Vector memory may contain sensitive project data
- Use persistent client for local-only storage
- Enable SSL for HTTP/Cloud clients
- Consider encrypting stored embeddings

## Performance Optimization

### 1. **HNSW Parameters**
```python
# Optimize for speed vs. accuracy
chroma_create_collection(
    name="fast_search",
    hnsw_space="cosine",
    hnsw_construction_ef=100,
    hnsw_search_ef=50
)
```

### 2. **Embedding Function Selection**
- **Default**: Good balance, no API costs
- **OpenAI**: High quality, API costs
- **Cohere**: Multilingual support
- **Jina**: Optimized for long documents

### 3. **Batch Operations**
```python
# Add documents in batches
chroma_add_documents(
    collection="bulk_data",
    documents=[doc1, doc2, ...doc1000],
    metadatas=[meta1, meta2, ...meta1000]
)
```

## Monitoring

### Metrics to Track
- Collection counts
- Query latencies
- Cache hit rates
- Storage size

### Integration with Existing Monitoring
```python
# Add Chroma metrics to Prometheus
from prometheus_client import Gauge

chroma_collections = Gauge('chroma_collections', 'Number of Chroma collections')
chroma_documents = Gauge('chroma_documents', 'Total documents in Chroma')
chroma_query_latency = Gauge('chroma_query_latency_ms', 'Query latency in ms')
```

## Next Steps

### Immediate (Phase 1)
1. ✅ Document integration plan
2. ⏳ Add Chroma MCP to Claude Desktop config
3. ⏳ Test basic MCP tools with existing memory
4. ⏳ Document usage patterns

### Short-term (Phase 2)
5. ⏳ Evaluate enhanced embedding functions
6. ⏳ Create test collections with different embeddings
7. ⏳ Benchmark performance differences

### Long-term (Phase 3+)
8. ⏳ Deploy self-hosted Chroma instance
9. ⏳ Migrate to HTTP client for production
10. ⏳ Implement authentication and SSL
11. ⏳ Add Chroma metrics to monitoring stack

## References

- **Chroma MCP Repository:** https://github.com/chroma-core/chroma-mcp
- **Chroma Documentation:** https://docs.trychroma.com
- **Model Context Protocol:** https://modelcontextprotocol.io
- **Current VectorMemory:** `src/utils/vector_store.py`

## Conclusion

**Recommendation:** Start with Phase 1 (side-by-side deployment)

- ✅ Zero risk (no code changes)
- ✅ Immediate value (Claude Desktop access)
- ✅ Easy to test and evaluate
- ✅ Maintains existing functionality
- ✅ Gradual enhancement path

The Chroma MCP server is a perfect complement to the existing vector memory system, providing standardized external access without disrupting current operations.

---

**Status:** Ready for Phase 1 implementation  
**Effort:** Low (configuration only)  
**Value:** High (enhanced debugging and AI assistant access)
