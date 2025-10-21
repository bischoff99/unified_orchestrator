# Production Orchestrator - Quick Start

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your settings (defaults work with Ollama)
```

### 3. Start Ollama (if using local backend)
```bash
ollama serve
ollama pull llama3.1:8b-instruct-q5_K_M
```

### 4. (Optional) Configure HuggingFace
```bash
# Add HF token to .env for better embeddings
HF_TOKEN=hf_your_token_here
```

## Production Tools

Agents are now equipped with specialized tools:

**FullStackAgent:** write_file(), read_file(), validate_python_code(), create_project_files()  
**DevOpsAgent:** create_project_structure(), generate_requirements(), write_file()  
**QAAgent:** test_code(), read_file(), validate_python_code()  
**DocsAgent:** write_file(), read_file(), get_current_date()

**Result:** Agents can write code, create files, and validate outputs!

## Usage

### Basic Usage
```bash
python main.py "Build a FastAPI notes service"
```

### With Specific Backend
```bash
# Ollama (default)
python main.py "Build a FastAPI notes service" --backend ollama

# MLX (Apple Silicon)
python main.py "Build a FastAPI notes service" --backend mlx

# OpenAI
python main.py "Build a FastAPI notes service" --backend openai
```

### With Benchmarking
```bash
python main.py "Build a FastAPI notes service" --benchmark
cat logs/metrics.json
```

### Run Benchmark Script
```bash
python benchmarks/parallel_benchmark.py
```

## Backend Configuration

The orchestrator reads backend settings from `.env`; adjust `MODEL_BACKEND` and provider credentials before switching away from the default Ollama setup.

## Using Production Tools

Agents now have specialized tools:

**FullStackAgent:**
- `write_file()` - Create code files
- `validate_python_code()` - Check syntax
- `create_project_files()` - Bulk file creation

**DevOpsAgent:**
- `create_project_structure()` - Directory scaffolding
- `generate_requirements()` - Dependency management

**QAAgent:**
- `test_code()` - Run validation tests
- `validate_python_code()` - Syntax checking

**DocsAgent:**
- `write_file()` - Create documentation
- `get_current_date()` - Add timestamps

## HuggingFace Integration

For better embeddings (memory system):

1. Get token from: https://huggingface.co/settings/tokens
2. Add to `.env`:
   ```bash
   HF_TOKEN=hf_your_token_here
   ```
3. Restart workflow - embeddings will use HF instead of OpenAI

**Benefits:**
- Free embedding model
- Better memory retrieval
- No OpenAI API key required

## Architecture

### 6-Agent Production Crew

1. **Architect** - Designs system architecture
2. **FullStack** - Implements code
3. **QA** - Tests implementation (>80% coverage)
4. **DevOps** - Creates deployment config
5. **Docs** - Generates documentation
6. **Critic** - Reviews everything

### Workflow

```
Architect → [FullStack, DevOps] → QA → Docs → Review
```

### Features

- ✅ MLX backend for Apple Silicon
- ✅ Chroma vector memory
- ✅ Performance metrics
- ✅ Multiple LLM backends
- ✅ Production-ready structure

## Outputs

Generated code appears in:
- `src/generated/` - Implementation code
- `logs/metrics.json` - Performance metrics
- `memory/` - Chroma DB storage

## Troubleshooting

**ModuleNotFoundError**: Install dependencies
```bash
pip install -r requirements.txt
```

**Ollama not found**: Install and start Ollama
```bash
brew install ollama
ollama serve
```

**MLX not available**: Only works on Apple Silicon
```bash
pip install mlx mlx-lm
```

## Examples

See `examples/` directory:
- `simple_example.py` - Basic CrewAI example
- `research_crew.py` - Research with tools
- `example_ollama.py` - Ollama integration
- `example_anthropic.py` - Claude integration

## Next Steps

1. Run your first task
2. Check `src/generated/` for outputs
3. Review `logs/metrics.json` for performance
4. Explore `src/orchestrator/crew_config.py` to customize agents
5. Add custom tools in `src/tools/`

## Documentation

See `docs/QUICK_START.md` for detailed documentation.
