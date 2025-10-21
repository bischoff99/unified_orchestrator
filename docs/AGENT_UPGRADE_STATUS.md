# Agent Upgrade Status

## Goal
Upgrade minimal crew from 35/100 quality score to 75-85/100 by improving prompts, adding validation, and enforcing tool usage.

## Completed Improvements

### 1. Enhanced Builder Agent
**File**: `src/orchestrator/minimal_crew_config.py`

**Changes**:
- Updated role to "Senior Full-Stack Implementation Engineer"
- Added comprehensive code example in backstory (60+ lines of complete FastAPI code)
- Added validation checklist with 7 mandatory requirements
- Emphasized "COMPLETE, RUNNABLE" code multiple times
- Added explicit tool usage examples

### 2. Enhanced Build Task Description
**File**: `src/orchestrator/minimal_crew_config.py`

**Changes**:
- Added "MANDATORY REQUIREMENTS" section with 7 specific items
- Included complete code structure example
- Added validation checklist before submission
- Changed expected output to emphasize FILES WRITTEN TO DISK
- Added output_file parameter to force file creation

### 3. Optimized LLM Parameters
**File**: `config.py`

**Changes**:
- Temperature: 0.7 → 0.3 (more deterministic code generation)
- Max Tokens: 2048 → 4096 (allow longer complete implementations)
- Model default: llama3.1:8b-instruct-q5_K_M

### 4. Created Code Validator
**New File**: `src/utils/code_validator.py`

**Features**:
- Check imports (20 points): Validates all required imports present
- Check endpoints (30 points): Counts API decorators
- Check implementations (30 points): Verifies actual code, not just pass
- Check syntax (15 points): AST parser validation
- Check structure (15 points): Project organization
- Total: 110 points possible

### 5. Created Automated Scorer
**New File**: `scripts/evaluate_generated_code.py`

**Features**:
- Comprehensive project scoring (145 points total)
- Code validation + documentation + structure
- Letter grade assignment (A-F)
- Actionable recommendations
- JSON report output
- Pass/fail threshold at 70%

---

## Critical Issue Discovered

### Problem: Agents Not Calling Tools

**Symptom**: Agents complete tasks but don't write files to disk

**Evidence from logs**:
```
Agent: Senior Full-Stack Implementation Engineer
Final Answer: To fulfill this complex request... we'll need to carefully execute...
Action: Create Project Structure
Task Status: ✅ Completed

# But src/generated/ is empty - no write_file() was called!
```

**Root Cause**: CrewAI agents sometimes provide textual answers without actually executing tools, even when tools are available and prompted.

### Solutions to Try

**Option 1: Force Tool Usage** (Implemented)
- Added output_file parameter to Task
- Changed expected_output to demand "FILES WRITTEN TO DISK"
- Emphasized "YOU MUST CALL write_file() TOOL"

**Option 2: Use Manager Agent** (Not yet implemented)
```python
crew = Crew(
    agents=list(self.agents.values()),
    tasks=self.tasks,
    process=Process.hierarchical,  # Use hierarchical with manager
    manager_llm=get_llm_backend(),
    verbose=True
)
```

**Option 3: Add Tool Enforcement Callback** (Not yet implemented)
```python
def enforce_tool_usage(task_output):
    if "write_file" not in str(task_output):
        raise ValueError("Task completed without calling write_file!")
    return task_output

build_task = Task(..., callback=enforce_tool_usage)
```

**Option 4: Simplify Agent Instructions** (Alternative approach)
Make backstory shorter and more directive:
```python
backstory="""You MUST use write_file() to save code.
Example: write_file('src/generated/main.py', code)
DO NOT complete task without calling write_file()."""
```

---

## Test Results

### Test 1: Upgraded Crew (Without Tool Enforcement)
- **Status**: ❌ Failed
- **Issue**: Agent didn't call write_file()
- **Files Generated**: 0
- **Score**: N/A (no files to score)

### Next Steps

1. Try Option 2 or 3 above to force tool execution
2. Or use simpler, more directive prompts (Option 4)
3. Or switch to full 6-agent crew which may have better tool usage
4. Or manually complete the generated code from previous runs

---

## Recommendations

### Short-term: Work Around the Issue
Use the full 6-agent crew which has been tested more extensively:
```bash
python main.py "Build complete notes API" --benchmark
```

### Medium-term: Fix Tool Enforcement
Implement one of the solutions above (hierarchical process or callbacks)

### Long-term: Train Custom Model
Fine-tune a model specifically for code generation with tool usage

---

## Files Modified

1. `src/orchestrator/minimal_crew_config.py` - Enhanced Builder agent and task
2. `config.py` - Optimized LLM parameters
3. `src/utils/code_validator.py` - New validation utility
4. `scripts/evaluate_generated_code.py` - New scoring automation

---

**Status**: Improvements implemented, but tool execution issue remains. Need to try alternative enforcement strategies.

**Date**: October 21, 2025

