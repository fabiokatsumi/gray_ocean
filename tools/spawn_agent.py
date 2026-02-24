"""
spawn_agent — Creates a new agent in Gray Ocean.

Unix analog: fork + mkdir
Input: name (str) — agent name
       purpose (str) — agent purpose/mission
       tools (list[str]) — list of authorized tool names
       personality (str, optional) — personality traits
Output: confirmation or error

Usage example:
    result = run(
        name="monitor",
        purpose="Monitors changes in gray ocean files",
        tools=["read_file", "list_dir", "append_file"],
        personality="Vigilant, methodical, reports anomalies clearly"
    )
"""

import os
from datetime import datetime

TOOL_NAME = "spawn_agent"
TOOL_DESCRIPTION = "Creates a new agent with its folder and 5 .md files. Receives 'name', 'purpose', 'tools' (list of authorized tools), and optionally 'personality'."
TOOL_PARAMETERS = {
    "name": "Agent name (used as folder name)",
    "purpose": "Agent purpose/mission",
    "tools": "List of tool names the agent can use",
    "personality": "(Optional) Personality traits of the agent"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(BASE_DIR, "agents")


BASE_TOOLS = ["read_file", "append_file", "list_dir"]


def run(name: str, purpose: str, tools: list = None, personality: str = "") -> str:
    """Creates the agent folder with its 5 .md files."""
    if tools is None:
        tools = []

    # Validation
    safe_name = name.lower().replace(" ", "_").replace("-", "_")
    if not safe_name.isidentifier():
        return f"ERROR: Name '{name}' is invalid for an agent."

    agent_dir = os.path.join(AGENTS_DIR, safe_name)
    if os.path.exists(agent_dir):
        return f"ERROR: Agent '{safe_name}' already exists in agents/{safe_name}/."

    specific_tools = [t for t in tools if t not in BASE_TOOLS]
    all_tools = BASE_TOOLS + specific_tools

    today = datetime.now().strftime("%Y-%m-%d")
    tools_list = ", ".join(all_tools)
    base_md_items = "\n".join(f"- `{t}`" for t in BASE_TOOLS)
    specific_md_items = "\n".join(f"- `{t}`" for t in specific_tools) if specific_tools else "- (no specific tools)"

    if not personality:
        personality = "Focused, efficient, communicates results clearly."

    # Content of the 5 .md files
    files = {
        "README.md": f"""# Agent: {safe_name}

## Purpose
{purpose}

## Created on
{today}

## Authorized Tools
{tools_list}

## Inputs
- Natural language messages related to its mission

## Outputs
- Text responses with results of executed actions
- Records in log.md for each action
""",
        "personality.md": f"""# Personality — {safe_name}

{personality}

## Communication Style
- Responds objectively and clearly
- Logs its actions and reasoning
- When it doesn't know something, says so explicitly
- Errors are reported with context for diagnosis
""",
        "system_prompt.md": f"""# System Prompt — {safe_name}

You are the **{safe_name}** agent of the Gray Ocean framework.

## Your Mission
{purpose}

## Rules
1. Use ONLY the tools listed in tools.md
2. Log EVERY action in log.md using append_file
3. When you don't know how to resolve something, say so explicitly
4. Follow the values in VALUES.md in all decisions
5. Prefer simple solutions over complex ones

## CRITICAL RULE — Never fake actions
You CANNOT modify files just by "thinking" about it. For any changes:
- To CREATE/OVERWRITE: use write_file with TOOL/ARGS
- To ADD content: use append_file with TOOL/ARGS
Reading a file is NOT modifying it. NEVER say "done" without having called the tool.

## Response Format
When you need to use a tool, respond EXACTLY in this format:

TOOL: tool_name
ARGS:
param1: value1
param2: value2

When the task is complete, respond with:

DONE: your final response here
""",
        "tools.md": f"""# Authorized Tools — {safe_name}

This agent has access to the following tools:

## Base Tools (all agents)
{base_md_items}

## Specific Tools
{specific_md_items}

> Least privilege principle: this agent accesses ONLY these tools.
> To request access to additional tools, the change must be approved.
""",
        "log.md": f"""# Log — {safe_name}

## {today} — Creation
- Agent created by the system
- Purpose: {purpose}
- Authorized tools: {tools_list}

---
""",
    }

    try:
        os.makedirs(agent_dir, exist_ok=True)

        for filename, content in files.items():
            filepath = os.path.join(agent_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        return (
            f"OK: Agent '{safe_name}' created successfully in agents/{safe_name}/.\n"
            f"Files created: {', '.join(files.keys())}\n"
            f"Authorized tools: {tools_list}"
        )

    except Exception as e:
        return f"ERROR creating agent '{safe_name}': {e}"
