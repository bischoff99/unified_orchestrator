# 🤖 MCP Server Generator

**Automatic MCP Server Creation using AI Agent Orchestration**

Generate complete, production-ready MCP (Model Context Protocol) servers automatically using a crew of specialized AI agents working together.

## What is This?

This is an **orchestration** - multiple AI agents working together to accomplish a complex task. Instead of manually coding MCP servers, you describe the API and the agents:

1. **Research** the API documentation
2. **Design** the MCP server architecture
3. **Write** production Python code
4. **Test** the implementation
5. **Configure** and document everything

## The Agent Crew

### 👥 Meet the Team

| Agent | Role | Responsibility |
|-------|------|----------------|
| 🔍 **Researcher** | API Analysis | Studies API docs, extracts specifications |
| 🏗️ **Architect** | System Design | Designs MCP server structure and tools |
| 💻 **Developer** | Implementation | Writes production-ready Python code |
| 🧪 **QA Engineer** | Testing | Validates code quality and functionality |
| ⚙️ **DevOps** | Configuration | Creates docs, configs, and setup files |

### 🔄 Workflow

```
API Name → [Researcher] → Specifications
                ↓
         [Architect] → Design
                ↓
         [Developer] → Code
                ↓
         [QA Engineer] → Tests
                ↓
         [DevOps] → Complete Package
                ↓
      Ready-to-Use MCP Server ✅
```

## Quick Start

### 1. List Supported APIs
```bash
python generate.py --list
```

### 2. Generate an MCP Server
```bash
# Generate Stripe MCP server
python generate.py --api stripe

# Generate with detailed output
python generate.py --api github --verbose

# Custom output directory
python generate.py --api shopify --output ../my-mcp-servers/
```

### 3. Use the Generated Server
```bash
cd output/stripe-mcp-server/
pip install -r requirements.txt
python server.py demo
```

## What Gets Generated

Each generated MCP server includes:

```
stripe-mcp-server/
├── server.py              # Complete MCP server implementation
├── requirements.txt       # All dependencies
├── .env.example          # Configuration template
├── README.md             # Full documentation
├── mcp_config.json       # Claude Desktop config
├── docs/
│   ├── INSTALLATION.md   # Setup guide
│   └── QUICK_START.md    # Usage guide
└── tests/
    └── test_server.py    # Basic tests
```

## Supported APIs

| API | Description |
|-----|-------------|
| **stripe** | Payment processing |
| **github** | Code hosting |
| **easyship** | Shipping logistics |
| **openai** | AI language models |
| **slack** | Team communication |
| **discord** | Community chat |
| **twitter** | Social media |
| **notion** | Workspace & notes |
| **airtable** | Databases |
| **shopify** | E-commerce |

**Not listed?** Try anyway! The generator can work with any REST API.

## Examples

### Example 1: Generate Stripe MCP Server
```bash
$ python generate.py --api stripe

🤖 MCP Generator Crew initialized for: stripe
👥 Agents ready: Researcher, Architect, Developer, QA, DevOps

🚀 Starting MCP server generation...
1️⃣  Research Phase - Analyzing API...
2️⃣  Architecture Phase - Designing MCP server...
3️⃣  Development Phase - Writing code...
4️⃣  Testing Phase - Validating quality...
5️⃣  Configuration Phase - Creating docs & config...

✅ MCP Server Generation Complete!
📦 Generated: stripe-mcp-server/
```

### Example 2: Generate GitHub MCP Server
```bash
$ python generate.py --api github --verbose

# Shows detailed agent reasoning and decision-making
# Agents discuss approach, make design choices, iterate on code
```

## How It Works (Learning Orchestrations)

This project demonstrates **real CrewAI orchestration**:

### 1. Agents (agents.py)
Specialized AI workers with specific skills:
```python
researcher = Agent(
    role="API Research Specialist",
    goal="Analyze API documentation",
    tools=[check_api_documentation],
    verbose=True
)
```

### 2. Tasks (tasks.py)
Specific jobs for each agent:
```python
research_task = Task(
    description="Research the Stripe API...",
    expected_output="API specification document",
    agent=researcher
)
```

### 3. Crew (crew.py)
Coordinates agents working together:
```python
crew = Crew(
    agents=[researcher, architect, developer, qa, devops],
    tasks=[research, design, code, test, configure],
    process=Process.sequential  # One after another
)

result = crew.kickoff()  # Start the work!
```

### 4. Tools (tools.py)
Functions agents use:
```python
@tool("Write File")
def write_file(path: str, content: str) -> str:
    """Agents use this to create files"""
    ...
```

