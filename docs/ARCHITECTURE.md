# Unified Orchestrator v2.1 Architecture

**Version:** 2.1.0  
**Last Updated:** 2025-10-22

## 📐 System Overview

Unified Orchestrator is a Python-based multi-agent orchestration system that uses DAG (Directed Acyclic Graph) execution, LLM provider abstraction, and comprehensive observability to generate code projects efficiently.

### Core Design Principles

1. **Observability First**: Every operation emits structured events
2. **Resilience**: Resume from failure without re-execution
3. **Efficiency**: Deterministic caching eliminates redundant LLM calls
4. **Type Safety**: Pydantic v2 models throughout
5. **Async-Native**: Built on asyncio for concurrency

---

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         CLI Interface                             │
│                    (orchestrator run/show/tail)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     DAG Orchestrator                              │
│  ┌────────────┐     ┌──────────────────────────────────────┐    │
│  │  Job Spec  │────▶│         DAG Builder                  │    │
│  └────────────┘     │  (architect → {builder, docs} → qa)  │    │
│                     └──────────────────────────────────────┘    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌───────────────────┐ ┌───────────────┐ ┌──────────────┐
│   Core Systems    │ │   Providers   │ │  FileStore   │
│                   │ │               │ │              │
│ • DAG Executor    │ │ • Ollama      │ │ • Safe Write │
│ • Event Emitter   │ │ • OpenAI      │ │ • SHA256     │
│ • Cache Manager   │ │ • Anthropic   │ │ • Locking    │
│ • Manifest Mgr    │ │ • MLX         │ │ • Events     │
└───────────────────┘ └───────────────┘ └──────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Run Folder Structure                           │
│                                                                   │
│  runs/<job_id>/                                                   │
│    ├── manifest.json      (metadata + step tracking)             │
│    ├── events.jsonl       (all events, chronological)            │
│    ├── inputs/            (input files)                          │
│    ├── outputs/           (generated code)                       │
│    ├── logs/              (step logs)                            │
│    ├── artifacts/         (binary artifacts)                     │
│    └── .cache/            (LLM response cache)                   │
│        └── <sha256>.json  (cached responses)                     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DAG Execution Model

### DAG Structure

The orchestrator uses a **Directed Acyclic Graph** to define workflow dependencies:

```python
# Example DAG: architect → {builder, docs} → qa

architect (no deps)
    ├─→ builder (depends on architect)
    └─→ docs    (depends on architect)
        └─→ qa (depends on builder + docs)
```

### Execution Phases

1. **Validation**: Check for cycles, verify dependencies exist
2. **Topological Sort**: Determine execution order
3. **Wave Execution**: Execute ready nodes in parallel
4. **Dependency Resolution**: Pass outputs from completed steps
5. **Result Collection**: Aggregate all step results

### Concurrency Control

```python
# Semaphore limits concurrent tasks
semaphore = asyncio.Semaphore(concurrency)

async with semaphore:
    # Execute step
    result = await execute_node(node)
```

**Benefits:**
- ✅ Parallel execution of independent steps
- ✅ Controlled resource usage
- ✅ Graceful failure handling

---

## 📊 Event System

### Event Schema (v2.1)

```typescript
Event {
  ts: string         // ISO8601 timestamp (e.g., "2025-10-22T10:00:00Z")
  level: "INFO" | "WARN" | "ERROR"
  job_id: string
  type: string       // Event type (see below)
  step?: string      // Optional step identifier
  data?: object      // Optional event-specific data
}
```

### Event Types

| Type | When Emitted | Data Fields |
|------|-------------|-------------|
| `job.started` | Job begins | project, provider, task |
| `job.succeeded` | Job completes | duration_s, artifacts |
| `job.failed` | Job fails | error, duration_s |
| `step.started` | Step begins | needs (dependencies) |
| `step.succeeded` | Step completes | duration_s, provider_calls |
| `step.failed` | Step fails | kind, message |
| `step.skipped` | Step skipped (resume) | reason |
| `llm.request` | Before LLM call | provider, model, prompt_tokens |
| `llm.response` | After LLM call | provider, duration_s, tokens, success |
| `file.written` | File written | path, sha256, wrote, reason |
| `cache.hit` | Cache hit | cache_key |
| `cache.miss` | Cache miss | cache_key |

