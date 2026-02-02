# AI Agent Framework with Ollama (Offline Tool-Calling Architecture)

A minimal but production-style AI agent framework built in Python, featuring:

- Offline LLM integration via Ollama  
- Strict JSON-based tool calling protocol  
- Deterministic tool execution (no hallucinations)  
- Multi-step agent loop with tracing  
- Extensible tool registry  

This project focuses on understanding and implementing modern AI agent architectures from first principles instead of relying on high-level frameworks.

---

## Architecture Overview

The agent follows a structured decision loop:

User Input
↓
Agent (intent detection + policy enforcement)
↓
LLM (Ollama local model)
↓
JSON command (tool call or final answer)
↓
Tool execution (deterministic)
↓
Observation back to LLM
↓
Final answer


Core components:

- `Agent` - orchestrates reasoning and tool usage  
- `ToolRegistry` - manages available tools  
- `OllamaLLM` - local LLM backend client  
- `Tracer` - step-by-step execution tracking  

This mirrors real-world agent systems used in modern AI platforms.

---

## Tool Calling Loop

The framework enforces a strict protocol.

### Tool call

```json
{"tool":"tool_name","args":{...}}
````

### Final answer

```json
{"final":"..."}
```

### Key guarantees

* LLM cannot invent tool outputs
* Arithmetic always goes through math tools
* Time queries always use time tool
* Invalid behavior is rejected and retried

This eliminates hallucinations and makes agent behavior deterministic.

---

## Ollama Integration (Offline LLM)

The agent uses Ollama as a local LLM backend:

* No API keys required
* Runs fully offline
* Supports large open models (e.g. Llama 3.1)

Configuration via `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

LLM client communicates with:

```
POST /api/chat
```

using lightweight HTTP requests.

---

## Built-in Tools

### Time tool

Returns current UTC time deterministically.

### Math tools

* `math_add(a, b)`
* `math_mul(a, b)`

All calculations are enforced through tools to ensure correctness.

---

## Tracing and Observability

Each agent run produces:

* LLM requests
* raw LLM outputs
* tool calls
* tool results
* final answer

All linked by a unique `trace_id`.

This makes debugging and reasoning transparent.

---

## Getting Started

### 1. Install Ollama

[https://ollama.com](https://ollama.com)

Pull a model:

```bash
ollama pull llama3.1:8b
```

---

### 2. Setup environment

```bash
cp .env.example .env
```

Edit:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

---

### 3. Install dependencies

```bash
pip install -e .
```

---

### 4. Run CLI

```bash
python -m agentkit.adapters.cli "Сколько сейчас времени?"
python -m agentkit.adapters.cli "Посчитай 17*23 + 5"
```

---

### 5. Run Web UI

```bash
uvicorn agentkit.adapters.web:app --reload --port 8000
```

Open:

[http://localhost:8000](http://localhost:8000)

---

## Roadmap

### Completed

* Offline LLM backend (Ollama)
* Strict JSON tool calling
* Deterministic math and time tools
* Multi-step agent loop
* Tracing

### In Progress / Planned

* Expression parser (automatic workflow decomposition)
* Memory and long-term context
* RAG (document retrieval)
* Planning agents
* Multi-agent orchestration
* Tool schemas and validation

---

## Project Goals

* Learn real AI agent architectures by building them
* Avoid black-box frameworks
* Create a clean, extensible agent core
* Provide a strong engineering portfolio example

---

## License

MIT (or choose later)

---
