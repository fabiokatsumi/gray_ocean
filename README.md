# Gray Ocean

A self-evolving AI agent framework inspired by Unix philosophy. Humans describe problems in natural language; agents solve, evolve, and govern themselves.

> *The gray ocean starts as a puddle. The agents decide what it becomes.*

---

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Single Message Mode](#single-message-mode)
  - [Interactive Mode](#interactive-mode)
  - [Choosing an Agent](#choosing-an-agent)
  - [Choosing a Model](#choosing-a-model)
  - [CLI Reference](#cli-reference)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Tools](#tools)
- [Agents](#agents)
  - [Anatomy of an Agent](#anatomy-of-an-agent)
  - [The Architect](#the-architect)
- [Self-Modification](#self-modification)
  - [Creating Tools](#creating-tools)
  - [Creating Agents](#creating-agents)
  - [Framework Changes](#framework-changes)
- [Auditing and Transparency](#auditing-and-transparency)
- [Values](#values)
- [Evolution Roadmap](#evolution-roadmap)
- [Troubleshooting](#troubleshooting)

---

## Overview

Gray Ocean is a Unix-inspired operating system for AI agents:

| Unix | Gray Ocean |
|---|---|
| Process | Agent |
| Binary / Program | Tool (`.py` file) |
| Filesystem | Markdown files (memory, logs, state) |
| Shell | `gray_ocean.py` (human interface) |
| Kernel | `core/runtime.py` (execution engine) |
| `/usr/bin` | `tools/` (shared tools) |
| `/home/user` | `agents/<name>/` (agent home) |
| `pipe \|` | Message bus between agents |
| `fork()` | `spawn_agent()` |
| `man pages` | `README.md` of each agent/tool |
| Package manager | Tool registry + `index.md` |

Everything is stored in Markdown files — readable by both humans and agents, versioned by Git, with no external database required.

---

## Requirements

- **Python 3.8+** (standard library only, no pip dependencies)
- **Ollama** (local LLM runtime)
- **curl** (for Ollama installation)

---

## Installation

### Automated Setup

```bash
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean
bash setup.sh
```

The setup script will:
1. Verify Python 3 is installed
2. Install Ollama (if not already present)
3. Download the `llama3.1` model

### Manual Setup

If you prefer to set things up manually:

```bash
# 1. Clone the repository
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean

# 2. Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# 3. Download the default model
ollama pull llama3.1

# 4. Start the Ollama server (if not running automatically)
ollama serve
```

### Verify Installation

```bash
# Check Ollama is running
ollama list

# Test Gray Ocean
python3 gray_ocean.py "liste todas as tools disponíveis"
```

---

## Quick Start

```bash
# Make sure Ollama is running
ollama serve &

# Ask the Architect to list available tools
python3 gray_ocean.py "list all available tools"

# Ask it to create a new tool
python3 gray_ocean.py "create a tool that calculates fibonacci numbers"

# Ask it to create a specialized agent
python3 gray_ocean.py "I need an agent that monitors file changes"

# Start an interactive session
python3 gray_ocean.py --interactive
```

---

## Usage

### Single Message Mode

Send a single message and get a response:

```bash
python3 gray_ocean.py "your message here"
```

Examples:

```bash
# Query existing capabilities
python3 gray_ocean.py "list all available tools"
python3 gray_ocean.py "what agents exist in the system?"

# Create things
python3 gray_ocean.py "create a tool that converts CSV to JSON"
python3 gray_ocean.py "I need an agent that summarizes PDF files"

# Solve problems
python3 gray_ocean.py "read the file tools/index.md and tell me how many tools exist"
python3 gray_ocean.py "write a Python script that counts words in a file and save it as a tool"
```

### Interactive Mode

Start a continuous conversation loop:

```bash
python3 gray_ocean.py --interactive
```

In interactive mode:
- Type your messages and press Enter
- Type `exit`, `quit`, or `sair` to end the session
- Press `Ctrl+C` to interrupt

```
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
       GRAY OCEAN — Agent Framework
       "Começa como uma poça.
        Os agentes decidem o resto."
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Agente: architect | Modelo: llama3.1
  Digite 'sair' ou 'exit' para encerrar.

  > list all tools
  ...

  > create a tool that generates random passwords
  ...

  > exit
```

### Choosing an Agent

By default, messages go to the `architect` agent. To use a different agent:

```bash
python3 gray_ocean.py --agent <agent_name> "your message"
python3 gray_ocean.py -a <agent_name> "your message"
```

Example (after creating a `monitor` agent):

```bash
python3 gray_ocean.py --agent monitor "check for changed files"
```

### Choosing a Model

By default, Ollama uses `llama3.1`. To use a different model:

```bash
python3 gray_ocean.py --model <model_name> "your message"
python3 gray_ocean.py -m <model_name> "your message"
```

Examples:

```bash
# Use a different Ollama model
python3 gray_ocean.py --model mistral "your message"
python3 gray_ocean.py --model codellama "write a sorting algorithm"

# Combine flags
python3 gray_ocean.py --agent architect --model mistral --interactive
```

> **Note:** The model must be available in Ollama. Pull it first with `ollama pull <model_name>`.

### CLI Reference

```
usage: gray_ocean.py [-h] [--agent AGENT] [--model MODEL] [--interactive] [message]

positional arguments:
  message                  Message in natural language for the agent

options:
  -h, --help               Show help message and exit
  --agent AGENT, -a AGENT  Agent to invoke (default: architect)
  --model MODEL, -m MODEL  LLM model via Ollama (default: llama3.1)
  --interactive, -i        Interactive mode (conversation loop)
```

---

## How It Works

Gray Ocean uses a **ReAct loop** (Reason + Act) — the agent thinks and acts in the same loop:

```
1. Human sends a message
2. Runtime loads the agent (personality, system prompt, authorized tools)
3. Message is sent to the LLM via Ollama
4. LLM responds with either:
   a. TOOL: <tool_name> + arguments → Runtime executes the tool,
      injects the result, and goes back to step 3
   b. DONE: <final answer> → Runtime logs the action and returns
      the response to the human
5. If max steps (15) reached → Returns with a timeout warning
```

The LLM has no memory between sessions. All persistent state lives in Markdown files that are read at the start of each invocation.

---

## Project Structure

```
gray_ocean/
├── README.md                  ← this file
├── GRAY_OCEAN.md              ← manifesto and system overview
├── GUIDE.md                   ← guide for humans and agents
├── VALUES.md                  ← immutable principles (the constitution)
├── gray_ocean.py              ← entry point (the shell)
├── setup.sh                   ← automated installation script
│
├── core/                      ← the kernel
│   ├── __init__.py
│   └── runtime.py             ← ReAct execution loop
│
├── tools/                     ← /usr/bin equivalent
│   ├── index.md               ← catalog of all tools
│   ├── read_file.py           ← read file contents
│   ├── write_file.py          ← create or overwrite files
│   ├── append_file.py         ← append to existing files
│   ├── list_dir.py            ← list directory contents
│   ├── run_python.py          ← sandboxed Python execution
│   ├── ask_llm.py             ← LLM API calls via Ollama
│   ├── register_tool.py       ← register new tools
│   └── spawn_agent.py         ← create new agents
│
├── agents/                    ← /home equivalent
│   └── architect/             ← the first agent
│       ├── README.md          ← what it does (man page)
│       ├── personality.md     ← how it thinks
│       ├── system_prompt.md   ← LLM instructions
│       ├── tools.md           ← authorized tools
│       └── log.md             ← action history
│
└── gray_ocean_ideas/          ← framework governance
    ├── pending_ideas.md       ← proposed changes to core framework
    └── approved_ideas.md      ← approved changes
```

---

## Tools

The 8 primitive tools are the system calls of Gray Ocean. Everything agents do is built on top of them.

| Tool | Unix Equivalent | Description |
|---|---|---|
| `read_file` | `cat` | Reads any file within gray_ocean |
| `write_file` | `echo >` | Creates or overwrites a file |
| `append_file` | `echo >>` | Appends to an existing file |
| `list_dir` | `ls` | Lists directory contents |
| `run_python` | `subprocess` | Executes Python code in a 30-second sandbox |
| `ask_llm` | `curl` | Calls the LLM via Ollama API |
| `register_tool` | `install` | Saves a new `.py` tool and updates `tools/index.md` |
| `spawn_agent` | `fork + mkdir` | Creates a new agent with its 5 `.md` files |

Every tool:
- Is a standalone `.py` file with a `run()` function
- Has a docstring, `TOOL_NAME`, `TOOL_DESCRIPTION`, and `TOOL_PARAMETERS`
- Validates inputs and returns descriptive errors on failure
- Is sandboxed to the `gray_ocean/` directory (path traversal is blocked)

The full catalog is always available at `tools/index.md`.

---

## Agents

### Anatomy of an Agent

Each agent is a folder with exactly 5 Markdown files:

| File | Purpose |
|---|---|
| `README.md` | What the agent does, inputs, outputs. The "man page". |
| `personality.md` | Who the agent is. Values, reasoning style, how it handles uncertainty. |
| `system_prompt.md` | Technical instructions injected into the LLM. Response format, constraints, tool usage. |
| `tools.md` | List of authorized tools. Principle of least privilege: only what's needed. |
| `log.md` | Chronological record of all actions. Auditable by humans. |

### The Architect

The Architect is the first and only manually created agent. All future agents are created by agents.

- Has access to all 8 primitive tools
- When it receives a request: checks existing tools, creates what's missing, resolves
- For recurring tasks: uses `spawn_agent` to create a specialized agent
- Always documents what it creates in `log.md` and `tools/index.md`

Its goal is to **make itself unnecessary** — by building an ecosystem of specialized agents.

---

## Self-Modification

The Gray Ocean grows organically through a controlled self-modification cycle:

```
1. Human describes a problem in natural language
2. Architect reads tools/index.md and checks what exists
3a. If existing tools solve it → resolves directly
3b. If a tool is missing → writes code (ask_llm)
                          → tests in sandbox (run_python)
                          → registers it (register_tool)
3c. If it's a recurring task → creates a dedicated agent (spawn_agent)
4. New tools appear in tools/index.md immediately
5. New agents are born with ONLY the tools they need
6. The system is slightly larger — repeat for the next request
```

### Creating Tools

Agents create tools by:
1. Writing Python code with a `run()` function
2. Testing it with `run_python`
3. Registering it with `register_tool` (saves the `.py` and updates `tools/index.md`)

Tools are created freely — no proposal or approval needed.

### Creating Agents

Agents create other agents by using `spawn_agent`, which:
1. Creates a new folder under `agents/`
2. Generates all 5 `.md` files
3. Assigns **only** the tools the new agent needs (least privilege)

Agents are created freely — no proposal or approval needed.

### Framework Changes

Changes to the **core framework** (`core/runtime.py`, `VALUES.md`, folder structure) follow a governance process:

1. Agent writes a proposal in `gray_ocean_ideas/pending_ideas.md`
2. Human reviews and approves
3. Approved proposals move to `gray_ocean_ideas/approved_ideas.md`
4. Changes are implemented

Proposal format:

```markdown
## [PROPOSTA] Name of the change
Data: YYYY-MM-DD
Proposta por: agent_name
Arquivo(s) afetado(s): core/runtime.py | VALUES.md | folder structure
Problema observado: objective description of the framework problem
Mudança proposta: what exactly should change
Impacto esperado: what improves system-wide
Riscos: what could break
Complexidade: low / medium / high
```

---

## Auditing and Transparency

Every action in the Gray Ocean leaves a readable trace:

- **Agent logs:** `agents/<name>/log.md` — timestamped history of every action
- **Tool catalog:** `tools/index.md` — always up-to-date list of all tools
- **Agent inventory:** `agents/` directory — every agent has its full config in readable `.md` files
- **Framework proposals:** `gray_ocean_ideas/` — all proposed and approved changes to the core

To audit the system at any point:

```bash
# What did the Architect do?
cat agents/architect/log.md

# What tools exist?
cat tools/index.md

# What agents exist?
ls agents/

# Any pending framework changes?
cat gray_ocean_ideas/pending_ideas.md
```

---

## Values

The Gray Ocean operates under 8 immutable principles defined in `VALUES.md`:

1. **Simplicity Above All** — Occam's Razor. Prefer the simplest solution that works.
2. **Total Transparency** — Every action is logged. No silent operations.
3. **Least Privilege** — Agents access only the tools their mission requires.
4. **Intentional Immutability** — Primitive tools are extended, not modified. Core changes go through governance.
5. **Incremental Evolution** — One tool at a time, one agent at a time. No big refactors.
6. **Reuse Before Creation** — Check `tools/index.md` before creating. Adapt if 70%+ similar.
7. **Safe Failure** — Descriptive errors, never silent failures. When in doubt, don't act.
8. **Human as Final Arbiter** — The system serves humans. Critical changes require human review.

See `VALUES.md` for the full text.

---

## Evolution Roadmap

| Phase | State | Description |
|---|---|---|
| **Phase 0** | The Puddle | 8 tools, 1 agent (Architect), simple ReAct loop, CLI interface, local Ollama |
| **Phase 1** | First Tools | Architect creates tools for real needs. 15-20 tools, 3-5 agents |
| **Phase 2** | Specialization | Specialized agents emerge. Agent collaboration. Tool categories |
| **Phase 3** | Governance | Governor agent reviews framework proposals. Tester agent validates tools |
| **Phase 4** | Autonomy | Humans describe high-level goals. System proposes its own evolutions |

---

## Troubleshooting

### Ollama is not running

```
ERRO: Não foi possível conectar ao Ollama...
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
ERRO: Agente 'nome' não encontrado
```

Check available agents:

```bash
ls agents/
```

### Tool execution timeout

The `run_python` tool has a 30-second timeout. If your code takes longer, break it into smaller steps or optimize the code.

### ReAct loop timeout

The agent has a maximum of 15 steps per invocation. If a task is too complex, break it into smaller sub-tasks.

### Path traversal blocked

All file tools are sandboxed to the `gray_ocean/` directory. Files outside this directory cannot be read or written.