### Event Storage

Events are stored in **ND-JSON** (Newline-Delimited JSON):

```bash
runs/job_abc123/events.jsonl
```

```json
{"ts":"2025-10-22T10:00:00Z","level":"INFO","job_id":"job_abc","type":"job.started",...}
{"ts":"2025-10-22T10:00:01Z","level":"INFO","job_id":"job_abc","type":"step.started","step":"architect"}
{"ts":"2025-10-22T10:00:05Z","level":"INFO","job_id":"job_abc","type":"llm.response","step":"architect",...}
```

**Benefits:**
- Streamable (tail -f)
- Parseable line-by-line
- Easy filtering with grep/jq

---

## 🗄️ Caching Strategy

### Deterministic Cache Keys

Cache keys are **SHA256 hashes** of:

```python
cache_input = {
  "provider": {
    "name": "ollama",
    "model": "llama3",
    "opts": {"temperature": 0.1}
  },
  "step": "architect",
  "inputs": {"task": "Build todo app"},
  "code_version": "abc123def"  # git commit or file hash
}

cache_key = SHA256(JSON.dumps(cache_input, sort_keys=True))
```

### Cache Lifecycle

```
1. Check cache: read_cache(cache_path)
   ├─ Hit:  Return cached response, emit cache.hit
   └─ Miss: Call provider, emit cache.miss

2. Call Provider: provider.generate(messages)

3. Store Response: write_cache(cache_path, response)
```

### Automatic Invalidation

Cache keys include **code version**:

```python
# Get version
git_commit = subprocess.run(["git", "rev-parse", "HEAD"])
# OR
file_hash = SHA256(concat(source_files))

# Any code change → new cache key → cache miss
```

**Benefits:**
- ✅ No stale responses after code changes
- ✅ Safe to share caches across runs
- ✅ Explicit versioning for debugging

---

## 🔄 Resume-from-Failure

### How It Works

1. **Job Fails Mid-Execution**
   - Steps 1-2 succeeded, step 3 failed
   - `events.jsonl` records: `step.succeeded` for 1-2

2. **User Runs with `--resume`**
   ```bash
   orchestrator run --spec job.yaml --resume
   ```

3. **Resume Logic**
   ```python
   # Read completed steps
   completed = read_completed_steps("runs/job_id/events.jsonl")
   # → {"step1", "step2"}
   
   # Mark as complete in DAG
   for step_id in completed:
       results[step_id] = placeholder_result
       emit(step.skipped)
   
   # Execute only pending steps
   run_dag(resume=True)  # Skips step1, step2; runs step3+
   ```

### Resume Guarantees

- ✅ **Idempotent**: Re-running with `--resume` is safe
- ✅ **Correct Dependencies**: Skipped steps provide placeholder outputs
- ✅ **Observable**: `step.skipped` events show what was skipped

---

## 🔌 Provider Abstraction

### LLMProvider Protocol

```python
class LLMProvider(Protocol):
    name: str
    
    def generate(self, messages: list[dict], **opts) -> str:
        """Generate response from messages."""
        ...
```

### Provider Implementations

| Provider | Module | Key Features |
|----------|--------|--------------|
| **Ollama** | `src/providers/ollama.py` | Local models, performance tuning |
| **OpenAI** | `src/providers/openai.py` | GPT-4, streaming support |
| **Anthropic** | `src/providers/anthropic.py` | Claude, structured outputs |
| **MLX** | `src/providers/mlx.py` | Apple Silicon optimized |

### Provider Selection

```python
# config.py
PROVIDER = os.getenv("PROVIDER", "ollama")

def get_provider() -> LLMProvider:
    if PROVIDER == "ollama":
        return OllamaProvider()
    elif PROVIDER == "openai":
        return OpenAIProvider()
    # ...
```

