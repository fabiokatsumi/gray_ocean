# GUIDE.md — Gray Ocean Guide

> Guide for humans and agents interacting with Gray Ocean.

---

## For Humans

### How to use

```bash
# Set up the environment (first time)
bash setup.sh

# Send a message to the Architect
python gray_ocean.py "your message here"

# Examples
python gray_ocean.py "list all available tools"
python gray_ocean.py "create a tool that calculates fibonacci"
python gray_ocean.py "I need an agent that monitors files"
```

### What happens when you send a message?

1. `gray_ocean.py` receives your message
2. `core/runtime.py` loads the Architect agent
3. The Architect reasons about how to resolve your request
4. It uses tools as needed (read files, execute code, etc.)
5. If it needs something that doesn't exist, it creates it (tool or agent)
6. You receive the final response

### How to check what happened?

- Read `agents/architect/log.md` to see all Architect actions
- Read `tools/index.md` to see all available tools
- List `agents/` to see all existing agents

### How to audit the system?

All Gray Ocean state is stored in readable Markdown files:
- Each agent has a `log.md` with complete history
- `tools/index.md` catalogs all tools
- `gray_ocean_ideas/` shows framework change proposals

---

## For Agents

### Conventions

1. **Every action must be logged** in the agent's `log.md`
2. **Check what exists before creating** — read `tools/index.md`
3. **Use only authorized tools** — listed in your `tools.md`
4. **Follow the values** — read and respect `VALUES.md`
5. **Response format** — use TOOL/DONE as defined in system_prompt.md

### How to create a tool

1. Write Python code with a `run()` function and docstring
2. Test with `run_python` to validate
3. Register with `register_tool` to make it available

### How to create an agent

Use the `spawn_agent` tool with:
- `name`: agent name
- `purpose`: mission/purpose
- `tools`: list of tools the agent needs
- `personality` (optional): personality traits

### Framework change proposals

To propose changes to `core/`, `VALUES.md`, or folder structure:
1. Write the proposal in `gray_ocean_ideas/pending_ideas.md`
2. Follow the standardized format
3. Wait for approval before implementing

> Changes to tools and agents do NOT need a proposal — create directly.
