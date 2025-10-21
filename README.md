# Unified Orchestrator

AI-powered multi-agent orchestration system optimized for Apple Silicon (M3 Max). Build complete software projects using specialized AI agents working in parallel.

## 🌟 Features

- **6 Specialized Agents**: Architect, FullStack, QA, DevOps, Docs, and Critic working together
- **Multiple LLM Backends**: Ollama (local), MLX (Apple Silicon native), OpenAI, Anthropic, HuggingFace
- **Optimized for M3 Max**: Native MLX support, Metal GPU acceleration, unified memory architecture
- **Production Tools**: Agents can write code, create files, validate implementations, and generate deployments
- **Vector Memory**: ChromaDB + FAISS for fast semantic search and agent memory
- **Parallel Execution**: Context-aware task dependencies with parallel agent execution
- **Performance Monitoring**: Built-in metrics collection and benchmarking

## 🏗️ Architecture

### Multi-Agent Workflow

```
┌─────────────┐
│  Architect  │ - Designs system architecture
└──────┬──────┘
       │
       ├───────────┬───────────────┐
       ▼           ▼               ▼
┌──────────┐ ┌─────────┐   ┌──────────┐
│FullStack │ │ DevOps  │   │   Docs   │
└────┬─────┘ └────┬────┘   └────┬─────┘
     │            │              │
     └────────────┼──────────────┘
                  ▼
            ┌──────────┐
            │    QA    │ - Tests implementation
            └────┬─────┘
                 ▼
            ┌──────────┐
            │  Critic  │ - Final review
            └──────────┘
```

### Agent Capabilities

| Agent | Role | Tools |
|-------|------|-------|
| **Architect** | System design & architecture | Planning, schema design |
| **FullStack** | Code implementation | write_file(), read_file(), validate_python_code() |
| **QA** | Testing & validation | test_code(), validate_python_code() |
| **DevOps** | Deployment & infrastructure | create_project_structure(), generate_requirements() |
| **Docs** | Documentation generation | write_file(), get_current_date() |
| **Critic** | Quality review | Code analysis, security review |

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (3.11+ recommended) ⚠️ *CrewAI requires 3.10+ for Union type syntax*
- macOS with Apple Silicon (M3 Max recommended) or any system for non-MLX backends
- Ollama (for local LLM) or API keys for cloud providers

### Installation

```bash
# Clone repository
git clone <repository-url>
cd unified_orchestrator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install Tier 1 performance libraries
pip install faiss-cpu beautifulsoup4 lxml numba orjson

# Optional: Install Tier 2 advanced libraries
pip install langchain langchain-community spacy rank-bm25
python -m spacy download en_core_web_sm
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# - MODEL_BACKEND: ollama (default), mlx, openai, anthropic
# - MODEL_NAME: llama3.1:8b-instruct-q5_K_M (for Ollama)
# - API keys if using cloud providers
```

### Start Ollama (for local backend)

```bash
# Install Ollama
brew install ollama

# Start Ollama server
ollama serve

# Pull model
ollama pull llama3.1:8b-instruct-q5_K_M
```

### Run Your First Task

```bash
# Basic usage (6-agent full crew)
python main.py "Build a FastAPI notes service"

# Minimal crew (4 agents - faster, 50% fewer tokens)
python main.py "Build a REST API for todo management" --minimal

# With specific backend
python main.py "Build a data pipeline" --backend mlx

# With performance benchmarking
python main.py "Create a web scraper" --benchmark
```

**Crew Modes:**
- **Default (6 agents)**: Architect, FullStack, DevOps, QA, Docs, Critic - comprehensive
- **--minimal (4 agents)**: Architect, Builder, QA, Docs - 40% faster, 50% less cost

## 📖 Usage Examples

### Example 1: Build a Web Service

```bash
python main.py "Build a FastAPI service with SQLite database for managing tasks"
```

**Output**: Complete implementation in `src/generated/` including:
- API endpoints
- Database models
- Configuration files
- Tests
- Documentation
- Deployment configs

### Example 2: Using MLX Backend (Apple Silicon)

```bash
python main.py "Create a data processing pipeline" --backend mlx
```

### Example 3: Benchmarking Performance

```bash
python main.py "Build a GraphQL API" --benchmark
cat logs/metrics.json
```

## 🔧 Configuration Options

### LLM Backends

Configure in `.env`:

```bash
# Ollama (Local)
MODEL_BACKEND=ollama
MODEL_NAME=llama3.1:8b-instruct-q5_K_M
OLLAMA_BASE_URL=http://localhost:11434

# MLX (Apple Silicon Native)
MODEL_BACKEND=mlx
MLX_MODEL_PATH=mlx_models/llama3-8b

# OpenAI
MODEL_BACKEND=openai
MODEL_NAME=gpt-4o
OPENAI_API_KEY=sk-...

# Anthropic
MODEL_BACKEND=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

### Performance Tuning (M3 Max)

```bash
# Parallel execution
PARALLEL_MODE=true
MAX_CONCURRENT_TASKS=8

# Ollama optimization
OLLAMA_NUM_THREAD=16
OLLAMA_NUM_BATCH=2048
OLLAMA_NUM_GPU=40
OLLAMA_NUM_CTX=8192
```

### Vector Store Options

```bash
# ChromaDB (default, <10K vectors)
MEMORY_TYPE=chroma