---

## 💾 FileStore with Events

### Safe Write Operations

```python
result = filestore.safe_write(
    path="main.py",
    content=code,
    mode="overwrite",
    emitter=events,
    job_id="job_123",
    step_id="builder"
)

# Returns:
{
    "path": Path("runs/job_123/outputs/main.py"),
    "sha256": "e3b0c44...",
    "size_bytes": 1234,
    "wrote": True,         # or False if content unchanged
    "reason": "created"    # or "nochange", "overwritten", "appended"
}

# Emits event:
{"type": "file.written", "step": "builder", "data": {...}}
```

### Write Modes

1. **create_new**: Fail if exists (unless content identical)
2. **overwrite**: Replace if content differs, skip if identical
3. **append**: Append content

---

## 📁 Run Folder Structure

```
runs/
└── job_abc123/
    ├── manifest.json          # Job metadata
    │   ├── job_id, status
    │   ├── started_at, finished_at
    │   ├── steps (status, duration, artifacts)
    │   ├── completed_steps    # For resume
    │   └── pending_steps
    │
    ├── events.jsonl           # All events (ND-JSON)
    │
    ├── inputs/                # Input files
    │   └── spec.yaml
    │
    ├── outputs/               # Generated files
    │   └── project_name/
    │       ├── main.py
    │       └── README.md
    │
    ├── logs/                  # Step-specific logs
    │   ├── architect.log
    │   ├── builder.log
    │   └── qa.log
    │
    ├── artifacts/             # Binary artifacts
    │
    └── .cache/                # LLM response cache
        ├── abc123def.json
        └── 456789ghi.json
```

---

## 🔍 Observability

### Querying Events

**Filter by type:**
```bash
grep '"type":"llm.response"' runs/job_123/events.jsonl | jq
```

**Calculate total LLM duration:**
```bash
jq -r 'select(.type=="llm.response") | .data.duration_s' events.jsonl | \
  awk '{sum+=$1} END {print sum}'
```

**Check cache effectiveness:**
```bash
echo "Hits: $(grep cache.hit events.jsonl | wc -l)"
echo "Misses: $(grep cache.miss events.jsonl | wc -l)"
```

---

## 🎯 Performance Characteristics

### Parallel Execution

- **Baseline (v1.0)**: Sequential, ~60s for 4-step workflow
- **DAG (v2.0)**: Parallel, ~35s for same workflow
- **Cached (v2.1)**: 2nd run ~2s (95% speedup)

### Resource Usage

- **Memory**: ~200MB per job (depends on model)
- **Disk**: ~10MB per run (with cache)
- **Concurrency**: Default 4, configurable

---

## 🔒 Safety & Reliability

### File Locking

```python
# Exclusive file locks prevent race conditions
with _file_lock(path):
    # Safe to write, no concurrent conflicts
    path.write_bytes(content)
```

### Idempotency

- **FileStore**: Writing identical content returns `wrote=False`
- **Resume**: Re-running with `--resume` skips completed work
- **Cache**: Same inputs always return same outputs

---

## 🧪 Testing Architecture

### Test Pyramid

```
        ┌────────────┐
        │   E2E (1)  │  Golden tests
        ├────────────┤
        │ Integration│  DAG + Provider + FileStore
        │    (10)    │
        ├────────────┤
        │   Unit     │  Individual functions
        │   (100+)   │
        └────────────┘
```

### Key Test Suites

- `test_filestore.py`: Safe writes, idempotency, locking
- `test_resume.py`: Resume logic, skip behavior
- `test_cache.py`: Deterministic keys, cache hits
- `test_dag.py`: DAG validation, execution, concurrency
- `test_golden.py`: End-to-end output verification

---

## 📚 Further Reading

- **MIGRATION.md**: Upgrading from v1.x to v2.x
- **CONTRIBUTING.md**: Development setup and guidelines
- **CHANGELOG.md**: Version history and changes
- **README.md**: Quick start and usage examples

---

**Architecture Version:** 2.1.0  
**Last Updated:** 2025-10-22
