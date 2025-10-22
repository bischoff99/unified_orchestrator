# Migration Guide: v1.x → v2.x

**From Version:** 1.x  
**To Version:** 2.1.0  
**Date:** 2025-10-22

This guide helps you migrate from Unified Orchestrator v1.x to v2.1.0.

---

## 🎯 Quick Summary

| Area | v1.x | v2.1 | Impact |
|------|------|------|--------|
| **Execution** | Sequential | DAG-based parallel | 🔴 Breaking |
| **Events** | `timestamp` | `ts` | 🔴 Breaking |
| **FileStore** | Tuple return | Dict return | 🔴 Breaking |
| **Caching** | None | Deterministic | ✅ New feature |
| **Resume** | None | `--resume` flag | ✅ New feature |

---

## 🔴 Breaking Changes

### 1. FileStore Return Type

**v1.x:**
```python
path, sha256, size = filestore.safe_write("file.txt", content)
```

**v2.1:**
```python
result = filestore.safe_write("file.txt", content)
# result = {
#     "path": Path(...),
#     "sha256": "...",
#     "size_bytes": 1234,
#     "wrote": True,
#     "reason": "created"
# }

# Access fields:
path = result["path"]
sha256 = result["sha256"]
```

**Migration:**
```python
# Option 1: Update to dict access
result = filestore.safe_write("file.txt", content)
if result["wrote"]:
    print(f"Wrote {result['size_bytes']} bytes to {result['path']}")

# Option 2: Maintain tuple unpacking temporarily
result = filestore.safe_write("file.txt", content)
path, sha256, size = result["path"], result["sha256"], result["size_bytes"]
```

### 2. Event Field Rename

**v1.x:**
```json
{"timestamp": "2025-10-22T10:00:00", "type": "job.started", ...}
```

**v2.1:**
```json
{"ts": "2025-10-22T10:00:00Z", "type": "job.started", ...}
```

**Migration:**
```python
# If you're parsing events:
for event in read_events(events_path):
    # v1.x
    # timestamp = event["timestamp"]
    
    # v2.1
    timestamp = event["ts"]  # Now includes 'Z' suffix
```

### 3. Sequential → DAG Execution

**v1.x:**
```python
# Linear execution (hardcoded order)
architect_result = run_architect()
builder_result = run_builder(architect_result)
docs_result = run_docs(architect_result)
qa_result = run_qa(builder_result, docs_result)
```

**v2.1:**
```python
# DAG-based (declare dependencies)
dag = DAG()
dag.add_node(DAGNode(id="architect", fn=run_architect, needs=[]))
dag.add_node(DAGNode(id="builder", fn=run_builder, needs=["architect"]))
dag.add_node(DAGNode(id="docs", fn=run_docs, needs=["architect"]))
dag.add_node(DAGNode(id="qa", fn=run_qa, needs=["builder", "docs"]))

results = await run_dag(dag, job_id, context, events)
```

**Impact:**
- ✅ Builder and docs run in parallel
- ✅ Faster execution (typical 40% speedup)
- 🔴 Must define dependencies explicitly

---

## ✅ New Features (Opt-In)

### 1. Caching

**Enable automatic LLM response caching:**

```python
# No code changes needed!
# Caching is automatic in v2.1

# First run: cache miss → calls LLM
orchestrator.run(spec)

# Second run with same inputs: cache hit → instant
orchestrator.run(spec)  # Same spec = cache reuse
```

**Check cache effectiveness:**
```bash
grep "cache.hit" runs/job_123/events.jsonl | wc -l
grep "cache.miss" runs/job_123/events.jsonl | wc -l
```

**Clear cache:**
```bash
rm -rf runs/job_123/.cache/
```

### 2. Resume-from-Failure

**Use `--resume` to continue failed jobs:**

```bash
# First run (fails at step 3)
orchestrator run --spec job.yaml
# Job: job_abc123, Status: failed

# Resume from failure
orchestrator run --spec job.yaml --resume
# Skips steps 1-2, continues from step 3
```

**Programmatic usage:**
```python
# First run
results = await run_dag(dag, job_id, context, events, resume=False)

# Resume run
results = await run_dag(dag, job_id, context, events, resume=True)
# Reads events.jsonl, skips completed steps
```

### 3. Enhanced Events

**New event types:**
```json
{"type": "llm.request", "step": "architect", "data": {"provider": "ollama"}}
{"type": "llm.response", "step": "architect", "data": {"duration_s": 3.2}}
{"type": "file.written", "step": "builder", "data": {"wrote": true, "reason": "created"}}
{"type": "cache.hit", "step": "architect", "data": {"cache_key": "abc123"}}
{"type": "cache.miss", "step": "builder", "data": {"cache_key": "def456"}}
```

