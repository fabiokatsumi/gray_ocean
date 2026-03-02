# Gray Ocean — Codebase Analysis & Improvement Recommendations

> **Date:** 2026-03-02
> **Scope:** Full codebase review covering architecture, runtime, tools, agents, security, deployment, and viability.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. What Gray Ocean Is](#2-what-gray-ocean-is)
- [3. Architecture Overview](#3-architecture-overview)
- [4. Strengths](#4-strengths)
- [5. Critical Issues (Must Fix)](#5-critical-issues-must-fix)
- [6. High-Priority Improvements](#6-high-priority-improvements)
- [7. Medium-Priority Improvements](#7-medium-priority-improvements)
- [8. Low-Priority / Nice-to-Have](#8-low-priority--nice-to-have)
- [9. Security Analysis](#9-security-analysis)
- [10. How to Start the Project](#10-how-to-start-the-project)
- [11. How to Put It Online (Deployment)](#11-how-to-put-it-online-deployment)
- [12. Viability Assessment](#12-viability-assessment)
- [13. Recommended Next Steps (Prioritized)](#13-recommended-next-steps-prioritized)

---

## 1. Executive Summary

Gray Ocean is a self-evolving AI agent framework with a compelling Unix-inspired philosophy: agents are processes, tools are programs, markdown files are the filesystem, and the runtime is the kernel. The concept is strong and the architecture is clean for an MVP.

However, several **critical gaps** prevent it from working reliably in practice:

1. **The `requests` library is imported but not installed** — the `pyproject.toml` declares it, but `setup.sh` never runs `uv pip install` or `uv sync`, so OpenAI/OpenRouter providers will crash on import.
2. **`setup.sh` has a broken output order** — the "Setup complete!" banner prints *before* any steps run.
3. **No conversation memory** — each invocation is stateless; the agent cannot remember prior context.
4. **`run_python` is an unrestricted code execution sandbox** — any Python code runs with full filesystem and network access.
5. **Path traversal protection is bypassable** — `os.path.normpath` + `startswith` can be tricked via symlinks.

The framework has strong bones. With the fixes below, it could be a genuinely useful experimental platform.

---

## 2. What Gray Ocean Is

Gray Ocean is a **self-evolving agent framework** where:

- A human sends natural language messages via CLI
- The **Architect** agent (the only bootstrapped agent) receives the message
- The runtime executes a **ReAct loop** (Reason + Act): the LLM reasons, calls tools, observes results, and repeats
- If a tool or agent doesn't exist, the Architect can **create** them at runtime
- All state is stored in **Markdown files** — human-readable, git-versioned, no database
- A **constitution** (`VALUES.md`) governs agent behavior with 8 immutable principles
- A **governance process** (`gray_ocean_ideas/`) manages changes to the core framework

The system is designed to start as a "puddle" (9 tools, 2 agents) and grow organically as agents create new tools and agents to solve problems.

---

## 3. Architecture Overview

```
                          ┌──────────────┐
                          │   Human CLI  │
                          │ gray_ocean.py│
                          └──────┬───────┘
                                 │ natural language
                                 ▼
                          ┌──────────────┐
                          │   Runtime    │
                          │ runtime.py   │
                          │  (ReAct Loop)│
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌───────────┐ ┌─────────┐ ┌──────────┐
             │  Agent .md │ │  Tools  │ │   LLM    │
             │  files     │ │  (.py)  │ │ Provider │
             └───────────┘ └─────────┘ └──────────┘

Flow:
  1. gray_ocean.py parses CLI args, calls run_agent()
  2. runtime.py loads agent .md files (system_prompt, personality, tools)
  3. Builds full system prompt with tool descriptions + VALUES.md
  4. Sends to LLM, parses response for TOOL: or DONE:
  5. If TOOL: executes tool, injects result, loops back to LLM
  6. If DONE: logs action, returns response
  7. Max 15 steps before timeout
```

### Key Files

| File | Role | Lines |
|---|---|---|
| `gray_ocean.py` | CLI entry point (shell) | 194 |
| `core/runtime.py` | ReAct loop engine (kernel) | 588 |
| `live.py` | Autonomous heartbeat loop | 187 |
| `tools/*.py` (9 files) | Primitive tool implementations | ~500 total |
| `agents/architect/*.md` | Architect agent definition | 5 files |
| `agents/my_chat_bot/*.md` | Chat bot agent definition | 5 files |
| `VALUES.md` | System constitution | 67 |
| `GRAY_OCEAN.md` | Manifesto | 49 |
| `GUIDE.md` | Human/agent guide | 80 |

---

## 4. Strengths

### 4.1 Clean Conceptual Model
The Unix analogy (agents=processes, tools=programs, markdown=filesystem) is intuitive and makes the system immediately understandable. This is a genuine differentiator.

### 4.2 Constitution-Driven Design
`VALUES.md` as an immutable constitution that all agents must follow is a smart governance mechanism. The 8 principles are well-thought-out and practical.

### 4.3 Transparency by Default
Everything is in Markdown. Logs, state, tool catalogs, agent definitions — all human-readable and git-versionable. This is a major strength for auditability.

### 4.4 Hallucination Guard
The `_response_claims_write()` / `_message_requests_write()` mechanism in `runtime.py` catches cases where the LLM claims to have written something without actually calling a write tool. This is a pragmatic and effective safeguard.

### 4.5 Multi-Provider LLM Support
Supporting Ollama (local), OpenAI, and OpenRouter gives flexibility. The streaming implementation is solid.

### 4.6 Controlled Self-Modification
The separation between "tools/agents can be created freely" and "core changes require proposals" is a balanced approach to self-evolution.

### 4.7 Live Loop (`live.py`)
The autonomous heartbeat loop is a creative addition — it allows the system to evolve itself periodically without human intervention, which is aligned with the self-evolving philosophy.

---

## 5. Critical Issues (Must Fix)

### 5.1 `setup.sh` is Broken — Banner Before Steps

**File:** `setup.sh` (lines 9-14 vs 15-82)

The "Setup complete!" banner and usage instructions print **before** any setup steps run. The `echo` block at lines 9-14 executes first, then the actual setup steps follow.

**Fix:** Move the banner block to the end of the script, after all steps complete.

### 5.2 Dependencies Not Installed

**File:** `pyproject.toml`, `setup.sh`

`pyproject.toml` declares `requests>=2.32.5` as a dependency, and `runtime.py` + `ask_llm.py` import it for OpenAI/OpenRouter providers. But `setup.sh` never runs `uv sync` or `uv pip install`, so `requests` is never actually installed.

**Fix:** Add `uv sync` or `uv pip install -e .` after creating the `.venv` in `setup.sh`.

### 5.3 `main.py` is a Dead File

**File:** `main.py`

Contains only `print("Hello from gray-ocean!")`. It's not referenced anywhere and creates confusion about the actual entry point (`gray_ocean.py`).

**Fix:** Remove `main.py` or replace it with a proper package entry point that delegates to `gray_ocean.py`.

### 5.4 `run_python` Has No Sandboxing

**File:** `tools/run_python.py`

The "sandbox" is just `subprocess.run` with a 30-second timeout. The executed code has:
- Full filesystem access (read/write anything the process can)
- Full network access (HTTP requests, sockets, etc.)
- Ability to install packages, modify system files, etc.
- Access to environment variables (including API keys)

An LLM-generated tool could exfiltrate API keys, delete files, or make external requests.

**Fix (incremental, per VALUES.md):**
1. **Immediate:** Add `env={}` to `subprocess.run()` to prevent environment variable leakage
2. **Short-term:** Use a restricted Python environment or at minimum block imports of `os`, `subprocess`, `socket` via a code check
3. **Long-term:** Consider using a proper sandbox (Docker, seccomp, or nsjail)

### 5.5 Path Traversal via Symlinks

**File:** All tools using `os.path.normpath` + `startswith`

The path validation in `read_file.py`, `write_file.py`, `append_file.py`, and `list_dir.py` uses:
```python
full_path = os.path.normpath(os.path.join(BASE_DIR, path))
if not full_path.startswith(BASE_DIR):
    return "ERROR: Access denied."
```

This is bypassed if a symlink inside `gray_ocean/` points outside the directory. `normpath` resolves `..` but not symlinks.

**Fix:** Use `os.path.realpath()` instead of `os.path.normpath()` to resolve symlinks before checking the prefix.

---

## 6. High-Priority Improvements

### 6.1 Add Conversation Memory

**Current:** Each `run_agent()` call starts with an empty conversation. The agent has zero context from previous interactions.

**Impact:** The agent cannot follow multi-turn workflows like "create a tool" → "now test it" → "now add error handling".

**Recommended approach:**
- Store conversation history in a per-agent JSON or Markdown file
- Load the last N exchanges when starting a new invocation
- Add a `--fresh` flag to start with no history
- Keep it simple: append to `agents/<name>/history.json`

### 6.2 Add Error Recovery to the ReAct Loop

**Current:** If the LLM returns a malformed response (no TOOL: or DONE:), it's treated as an implicit DONE and the loop ends.

**Impact:** An LLM that rambles or produces partially correct output terminates the task prematurely.

**Fix:** When a response has no TOOL: or DONE:, instead of silently treating it as DONE, re-prompt the LLM with:
```
"Your response did not contain a TOOL: or DONE: directive. Please respond with either TOOL: to call a tool, or DONE: to provide your final answer."
```

### 6.3 `.env` Loading is Duplicated 4 Times

**Files:** `gray_ocean.py`, `core/runtime.py`, `live.py`, `tools/ask_llm.py`

The same `.env` parsing logic is copy-pasted across 4 files. Each has its own `load_env()` function with identical code.

**Fix:** Create a single `core/config.py` that loads and exposes configuration. All files import from it.

### 6.4 `core/__init__.py` Has a Portuguese Comment

**File:** `core/__init__.py`

Contains: `# Gray Ocean Core — Motor de execução de agentes`

The rest of the codebase was translated to English, but this was missed.

**Fix:** Update to `# Gray Ocean Core — Agent execution engine`

### 6.5 Tool Parsing is Fragile

**File:** `core/runtime.py` — `parse_llm_response()` (lines 207-282)

The TOOL/ARGS parser has issues:
- A colon in a parameter value (e.g., `url: http://example.com`) will be misinterpreted as a new key-value pair
- The `not line.startswith(" " * 4)` heuristic for distinguishing keys from content is brittle
- If the LLM produces `TOOL: read_file` followed by `DONE: here is the result`, only the TOOL is parsed (DONE check happens first but is ordered after TOOL in the if-else)

**Fix:**
- Parse key-value pairs only after `ARGS:` line and before a blank line or `DONE:`
- Use `line.split(":", 1)` only if the key part contains no spaces (tool parameter names shouldn't have spaces)
- Consider requiring all multi-character values to use the `<<<>>>` delimiter

### 6.6 The `requests` Import Should Be Conditional

**File:** `core/runtime.py` (line 362)

`import requests` is at the top of `call_llm()`, which means it runs even for the `ollama` provider (which uses only `urllib`). If `requests` is not installed, even the Ollama path fails.

**Fix:** Move `import requests` inside the `elif provider in ("openai", "openrouter"):` branch.

### 6.7 `send_message` Tool Missing from Architect's README

**File:** `agents/architect/README.md` (line 17)

The README lists 8 tools but the Architect has 9 (the `send_message` tool is missing from the README list, though it's present in `tools.md`).

**Fix:** Add `send_message` to the Authorized Tools list in the README.

---

## 7. Medium-Priority Improvements

### 7.1 Add a `--version` Flag

Currently there's no way to check the installed version. `pyproject.toml` defines `version = "0.1.0"` but it's not exposed via CLI.

### 7.2 Add Input Validation to `spawn_agent`

The `spawn_agent` tool accepts any list of tool names without checking if those tools actually exist in `tools/`. An agent could be created with tools that don't exist, leading to confusing errors at runtime.

### 7.3 Implement the Router Agent Proposal

The pending proposal for a Router Agent (`gray_ocean_ideas/pending_ideas.md`) is well-reasoned and would significantly improve usability. Instead of all messages going to the Architect, a lightweight router could dispatch to the right agent.

### 7.4 Add Token/Cost Tracking

The system makes LLM calls but has no visibility into token usage or cost. For OpenAI/OpenRouter providers, response headers include token counts. Logging these would help monitor usage.

### 7.5 Add a `delete_file` Tool

The system can create and modify files but cannot delete them. This limits the Architect's ability to clean up after itself.

### 7.6 Support for `.env` Quoted Values

The `.env` parser doesn't handle quoted values. A value like `OPENAI_API_KEY="sk-xxx"` would include the quotes as part of the value.

### 7.7 `live.py` Should Log to a File

The live loop prints to stdout but doesn't persist its output. If run as a background process, all output is lost.

### 7.8 Tool Result Size Limits

There's no limit on tool result size. A `read_file` on a large file could blow up the LLM context window. Consider truncating results beyond a threshold (e.g., 10,000 characters) with a note about truncation.

---

## 8. Low-Priority / Nice-to-Have

### 8.1 Add Unit Tests
No tests exist. Even basic tests for `parse_llm_response()`, `parse_authorized_tools()`, and the path validation in tools would catch regressions.

### 8.2 Add a Web Interface
The CLI is functional but a simple web UI (even a basic Flask/FastAPI app) would dramatically improve accessibility.

### 8.3 Support Anthropic Claude as a Provider
The `call_llm()` function supports Ollama, OpenAI, and OpenRouter. Adding native Anthropic API support would be straightforward and valuable given Claude's strong tool-use capabilities.

### 8.4 Agent-to-Agent Communication Patterns
Currently `send_message` is a simple pipe. More sophisticated patterns (broadcast, pub/sub, shared mailbox) could enable richer agent collaboration.

### 8.5 Tool Versioning
When a tool is updated, the old version is lost. A simple versioning scheme (copy to `tools/archive/`) before overwrite would help.

---

## 9. Security Analysis

### 9.1 Threat Model

| Threat | Severity | Status |
|---|---|---|
| **Arbitrary code execution** via `run_python` | **Critical** | No sandboxing beyond timeout |
| **Path traversal** via symlinks | **High** | Uses `normpath` instead of `realpath` |
| **API key leakage** via `run_python` env access | **High** | Env vars accessible to subprocess |
| **Prompt injection** via tool results | **Medium** | No sanitization of tool output before re-injection into LLM |
| **Denial of service** via infinite agent loops | **Low** | Mitigated by MAX_STEPS=15 and MAX_PIPE_DEPTH=3 |
| **File overwrite** — agent overwrites critical files | **Medium** | No write-protection on VALUES.md, runtime.py from tools |

### 9.2 Recommendations

1. **Protect immutable files:** `write_file` and `append_file` should refuse to modify `VALUES.md`, `core/runtime.py`, and `core/__init__.py` — enforcing the constitution's immutability rule at the tool level, not just the prompt level.
2. **Sanitize tool results:** Before injecting tool results back into the LLM conversation, escape or truncate content that could be interpreted as TOOL:/DONE: directives.
3. **Add `os.path.realpath()`** to all path validations.
4. **Strip env vars** from `run_python` subprocess.
5. **Rate-limit LLM calls** — a runaway live loop could make thousands of API calls.

---

## 10. How to Start the Project

### Prerequisites

- **Python 3.12+** (as specified in `.python-version`)
- **git** (for cloning)
- **curl** (for Ollama installation)
- ~4GB disk space for the LLM model

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean

# 2. Run the setup script (installs uv, creates venv, installs Ollama + model)
bash setup.sh

# 3. Activate the virtual environment
source .venv/bin/activate

# 4. Install Python dependencies (IMPORTANT — setup.sh doesn't do this yet)
uv sync
# or: uv pip install -e .

# 5. Copy and configure the environment file
cp .env.example .env
# Edit .env to choose your LLM provider (ollama is default, no edits needed)

# 6. Start the Ollama server (if not already running)
ollama serve &

# 7. Test it
python gray_ocean.py "list all available tools"

# 8. Start an interactive session
python gray_ocean.py --interactive

# 9. (Optional) Run the autonomous live loop
python live.py --once    # single cycle, good for testing
python live.py           # continuous, every 5 minutes
```

### Using Different LLM Providers

**Ollama (local, free, default):**
```bash
# .env
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

**OpenAI:**
```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
```

**OpenRouter (access to many models):**
```bash
# .env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct
```

---

## 11. How to Put It Online (Deployment)

### Option A: Run on a VPS (Simplest)

Best for: personal use, experimentation, small teams.

```bash
# 1. Get a VPS (DigitalOcean, Hetzner, Linode — $10-20/mo)
#    Minimum: 2 CPU, 4GB RAM (8GB+ if running Ollama locally)

# 2. SSH into the server
ssh user@your-server

# 3. Install prerequisites
sudo apt update && sudo apt install -y python3 python3-pip curl git

# 4. Clone and set up
git clone https://github.com/fabiokatsumi/gray_ocean.git
cd gray_ocean
bash setup.sh
source .venv/bin/activate
uv sync

# 5. Configure .env (use OpenAI/OpenRouter to avoid running Ollama on VPS)
cp .env.example .env
nano .env  # set LLM_PROVIDER=openai and your API key

# 6. Run the live loop as a background service
nohup python live.py > live.log 2>&1 &

# 7. Or use systemd for persistence
sudo tee /etc/systemd/system/gray-ocean.service << 'EOF'
[Unit]
Description=Gray Ocean Live Loop
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/gray_ocean
ExecStart=/home/your-user/gray_ocean/.venv/bin/python live.py
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable gray-ocean
sudo systemctl start gray-ocean
```

### Option B: Add a Web API Layer

To make Gray Ocean accessible over HTTP, add a thin API wrapper:

```python
# api.py (new file — example using FastAPI)
from fastapi import FastAPI
from pydantic import BaseModel
from core.runtime import run_agent

app = FastAPI(title="Gray Ocean API")

class MessageRequest(BaseModel):
    message: str
    agent: str = "architect"
    model: str = None

@app.post("/message")
def send_message(req: MessageRequest):
    response = run_agent(req.agent, req.message, model=req.model)
    return {"response": response}
```

Then deploy with:
```bash
pip install fastapi uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Note:** You'd need to modify `run_agent` to return the response as a string instead of streaming to stdout. This is the biggest deployment blocker — the current architecture is CLI-first.

### Option C: Docker Container

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

# For OpenAI/OpenRouter (no Ollama needed)
ENV LLM_PROVIDER=openai

CMD ["python", "live.py"]
```

```bash
docker build -t gray-ocean .
docker run -d --env-file .env gray-ocean
```

### Option D: Connect to Chat Platforms

The most natural "online" deployment is connecting Gray Ocean to a chat platform:

1. **Telegram Bot** — Add a `telegram_bot.py` that receives messages via Telegram's Bot API and pipes them through `run_agent()`
2. **Discord Bot** — Same pattern with Discord.py
3. **Slack Bot** — Webhook-based integration

This would require:
- A new tool or wrapper script for each platform
- Modifying `run_agent()` to capture output as a string (not print to stdout)
- Running on a VPS with the bot as a long-running process

### Deployment Blockers to Address First

1. **`run_agent()` streams to stdout** — Need a mode that captures and returns the response string for non-CLI use
2. **No authentication** — Anyone with access could send messages. Add API key auth for web deployments
3. **No rate limiting** — Exposed API could be abused
4. **`run_python` security** — Must be sandboxed before any online deployment

---

## 12. Viability Assessment

### What Works Today

- The core ReAct loop functions correctly with Ollama
- The Architect can create tools and agents via natural language
- The tool/agent creation pipeline works end-to-end
- The hallucination guard catches a real class of LLM errors
- The live loop enables autonomous operation
- Multi-provider LLM support gives flexibility

### What Needs Work to Be Viable

| Area | Current State | Needed for Viability |
|---|---|---|
| **Setup** | Broken `setup.sh`, missing `uv sync` | Fix script, add dependency install |
| **Memory** | No conversation history | At minimum per-session, ideally persistent |
| **Security** | `run_python` is wide open | Sandbox or restrict before any deployment |
| **Reliability** | Fragile TOOL/ARGS parser | Improve parsing, add retry on malformed responses |
| **Deployment** | CLI-only, stdout-coupled | Add string-return mode for `run_agent()` |
| **Testing** | Zero tests | Basic tests for parser and tools |

### Verdict

**Gray Ocean is a solid MVP with a compelling concept.** The Unix philosophy mapping is genuinely insightful, the constitution-based governance is novel, and the self-evolving design is ambitious in the right way. The codebase is clean and readable.

The critical issues are all fixable with modest effort. The biggest gap is the lack of proper sandboxing for `run_python`, which must be addressed before any online deployment. The second biggest gap is the stdout-coupled architecture, which limits deployment options.

**With 2-3 focused days of fixes, this could be a genuinely useful experimental framework.**

---

## 13. Recommended Next Steps (Prioritized)

### Immediate (Day 1)

1. Fix `setup.sh` — move banner to end, add `uv sync`
2. Fix `requests` import — make it conditional in `runtime.py`
3. Fix `core/__init__.py` Portuguese comment
4. Remove or repurpose `main.py`
5. Fix path traversal — use `os.path.realpath()` in all tools
6. Strip env vars from `run_python` subprocess

### Short-Term (Week 1)

7. Consolidate `.env` loading into `core/config.py`
8. Add conversation memory (per-agent history file)
9. Improve TOOL/ARGS parser robustness
10. Add retry logic for malformed LLM responses
11. Protect immutable files (`VALUES.md`, `core/`) at the tool level
12. Add `--version` flag
13. Fix `send_message` missing from Architect README

### Medium-Term (Week 2-4)

14. Add basic unit tests for parser and tools
15. Implement Router Agent proposal
16. Add a string-return mode to `run_agent()` for non-CLI use
17. Add token/cost tracking
18. Build a simple web API layer
19. Add tool result size limits

### Long-Term (Month 2+)

20. Implement Evolution Agent proposal
21. Add proper sandboxing for `run_python` (Docker/nsjail)
22. Build chat platform integrations (Telegram, Discord)
23. Add a web UI
24. Add tool versioning
25. Add Anthropic Claude as a native provider