## Architecture

### Why This Approach?

**Traditional (Manual):**
```
You → Research API → Design → Code → Test → Configure
(Hours of work)
```

**Orchestration (Automated):**
```
You → Describe API → Agents do everything → Complete MCP Server
(Minutes, automated)
```

### Benefits

✅ **Fast** - Generate servers in minutes vs hours  
✅ **Consistent** - Same quality every time  
✅ **Educational** - See agents work together  
✅ **Reusable** - Generate servers for any API  
✅ **Production-Ready** - Complete, tested code  

## Understanding Orchestrations

### Orchestration = Agents Working Together

Think of it like a software company:

- **Researcher** = Market analyst (studies the API)
- **Architect** = System designer (plans structure)
- **Developer** = Engineer (writes code)
- **QA** = Tester (ensures quality)
- **DevOps** = Ops engineer (sets up deployment)

They coordinate to build a complete product!

### Sequential vs Parallel

**Sequential (Current):**
```
Research → Design → Code → Test → Configure
(One agent at a time, each uses previous results)
```

**Parallel (Advanced):**
```
       ┌─ Agent A ─┐
Start ─┼─ Agent B ─┼─ Combine → Result
       └─ Agent C ─┘
(Multiple agents work simultaneously)
```

## Customization

### Add Custom Tools
Edit `tools.py`:
```python
@tool("Your Custom Tool")
def your_tool(param: str) -> str:
    """Custom tool for agents to use"""
    # Your logic here
    return result
```

### Modify Agent Behavior
Edit `agents.py`:
```python
def create_custom_agent() -> Agent:
    return Agent(
        role="Your Role",
        goal="Your goal",
        tools=[your_tools],
        backstory="Your agent's expertise..."
    )
```

### Change Workflow
Edit `crew.py`:
```python
crew = Crew(
    agents=your_agents,
    tasks=your_tasks,
    process=Process.hierarchical  # Try different process types
)
```

## Requirements

```bash
pip install crewai crewai-tools python-dotenv
```

## Troubleshooting

### Generation Fails
- Check internet connection (agents need access to API docs)
- Try with `--verbose` to see where it fails
- Verify API name spelling

### Code Has Issues
- QA agent tests automatically
- Review generated code manually
- Regenerate if needed

### Want Different Output
- Modify agent instructions in `agents.py`
- Adjust task descriptions in `tasks.py`
- Add custom tools in `tools.py`

## Advanced Usage

### Custom API Not in List
```bash
python generate.py --api your-custom-api --verbose
```
The agents will try to find and analyze it!

### Multiple Servers
```bash
# Generate multiple MCP servers
for api in stripe github notion; do
    python generate.py --api $api
done
```

### Integration with Existing MCP Server
Use generated code as reference:
```bash
python generate.py --api easyship
# Compare with ../easyship-mcp-server/
# Learn from agent-generated approach
```

## Learning Path

### Beginner
1. Run `python generate.py --list`
2. Generate a simple MCP server: `python generate.py --api stripe`
3. Examine generated files
4. Try the demo: `cd output/stripe-mcp-server && python server.py demo`

### Intermediate
1. Study `agents.py` - See how agents are defined
2. Study `tasks.py` - Understand task structure
3. Study `crew.py` - Learn orchestration coordination
4. Run with `--verbose` to see agent reasoning

### Advanced
1. Add custom tools in `tools.py`
2. Create new agent types in `agents.py`
3. Modify workflow in `crew.py`
4. Experiment with different process types

## Related Projects

- **easyship-mcp-server/** - Example of a standalone MCP server (what this generates)
- **workflows/examples/** - Learn basic CrewAI concepts
- **workflows/integrations/** - See other orchestration patterns

## Philosophy

**Workflows = Orchestrations**
- Multiple agents coordinate
- Each has specific expertise
- They work together on complex tasks
- Output is greater than individual parts

**Services = Standalone Tools**
- MCP servers (what this generates)
- Independent, reusable
- Provide tools to AI assistants

**This project bridges both:**
- Uses orchestration (agents) to BUILD services (MCP servers)
- Meta: AI building AI tools!

## Next Steps

1. **Try It**: `python generate.py --api stripe`
2. **Learn**: Read the generated code
3. **Customize**: Modify agents and tasks
4. **Expand**: Add support for more APIs
5. **Share**: Generate MCP servers for your favorite APIs

---

**Made with CrewAI** 🤖

This is a real working orchestration demonstrating:
- Multi-agent coordination
- Sequential task workflow
- Tool usage
- Production code generation

Perfect for learning how orchestrations work in practice!
