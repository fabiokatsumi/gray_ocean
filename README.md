# Gray Ocean

A self-evolving AI agent framework inspired by Unix philosophy. Humans describe problems in natural language; agents solve, evolve, and govern themselves.

> *The gray ocean starts as a puddle. The agents decide what it becomes.*

---

## Table of Contents

- [Overview](#overview)
- [The Unix Analogy](#the-unix-analogy)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Automated Setup](#automated-setup)
  - [Manual Setup](#manual-setup)
  - [LLM Provider Configuration](#llm-provider-configuration)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Single Message Mode](#single-message-mode)
  - [Interactive Mode](#interactive-mode)
  - [Choosing an Agent (@mentions)](#choosing-an-agent-mentions)
  - [Choosing a Model](#choosing-a-model)
  - [Live Loop (Autonomous Mode)](#live-loop-autonomous-mode)
  - [CLI Reference](#cli-reference)
- [How It Works](#how-it-works)
  - [The ReAct Loop](#the-react-loop)
  - [Hallucination Guard](#hallucination-guard)
- [Project Structure](#project-structure)
- [Tools](#tools)
  - [Primitive Tools (Built-in)](#primitive-tools-built-in)
  - [Tool Architecture](#tool-architecture)
  - [Agent-Created Tools](#agent-created-tools)
- [Agents](#agents)
  - [Anatomy of an Agent](#anatomy-of-an-agent)
  - [The Architect](#the-architect)
  - [my_chat_bot](#my_chat_bot)
  - [Agent Communication](#agent-communication)
- [Self-Modification](#self-modification)
  - [Creating Tools](#creating-tools)
  - [Creating Agents](#creating-agents)
  - [Framework Changes (Governance)](#framework-changes-governance)
- [The Constitution (VALUES.md)](#the-constitution-valuesmd)
- [Auditing and Transparency](#auditing-and-transparency)
- [Key Files Reference](#key-files-reference)
- [Evolution Roadmap](#evolution-roadmap)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

Gray Ocean is an experimental framework where AI agents operate like Unix processes. Instead of writing code, you describe what you need in plain English, and agents build the solution — including creating new tools and agents as needed.

The system starts minimal (a "puddle") with 9 primitive tools and 2 agents. As you use it, agents create new tools and spawn specialized agents, organically growing the system to handle increasingly complex tasks.

All state — agent definitions, logs, tool catalogs, governance proposals — is stored in **Markdown files**, making the entire system human-readable, git-versionable, and auditable.

---

## The Unix Analogy

| Unix Concept | Gray Ocean Equivalent | Implementation |
|---|---|---|
| Process | Agent | Folder with 5 `.md` files under `agents/` |
| Binary / Program | Tool | `.py` file with a `run()` function under `tools/` |
| Filesystem | Markdown files | All state, memory, logs, and config in `.md` files |
| Shell | `gray_ocean.py` | CLI entry point for human interaction |
| Kernel | `core/runtime.py` | ReAct loop execution engine |
| `/usr/bin` | `tools/` | Shared tool directory |
| `/home/user` | `agents/<name>/` | Per-agent home directory |
| `pipe \|` | `send_message` tool | Agent-to-agent message passing |
| `fork()` | `spawn_agent` tool | Creates new agents at runtime |
| `man` pages | `README.md` per agent/tool | Documentation for each component |
| Package manager | `register_tool` + `tools/index.md` | Tool registry and catalog |
| `/etc/constitution` | `VALUES.md` | Immutable system principles |

---

## Requirements

- **Python 3.12+** (specified in `.python-version`)
- **One of the following LLM backends:**
  - [Ollama](https://ollama.com) (local, free, default) — requires ~4GB disk for the model
  - [OpenAI API](https://platform.openai.com) — requires API key
  - [OpenRouter](https://openrouter.ai) — requires API key
- **curl** (for Ollama installation via `setup.sh`)
- **git** (for cloning)

---

## Installation

### Automated Setup

```bash
# Clone the repository
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean

# Run setup (installs uv, creates .venv, installs Ollama + llama3.1 model)
bash setup.sh

# Activate the virtual environment
source .venv/bin/activate

# Install Python dependencies
uv sync

# Start the Ollama server (if not running)
ollama serve &

# Test it
python gray_ocean.py "list all available tools"
```

The setup script:
1. Verifies Python 3 is installed
2. Installs [uv](https://github.com/astral-sh/uv) (Python package manager) if not present
3. Creates an isolated `.venv` virtual environment
4. Installs [Ollama](https://ollama.com) if not present
5. Downloads the `llama3.1` model (~4GB)

### Manual Setup

```bash
# 1. Clone the repository
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install requests

# 4. Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# 5. Download the default model
ollama pull llama3.1

# 6. Start the Ollama server
ollama serve &

# 7. Verify
python gray_ocean.py "list all available tools"
```

### LLM Provider Configuration

Copy the example env file and configure your preferred provider:

```bash
cp .env.example .env
```

**Ollama (local, free — default):**
```env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

**OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

**OpenRouter (access to many models via single API):**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct
```

> **Note:** The `.env` file is gitignored. Never commit API keys.

---

## Quick Start

```bash
# Make sure Ollama is running (skip if using OpenAI/OpenRouter)
ollama serve &

# Ask the Architect to list available tools
python gray_ocean.py "list all available tools"

# Ask it to create a new tool
python gray_ocean.py "create a tool that calculates fibonacci numbers"

# Ask it to create a specialized agent
python gray_ocean.py "I need an agent that monitors file changes"

# Talk to a specific agent using @mention
python gray_ocean.py "@my_chat_bot hello, who are you?"

# Start an interactive session
python gray_ocean.py --interactive

# Run the autonomous self-improvement loop (once, for testing)
python live.py --once
```

---

## Usage

### Single Message Mode

Send a single message and get a response:

```bash
python gray_ocean.py "your message here"
```

Examples:

```bash
# Query capabilities
python gray_ocean.py "list all available tools"
python gray_ocean.py "what agents exist in the system?"

# Create things
python gray_ocean.py "create a tool that converts CSV to JSON"
python gray_ocean.py "I need an agent that summarizes text files"

# Solve problems
python gray_ocean.py "read tools/index.md and tell me how many tools exist"
python gray_ocean.py "write a Python script that counts words in a file and save it as a tool"
```

### Interactive Mode

Start a continuous conversation loop:

```bash
python gray_ocean.py --interactive
```

```
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       GRAY OCEAN — Agent Framework
       "Starts as a puddle.
        Agents decide the rest."
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Default agent: architect | Model: llama3.1:8b
  Available agents: @architect, @my_chat_bot
  Use @agent_name message to talk to a specific agent.
  Type 'exit' or 'quit' to end the session.

  > list all tools
  ...

  > @my_chat_bot tell me a joke
  ...

  > create a tool that generates random passwords
  ...

  > exit
```

### Choosing an Agent (@mentions)

By default, messages go to the `architect` agent. You can target a specific agent in two ways:

**Using @mention (in any mode):**
```bash
python gray_ocean.py "@my_chat_bot hello"
```

**Using the --agent flag:**
```bash
python gray_ocean.py --agent my_chat_bot "hello"
python gray_ocean.py -a my_chat_bot "hello"
```

In interactive mode, use `@agent_name` at the start of any message to switch agents for that message.

### Choosing a Model

Override the default model from `.env`:

```bash
python gray_ocean.py --model mistral "your message"
python gray_ocean.py -m codellama "write a sorting algorithm"

# Combine flags
python gray_ocean.py --agent architect --model llama3.1:70b --interactive
```

> The model must be available in Ollama (`ollama pull <model_name>`), or supported by your configured API provider.

### Live Loop (Autonomous Mode)

The live loop runs an agent on a repeating heartbeat, giving it periodic prompts to review the system and make one improvement per cycle:

```bash
# Run once (good for testing)
python live.py --once

# Run every 5 minutes (default)
python live.py

# Custom interval
python live.py --interval 15

# Custom prompt
python live.py --prompt "Review all tools and improve the weakest one"

# Different agent and model
python live.py --agent architect --model llama3.1:70b
```

Press `Ctrl+C` to stop gracefully — the current cycle finishes before shutdown.

### CLI Reference

**`gray_ocean.py`** — Main entry point:

```
usage: gray_ocean.py [-h] [--agent AGENT] [--model MODEL] [--interactive] [message]

positional arguments:
  message                  Natural language message for the agent

options:
  -h, --help               Show help message and exit
  --agent AGENT, -a AGENT  Agent to invoke (default: architect)
  --model MODEL, -m MODEL  LLM model to use (default: from .env)
  --interactive, -i        Interactive mode (conversation loop)
```

**`live.py`** — Autonomous loop:

```
usage: live.py [-h] [--interval MINUTES] [--agent AGENT] [--model MODEL]
               [--prompt PROMPT] [--once]

options:
  --interval MINUTES, -n   Minutes between cycles (default: 5)
  --agent AGENT, -a        Agent to invoke each cycle (default: architect)
  --model MODEL, -m        LLM model to use (default: from .env)
  --prompt PROMPT, -p      Heartbeat prompt sent each cycle
  --once                   Run a single cycle then exit
```

---

## How It Works

### The ReAct Loop

Gray Ocean uses a **ReAct loop** (Reason + Act) — the core pattern where the LLM alternates between reasoning and taking action:

```
1. Human sends a natural language message
2. Runtime loads the target agent:
   - system_prompt.md → LLM instructions
   - personality.md   → reasoning style
   - tools.md         → authorized tool list
   - VALUES.md        → system constitution
3. Builds full system prompt with tool descriptions
4. Sends message to LLM (via Ollama/OpenAI/OpenRouter)
5. LLM responds with one of:
   a. TOOL: <tool_name> + ARGS: <params>
      → Runtime executes the tool
      → Injects tool result into conversation
      → Goes back to step 4
   b. DONE: <final answer>
      → Runtime logs the action
      → Returns response to human
6. If 15 steps reached → returns with a timeout warning
```

The LLM has **no memory between sessions**. All persistent state lives in Markdown files that are read fresh at each invocation.

### Hallucination Guard

A common failure mode is the LLM claiming "I've created the file" without actually calling a write tool. Gray Ocean detects this:

1. If the user's message requests a write action (e.g., "create", "add", "write")
2. And the LLM responds with DONE claiming it was done (e.g., "file created", "added successfully")
3. But no write tool (`write_file`, `append_file`, `register_tool`, `spawn_agent`) was called during the session
4. → The runtime rejects the response and re-prompts the LLM to actually call the tool

This catches a real class of LLM hallucination and has up to 2 retry attempts.

---

## Project Structure

```
gray_ocean/
├── gray_ocean.py              ← CLI entry point (the shell)
├── live.py                    ← Autonomous heartbeat loop
├── main.py                    ← Package entry point (placeholder)
├── setup.sh                   ← Automated installation script
├── pyproject.toml             ← Python project config (dependencies)
├── uv.lock                    ← Dependency lock file
├── .python-version            ← Python version (3.12)
├── .env.example               ← LLM provider config template
├── .gitignore                 ← Ignores .env, __pycache__, log files
│
├── GRAY_OCEAN.md              ← Manifesto and philosophy
├── VALUES.md                  ← The Constitution (8 immutable principles)
├── GUIDE.md                   ← Guide for humans and agents
├── ANALYSIS.md                ← Codebase analysis and improvement plan
├── README.md                  ← This file
│
├── core/                      ← The Kernel
│   ├── __init__.py            ← Package marker
│   └── runtime.py             ← ReAct execution loop, LLM calls, tool dispatch
│
├── tools/                     ← /usr/bin equivalent (shared tools)
│   ├── index.md               ← Catalog of all registered tools
│   ├── read_file.py           ← Read file contents (cat)
│   ├── write_file.py          ← Create or overwrite files (echo >)
│   ├── append_file.py         ← Append to existing files (echo >>)
│   ├── list_dir.py            ← List directory contents (ls)
│   ├── run_python.py          ← Sandboxed Python execution (subprocess)
│   ├── ask_llm.py             ← LLM API calls (curl for API)
│   ├── register_tool.py       ← Register new tools (install)
│   ├── spawn_agent.py         ← Create new agents (fork + mkdir)
│   └── send_message.py        ← Inter-agent messaging (pipe |)
│
├── agents/                    ← /home equivalent (agent directories)
│   ├── architect/             ← The Architect (first agent, full access)
│   │   ├── README.md          ← Mission and capabilities
│   │   ├── personality.md     ← Reasoning style and traits
│   │   ├── system_prompt.md   ← LLM instructions and rules
│   │   ├── tools.md           ← Authorized tools (all 9)
│   │   └── log.md             ← Action history (gitignored)
│   │
│   └── my_chat_bot/           ← Simple chat agent (limited access)
│       ├── README.md          ← Mission and capabilities
│       ├── personality.md     ← Reasoning style and traits
│       ├── system_prompt.md   ← LLM instructions and rules
│       ├── tools.md           ← Authorized tools (4: read, append, list, ask_llm)
│       └── log.md             ← Action history (gitignored)
│
├── gray_ocean_ideas/          ← Framework governance
│   ├── pending_ideas.md       ← Proposed changes to core framework
│   └── approved_ideas.md      ← Approved and implemented changes
│
└── messages.md                ← Inter-agent communication log
```

---

## Tools

### Primitive Tools (Built-in)

Gray Ocean ships with 9 primitive tools — the "system calls" that all agent capabilities are built on:

| Tool | Unix Analog | Description | Parameters |
|---|---|---|---|
| `read_file` | `cat` | Reads any file within gray_ocean | `path` |
| `write_file` | `echo >` | Creates or overwrites a file | `path`, `content` |
| `append_file` | `echo >>` | Appends to an existing file | `path`, `content` |
| `list_dir` | `ls` | Lists directory contents | `path` (default: root) |
| `run_python` | `subprocess` | Executes Python in a 30s sandbox | `code` |
| `ask_llm` | `curl` | Calls the configured LLM API | `prompt`, `system`?, `model`? |
| `register_tool` | `install` | Registers a new `.py` tool | `name`, `code`, `description` |
| `spawn_agent` | `fork+mkdir` | Creates a new agent | `name`, `purpose`, `tools`, `personality`? |
| `send_message` | `pipe \|` | Sends a message to another agent | `to`, `message` |

### Tool Architecture

Every tool is a standalone Python file with:

```python
# Required constants
TOOL_NAME = "tool_name"
TOOL_DESCRIPTION = "What this tool does"
TOOL_PARAMETERS = {"param": "Description of param"}

# Required function
def run(param: str) -> str:
    """Does the thing. Returns result or ERROR: message."""
    ...
```

Tools are:
- **Self-describing** — `TOOL_DESCRIPTION` and `TOOL_PARAMETERS` are injected into the LLM's system prompt
- **Sandboxed** — All file operations are restricted to the `gray_ocean/` directory (path traversal is blocked)
- **Typed** — The runtime automatically converts string arguments to the correct Python types using function annotations
- **Error-safe** — All tools return descriptive error strings instead of raising exceptions

### Agent-Created Tools

New tools created by agents appear automatically in `tools/index.md`. The full catalog is always available:

```bash
cat tools/index.md
```

---

## Agents

### Anatomy of an Agent

Each agent is a folder under `agents/` with exactly 5 Markdown files:

| File | Purpose | Analogy |
|---|---|---|
| `README.md` | What the agent does, inputs, outputs | `man` page |
| `personality.md` | Reasoning style, values, how it handles uncertainty | Character sheet |
| `system_prompt.md` | Technical instructions for the LLM | Process config |
| `tools.md` | List of authorized tools (least privilege) | Permissions |
| `log.md` | Timestamped record of all actions (gitignored) | Process log |

### The Architect

The Architect is the **first and only manually created agent**. It has access to all 9 primitive tools and is the bootstrapping mechanism for the entire system.

- **Purpose:** Build gray ocean by resolving human requests. Create tools and agents as needed. Make itself unnecessary by delegating recurring tasks to specialized agents.
- **Tools:** All 9 (read_file, write_file, append_file, list_dir, run_python, ask_llm, register_tool, spawn_agent, send_message)
- **Personality:** Methodical, pragmatic, results-oriented. Tests before registering, documents before forgetting.

When it receives a request:
1. Checks existing tools in `tools/index.md`
2. If existing tools solve it → resolves directly
3. If a tool is missing → writes code, tests in sandbox, registers it
4. For recurring tasks → spawns a specialized agent
5. Logs everything to `log.md`

### my_chat_bot

A simple chat agent created by the Architect for general conversation.

- **Purpose:** Chat with users using a local LLM
- **Tools:** 4 (read_file, append_file, list_dir, ask_llm)
- **Personality:** Objective, clear communicator

### Agent Communication

Agents communicate via the `send_message` tool, which works like a Unix pipe:

```
Agent A  →  send_message(to="agent_b", message="...")  →  Agent B processes  →  response
```

All inter-agent traffic is logged to `messages.md`. A recursion guard (`MAX_PIPE_DEPTH=3`) prevents infinite agent-to-agent call chains.

---

## Self-Modification

Gray Ocean grows organically through controlled self-modification:

```
1. Human describes a problem in natural language
2. Architect checks what tools/agents already exist
3. If existing tools solve it → resolves directly
4. If a tool is missing:
   a. Writes Python code (optionally using ask_llm)
   b. Tests in sandbox (run_python)
   c. Registers it (register_tool) → appears in tools/index.md
5. If it's a recurring task → creates a dedicated agent (spawn_agent)
6. System is slightly larger — ready for the next request
```

### Creating Tools

Agents create tools by:
1. Writing Python code with a `run()` function, `TOOL_DESCRIPTION`, and `TOOL_PARAMETERS`
2. Testing it with `run_python` to verify it works
3. Registering it with `register_tool` (saves the `.py` file and updates `tools/index.md`)

Tools are created freely — no proposal or approval needed.

### Creating Agents

Agents create other agents by using `spawn_agent`, which:
1. Creates a new folder under `agents/`
2. Generates all 5 `.md` files from the provided purpose, tools, and personality
3. Assigns **only** the tools the new agent needs (least privilege principle)
4. All new agents get the 3 base tools (`read_file`, `append_file`, `list_dir`) plus their specific tools

Agents are created freely — no proposal or approval needed.

### Framework Changes (Governance)

Changes to the **core framework** (`core/runtime.py`, `VALUES.md`, folder structure) follow a governance process:

1. Agent writes a proposal in `gray_ocean_ideas/pending_ideas.md` using the standardized format
2. Human reviews and approves (or rejects)
3. Approved proposals move to `gray_ocean_ideas/approved_ideas.md`
4. Changes are implemented

Proposal format:
```markdown
## [PROPOSAL] Name of the change
Date: YYYY-MM-DD
Proposed by: agent_name
Affected file(s): core/runtime.py | VALUES.md | folder structure
Observed problem: objective description of the framework problem
Proposed change: what exactly should change
Expected impact: what improves system-wide
Risks: what could break
Complexity: low / medium / high
```

Currently pending proposals:
- **Router Agent** — A triage layer to route messages to the right agent instead of everything going to the Architect
- **Evolution Agent** — An agent dedicated to proactively analyzing the system and proposing improvements

---

## The Constitution (VALUES.md)

Gray Ocean operates under 8 immutable principles defined in `VALUES.md`. This file is **never modified by agents** — only by humans deliberately.

1. **Simplicity Above All** — Occam's Razor. Before creating something new, ask: is there a simpler way?
2. **Total Transparency** — Every agent logs every action. No silent operations. The system state must be understandable by reading `.md` files.
3. **Least Privilege** — Each agent accesses only the tools its mission requires. No agent modifies files belonging to other agents.
4. **Intentional Immutability** — Primitive tools are extended, not modified. Core changes go through the governance process.
5. **Incremental Evolution** — One tool at a time, one agent at a time. No big refactors. Today's system must work better than yesterday's.
6. **Reuse Before Creation** — Check `tools/index.md` before creating. If 70%+ similar exists, adapt or combine.
7. **Safe Failure** — Descriptive errors, never silent failures. When in doubt between acting and not acting, don't act.
8. **Human as Final Arbiter** — The system serves humans. Critical changes require human review. Full autonomy is earned, not assumed.

See [`VALUES.md`](VALUES.md) for the full text.

---

## Auditing and Transparency

Every action leaves a human-readable trace:

```bash
# What did the Architect do?
cat agents/architect/log.md

# What tools exist?
cat tools/index.md

# What agents exist?
ls agents/

# Inter-agent communication history
cat messages.md

# Pending framework change proposals
cat gray_ocean_ideas/pending_ideas.md

# Approved framework changes
cat gray_ocean_ideas/approved_ideas.md
```

---

## Key Files Reference

| File | Description | Modified by |
|---|---|---|
| `gray_ocean.py` | CLI entry point, argument parsing, @mention routing | Humans only |
| `core/runtime.py` | ReAct loop, LLM calls, tool execution, hallucination guard | Humans only (via governance) |
| `VALUES.md` | System constitution (8 principles) | Humans only |
| `GRAY_OCEAN.md` | Manifesto and philosophy | Humans only |
| `GUIDE.md` | Guide for humans and agents | Humans only |
| `tools/index.md` | Auto-updated tool catalog | Agents (via `register_tool`) |
| `tools/*.py` | Tool implementations | Agents (via `register_tool`) |
| `agents/*/README.md` | Agent documentation | Agents (via `spawn_agent`) |
| `agents/*/log.md` | Agent action history | Agents (via `append_file`) |
| `messages.md` | Inter-agent pipe traffic log | Agents (via `send_message`) |
| `gray_ocean_ideas/pending_ideas.md` | Framework change proposals | Agents propose, humans review |
| `gray_ocean_ideas/approved_ideas.md` | Approved changes | Humans only |
| `live.py` | Autonomous heartbeat loop | Humans only |
| `.env` | LLM provider config (gitignored) | Humans only |
| `setup.sh` | Installation script | Humans only |

---

## Evolution Roadmap

| Phase | State | Description |
|---|---|---|
| **Phase 0** | The Puddle (current) | 9 tools, 2 agents (Architect + my_chat_bot), ReAct loop, CLI, multi-provider LLM |
| **Phase 1** | First Tools | Architect creates tools for real needs. 15-20 tools, 3-5 agents |
| **Phase 2** | Specialization | Specialized agents emerge. Agent collaboration via `send_message`. Tool categories |
| **Phase 3** | Governance | Router agent for message triage. Evolution agent for self-improvement proposals |
| **Phase 4** | Autonomy | Humans describe high-level goals. System proposes its own evolutions. Earned autonomy |

---

## Troubleshooting

### Ollama is not running

```
ERROR: Could not connect to LLM...
```

Start the Ollama server:
```bash
ollama serve
```

### Model not found

Pull the model first:
```bash
ollama pull llama3.1
```

### Agent not found

```
ERROR: Agent 'name' not found
```

Check available agents:
```bash
ls agents/
```

### `requests` module not found

```
ModuleNotFoundError: No module named 'requests'
```

Install dependencies:
```bash
source .venv/bin/activate
uv sync
# or: pip install requests
```

### Tool execution timeout

The `run_python` tool has a 30-second timeout. Break complex operations into smaller steps or optimize the code.

### ReAct loop timeout

The agent has a maximum of 15 steps per invocation. For complex tasks, break them into smaller sub-tasks or use the live loop for incremental work.

### Path traversal blocked

All file tools are sandboxed to the `gray_ocean/` directory. Files outside this directory cannot be read or written by agents.

### OpenAI/OpenRouter returns errors

Check that your `.env` has the correct:
- `LLM_PROVIDER` value (`openai` or `openrouter`)
- Valid API key (`OPENAI_API_KEY` or `OPENROUTER_API_KEY`)
- Supported model name (`OPENAI_MODEL` or `OPENROUTER_MODEL`)

---

## Contributing

Gray Ocean is an experimental project. Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For changes to core framework files (`core/runtime.py`, `VALUES.md`), please follow the governance process described in [Framework Changes](#framework-changes-governance).

---

## License

This project is open source. See the repository for license details.