**Query events:**
```bash
# Get all LLM calls
jq 'select(.type=="llm.response")' runs/job_123/events.jsonl

# Calculate total LLM time
jq -r 'select(.type=="llm.response") | .data.duration_s' events.jsonl | \
  awk '{sum+=$1} END {print sum}'

# Count cache hits
grep -c "cache.hit" events.jsonl
```

---

## 🛠️ Step-by-Step Migration

### Step 1: Install v2.1

```bash
# Update package
pip install --upgrade unified-orchestrator==2.1.0

# OR from source
git pull origin main
pip install -e ".[dev]"
```

### Step 2: Update FileStore Calls

**Find all uses:**
```bash
grep -r "filestore.safe_write" src/
```

**Update pattern:**
```python
# Before
path, sha256, size = filestore.safe_write(...)

# After
result = filestore.safe_write(...)
path = result["path"]
sha256 = result["sha256"]
size = result["size_bytes"]
```

### Step 3: Update Event Parsing (if applicable)

```python
# Before
timestamp = event["timestamp"]

# After
timestamp = event["ts"]
```

### Step 4: Test Your Code

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/test_integration_basic.py

# Run a smoke test
orchestrator run --spec examples/tiny_spec.yaml
```

### Step 5: Opt Into New Features

**Enable resume:**
```bash
orchestrator run --spec job.yaml --resume
```

**Verify caching works:**
```bash
# Run twice, check events
orchestrator run --spec job.yaml
grep cache.miss runs/*/events.jsonl  # Should see misses

orchestrator run --spec job.yaml
grep cache.hit runs/*/events.jsonl  # Should see hits
```

---

## 🔍 Troubleshooting

### Issue: "TypeError: 'WriteResult' object is not iterable"

**Cause:** Tuple unpacking FileStore result

**Fix:**
```python
# Change this:
path, sha256, size = filestore.safe_write(...)

# To this:
result = filestore.safe_write(...)
path, sha256, size = result["path"], result["sha256"], result["size_bytes"]
```

### Issue: "KeyError: 'timestamp'"

**Cause:** Using old event field name

**Fix:**
```python
# Change:
ts = event["timestamp"]

# To:
ts = event["ts"]
```

### Issue: Cache not working

**Check:**
```bash
# Verify cache directory exists
ls -la runs/job_*//.cache/

# Check for cache events
grep cache runs/job_*/events.jsonl
```

**Common causes:**
- Different inputs (cache miss expected)
- Code version changed (cache invalidated)
- Cache directory permissions

### Issue: Resume not skipping steps

**Check:**
```bash
# Verify events.jsonl has step.succeeded
grep step.succeeded runs/job_*/events.jsonl

# Verify resume=True
orchestrator run --spec job.yaml --resume  # Note --resume flag
```

---

## 📊 Performance Comparison

### Typical Workflow (4 steps)

| Version | Mode | Time | Cache | Notes |
|---------|------|------|-------|-------|
| v1.x | Sequential | 60s | N/A | Baseline |
| v2.0 | Parallel | 35s | N/A | 42% faster |
| v2.1 | Parallel | 35s | Miss | First run |
| v2.1 | Parallel | 2s | Hit | 95% faster |

---

## 🧪 Testing Your Migration

### Validation Checklist

- [ ] All tests pass: `pytest`
- [ ] FileStore returns dicts with `wrote` and `reason`
- [ ] Events use `ts` field instead of `timestamp`
- [ ] Caching works (2nd run faster, cache.hit events)
- [ ] Resume works (skips completed steps)
- [ ] DAG execution order correct
- [ ] No unexpected breaking changes

### Smoke Test

```bash
# Run a simple job
orchestrator run --spec examples/tiny_spec.yaml

# Verify structure
ls runs/job_*/
# Should see: manifest.json, events.jsonl, outputs/, .cache/

# Check events
cat runs/job_*/events.jsonl | jq
# Should see: job.started, step.*, cache.*, file.written

# Test resume
orchestrator run --spec examples/tiny_spec.yaml --resume
grep step.skipped runs/job_*/events.jsonl
# Should see skipped events
```

---

## 📚 Additional Resources

- **ARCHITECTURE.md**: System design details
- **CHANGELOG.md**: Full list of changes
- **CONTRIBUTING.md**: Development guidelines
- **README.md**: Quick start and examples

---

## 💬 Getting Help

If you encounter issues during migration:

1. Check this guide's Troubleshooting section
2. Review error messages in logs/events.jsonl
3. Open an issue on GitHub with:
   - Migration step where you're stuck
   - Error messages and logs
   - Your environment (OS, Python version)

---

**Migration Guide Version:** 2.1.0  
**Last Updated:** 2025-10-22