# FAISS (recommended for >10K vectors, 50-125x faster)
# Requires: pip install faiss-cpu
VECTOR_STORE=faiss
FAISS_INDEX_PATH=.faiss
```

## 📊 Performance

### Benchmarks (M3 Max)

| Component | Performance | Notes |
|-----------|-------------|-------|
| **Vector Search** | 50-125x faster | FAISS vs ChromaDB (10K+ vectors) |
| **Numerical Ops** | 10-100x faster | Numba JIT compilation |
| **JSON Parsing** | 3x faster | orjson vs standard library |
| **MLX Inference** | Native speed | Metal GPU, unified memory |

### Optimization Levels

- **Base**: 2.0 GB venv, ChromaDB, standard libraries
- **Tier 1** (+100 MB): FAISS, Numba, BeautifulSoup, orjson
- **Tier 2** (+200 MB): LangChain, spaCy, rank-bm25
- **Tier 3** (+200 MB): Selenium, datasets, SQLAlchemy, Redis

See [`LIBRARY_RECOMMENDATIONS.md`](LIBRARY_RECOMMENDATIONS.md) for details.

## 📁 Project Structure

```
unified_orchestrator/
├── src/
│   ├── agents/           # Agent definitions
│   │   ├── architect_agent.py
│   │   ├── fullstack_agent.py
│   │   ├── qa_agent.py
│   │   ├── devops_agent.py
│   │   ├── docs_agent.py
│   │   └── critic_agent.py
│   ├── orchestrator/     # Crew configuration
│   │   └── crew_config.py
│   ├── tools/            # Agent tools
│   │   └── production_tools.py
│   ├── utils/            # Utilities
│   │   ├── llm_tools.py
│   │   ├── mlx_backend.py
│   │   ├── metrics.py
│   │   └── logging_setup.py
│   └── generated/        # Agent outputs
├── examples/             # Usage examples
├── tests/                # Test suite
├── docs/                 # Documentation
├── main.py              # Entry point
├── config.py            # Configuration
└── requirements.txt     # Dependencies
```

## 🛠️ Advanced Usage

### Custom Agents

See [`src/agents/`](src/agents/) for examples. Create custom agents by extending the base agent class.

### Adding Tools

Add custom tools in [`src/tools/production_tools.py`](src/tools/production_tools.py). Tools are automatically discovered and loaded.

### HuggingFace Integration

For better embeddings and optional inference:

```bash
# Get token from https://huggingface.co/settings/tokens
# Add to .env
HF_TOKEN=hf_your_token_here
HF_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Metrics Collection

Enable comprehensive metrics:

```bash
python main.py "Your task" --benchmark
cat logs/metrics.json
```

Metrics include:
- Agent execution times
- LLM token usage
- Memory operations
- Task completion rates

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Detailed setup and usage
- [Library Recommendations](LIBRARY_RECOMMENDATIONS.md) - Performance optimization
- [M3 Max Optimization](M3_MAX_OPTIMIZATION_GUIDE.md) - Apple Silicon tuning
- [Integration Plan](INTEGRATION_PLAN.md) - System integration details
- [API Documentation](API.md) - API endpoints and contracts

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/test_orchestration.py

# Run with coverage
pytest --cov=src tests/
```

## 🐛 Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
pip install -r requirements.txt
```

**Ollama Connection Error**
```bash
# Start Ollama server
ollama serve

# Verify model is pulled
ollama list
ollama pull llama3.1:8b-instruct-q5_K_M
```

**MLX Not Available**
```bash
# Only works on Apple Silicon
pip install mlx mlx-lm
```

**Slow Vector Search**
```bash
# Install FAISS for 50-125x speedup
pip install faiss-cpu
```

## 🎓 HuggingFace Pro Training & Inference

### Train Custom Models

```bash
# Train with LoRA fine-tuning on M3 Max
python examples/train_custom_model.py

# With HF Pro upload
python -c "
from src.agents.hf_trainer_agent import HFTrainerAgent
result = HFTrainerAgent.train_with_profiling(
    dataset_path='data/your_data.jsonl',
    hf_repo='your-username/model-name',
    max_steps=100
)
print(f'Model trained: {result}')
"
```

### Use HF Pro Inference

```bash
# With cost monitoring and safety validation
python examples/hf_pro_inference_example.py
```

### Cost Management

- **Budget:** £3.33/day, £100/month
- **Auto-fallback** to Ollama when budget exceeded
- **Safety validation** on all outputs
- **Usage tracking** with detailed reports

## 📊 Production Monitoring

### Start Monitoring Stack

```bash
# One-command startup
./scripts/start_monitoring.sh

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# MLflow: http://localhost:5000
```

### Metrics Tracked

- **Inference latency** (target: <100ms/token)
- **Daily costs** (budget: £3.33)
- **GPU memory** (M3 Max 40-core)
- **Safety filter pass rate** (target: >99%)
- **Token generation rate**
- **Training progress**

### Automated Monitoring

```bash
# Setup nightly profiling (runs at 2 AM)
./scripts/setup_cron.sh

# View profiling logs
tail -f logs/nightly_profiling.log
```

### Alerts

15 configured alert rules:
- High latency (>100ms)
- Budget warnings (>80%)
- Safety failures (>1%)
- GPU memory (>80%)
- Training issues

See [monitoring/README.md](monitoring/README.md) for complete documentation.

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [CrewAI](https://github.com/joaomdmoura/crewAI)
- Optimized for [MLX](https://github.com/ml-explore/mlx) on Apple Silicon
- Powered by various LLM providers (Ollama, OpenAI, Anthropic)

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: See [`docs/`](docs/) directory
- Examples: See [`examples/`](examples/) directory

---

**Version**: 1.0.0  
**Platform**: Cross-platform (Optimized for M3 Max / Apple Silicon)  
**Python**: 3.9+  
**Created**: 2025-10-21