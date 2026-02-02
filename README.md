# AI Agent Starter Kit (Python)

Minimal AI agent framework with:

- CLI interface
- Web UI (FastAPI)
- Tool registry system
- Tracing / observability
- Extensible architecture for LLMs and tools

## Features

- Agent input → decision → tool execution → response loop
- Built-in example tool (UTC time)
- CLI adapter
- Web adapter
- Clean modular design

## Project structure

src/
  agentkit/
    core/        # agent logic, models, tracing
    tools/       # tools and registry
    adapters/   # CLI and Web interfaces

## Run CLI

```bash
source .venv/bin/activate
python -m agentkit.adapters.cli "what time is it?"
